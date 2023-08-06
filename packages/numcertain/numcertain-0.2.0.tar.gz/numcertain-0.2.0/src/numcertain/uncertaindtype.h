#ifndef UNCERTAINDTYPE_H
#define UNCERTAINDTYPE_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

#include <stdbool.h>
#include <math.h>

#define error_converting(x) (((x) == -1) && PyErr_Occurred())

void set_overflow(void);

typedef struct Uncertain
{
    double nominal;
    double uncertainity;
} Uncertain_t;

Uncertain_t make_uncertain_longs(long nominal, long uncertainty);
Uncertain_t make_uncertain_long(long nominal);
Uncertain_t make_uncertain_doubles(double nominal, double uncertainty);
Uncertain_t make_uncertain_double(double nominal);
Uncertain_t uncertain_add(Uncertain_t a, Uncertain_t b);
Uncertain_t uncertain_subtract(Uncertain_t a, Uncertain_t b);
Uncertain_t uncertain_multiply(Uncertain_t a, Uncertain_t b);
Uncertain_t uncertain_divide(Uncertain_t a, Uncertain_t b);
bool uncertain_eq(Uncertain_t a, Uncertain_t b);
bool uncertain_ne(Uncertain_t a, Uncertain_t b);
double uncertain_double(Uncertain_t u);
long uncertain_long(Uncertain_t u);
int uncertain_nonzero(Uncertain_t u);

typedef struct PyUncertain
{
    PyObject_HEAD
        Uncertain_t u;
} PyUncertain_t;

extern PyTypeObject PyUncertain_Type;

int PyUncertain_Check(PyObject *object);
PyObject *PyUncertain_from_Uncertain(Uncertain_t u);
PyObject *PyUncertain_new(PyTypeObject *type, PyObject *args, PyObject *kwds);
PyObject *PyUncertain_repr(PyObject *self);

#define UNCERTAIN_BINOP(name) \
    PyObject *PyUncertain_##name(PyObject *pya, PyObject *pyb);

UNCERTAIN_BINOP(add)
UNCERTAIN_BINOP(subtract)
UNCERTAIN_BINOP(multiply)
UNCERTAIN_BINOP(divide)

PyObject *PyUncertain_int(PyObject *self);
PyObject *PyUncertain_float(PyObject *self);

#undef UNCERTAIN_BINOP

Py_hash_t PyUncertain_hash(PyObject *self);
PyObject *PyUncertain_str(PyObject *self);
PyObject *PyUncertain_nominal(PyObject *self, void *closure);
PyObject *PyUncertain_uncertainty(PyObject *self, void *closure);
PyTypeObject *PyUncertain_richcompare(PyObject *self, PyObject *other, int op);

PyMODINIT_FUNC PyInit_uncertain(void);

#endif