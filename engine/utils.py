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

from typing import List, Tuple
from loguru import logger


from engine.data_handler.get import get_summary


def extract_episode_from_docs(docs) -> List[Tuple[str, str]]:
    """
    Extracts and returns a list of episode numbers and podcast titles from given documents.

    Iterates over the provided documents, extracting metadata containing episode numbers and podcast titles.
    Each episode is represented as a tuple with the episode number and podcast title. Duplicates are omitted.

    Args:
        docs (List[Document]): A list of documents from which to extract episode information.

    Returns:
        List[Tuple[str, str]]: A list of tuples, each containing the episode number and podcast title.
    """
    visited = set()
    ls = []
    for doc in docs:
        try:
            epi_num = str(doc[0].metadata["epi_num"])
            podcast_title = doc[0].metadata["podcast"]
            if (podcast_title, epi_num) in visited:
                continue
            visited.add((podcast_title, epi_num))
            ls.append((epi_num, podcast_title))

        except Exception as e:
            logger.warning(doc.metadata)

    return ls


def attach_summaries(
    episodes: List[Tuple[int, str]], exclude_episodes: List[Tuple[int, str]] = None
) -> List[Tuple[Tuple[int, str], str]]:
    """
    Attaches summaries to the provided list of episodes, excluding specified episodes.

    This function queries for summaries of the given episodes and returns a list where each element is a tuple.
    The tuple consists of the episode information and its summary. Episodes in the exclude list won't have summaries.

    Args:
        episodes (List[Tuple[int, str]]): A list of tuples with episode numbers and podcast names.
        exclude_episodes (List[Tuple[int, str]], optional): Episodes to exclude from summary attachment.

    Returns:
        List[Tuple[Tuple[int, str], str]]: A list of tuples, each containing episode information and its summary.
    """
    exclude_episodes = [] if exclude_episodes is None else exclude_episodes

    return [
        (
            ((epi_num, pod_name), get_summary(ep_num=epi_num, podcast_name=pod_name))
            if epi_num not in exclude_episodes
            else (epi_num, "")
        )
        for epi_num, pod_name in episodes
    ]
