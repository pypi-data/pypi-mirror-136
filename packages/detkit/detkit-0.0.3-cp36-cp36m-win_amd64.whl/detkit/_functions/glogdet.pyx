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
from .._definitions.types cimport LongIndexType, FlagType
from .._c_linear_algebra.c_matrix_functions cimport cMatrixFunctions

# To avoid cython's bug that does not recognizes "long double" in template []
ctypedef long double long_double

__all__ = ['glogdet']


# =======
# glogdet
# =======

def glogdet(A, X, sym_pos=False, method='proj', X_orth=False, flops=False):
    """
    """

    if method not in ['legacy', 'proj']:
        raise ValueError('"method" should be either "legacy" or "proj".')
    elif method == 'legacy':
        method = 0
    elif method == 'proj':
        method = 1

    # flops determines whether to compute flops of the algorithm
    flops = int(flops)

    # X_orth only applicable to proj method
    if X_orth and method == 'legacy':
        raise ValueError('"X_orth=True" can only used in "proj" method.')
    else:
        X_orth = int(X_orth)

    # sym_pos is only applicable to legacy method
    if sym_pos and method == 'proj':
        raise ValueError('"sym_pos=True" can only used in "legacy" method.')
    else:
        sym_pos = int(sym_pos)

    data_type_name = get_data_type_name(A)
    glogdet_, sign, flops_ = pyc_glogdet(A, X, A.shape[0], X.shape[1],
                                         data_type_name, sym_pos, method,
                                         X_orth, flops)

    if flops != 0:
        return glogdet_, sign, flops_
    else:
        return glogdet_, sign


# ===========
# pyc glogdet
# ===========

cpdef pyc_glogdet(
        A,
        X,
        num_rows,
        num_columns,
        data_type_name,
        sym_pos,
        method,
        X_orth,
        flops):
    """
    """

    sign = numpy.array([0], dtype=numpy.int32)
    cdef FlagType[:] mv_sign = sign
    cdef FlagType* c_sign = &mv_sign[0]
    cdef long long flops_ = flops

    if data_type_name == b'float32':
        glogdet_ = pyc_glogdet_float(A, X, num_rows, num_columns, sym_pos,
                                     method, X_orth, c_sign, flops_)
    elif data_type_name == b'float64':
        glogdet_ = pyc_glogdet_double(A, X, num_rows, num_columns, sym_pos,
                                      method, X_orth, c_sign, flops_)
    elif data_type_name == b'float128':
        glogdet_ = pyc_glogdet_long_double(A, X, num_rows, num_columns,
                                           method, X_orth, sym_pos, c_sign,
                                           flops_)
    else:
        raise TypeError('Data type should be "float32", "float64", or ' +
                        '"float128".')

    if sign[0] == -2:
        glogdet_ = -numpy.inf
    elif sign[0] == 2:
        glogdet_ = numpy.inf

    return glogdet_, sign[0], flops_


# =================
# pyc glogdet float
# =================

cdef float pyc_glogdet_float(
        float[:, ::1] A,
        float[:, ::1] X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType method,
        const FlagType X_orth,
        FlagType* sign,
        long long& flops) except *:
    """
    """

    # Get c-pointer from memoryviews
    cdef float* c_A = &A[0, 0]
    cdef float* c_X = &X[0, 0]

    # Compute glogdet
    cdef float glogdet_ = cMatrixFunctions[float].glogdet(
            c_A, c_X, num_rows, num_columns, sym_pos, method, X_orth, sign[0],
            flops)

    return glogdet_


# ==================
# pyc glogdet double
# ==================

cdef double pyc_glogdet_double(
        double[:, ::1] A,
        double[:, ::1] X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType method,
        const FlagType X_orth,
        FlagType* sign,
        long long& flops) except *:
    """
    """

    # Get c-pointer from memoryviews
    cdef double* c_A = &A[0, 0]
    cdef double* c_X = &X[0, 0]

    # Compute glogdet
    cdef double glogdet_ = cMatrixFunctions[double].glogdet(
            c_A, c_X, num_rows, num_columns, sym_pos, method, X_orth, sign[0],
            flops)

    return glogdet_


# =======================
# pyc glogdet long double
# =======================

cdef long double pyc_glogdet_long_double(
        long double[:, ::1] A,
        long double[:, ::1] X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType method,
        const FlagType X_orth,
        FlagType* sign,
        long long& flops) except *:
    """
    """

    # Get c-pointer from memoryviews
    cdef long double* c_A = &A[0, 0]
    cdef long double* c_X = &X[0, 0]

    # Compute glogdet
    cdef long double glogdet_ = cMatrixFunctions[long_double].glogdet(
            c_A, c_X, num_rows, num_columns, sym_pos, method, X_orth, sign[0],
            flops)

    return glogdet_
