# SPDX-FileCopyrightText: Copyright 2021, Siavash Ameli <sameli@berkeley.edu>
# SPDX-License-Identifier: BSD-3-Clause
# SPDX-FileType: SOURCE
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the license found in the LICENSE.txt file in the root directory
# of this source tree.


# =======
# Imports
# =======

from .c_get_config cimport is_use_symmetry, is_use_openmp, is_count_perf, \
        is_chunk_tasks


# ==========
# get config
# ==========

def get_config():
    """
    Get the compile-time definitions, such as USE_SYMMETRY, 
    """

    config = {
        'use_symmetry': bool(is_use_symmetry()),
        'use_openmp': bool(is_use_openmp()),
        'count_perf': bool(is_count_perf()),
        'chunk_tasks': bool(is_chunk_tasks()),
    }

    return config
