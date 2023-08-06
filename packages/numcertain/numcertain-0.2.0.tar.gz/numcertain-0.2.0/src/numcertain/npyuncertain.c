#include "npyuncertain.h"

PyObject *npyuncertain_getitem(void *data, void *arr)
{
    Uncertain_t u;
    memcpy(&u, data, sizeof(Uncertain_t));
    return PyUncertain_from_Uncertain(u);
};

int npyuncertain_setitem(PyObject *item, void *data, void *arr)
{
    Uncertain_t u;
    if (PyUncertain_Check(item))
        u = ((PyUncertain_t *)item)->u;
    else
    {
        long long n = PyLong_AsLongLong(item);
        if (error_converting(n))
            return -1;
        PyObject *y = PyLong_FromLongLong(n);
        if (!y)
            return -1;
        int eq = PyObject_RichCompareBool(item, y, Py_EQ);
        Py_DECREF(y);
        if (eq < 0)
            return -1;
        if (!eq)
            PyErr_Format(
                PyExc_TypeError,
                "expected uncertain, got %s", item->ob_type->tp_name);
        u = make_uncertain_long(n);
    }
    memcpy(data, &u, sizeof(Uncertain_t));
    return 0;
};

#define BYTESWAP(Type)                           \
    inline void byteswap_##Type(Type *x)         \
    {                                            \
        char *p = (char *)x;                     \
        size_t i;                                \
        for (i = 0; i < sizeof(Type *) / 2; i++) \
        {                                        \
            size_t j = sizeof(*x) - 1 - i;       \
            char t = p[i];                       \
            p[i] = p[j];                         \
            p[j] = t;                            \
        }                                        \
    };

BYTESWAP(double)

void npyuncertain_copyswapn(
    void *dst_,
    npy_intp dstride,
    void *src_,
    npy_intp sstride,
    npy_intp n,
    int swap,
    void *arr)
{
    char *dst = (char *)dst_,
         *src = (char *)src_;
    if (!src)
        return;
    if (swap)
    {
        for (npy_intp i = 0; i < n; i++)
        {
            Uncertain_t *u = (Uncertain_t *)(dst + dstride * i);
            memcpy(u, src + sstride * i, sizeof(Uncertain_t));
            byteswap_double(&u->nominal);
            byteswap_double(&u->uncertainity);
        }
    }
    else if (dstride == sizeof(Uncertain_t) && sstride == sizeof(Uncertain_t))
    {
        memcpy(dst, src, n * sizeof(Uncertain_t));
    }
    else
    {
        for (npy_intp i = 0; i < n; i++)
        {
            memcpy(dst + dstride * i, src + sstride * i, sizeof(Uncertain_t));
        }
    }
};

void npyuncertain_copyswap(
    void *dst,
    void *src,
    int swap,
    void *arr)
{
    if (!src)
        return;
    Uncertain_t *u = (Uncertain_t *)dst;
    memcpy(u, src, sizeof(Uncertain_t));
    if (swap)
    {
        byteswap_double(&u->nominal);
        byteswap_double(&u->uncertainity);
    }
};

npy_bool npyuncertain_nonzero(void *data, void *arr)
{
    Uncertain_t u;
    memcpy(&u, data, sizeof(Uncertain_t));
    return uncertain_nonzero(u) ? NPY_TRUE : NPY_FALSE;
}

PyArray_ArrFuncs npyuncertain_arrfuncs;

PyArray_Descr npyuncertain_descr = {
    PyObject_HEAD_INIT(0) & PyUncertain_Type,            // typeobj
    'V',                                                 // kind
    'r',                                                 // type
    '=',                                                 // byteorder
    NPY_NEEDS_PYAPI | NPY_USE_GETITEM | NPY_USE_SETITEM, // hasobject
    0,                                                   // type_num
    sizeof(Uncertain_t),                                 // elsize
    offsetof(align_test, u),                             // alignment
    0,                                                   // subarray
    0,                                                   // fields
    0,                                                   // names
    &npyuncertain_arrfuncs};                             // f

#define DEFINE_CAST(From, To, statement)  \
    void npycast_##From##_##To(           \
        void *from_,                      \
        void *to_,                        \
        npy_intp n,                       \
        void *fromarr,                    \
        void *toarr)                      \
    {                                     \
        const From *from = (From *)from_; \
        To *to = (To *)to_;               \
        for (npy_intp i = 0; i < n; i++)  \
        {                                 \
            From x = from[i];             \
            statement;                    \
            to[i] = y;                    \
        }                                 \
    }

#define DEFINE_FLOAT_CAST(bits)                          \
    DEFINE_CAST(                                         \
        npy_float##bits,                                 \
        Uncertain_t,                                     \
        Uncertain_t y = make_uncertain_double(x);)       \
    DEFINE_CAST(Uncertain_t,                             \
                npy_float##bits,                         \
                npy_float##bits z = uncertain_double(x); \
                npy_float##bits y = z;                   \
                if (y != z) set_overflow();)

#define DEFINE_INT_CAST(bits)                        \
    DEFINE_CAST(                                     \
        npy_int##bits,                               \
        Uncertain_t,                                 \
        Uncertain_t y = make_uncertain_long(x);)     \
    DEFINE_CAST(Uncertain_t,                         \
                npy_int##bits,                       \
                npy_int##bits z = uncertain_long(x); \
                npy_int##bits y = z;                 \
                if (y != z) set_overflow();)

DEFINE_FLOAT_CAST(32)
DEFINE_FLOAT_CAST(64)

DEFINE_INT_CAST(8)
DEFINE_INT_CAST(16)
DEFINE_INT_CAST(32)
DEFINE_INT_CAST(64)

DEFINE_CAST(npy_bool, Uncertain_t, Uncertain_t y = make_uncertain_long(x);)
DEFINE_CAST(Uncertain_t, npy_bool, npy_bool y = uncertain_nonzero(x);)

#define UNCERTAIN_BINOP_UFUNC(name, outtype, exp)           \
    void uncertain_ufunc_##name(char **args,                \
                                npy_intp const *dimensions, \
                                npy_intp const *steps,      \
                                void *data)                 \
    {                                                       \
        npy_intp in_a_step = steps[0],                      \
                 in_b_step = steps[1],                      \
                 out_step = steps[2];                       \
                                                            \
        char *in_a = args[0],                               \
             *in_b = args[1],                               \
             *out = args[2];                                \
                                                            \
        for (int i = 0; i < *dimensions; i++)               \
        {                                                   \
            Uncertain_t a = *(Uncertain_t *)in_a;           \
            Uncertain_t b = *(Uncertain_t *)in_b;           \
            *(outtype *)out = exp(a, b);                    \
            in_a += in_a_step;                              \
            in_b += in_b_step;                              \
            out += out_step;                                \
        }                                                   \
    }

UNCERTAIN_BINOP_UFUNC(add, Uncertain_t, uncertain_add)
UNCERTAIN_BINOP_UFUNC(subtract, Uncertain_t, uncertain_subtract)
UNCERTAIN_BINOP_UFUNC(multiply, Uncertain_t, uncertain_multiply)
UNCERTAIN_BINOP_UFUNC(divide, Uncertain_t, uncertain_divide)

UNCERTAIN_BINOP_UFUNC(equal, bool, uncertain_eq)
UNCERTAIN_BINOP_UFUNC(not_equal, bool, uncertain_ne)