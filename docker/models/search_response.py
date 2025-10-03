# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Search response model.

DEPRECATED: Import from models.responses.search_response instead.
"""

import warnings

from models.responses.search_response import SearchResponse

warnings.warn(
    "Importing from 'models.search_response' is deprecated. Use 'models.responses.search_response' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["SearchResponse"]
