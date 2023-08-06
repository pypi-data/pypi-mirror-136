/*
 *  SPDX-FileCopyrightText: Copyright 2022, Siavash Ameli <sameli@berkeley.edu>
 *  SPDX-License-Identifier: BSD-3-Clause
 *  SPDX-FileType: SOURCE
 *
 *  This program is free software: you can redistribute it and/or modify it
 *  under the terms of the license found in the LICENSE.txt file in the root
 *  directory of this source tree.
 */


// =======
// Headers
// =======

#include "./c_matrix_functions.h"
#include <cmath>  // log, abs, exp
#include <cstddef>  // NULL
#include "../_c_basic_algebra/c_matrix_operations.h"  // cMatrixOperations
#include "./c_matrix_decompositions.h"  // cMatrixDecompositions
#include "./c_matrix_solvers.h"  // cMatrixSolver
#include "../_device/instructions_counter.h"  // InstructionsCounter
#include "../_definitions/definitions.h"


// ======
// logdet
// ======

/// \brief      Computes the matrix vector multiplication \f$ \boldsymbol{c} =
///             \mathbf{A} \boldsymbol{b} \f$ where \f$ \mathbf{A} \f$ is a
///             dense matrix.
///
/// \details    The reduction variable (here, \c sum ) is of the type
///             \c{long double}. This is becase when \c DataType is \c float,
///             the summation loses the precision, especially when the vector
///             size is large. It seems that using \c{long double} is slightly
///             faster than using \c double. The advantage of using a type
///             with larger bits for the reduction variable is only sensible
///             if the compiler is optimized with \c -O2 or \c -O3 flags.
///
/// \param[in]  A
///             1D array that represents a 2D dense array with either C (row)
///             major ordering or Fortran (column) major ordering. The major
///             ordering should de defined by \c A_is_row_major flag.
/// \param[in]  b
///             Column vector
/// \param[in]  num_rows
///             Number of rows of \c A
/// \param[in]  num_columns
///             Number of columns of \c A
/// \param[in]  A_is_row_major
///             Boolean, can be \c 0 or \c 1 as follows:
///             * If \c A is row major (C ordering where the last index is
///               contiguous) this value should be \c 1.
///             * If \c A is column major (Fortran ordering where the first
///               index is contiguous), this value should be set to \c 0.
/// \param[out] c
///             The output column vector (written in-place).

template <typename DataType>
DataType cMatrixFunctions<DataType>::logdet(
        DataType* A,
        const LongIndexType num_rows,
        const FlagType sym_pos,
        FlagType& sign)
{
    DataType logdet_;

    // Allocate matrices
    DataType* L = NULL;
    LongIndexType* P = NULL;
    DataType tol = 1e-8;

    // Perform matrix decomposition
    if (sym_pos == 1)
    {
        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_rows*num_rows];
        cMatrixDecompositions<DataType>::cholesky(A, num_rows, L);

        // Compute logdet based on the diagonals of A
        logdet_ = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_rows, sign);
    }
    else
    {
        // Perform LU Decomposition. A is overwritten to LU.
        P = new LongIndexType[num_rows+1];
        cMatrixDecompositions<DataType>::lup(A, P, num_rows, tol);

        // Compute logdet based on the diagonals of A
        logdet_ = cMatrixFunctions<DataType>::triang_logdet(
                A, P, num_rows, sign);
    }

    // Free array
    if (L != NULL)
    {
        delete[] L;
        L = NULL;
    }

    if (P != NULL)
    {
        delete[] P;
        P = NULL;
    }
    
    return logdet_;
}


// =============
// triang logdet
// =============

/// \brief Computes logdet for triangular matrices.
///

template <typename DataType>
DataType cMatrixFunctions<DataType>::triang_logdet(
        const DataType* A,
        const LongIndexType* P,
        const LongIndexType num_rows,
        FlagType& sign)
{
    DataType logdet_ = 0.0;
    DataType diag;
    sign = 1;
    
    for (LongIndexType i=0; i < num_rows; ++i)
    {
        // Get the i-th element of the diagonal of A
        if (P == NULL)
        {
            diag = A[i*num_rows + i];
        }
        else
        {
            // When permutation is given, use the i-th permuted row of A.
            diag = A[P[i]*num_rows + i];
        }

        if (diag == 0.0)
        {
            // Logdet is -inf, however, here we set it to zero and flag sign to
            // negative two to identify this special case later.
            logdet_ = 0.0;
            sign = -2;
            break;
        }
        else if (diag < 0.0)
        {
            sign = -sign;
            logdet_ += log(fabs(diag));
        }
        else
        {
            logdet_ += log(diag);
        }
    }

    // Adjust sign due to permutations of the rows of A
    if (P != NULL)
    {
        // Change sing if the number of permutations is an odd number
        if ((P[num_rows] - num_rows) % 2 == 1)
        {
            sign = -sign;
        }
    }

    return logdet_;
}


// ===
// det
// ===

/// \brief  Computes the determinant of a matrix.
///

template <typename DataType>
DataType cMatrixFunctions<DataType>::det(
        DataType* A,
        const LongIndexType num_rows,
        const FlagType sym_pos)
{
    // Compute logdet
    FlagType sign;
    DataType logdet_ = cMatrixFunctions<DataType>::logdet(
            A, num_rows, sym_pos, sign);

    // Convert logdet to det
    DataType det;
    if (sign == -2)
    {
        det = 0.0;
    }
    else
    {
        det = exp(logdet_) * static_cast<DataType>(sign);
    }
    
    return det;
}


// =======
// glogdet
// =======

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::glogdet(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType method,
        const FlagType X_orth,
        FlagType& sign,
        long long& flops)
{
    DataType glogdet_;

    #if COUNT_PERF
    // Measure flops
    InstructionsCounter* instructions_counter = NULL;
    if (flops == 1)
    {
        instructions_counter = new InstructionsCounter();
        instructions_counter->start();
    }
    #endif

    if (method == 0)
    {
        // Using legacy method
        glogdet_ = cMatrixFunctions<DataType>::_glogdet_legacy(
                A, X, num_rows, num_columns, sym_pos, sign);
    }
    else
    {
        // Using projection method
        glogdet_ = cMatrixFunctions<DataType>::_glogdet_proj(
                A, X, num_rows, num_columns, X_orth, sign);
    }

    #if COUNT_PERF
    if (flops == 1)
    {
        instructions_counter->stop();
        flops = instructions_counter->get_count();

        if (instructions_counter != NULL)
        {
            delete instructions_counter;
            instructions_counter = NULL;
        }
    }
    #endif

    return glogdet_;
}


// ==============
// glogdet legacy
// ==============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_glogdet_legacy(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        FlagType& sign)
{
    DataType glogdet_;
    DataType logdet_A;
    DataType logdet_W;
    DataType coeff = 0;
    FlagType sign_A;
    FlagType sign_W;

    // Allocate matrix L
    DataType* A_copy = new DataType[num_rows*num_rows];
    DataType* Y = new DataType[num_rows*num_rows];
    DataType* W = new DataType[num_rows*num_rows];
    DataType* L = NULL;
    LongIndexType* P = NULL;
    DataType tol = 1e-8;

    // Copy A to A_copy since A_copy will be overwritten during decompositions
    cMatrixOperations<DataType>::copy(A, A_copy, num_rows, num_rows);

    // Perform matrix decomposition
    if (sym_pos == 1)
    {
        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_rows*num_rows];
        cMatrixDecompositions<DataType>::cholesky(A_copy, num_rows, L);

        // Compute logdet based on the diagonals of A
        logdet_A = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_rows, sign_A);

        // Solve Y = Linv * X
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = Y.T * Y
        cMatrixOperations<DataType>::grammian(
                Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }
    else
    {
        // Perform LU Decomposition. A is overwritten to U.
        // cMatrixDecompositions<DataType>::lu(A_copy, num_rows, L);
        P = new LongIndexType[num_rows+1];
        cMatrixDecompositions<DataType>::lup(A_copy, P, num_rows, tol);

        // Compute logdet based on the diagonals of A
        // logdet_A = cMatrixFunctions<DataType>::triang_logdet(
        //         A_copy, num_rows, sign);
        logdet_A = cMatrixFunctions<DataType>::triang_logdet(
                A_copy, P, num_rows, sign_A);

        // Solve Y = Ainv * X using LU decomposition of A_copy. A_copy is U.
        // cMatrixSolvers<DataType>::solve(
        //         L, A_copy, X, Y, num_rows, num_columns, 0, 0);
        cMatrixSolvers<DataType>::lup_solve(
                A_copy, P, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = X.T * Y
        cMatrixOperations<DataType>::inner_prod(
                X, Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }

    // Compute glogdet
    glogdet_ = logdet_A + logdet_W;

    // Sign
    if ((sign_A == -2) || (sign_W == -2))
    {
        // Indicates that det of one of A or W is zero.
        sign = -2;
    }
    else
    {
        sign = sign_A * sign_W;
    }

    // Free array
    delete[] A_copy;
    delete[] Y;
    delete[] W;

    if (L != NULL)
    {
        delete[] L;
        L = NULL;
    }

    if (P != NULL)
    {
        delete[] P;
        P = NULL;
    }

    return glogdet_;
}


// ============
// glogdet proj
// ============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_glogdet_proj(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType glogdet_;
    DataType logdet_N;
    DataType logdet_XtX = 0.0;
    FlagType sign_XtX = 1;
    FlagType sign_N;

    // Allocate matrix L
    DataType* N = new DataType[num_rows*num_rows];
    DataType* A_I = new DataType[num_rows*num_rows];
    DataType* M = new DataType[num_rows*num_columns];
    DataType* S = new DataType[num_rows*num_rows];
    DataType* Y = NULL;
    DataType* XtX = NULL;
    DataType* L = NULL;
    LongIndexType* P = NULL;  // will not be used

    // Initialize N with A
    cMatrixOperations<DataType>::copy(A, N, num_rows, num_rows);

    // Initialize A_I with A
    cMatrixOperations<DataType>::copy(A, A_I, num_rows, num_rows);

    // Subtract identity from A_I, so at this point, A_I becomes A-I
    cMatrixOperations<DataType>::add_diagonal_inplace(A_I, -1.0, num_rows);

    // Compute S = (A-I)*X or S=(A-I)*Y
    if (X_orth == 1)
    {
        // Perform M = (A-I)*X
        cMatrixOperations<DataType>::matmat(
                A_I, X, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*X.T
        cMatrixOperations<DataType>::outer_prod(
                M, X, S, num_rows, num_columns, 0);
    }
    else
    {
        // Compute XtX
        XtX = new DataType[num_columns*num_columns];
        cMatrixOperations<DataType>::grammian(
                X, XtX, num_rows, num_columns, 0);

        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_columns*num_columns];
        cMatrixDecompositions<DataType>::cholesky(XtX, num_columns, L);

        // Compute logdet of XtX. Note XtX_sign is always 1, will not be used.
        logdet_XtX = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_columns, sign_XtX);

        // Compute Y.T = Linv * X.T
        Y = new DataType[num_rows*num_columns];
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_columns, num_rows, 1, 1);

        // Perform M = (A-I)*Y
        cMatrixOperations<DataType>::matmat(
                A_I, Y, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*Y.T
        cMatrixOperations<DataType>::outer_prod(
                M, Y, S, num_rows, num_columns, 0);
    }

    // Perform N = A - S (N is subtracted from A since N is initialized as A)
    cMatrixOperations<DataType>::subtract_inplace(
            N, S, num_rows, num_rows);

    // Compute logdet of N
    logdet_N = cMatrixFunctions<DataType>::logdet(N, num_rows, 0, sign_N);

    // Compute glogdet
    glogdet_ = logdet_N + logdet_XtX;

    // Sign
    if ((sign_N == -2) || (sign_XtX == -2))
    {
        sign = -2;
    }
    else
    {
        sign = sign_N * sign_XtX;
    }

    // Free array
    delete[] N;
    delete[] A_I;
    delete[] M;
    delete[] S;

    if (XtX != NULL)
    {
        delete[] XtX;
        XtX = NULL;
    }

    if (L != NULL)
    {
        delete[] L;
        L = NULL;
    }

    if (P != NULL)
    {
        delete[] P;
        P = NULL;
    }

    if (Y != NULL)
    {
        delete[] Y;
        Y = NULL;
    }

    return glogdet_;
}


// =======
// plogdet
// =======

/// \brief Computes the pseudo logdet of M.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::plogdet(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType method,
        const FlagType X_orth,
        FlagType& sign,
        long long& flops)
{
    DataType plogdet_;
    
    #if COUNT_PERF
    // Measure flops
    InstructionsCounter* instructions_counter = NULL;
    if (flops == 1)
    {
        instructions_counter = new InstructionsCounter();
        instructions_counter->start();
    }
    #endif

    if (method == 0)
    {
        // Using legacy method
        plogdet_ = cMatrixFunctions<DataType>::_plogdet_legacy(
                A, X, num_rows, num_columns, sym_pos, X_orth, sign);
    }
    else
    {
        // Using projection method
        plogdet_ = cMatrixFunctions<DataType>::_plogdet_proj(
                A, X, num_rows, num_columns, X_orth, sign);
    }

    #if COUNT_PERF
    if (flops == 1)
    {
        instructions_counter->stop();
        flops = instructions_counter->get_count();

        if (instructions_counter != NULL)
        {
            delete instructions_counter;
            instructions_counter = NULL;
        }
    }
    #endif

    return plogdet_;
}


// ==============
// plogdet legacy
// ==============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_plogdet_legacy(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType sym_pos,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType plogdet_;
    DataType logdet_A;
    DataType logdet_W;
    DataType logdet_XtX;
    FlagType XtX_sign;
    DataType coeff = 0;
    FlagType sign_A;
    FlagType sign_W;
    FlagType sign_XtX;

    // Allocate matrix L
    DataType* A_copy = new DataType[num_rows*num_rows];
    DataType* Y = new DataType[num_rows*num_rows];
    DataType* W = new DataType[num_rows*num_rows];
    DataType* XtX = NULL;
    DataType* L = NULL;
    LongIndexType* P = NULL;
    DataType tol = 1e-8;

    // Copy A to A_copy since A_copy will be overwritten during decompositions
    cMatrixOperations<DataType>::copy(A, A_copy, num_rows, num_rows);

    // Perform matrix decomposition
    if (sym_pos == 1)
    {
        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_rows*num_rows];
        cMatrixDecompositions<DataType>::cholesky(A_copy, num_rows, L);

        // Compute logdet based on the diagonals of A
        logdet_A = 2.0 * cMatrixFunctions<DataType>::triang_logdet(
                L, P, num_rows, sign_A);

        // Solve Y = Linv * X
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = Y.T * Y
        cMatrixOperations<DataType>::grammian(
                Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }
    else
    {
        // Perform LU Decomposition. A is overwritten to U.
        P = new LongIndexType[num_rows+1];
        cMatrixDecompositions<DataType>::lup(A_copy, P, num_rows, tol);

        // Compute logdet based on the diagonals of A
        logdet_A = cMatrixFunctions<DataType>::triang_logdet(
                A_copy, P, num_rows, sign_A);

        // Solve Y = Ainv * X using LU decomposition of A_copy. A_copy is U.
        // cMatrixSolvers<DataType>::solve(
        //         L, A_copy, X, Y, num_rows, num_columns, 0, 0);
        cMatrixSolvers<DataType>::lup_solve(
                A_copy, P, X, Y, num_rows, num_columns, 0, 0);

        // Compute W = X.T * Y
        cMatrixOperations<DataType>::inner_prod(
                X, Y, W, num_rows, num_columns, coeff);

        // Compute determinant of W
        logdet_W = cMatrixFunctions<DataType>::logdet(
                W, num_columns, sym_pos, sign_W);
    }

    if (X_orth == 1)
    {
        logdet_XtX = 0.0;
        sign_XtX = 1;
    }
    else
    {
        // Compute XtX
        XtX = new DataType[num_columns*num_columns];
        cMatrixOperations<DataType>::grammian(
                X, XtX, num_rows, num_columns, 0);

        logdet_XtX = cMatrixFunctions<DataType>::logdet(
                XtX, num_columns, 1, XtX_sign);
    }

    // Compute plogdet
    plogdet_ = logdet_XtX - logdet_A - logdet_W;

    // Sign
    if (sign_XtX == -2)
    {
        // This indicates logdet_XtX is -inf.
        sign = -2;
    }
    else if ((sign_A == -2) || (sign_W == -2))
    {
        // This indicates that logdet of A or W is -inf.
        sign = 2;
    }
    else
    {
        sign = sign_XtX * sign_A * sign_W;
    }

    // Free array
    delete[] A_copy;
    delete[] Y;
    delete[] W;

    if (L != NULL)
    {
        delete[] L;
        L = NULL;
    }

    if (P != NULL)
    {
        delete[] P;
        P = NULL;
    }

    if (XtX != NULL)
    {
        delete[] XtX;
        XtX = NULL;
    }

    return plogdet_;
}


// ============
// plogdet proj
// ============

/// \brief Computes the logdet of likelihood function of Gaussian process.
///        The matrix \c A is assumd to be \c (n,n), where \c n is \c num_rows,
///        and the matrix \c X is \c (n,m), where \c m is \c num_columns.

template <typename DataType>
DataType cMatrixFunctions<DataType>::_plogdet_proj(
        const DataType* A,
        const DataType* X,
        const LongIndexType num_rows,
        const LongIndexType num_columns,
        const FlagType X_orth,
        FlagType& sign)
{
    DataType plogdet_;
    DataType logdet_N;
    FlagType sign_N;

    // Allocate matrix L
    DataType* N = new DataType[num_rows*num_rows];
    DataType* A_I = new DataType[num_rows*num_rows];
    DataType* M = new DataType[num_rows*num_columns];
    DataType* S = new DataType[num_rows*num_rows];
    DataType* Y = NULL;
    DataType* XtX = NULL;
    DataType* L = NULL;

    // Initialize N with A
    cMatrixOperations<DataType>::copy(A, N, num_rows, num_rows);

    // Initialize A_I with A
    cMatrixOperations<DataType>::copy(A, A_I, num_rows, num_rows);

    // Subtract identity from A_I, so at this point, A_I becomes A-I
    cMatrixOperations<DataType>::add_diagonal_inplace(A_I, -1.0, num_rows);

    // Compute S = (A-I)*X or S=(A-I)*Y
    if (X_orth == 1)
    {
        // Perform M = (A-I)*X
        cMatrixOperations<DataType>::matmat(
                A_I, X, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*X.T
        cMatrixOperations<DataType>::outer_prod(
                M, X, S, num_rows, num_columns, 0);
    }
    else
    {
        // Compute XtX
        XtX = new DataType[num_columns*num_columns];
        cMatrixOperations<DataType>::grammian(
                X, XtX, num_rows, num_columns, 0);

        // Perform Cholesky Decomposition. A is overwritten (not to U)
        L = new DataType[num_columns*num_columns];
        cMatrixDecompositions<DataType>::cholesky(XtX, num_columns, L);

        // Compute Y.T = Linv * X.T
        Y = new DataType[num_rows*num_columns];
        cMatrixSolvers<DataType>::lower_triang_solve(
                L, X, Y, num_columns, num_rows, 1, 1);

        // Perform M = (A-I)*Y
        cMatrixOperations<DataType>::matmat(
                A_I, Y, M, num_rows, num_rows, num_columns, 0);

        // Perform S = M*Y.T
        cMatrixOperations<DataType>::outer_prod(
                M, Y, S, num_rows, num_columns, 0);
    }

    // Perform N = A - S (N is subtracted from A since N is initialized as A)
    cMatrixOperations<DataType>::subtract_inplace(
            N, S, num_rows, num_rows);

    // Compute logdet of N
    logdet_N = cMatrixFunctions<DataType>::logdet(N, num_rows, 0, sign_N);

    // Compute plogdet
    plogdet_ = -logdet_N;

    if (sign_N == -2)
    {
        // Indicates that det of N is 0, so logdet of 1/N is +inf.
        sign = 2;
    }
    else
    {
        sign = sign_N;
    }

    // Free array
    delete[] N;
    delete[] A_I;
    delete[] M;
    delete[] S;

    if (L != NULL)
    {
        delete[] L;
        L = NULL;
    }

    if (Y != NULL)
    {
        delete[] Y;
        Y = NULL;
    }

    if (XtX != NULL)
    {
        delete[] XtX;
        XtX = NULL;
    }

    return plogdet_;
}


// ===============================
// Explicit template instantiation
// ===============================

template class cMatrixFunctions<float>;
template class cMatrixFunctions<double>;
template class cMatrixFunctions<long double>;
