# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""Error response model.

DEPRECATED: Import from models.responses.error_response instead.
"""

import warnings

from models.responses.error_response import ErrorResponse

warnings.warn(
    "Importing from 'models.error_response' is deprecated. Use 'models.responses.error_response' instead.",
    DeprecationWarning,
    stacklevel=2,
)

__all__ = ["ErrorResponse"]
