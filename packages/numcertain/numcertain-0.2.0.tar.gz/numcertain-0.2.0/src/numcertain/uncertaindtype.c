#include "uncertaindtype.h"

void set_overflow(void)
{
    if (!PyErr_Occurred())
    {
        PyErr_SetString(
            PyExc_OverflowError,
            "overflow in Uncertain_t arithmetic");
    }
}

Uncertain_t make_uncertain_longs(long nominal, long uncertainty)
{
    Uncertain_t u = {nominal, uncertainty};
    if (u.nominal != nominal || u.uncertainity != uncertainty)
        set_overflow();
    return u;
};

Uncertain_t make_uncertain_long(long nominal)
{
    return make_uncertain_longs(nominal, 0);
};

Uncertain_t make_uncertain_doubles(double nominal, double uncertainty)
{
    Uncertain_t u = {nominal, uncertainty};
    return u;
};

Uncertain_t make_uncertain_double(double nominal)
{
    return make_uncertain_doubles(nominal, 0);
};

Uncertain_t uncertain_add(Uncertain_t a, Uncertain_t b)
{
    Uncertain_t result = {
        a.nominal + b.nominal, hypot(a.uncertainity, b.uncertainity)};
    return result;
};

Uncertain_t uncertain_subtract(Uncertain_t a, Uncertain_t b)
{
    Uncertain_t result = {
        a.nominal - b.nominal, hypot(a.uncertainity, b.uncertainity)};
    return result;
};

Uncertain_t uncertain_multiply(Uncertain_t a, Uncertain_t b)
{
    Uncertain_t result = {
        a.nominal * b.nominal,
        (a.nominal * b.nominal) * hypot(a.uncertainity / a.nominal, b.uncertainity / b.nominal)};
    return result;
};

Uncertain_t uncertain_divide(Uncertain_t a, Uncertain_t b)
{
    Uncertain_t result = {
        a.nominal / b.nominal,
        (a.nominal / b.nominal) * hypot(a.uncertainity / a.nominal, b.uncertainity / b.nominal)};
    return result;
};

double uncertain_double(Uncertain_t u)
{
    return u.nominal;
};

long uncertain_long(Uncertain_t u)
{
    return (long)u.nominal;
};

bool uncertain_eq(Uncertain_t a, Uncertain_t b)
{
    return a.nominal == b.nominal && a.uncertainity == b.uncertainity;
};

bool uncertain_ne(Uncertain_t a, Uncertain_t b)
{
    return a.nominal != b.nominal || a.uncertainity != b.uncertainity;
};

int uncertain_nonzero(Uncertain_t u)
{
    return u.nominal != 0 || u.uncertainity != 0;
};

int PyUncertain_Check(PyObject *object)
{
    return PyObject_IsInstance(object, (PyObject *)&PyUncertain_Type);
};

PyObject *PyUncertain_from_Uncertain(Uncertain_t u)
{
    PyUncertain_t *py_uncertain = (PyUncertain_t *)PyUncertain_Type.tp_alloc(&PyUncertain_Type, 0);
    if (py_uncertain)
    {
        py_uncertain->u = u;
    }
    return (PyObject *)py_uncertain;
}

PyObject *PyUncertain_new(PyTypeObject *type, PyObject *args, PyObject *kwds)
{
    if (kwds && PyDict_Size(kwds))
    {
        PyErr_SetString(
            PyExc_TypeError,
            "constructor takes no keyword arguments");
        return NULL;
    }

    Py_ssize_t n_args = PyTuple_GET_SIZE(args);
    if (n_args > 2)
    {
        PyErr_SetString(
            PyExc_TypeError,
            "constructor expects nominal and optional uncertainity");
        return NULL;
    };

    if (n_args == 1)
    {
        PyObject *arg = PyTuple_GET_ITEM(args, 0);
        if (PyUncertain_Check(arg))
        {
            Py_INCREF(arg);
            return arg;
        }
        else if (PyLong_Check(arg) || PyFloat_Check(arg))
        {
            double nominal = PyFloat_AsDouble(arg);
            Uncertain_t u = make_uncertain_double(nominal);
            return PyUncertain_from_Uncertain(u);
        }
    }

    if (n_args == 2)
    {
        PyObject *py_nominal = PyTuple_GET_ITEM(args, 0);
        double nominal = PyFloat_AsDouble(py_nominal);

        PyObject *py_uncertainty = PyTuple_GET_ITEM(args, 1);
        double uncertainty = PyFloat_AsDouble(py_uncertainty);

        Uncertain_t u = make_uncertain_doubles(nominal, uncertainty);
        return PyUncertain_from_Uncertain(u);
    }

    return NULL;
};

PyObject *PyUncertain_repr(PyObject *self)
{
    Uncertain_t u = ((PyUncertain_t *)self)->u;
    char *nominal_str = PyOS_double_to_string(u.nominal, 'r', 0, Py_DTSF_ADD_DOT_0, NULL);
    char *uncertainty_str = PyOS_double_to_string(u.uncertainity, 'r', 0, Py_DTSF_ADD_DOT_0, NULL);
    return PyUnicode_FromFormat("uncertain(%s, %s)", nominal_str, uncertainty_str);
};

#define UNCERTAIN_BINOP(name)                                  \
    PyObject *PyUncertain_##name(PyObject *pya, PyObject *pyb) \
    {                                                          \
        Uncertain_t a = ((PyUncertain_t *)pya)->u;             \
        Uncertain_t b = ((PyUncertain_t *)pyb)->u;             \
        return PyUncertain_from_Uncertain(                     \
            uncertain_##name(a, b));                           \
    };

UNCERTAIN_BINOP(add)
UNCERTAIN_BINOP(subtract)
UNCERTAIN_BINOP(multiply)
UNCERTAIN_BINOP(divide)

PyObject *PyUncertain_int(PyObject *self)
{
    Uncertain_t u = ((PyUncertain_t *)self)->u;
    return PyLong_FromDouble(u.nominal);
};

PyObject *PyUncertain_float(PyObject *self)
{
    Uncertain_t u = ((PyUncertain_t *)self)->u;
    return PyFloat_FromDouble(u.nominal);
};

PyNumberMethods PyUncertain_as_number = {
    PyUncertain_add,      // nb_add
    PyUncertain_subtract, // nb_subtract
    PyUncertain_multiply, // nb_multiply
    0,                    // nb_remainer
    0,                    // nb_divmod
    0,                    // nb_power
    0,                    // nb_negative
    0,                    // nb_positive
    0,                    // nb_absolute
    0,                    // nb_bool
    0,                    // nb_invert
    0,                    // nb_lshift
    0,                    // nb_rshift
    0,                    // nb_and
    0,                    // nb_xor
    0,                    // nb_or
    PyUncertain_int,      // nb_int
    0,                    // nb_reserved
    PyUncertain_float,    // nb_float
    0,                    // nb_inplace_add
    0,                    // nb_inplace_subtract
    0,                    // nb_inplace_multiply
    0,                    // nb_inplace_remainder
    0,                    // nb_inplace_power
    0,                    // nb_inplace_lshift
    0,                    // nb_inplace_rshift
    0,                    // nb_inplace_and
    0,                    // nb_inplace_xor
    0,                    // nb_inplace_or
    0,                    // nb_floor_divide
    PyUncertain_divide,   // nb_true_divide
    0,                    // nb_inplace_floor_divide
    0,                    // nb_inplace_true_divide
    0,                    // nb_index
    0,                    // nb_matrix_multiply
    0                     // nb_inplace_matrix_multiply
};

Py_hash_t PyUncertain_hash(PyObject *self)
{
    Uncertain_t u = ((PyUncertain_t *)self)->u;
    long hash = 131071 * u.nominal + 524287 * u.uncertainity;
    return hash == -1 ? 2 : hash;
};

PyObject *PyUncertain_str(PyObject *self)
{
    Uncertain_t u = ((PyUncertain_t *)self)->u;
    char *nominal_str = PyOS_double_to_string(u.nominal, 'r', 0, Py_DTSF_ADD_DOT_0, NULL);
    char *uncertainty_str = PyOS_double_to_string(u.uncertainity, 'r', 0, Py_DTSF_ADD_DOT_0, NULL);
    PyObject *plus_minus = PyUnicode_FromOrdinal(0x000000B1);
    return PyUnicode_FromFormat("%s%U%s", nominal_str, plus_minus, uncertainty_str);
};

PyTypeObject *PyUncertain_richcompare(PyObject *self, PyObject *other, int op)
{
    Uncertain_t uncertain_self = ((PyUncertain_t *)self)->u;
    Uncertain_t uncertain_other = ((PyUncertain_t *)other)->u;
    switch (op)
    {
    case Py_EQ:
        if (uncertain_eq(uncertain_self, uncertain_other))
            Py_RETURN_TRUE;
        else
            Py_RETURN_FALSE;
    case Py_NE:
        if (uncertain_ne(uncertain_self, uncertain_other))
            Py_RETURN_TRUE;
        else
            Py_RETURN_FALSE;
    default:
        Py_RETURN_FALSE;
    }
};

PyObject *PyUncertain_nominal(PyObject *self, void *closure)
{
    return PyFloat_FromDouble(((PyUncertain_t *)self)->u.nominal);
};

PyObject *PyUncertain_uncertainty(PyObject *self, void *closure)
{
    Uncertain_t u = ((PyUncertain_t *)self)->u;
    return PyFloat_FromDouble(u.uncertainity);
};

PyGetSetDef PyUncertain_getset[] = {
    {(char *)"nominal", PyUncertain_nominal, 0, "nominal value", 0},
    {(char *)"uncertainty", PyUncertain_uncertainty, 0, "uncertainty", 0},
    {0}};

PyTypeObject PyUncertain_Type = {
    PyVarObject_HEAD_INIT(NULL, 0) "numcertain.uncertain", // tp_name
    sizeof(PyUncertain_t),                                 // tp_basicssize
    0,                                                     // tp_itemsize
    0,                                                     // tp_dealloc
    0,                                                     // tp_vectorcall_offset
    0,                                                     // tp_getattr
    0,                                                     // tp_setattr
    0,                                                     // tp_as_async
    PyUncertain_repr,                                      // tp_repr
    &PyUncertain_as_number,                                // tp_as_number
    0,                                                     // tp_as_sequence
    0,                                                     // tp_as_mapping
    PyUncertain_hash,                                      // tp_hash
    0,                                                     // tp_call
    PyUncertain_str,                                       // tp_str
    0,                                                     // tp_getattro
    0,                                                     // tp_setattro
    0,                                                     // tp_as_buffer
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE,              // tp_flags
    "Fixed precision number with quantified uncertainty",  // tp_doc
    0,                                                     // tp_traverse
    0,                                                     // tp_clear
    PyUncertain_richcompare,                               // tp_richcompare
    0,                                                     // tp_weaklistoffset
    0,                                                     // tp_iter
    0,                                                     // tp_iternext
    0,                                                     // tp_methods
    0,                                                     // tp_members
    PyUncertain_getset,                                    // tp_getset
    0,                                                     // tp_base
    0,                                                     // tp_dict
    0,                                                     // tp_descr_get
    0,                                                     // tp_descr_set
    0,                                                     // tp_dictoffset
    0,                                                     // tp_init
    0,                                                     // tp_alloc
    PyUncertain_new,                                       // tp_new
    0,                                                     // tp_free
    0,                                                     // tp_is_gc
    0,                                                     // tp_bases
    0,                                                     // tp_mro
    0,                                                     // tp_cache
    0,                                                     // tp_subclasses
    0,                                                     // tp_weaklist
    0,                                                     // tp_del
    0,                                                     // tp_version_tag
    0,                                                     // tp_finalize
    0,                                                     // tp_vectorcall
};
