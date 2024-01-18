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

"""
This module facilitates interactions with a podcast-related SQLite database. 

It includes functions to establish database connections and to perform various queries 
such as retrieving text, full episode data, summaries, URL links, and titles of specific 
podcast episodes. Additionally, the module contains constants for database path and table name.

Functions in this module generally accept episode numbers and podcast names as parameters 
and return relevant data from the database. Some functions also include the capability to 
insert new data or update existing records in the database.

Constants:
- DATA_BASE_PATH: The file path to the SQLite database.
- TABLE_NAME: The name of the main table in the database containing podcast data.

Functions:
- database_connection: Establishes a connection to the database.
- get_text: Retrieves text content of a specified podcast episode.
- get_episode: Fetches all data for a specified podcast episode.
- get_summary: Obtains the summary of a specified podcast episode.
- get_link: Retrieves the URL link of a specified podcast episode.
- get_title: Fetches the title of a specified podcast episode.
- replace_summary: Updates the summary of a specified podcast episode.
- insert_episode: Inserts a new episode record into the database.
"""
import sqlite3
import os
from typing import List, Union, Tuple
from loguru import logger


DATA_BASE_PATH = os.sep.join("./data/merged/metadata.db".split("/"))
TABLE_NAME = "merged_data"

# def database_connection():
#     """
#     Returns:
#         sqlite3.Connection: A connection object to the SQLite database.
#     """
#     return sqlite3.connect(DATA_BASE_PATH)


def run_query(query: str, parameters: Tuple) -> any:
    """
    Runs query

    Args:
        query (str): query text.
        parameters (str): a tuple containing parameters required for query.

    Returns:
        Returns the queries output with no modifications             
    """
    conn = sqlite3.connect(DATA_BASE_PATH)
    cursor = conn.cursor()
    cursor.execute(query, parameters)
    results = cursor.fetchall()
    cursor.close()
    return results


def get_text(ep_num: int, podcast_name: str) -> List:
    """
    Retrieves the text of a specified podcast episode from the database.

    Args:
        ep_num (int): The episode number.
        podcast_name (str): The name of the podcast.

    Returns:
        list: A list containing the text of the specified episode,
              or an empty list if no text is found.              
    """
    query = "SELECT Text FROM merged_data WHERE Number = ? AND Podcast_Name = ?"

    # conn = conn if conn is not None else database_connection()
    # cursor = conn.cursor()
    # cursor.execute(query, (ep_num, podcast_name))
    # results = cursor.fetchall()
    # cursor.close()
    results = run_query(query=query, parameters=(ep_num, podcast_name))
    return results


def get_episode(
    ep_num: int, podcast_name: str) -> List:
    """
    Retrieves all data for a specific podcast episode from the database.

    Args:
        ep_num (int): The episode number.
        podcast_name (str): The name of the podcast.
        conn (sqlite3.Connection, optional): An active database connection.
            If None, a new connection will be established. Defaults to None.

    Returns:
        list: A list of tuples containing all data fields for the specified episode.
              Each tuple represents one row in the database.
    """
    query = "SELECT * FROM merged_data WHERE Number = ? AND Podcast_Name = ?"
    # conn = conn if conn is not None else database_connection()
    # cursor = conn.cursor()
    # cursor.execute(query, (ep_num, podcast_name))
    # results = cursor.fetchall()
    # cursor.close()
    results = run_query(query=query, parameters=(ep_num, podcast_name))
    return results


def get_summary(
    ep_num: int, podcast_name: str) -> Union[List[Tuple[str]], List[str]]:
    """
    Retrieves the summary of a specified podcast episode from the database.

    Args:
        ep_num (int): The episode number.
        podcast_name (Podcast): The enum instance representing the name of the podcast.

    Returns:
        Union[List[Tuple[str]], List[str]]: A list containing a tuple with the episode's summary.
            Returns a single-item list with a default message if the summary is not found.
    """
    query = "SELECT Summary FROM merged_data WHERE Number = ? AND Podcast_Name = ?"
    # conn = conn if conn is not None else database_connection()
    # cursor = conn.cursor()
    # cursor.execute(query, (ep_num, podcast_name.value))
    # results = cursor.fetchall()
    # cursor.close()
    results = run_query(query=query, parameters=(ep_num, podcast_name.value))
    if len(results) == 0:
        logger.warning(f"Summary not found: {ep_num}, {podcast_name}")
        return [
            ("summary didn't exists!"),
        ]
    return results


def get_link(
    ep_num: int, podcast_name: str) -> List[Tuple[str]]:
    """
    Retrieves the URL link of a specific podcast episode from the database.

    Args:
        ep_num (int): The episode number.
        podcast_name (Podcast): The enum instance representing the name of the podcast.

    Returns:
        List[Tuple[str]]: A list containing a tuple with the URL link of the episode.
                          Each tuple represents one row in the database.
    """
    query = "SELECT URL FROM merged_data WHERE Number = ? AND Podcast_Name = ?"
    # conn = conn if conn is not None else database_connection()
    # cursor = conn.cursor()
    # cursor.execute(query, (ep_num, podcast_name.value))
    # results = cursor.fetchall()
    # cursor.close()
    results = run_query(query=query, parameters=(ep_num, podcast_name.value))
    return results


def get_title(ep_num: int, podcast_name: str) -> str:
    """
    Retrieves the title of a specific podcast episode from the database.

    Args:
        ep_num (int): The episode number.
        podcast_name (Podcast): The enum instance representing the name of the podcast.
    Returns:
        str: The title of the specified podcast episode.
    """
    query = "SELECT Title FROM merged_data WHERE Number = ? AND Podcast_Name = ?"
    # conn = conn if conn is not None else database_connection()
    # cursor = conn.cursor()
    # cursor.execute(query, (str(ep_num), podcast_name.value))
    # results = cursor.fetchall()
    # cursor.close()
    results = run_query(query=query, parameters=(str(ep_num), podcast_name.value))
    return results[0][0]
