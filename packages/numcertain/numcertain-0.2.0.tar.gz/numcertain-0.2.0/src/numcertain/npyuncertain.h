#ifndef NPYUNCERTAIN_H
#define NPYUNCERTAIN_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

#define NPY_NO_DEPRECATED_API NPY_API_VERSION
#include "numpy/arrayobject.h"
#include "numpy/ufuncobject.h"
#include "numpy/npy_3kcompat.h"

#include "uncertaindtype.h"

PyObject *npyuncertain_getitem(void *data, void *arr);
int npyuncertain_setitem(PyObject *item, void *data, void *arr);
void npyuncertain_copyswapn(
    void *dst_,
    npy_intp dstride,
    void *src_,
    npy_intp sstride,
    npy_intp n,
    int swap,
    void *arr);
void npyuncertain_copyswap(
    void *dst,
    void *src,
    int swap,
    void *arr);
npy_bool npyuncertain_nonzero(void *data, void *arr);

extern PyArray_Descr npyuncertain_descr;

typedef struct
{
    char c;
    Uncertain_t u;
} align_test;

extern PyArray_ArrFuncs npyuncertain_arrfuncs;

#define DEFINE_CAST(From, To, statement) \
    void npycast_##From##_##To(          \
        void *from_,                     \
        void *to_,                       \
        npy_intp n,                      \
        void *fromarr,                   \
        void *toarr);

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

#undef DEFINE_INT_CAST
#undef DEFINE_FLOAT_CAST
#undef DEFINE_CAST

#define BINOP_UFUNC(name)                                   \
    void uncertain_ufunc_##name(char **args,                \
                                npy_intp const *dimensions, \
                                npy_intp const *steps,      \
                                void *data);

BINOP_UFUNC(add)
BINOP_UFUNC(subtract)
BINOP_UFUNC(multiply)
BINOP_UFUNC(divide)

BINOP_UFUNC(equal)
BINOP_UFUNC(not_equal)

#undef BINOP_UFUNC

#endif