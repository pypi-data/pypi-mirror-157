#ifndef UNCERTAIN_H
#define UNCERTAIN_H

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#include <structmember.h>

#define NPY_NO_DEPRECATED_API NPY_API_VERSION
#include "numpy/arrayobject.h"
#include "numpy/ufuncobject.h"
#include "numpy/npy_3kcompat.h"

#include "uncertaindtype.h"
#include "npyuncertain.h"

#endif