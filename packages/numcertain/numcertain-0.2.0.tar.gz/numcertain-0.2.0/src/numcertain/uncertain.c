#include "uncertain.h"

static PyMethodDef module_methods[] = {
    {0}};

static struct PyModuleDef moduledef = {
    PyModuleDef_HEAD_INIT,
    "uncertain",
    NULL,
    -1,
    module_methods,
    NULL,
    NULL,
    NULL,
    NULL};

PyMODINIT_FUNC PyInit_uncertain(void)
{
    import_array();
    import_umath();

    PyObject *numpy_str = PyUnicode_FromString("numpy");
    if (!numpy_str)
        return NULL;
    PyObject *numpy = PyImport_Import(numpy_str);
    Py_DECREF(numpy_str);
    if (!numpy)
        return NULL;

    PyUncertain_Type.tp_base = &PyGenericArrType_Type;

    if (PyType_Ready(&PyUncertain_Type) < 0)
        return NULL;

    PyArray_InitArrFuncs(&npyuncertain_arrfuncs);
    npyuncertain_arrfuncs.getitem = npyuncertain_getitem;
    npyuncertain_arrfuncs.setitem = npyuncertain_setitem;
    npyuncertain_arrfuncs.copyswapn = npyuncertain_copyswapn;
    npyuncertain_arrfuncs.copyswap = npyuncertain_copyswap;
    npyuncertain_arrfuncs.nonzero = npyuncertain_nonzero;

    Py_SET_TYPE(&npyuncertain_descr, &PyArrayDescr_Type);

    int npy_uncertain = PyArray_RegisterDataType(&npyuncertain_descr);
    if (npy_uncertain < 0)
    {
        return NULL;
    }

    if (PyDict_SetItemString(PyUncertain_Type.tp_dict, "dtype",
                             (PyObject *)&npyuncertain_descr) < 0)
        return NULL;

#define REGISTER_CAST(From, To, from_descr, to_typenum, safe) \
    {                                                         \
        if (PyArray_RegisterCastFunc(                         \
                (from_descr),                                 \
                (to_typenum),                                 \
                npycast_##From##_##To) < 0)                   \
            return NULL;                                      \
        if (safe && PyArray_RegisterCanCast(                  \
                        (from_descr),                         \
                        (to_typenum),                         \
                        NPY_NOSCALAR) < 0)                    \
            return NULL;                                      \
    };

#define REGISTER_FLOAT_CAST(bits)               \
    REGISTER_CAST(                              \
        npy_float##bits,                        \
        Uncertain_t,                            \
        PyArray_DescrFromType(NPY_FLOAT##bits), \
        npy_uncertain,                          \
        1)                                      \
    REGISTER_CAST(                              \
        Uncertain_t,                            \
        npy_float##bits,                        \
        &npyuncertain_descr,                    \
        NPY_FLOAT##bits,                        \
        0)

#define REGISTER_INT_CAST(bits)               \
    REGISTER_CAST(                            \
        npy_int##bits,                        \
        Uncertain_t,                          \
        PyArray_DescrFromType(NPY_INT##bits), \
        npy_uncertain,                        \
        1)                                    \
    REGISTER_CAST(                            \
        Uncertain_t,                          \
        npy_int##bits,                        \
        &npyuncertain_descr,                  \
        NPY_INT##bits,                        \
        0)

    REGISTER_FLOAT_CAST(32)
    REGISTER_FLOAT_CAST(64)

    REGISTER_INT_CAST(8)
    REGISTER_INT_CAST(16)
    REGISTER_INT_CAST(32)
    REGISTER_INT_CAST(64)

    REGISTER_CAST(npy_bool, Uncertain_t, PyArray_DescrFromType(NPY_BOOL), npy_uncertain, 1)
    REGISTER_CAST(Uncertain_t, npy_bool, &npyuncertain_descr, NPY_BOOL, 0)

#define REGISTER_UFUNC(name, ...)                                                     \
    {                                                                                 \
        PyUFuncObject *ufunc = (PyUFuncObject *)PyObject_GetAttrString(numpy, #name); \
        if (!ufunc)                                                                   \
        {                                                                             \
            return NULL;                                                              \
        }                                                                             \
        int arg_types[] = __VA_ARGS__;                                                \
        if (sizeof(arg_types) / sizeof(int) != ufunc->nargs)                          \
        {                                                                             \
            Py_DECREF(ufunc);                                                         \
            return NULL;                                                              \
        }                                                                             \
        if (PyUFunc_RegisterLoopForType(                                              \
                (PyUFuncObject *)ufunc,                                               \
                npy_uncertain,                                                        \
                uncertain_ufunc_##name,                                               \
                arg_types,                                                            \
                0) < 0)                                                               \
        {                                                                             \
            Py_DECREF(ufunc);                                                         \
            return NULL;                                                              \
        }                                                                             \
        Py_DECREF(ufunc);                                                             \
    }

#define REGISTER_UFUNC_BINOP_UNCERTAIN(name) \
    REGISTER_UFUNC(name, {npy_uncertain, npy_uncertain, npy_uncertain})
#define REGISTER_UFUNC_BINOP_BOOL(name) \
    REGISTER_UFUNC(name, {npy_uncertain, npy_uncertain, NPY_BOOL})

    REGISTER_UFUNC_BINOP_UNCERTAIN(add)
    REGISTER_UFUNC_BINOP_UNCERTAIN(subtract)
    REGISTER_UFUNC_BINOP_UNCERTAIN(multiply)
    REGISTER_UFUNC_BINOP_UNCERTAIN(divide)

    REGISTER_UFUNC_BINOP_BOOL(equal)
    REGISTER_UFUNC_BINOP_BOOL(not_equal)

    PyObject *module = PyModule_Create(&moduledef);
    if (!module)
        return NULL;

    Py_INCREF(&PyUncertain_Type);
    PyModule_AddObject(module, "uncertain", (PyObject *)&PyUncertain_Type);

    return module;
};
