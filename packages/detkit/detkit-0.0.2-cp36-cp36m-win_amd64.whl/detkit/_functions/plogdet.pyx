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

__all__ = ['plogdet']


# =======
# plogdet
# =======

def plogdet(A, X, sym_pos=False, method='proj', X_orth=False, flops=False):
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

    # X_orth can apply to both legacy and proj methods
    X_orth = int(X_orth)

    # sym_pos is only applicable to legacy method
    if sym_pos and method == 'proj':
        raise ValueError('"sym_pos=True" can only used in "legacy" method.')
    else:
        sym_pos = int(sym_pos)

    data_type_name = get_data_type_name(A)
    plogdet_, sign, flops_ = pyc_plogdet(A, X, A.shape[0], X.shape[1],
                                         data_type_name, sym_pos, method,
                                         X_orth, flops)

    if flops != 0:
        return plogdet_, sign, flops_
    else:
        return plogdet_, sign


# ===========
# pyc plogdet
# ===========

cpdef pyc_plogdet(
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
        plogdet_ = pyc_plogdet_float(A, X, num_rows, num_columns, sym_pos,
                                     method, X_orth, c_sign, flops_)
    elif data_type_name == b'float64':
        plogdet_ = pyc_plogdet_double(A, X, num_rows, num_columns, sym_pos,
                                      method, X_orth, c_sign, flops_)
    elif data_type_name == b'float128':
        plogdet_ = pyc_plogdet_long_double(A, X, num_rows, num_columns,
                                           method, X_orth, sym_pos, c_sign,
                                           flops_)
    else:
        raise TypeError('Data type should be "float32", "float64", or ' +
                        '"float128".')

    if sign[0] == -2:
        plogdet_ = -numpy.inf
    if sign[0] == 2:
        plogdet_ = numpy.inf

    return plogdet_, sign[0], flops_


# =================
# pyc plogdet float
# =================

cdef float pyc_plogdet_float(
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

    # Compute plogdet
    cdef float plogdet_ = cMatrixFunctions[float].plogdet(
            c_A, c_X, num_rows, num_columns, sym_pos, method, X_orth, sign[0],
            flops)

    return plogdet_


# ==================
# pyc plogdet double
# ==================

cdef double pyc_plogdet_double(
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

    # Compute plogdet
    cdef double plogdet_ = cMatrixFunctions[double].plogdet(
            c_A, c_X, num_rows, num_columns, sym_pos, method, X_orth, sign[0],
            flops)

    return plogdet_


# =======================
# pyc plogdet long double
# =======================

cdef long double pyc_plogdet_long_double(
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

    # Compute plogdet
    cdef long double plogdet_ = cMatrixFunctions[long_double].plogdet(
            c_A, c_X, num_rows, num_columns, sym_pos, method, X_orth, sign[0],
            flops)

    return plogdet_
