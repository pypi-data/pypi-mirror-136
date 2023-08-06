# SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

import numpy
from ._utilities import get_data_type_name
from .._definitions.types cimport DataType, LongIndexType, FlagType, \
        MemoryViewIndexType, MemoryViewFlagType
from .._c_linear_algebra.c_matrix_functions cimport cMatrixFunctions

# To avoid cython's bug that does not recognizes "long double" in template []
ctypedef long double long_double

__all__ = ['logdet']


# ======
# logdet
# ======

def logdet(A, sym_pos=False):
    """
    """

    data_type_name = get_data_type_name(A)
    sym_pos = int(sym_pos)
    logdet_, sign = pyc_logdet(A, A.shape[0], data_type_name, sym_pos)

    return logdet_, sign


# ==========
# pyc logdet
# ==========

cpdef pyc_logdet(
        A,
        num_rows,
        data_type_name,
        sym_pos):
    """
    """

    sign = numpy.array([0], dtype=numpy.int32)
    cdef FlagType[:] mv_sign = sign
    cdef FlagType* c_sign = &mv_sign[0]

    if data_type_name == b'float32':
        logdet_ = pyc_logdet_float(A, num_rows, sym_pos, c_sign)
    elif data_type_name == b'float64':
        logdet_ = pyc_logdet_double(A, num_rows, sym_pos, c_sign)
    elif data_type_name == b'float128':
        logdet_ = pyc_logdet_long_double(A, num_rows, sym_pos, c_sign)
    else:
        raise TypeError('Data type should be "float32", "float64", or ' +
                        '"float128".')

    if sign[0] == -2:
        logdet_ = -numpy.inf
    if sign[0] == 2:
        logdet_ = numpy.inf

    return logdet_, sign[0]


# ================
# pyc logdet float
# ================

cdef float pyc_logdet_float(
        float[:, ::1] A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType* sign) except *:
    """
    """

    # Get c-pointer from memoryviews
    cdef float* c_A = &A[0, 0]

    # Compute logdet
    cdef float logdet_ = cMatrixFunctions[float].logdet(
            c_A, num_rows, sym_pos, sign[0])

    return logdet_


# =================
# pyc logdet double
# =================

cdef double pyc_logdet_double(
        double[:, ::1] A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType* sign) except *:
    """
    """

    # Get c-pointer from memoryviews
    cdef double* c_A = &A[0, 0]

    # Compute logdet
    cdef double logdet_ = cMatrixFunctions[double].logdet(
            c_A, num_rows, sym_pos, sign[0])

    return logdet_


# ======================
# pyc logdet long double
# ======================

cdef long double pyc_logdet_long_double(
        long double[:, ::1] A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType* sign) except *:
    """
    """

    # Get c-pointer from memoryviews
    cdef long double* c_A = &A[0, 0]

    # Compute logdet
    cdef long double logdet_ = cMatrixFunctions[long_double].logdet(
            c_A, num_rows, sym_pos, sign[0])

    return logdet_
