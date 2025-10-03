# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""API search result model.

DEPRECATED: Import from models.domain.api_search_result instead.
"""

import warnings

from models.domain.api_search_result import APISearchResult

warnings.warn(
    "Importing from 'models.api_search_result' is deprecated. Use 'models.domain.api_search_result' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["APISearchResult"]
