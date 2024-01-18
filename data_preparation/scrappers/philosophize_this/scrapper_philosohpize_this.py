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

import re
import os
import time
import csv
from typing import Optional, List, Tuple
import requests
from bs4 import BeautifulSoup
from loguru import logger
import pandas as pd
import numpy as np

DATA_DIR_PATH = "./data/philosophize_this"
EPISODE_TRANSCRIPT_DIR_PATH = DATA_DIR_PATH + "/episode_transcripts"
EPISODE_CSV_FILE_DIR_PATH = DATA_DIR_PATH + "/episode_transcripts/ep_data.csv"
PODCAST_CSV_FILE_DIR_PATH = DATA_DIR_PATH + "/episode_transcripts/pc_data.csv"
EP_SUMMARY_DIR = DATA_DIR_PATH + "/episode_transcripts/"

TRANSCRIPT_BASE_URL = "https://www.philosophizethis.org/transcripts"
PODCASTS_BASE_URL = "https://www.philosophizethis.org/podcasts"
BASE_URL = "https://www.philosophizethis.org"

EPISODE_HREF = r"transcript"
PODCAST_HREF = r"podcast"

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.111 Safari/537.36"

headers = {"User-Agent": USER_AGENT}

MAX_RETRIES = 5


def exponential_backoff(retries: int) -> int:
    return min(2**retries, 60)


# CSV structure:
#   1 : { EP_Num , EP_Name , EP_URL}
def get_page(url: str) -> Optional[BeautifulSoup]:
    retries = 0

    while retries < MAX_RETRIES:
        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            page = BeautifulSoup(response.text, "html.parser")
            return page
        elif response.status_code == 429:
            wait_time = exponential_backoff(retries)
            logger.info(
                "Rate limited. Waiting for {wait_time} seconds...", wait_time=wait_time
            )
            time.sleep(wait_time)
            retries += 1
        else:
            logger.info(
                "Failed to retrieve the page: {status} , URL : {url}",
                status=response.status_code,
                url=url,
            )
            page = None
            return page

    return None


def find_podcasts(page: BeautifulSoup) -> List[str]:
    podcasts = []

    pattern = re.compile(PODCAST_HREF + "/")
    matching_links = page.find_all("a", href=pattern)

    for link in matching_links:
        text_value = link.get_text()
        podcasts.append(text_value)

    return podcasts


def find_episodes(page: BeautifulSoup) -> List[str]:
    episodes = []

    pattern = re.compile(EPISODE_HREF + "/")
    matching_links = page.find_all("a", href=pattern)

    for link in matching_links:
        href_value = link.get("href")
        episodes.append(href_value)

    return episodes


def get_header(page: BeautifulSoup, url: str) -> Optional[str]:
    h1_tag = page.find("h1")

    if h1_tag:
        data_content_field = h1_tag.get_text()
        if data_content_field:
            return data_content_field
        else:
            logger.info(
                "No data_content_field attribute found in <h1> tag on the page : {url}.",
                url=url,
            )
    else:
        logger.info("No <h1> tag found on the page : {url}.", url=url)

    return None


def get_text_transcript(page: BeautifulSoup) -> List[str]:
    text = []
    selected_tags = page.find_all(["em", "p"])

    for tag in selected_tags:
        tag_text = tag.get_text()
        text.append(tag_text)

    return text


def extract_podcasts_data(podcasts: List[str]) -> None:
    for pc in podcasts:
        split_link = pc.split("-", maxsplit=2)

        try:
            # uplift to regex
            number = split_link[0].split("#")[1].lstrip().rstrip()
            title = split_link[1].lstrip().rstrip()

            save_podcast_csv((number, title))
        except Exception as e:
            logger.info("Exception Error {error}", error=e)


def get_ep_title(ep_number: str) -> str:
    df = pd.read_csv(PODCAST_CSV_FILE_DIR_PATH)

    if int(ep_number) in df["Number"].values:
        matching_row_index = df[df["Number"] == int(ep_number)].index[0]

        return df.loc[matching_row_index, "Title"]

    else:
        return "-- NO TITLE --"


def extract_episodes_data(episodes: List[str]) -> None:
    for ep in episodes:
        time.sleep(1)
        new_url = BASE_URL + ep
        page = get_page(new_url)
        if page is not None:
            header = get_header(page, new_url)

            if header is None:
                continue

            try:
                split_header = header.split("-")

                ep_number = split_header[0].split("#")[1].lstrip().rstrip()

                ep_title = get_ep_title(ep_number)

                save_episode_csv((ep_number, ep_title, new_url))

                text = get_text_transcript(page)
                save_episode_transcript((ep_number, ep_title, text))
            except Exception as e:
                logger.info("Exception Error {error}", error=e)


# pc_cv structure:
#   { EP_Num , EP_Title}
def save_podcast_csv(pc_cv: Tuple) -> None:
    df = pd.read_csv(PODCAST_CSV_FILE_DIR_PATH)

    if int(pc_cv[0]) in df["Number"].values:
        matching_row_index = df[df["Number"] == int(pc_cv[0])].index[0]

        df.loc[matching_row_index, "Title"] = pc_cv[1]

        df.to_csv(PODCAST_CSV_FILE_DIR_PATH, index=False)
        logger.info("EP {num} edited in PC_CSV file.", num=pc_cv[0])
    else:
        new_data = {"Number": [pc_cv[0]], "Title": [pc_cv[1]]}

        new_data_df = pd.DataFrame(new_data)

        df = pd.concat([df, new_data_df], ignore_index=True)
        df.to_csv(PODCAST_CSV_FILE_DIR_PATH, index=False)

        logger.info("EP {num} added to the PC_CSV file.", num=pc_cv[0])


# ep_cv structure:
#   { EP_Num , EP_Name , EP_URL}
def save_episode_csv(ep_cv: Tuple) -> None:
    df = pd.read_csv(EPISODE_CSV_FILE_DIR_PATH)

    if int(ep_cv[0]) in df["Number"].values:
        matching_row_index = df[df["Number"] == int(ep_cv[0])].index[0]

        df.loc[matching_row_index, "Name"] = ep_cv[1]
        df.loc[matching_row_index, "URL"] = ep_cv[2]

        df.to_csv(EPISODE_CSV_FILE_DIR_PATH, index=False)
        logger.info("EP {num} edited in EP_CSV file.", num=ep_cv[0])
    else:
        new_data = {"Number": [ep_cv[0]], "Name": [ep_cv[1]], "URL": [ep_cv[2]]}

        new_data_df = pd.DataFrame(new_data)

        df = pd.concat([df, new_data_df], ignore_index=True)
        df.to_csv(EPISODE_CSV_FILE_DIR_PATH, index=False)

        logger.info("EP {num} added to the EP_CSV file.", num=ep_cv[0])


# todo : implement in the future -> check with hash or checksum
def check_change_data():
    return True


def write_data(file_path: str, data: str) -> None:
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(data)


def data_preparing(ep_txt: Tuple) -> str:
    text = ep_txt[1]

    for i in ep_txt[2]:
        text += "\n" + i

    return text


# episode transcript structure:
#   ep_number.txt --> title + transcript


# ep_txt structure:
#   { EP_Num , EP_Name , Text}
def save_episode_transcript(ep_txt: Tuple) -> None:
    file_name = ep_txt[0] + ".txt"
    file_path = EP_SUMMARY_DIR + "/" + file_name

    new_data = data_preparing(ep_txt)

    for f in os.listdir(EP_SUMMARY_DIR):
        if f == file_name:
            if check_change_data():
                write_data(file_path, new_data)
                logger.info("File {num} edited successfully.", num=ep_txt[0])
                return
            break

    write_data(file_path, new_data)
    logger.info("File {num} saved successfully.", num=ep_txt[0])


def check_files_and_directories() -> None:
    if os.path.exists(DATA_DIR_PATH):
        if not os.path.exists(EPISODE_TRANSCRIPT_DIR_PATH):
            os.makedirs(EPISODE_TRANSCRIPT_DIR_PATH, exist_ok=True)

        if not os.path.exists(EPISODE_CSV_FILE_DIR_PATH):
            data1 = [["Number", "Name", "URL"]]

            with open(EPISODE_CSV_FILE_DIR_PATH, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(data1)

        if not os.path.exists(PODCAST_CSV_FILE_DIR_PATH):
            data2 = [["Number", "Title"]]

            with open(PODCAST_CSV_FILE_DIR_PATH, mode="w", newline="") as file:
                writer = csv.writer(file)
                writer.writerows(data2)

    else:
        os.makedirs(DATA_DIR_PATH, exist_ok=True)
        os.makedirs(EPISODE_TRANSCRIPT_DIR_PATH, exist_ok=True)

        data1 = [["Number", "Name", "URL"]]

        with open(EPISODE_CSV_FILE_DIR_PATH, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data1)

        data2 = [["Number", "Title"]]

        with open(PODCAST_CSV_FILE_DIR_PATH, mode="w", newline="") as file:
            writer = csv.writer(file)
            writer.writerows(data2)


def run() -> None:
    check_files_and_directories()

    podcasts_page = get_page(PODCASTS_BASE_URL)

    episode_details = find_podcasts(podcasts_page)  
    # grab episode num, title
    extract_podcasts_data(
        episode_details
    )  # save episode num, title as much as available

    transcripts_page = get_page(TRANSCRIPT_BASE_URL)
    episodes_links = find_episodes(transcripts_page)  # grab all the links
    extract_episodes_data(episodes_links)  # scrap all transcripts


def info() -> None:
    try:
        df = pd.read_csv(EPISODE_CSV_FILE_DIR_PATH)

        np_df = df["Number"].to_numpy()
        max_number = np_df.max()
        logger.info(
            "Number of all founded Episodes : {max_number}", max_number=max_number
        )

        for index, i in enumerate(df["Name"]):
            if i == "-- NO TITLE --":
                logger.info(
                    "Episode number {number} has no Title .", number=df["Number"][index]
                )

        missing_values = np.setdiff1d(np.arange(1, max_number), np_df)
        for i in missing_values:
            logger.info("Episode number {number} Not Found.", number=i)
    except Exception as e:
        logger.info("Exception Error {error}", error=e)


if __name__ == "__main__":
    run()
    info()
