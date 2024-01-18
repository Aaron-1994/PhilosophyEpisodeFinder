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
from typing import List
from loguru import logger
from engine.constants import Podcast

FILE_PATH = "./data/philosophize_this"
EPISODE_TRANSCRIPT_PATH = FILE_PATH + "/episode_transcripts"
SHORTS_PATH = FILE_PATH + "/shorts"
EP_DATA = EPISODE_TRANSCRIPT_PATH + "/ep_data.csv"

MERGED_DATA_PATH = "./data/philosophize_this/merged_data.csv"

# PODCAST_NAME = "Philosophize This"
PODCAST_NAME = Podcast.PHILOSOPHIZE_THIS


def save_data(df: pd.DataFrame) -> None:
    df.to_csv(MERGED_DATA_PATH, index=False)


def read_csv() -> pd.DataFrame:
    return pd.read_csv(EP_DATA)


def make_data_structure() -> pd.DataFrame:
    column_names = [
        "EP_Number",
        "EP_Title",
        "EP_Text",
        "EP_Summary",
        "EP_URL",
        "Podcast_Name",
    ]

    empty_df = pd.DataFrame(columns=column_names)

    return empty_df


def index_converter(index: int) -> str:
    if index < 10:
        return f"00{index}"
    elif 10 <= index < 100:
        return f"0{index}"
    elif 100 <= index < 1000:
        return f"{index}"


def text_reader(file_path) -> str:
    try:
        with open(file_path, encoding="utf8", mode="r") as file:
            return file.read()
    except FileNotFoundError:
        logger.warning("The file '{file_path}' was not found.", file_path=file_path)
    except Exception as e:
        logger.warning("An error occurred: {e}", e=e)


def collect_data(index: int, ep_data: pd.DataFrame) -> List:
    result_row = ep_data[ep_data.iloc[:, 0] == index]
    ep_title = result_row["Name"].values[0]
    ep_url = result_row["URL"].values[0]

    new_index = index_converter(index)

    ep_text = text_reader(f"{EPISODE_TRANSCRIPT_PATH}/{new_index}.txt")
    ep_summary = text_reader(f"{SHORTS_PATH}/{new_index}summary.txt")

    return [index, ep_title, ep_text, ep_summary, ep_url, PODCAST_NAME]


def run():
    ep_data = read_csv()

    output_struc = make_data_structure()

    number = ep_data.shape[0]

    for i in range(number, 0, -1):
        data = collect_data(i, ep_data)
        new_row_df = pd.DataFrame([data], columns=output_struc.columns)
        output_struc = pd.concat([output_struc, new_row_df], ignore_index=True)

    save_data(output_struc)


if __name__ == "__main__":
    run()
