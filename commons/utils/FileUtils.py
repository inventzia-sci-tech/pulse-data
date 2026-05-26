# SPDX-License-Identifier: AGPL-3.0-or-later OR LicenseRef-Inventzia-Commercial
# Copyright (c) 2013-2026 Magrino Bini, Paola Apruzzese, Inventzia Science and Technology Ltd.
#
# This file is part of pulse-data.
#
# pulse-data is dual-licensed:
#   - Under the GNU Affero General Public License v3.0 or later (see LICENSE-AGPL-3.0).
#   - Under a commercial license (see LICENSE-COMMERCIAL.txt).
#     Contact operations@inventzia.com.

import subprocess
import os

def extract_with_7zip(archive_path, output_folder):
    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)
    # Command to extract with 7zip
    command = f'7z x "{archive_path}" -o"{output_folder}"'
    try:
        # Run the command using subprocess
        subprocess.run(command, shell=True, check=True)
        print(f"Extraction successful to {output_folder}")
    except subprocess.CalledProcessError as e:
        print(f"Extraction failed with error: {e}")
        raise e