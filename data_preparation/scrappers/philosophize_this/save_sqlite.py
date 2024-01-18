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

import pandas as pd
from loguru import logger
import sqlite3
import csv
from engine.constants import Podcast

MERGED_DATA_PATH = "./data/philosophize_this/merged_data.csv"

SQL_NAME = "./data/philosophize_this./podcast.db"
TABLE_NAME = "merged_data"


def save_as_sql(file_path: str):
    df = pd.read_csv(file_path)

    conn = sqlite3.connect(SQL_NAME)

    cursor = conn.cursor()

    cols = df.columns.values

    # PRIMARY_KEY_COLUMNS = [cols[0], cols[1]]

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
        {cols[0]} TEXT NOT NULL,
        {cols[1]} TEXT NOT NULL,
        {cols[2]} TEXT,
        {cols[3]} TEXT,
        {cols[4]} TEXT,
        {cols[5]} TEXT,
        PRIMARY KEY ({cols[0]}, {cols[1]})
    );
    """

    cursor.execute(create_table_sql)

    with open(MERGED_DATA_PATH, "r") as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            column1_value = row[cols[0]]
            column2_value = row[cols[1]]
            column3_value = row[cols[2]]
            column4_value = row[cols[3]]
            column5_value = row[cols[4]]
            column6_value = Podcast.PHILOSOPHIZE_THIS.value

            insert_sql = f"""
            INSERT OR REPLACE INTO {TABLE_NAME}
            ({cols[0]}, {cols[1]}, {cols[2]}, {cols[3]}, {cols[4]}, {cols[5]})
            VALUES (?, ?, ?, ?, ?, ?);
            """
            cursor.execute(
                insert_sql,
                (
                    column1_value,
                    column2_value,
                    column3_value,
                    column4_value,
                    column5_value,
                    column6_value,
                ),
            )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    save_as_sql(MERGED_DATA_PATH)
