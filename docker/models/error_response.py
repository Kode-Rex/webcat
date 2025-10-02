# Copyright (c) 2024 Travis Frisinger
#
# This source code is licensed under the MIT license found in the
# LICENSE file in the root directory of this source tree.

"""ErrorResponse model - standardized error response format."""

from typing import Optional

from pydantic import BaseModel


class ErrorResponse(BaseModel):
    """Error response format."""

    error: str
    query: Optional[str] = None
    details: Optional[str] = None
