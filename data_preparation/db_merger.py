# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
import sqlite3
from engine.constants import Podcast


def merge():
    # Paths to the existing databases and the new database
    pz_path = "./data/philosophize_this/podcast.db"
    merged_path = "./data/merged/metadata.db"

    # Connect to the existing databases
    conn_pz = sqlite3.connect(pz_path)

    # Connect to the new database, creating it if it doesn't exist
    conn_merged = sqlite3.connect(merged_path)

    # Create the new table in the merged database
    conn_merged.execute(
        """
    CREATE TABLE merged_data (
        Number TEXT NOT NULL,
        Title TEXT NOT NULL,
        Text TEXT,
        Summary TEXT,
        URL TEXT,
        Podcast_Name TEXT,
        PRIMARY KEY (Number, Title)
    )
    """
    )

    # Extract data from the first database (pz)
    cursor_pz = conn_pz.cursor()
    cursor_pz.execute(
        "SELECT EP_Number, EP_Title, EP_Text, EP_Summary, EP_URL FROM merged_data"
    )
    rows_pz = cursor_pz.fetchall()

    # Transform and insert data from pz into the new database
    for row in rows_pz:
        conn_merged.execute(
            """
        INSERT INTO merged_data (Number, Title, Text, Summary, URL, Podcast_Name) 
        VALUES (?, ?, ?, ?, ?, ?)
        """,
            (row[0], row[1], row[2], row[3], row[4], Podcast.PHILOSOPHIZE_THIS.value),
        )

    # Commit changes and close connections
    conn_merged.commit()
    conn_pz.close()
    conn_merged.close()


if __name__ == "__main__":
    merge()
