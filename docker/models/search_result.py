# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search result model.

DEPRECATED: Import from models.domain.search_result instead.
"""

import warnings

from models.domain.search_result import SearchResult

warnings.warn(
    "Importing from 'models.search_result' is deprecated. Use 'models.domain.search_result' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SearchResult"]
