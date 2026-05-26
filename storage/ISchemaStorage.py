# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.

from typing import TypeVar, Generic, Optional,Protocol, List

T = TypeVar('T')  # generic data model type (usually pd.DataFrame or domain object)

class ISchemaStorage(Protocol, Generic[T]):
    """Storage interface for arbitrary data model/schema T."""
    def configure_from_config(self, config_file: str) -> None: ...
    def read(self, **kwargs) -> Optional[T]: ...
    def write(self, data: T, **kwargs) -> None: ...

    def get_primary_keys(self) -> List[str]: ...
