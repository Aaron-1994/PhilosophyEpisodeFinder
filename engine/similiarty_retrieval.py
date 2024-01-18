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
This module is designed for advanced processing and retrieval of podcast episode content, leveraging 
large language models (LLMs) and similarity search techniques. It offers functionalities to suggest,
summarize, and find podcast episodes based on user-provided prompts or questions.

Key Components and Functionalities:
- Chroma Database: Utilizes Chroma, a vector store, for efficient similarity searches with podcast content.
- Large Language Models: Employs language models from OpenAI (like GPT-3.5-turbo-16k) for generating summaries and assessing content relevancy.
- Episode Suggestion: Provides capabilities to suggest podcast episodes similar to a given prompt using similarity search.
- Summary Generation: Generates concise summaries of podcast episodes, tailored to specific hints or questions.
- Relevancy Assessment: Determines the relevance of podcast episodes to a given prompt, ensuring suggested content is contextually appropriate.
- Episode Retrieval: Retrieves detailed information about podcast episodes, including titles, text content, and links.
"""
import os
from typing import List, Tuple
import functools
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from langchain.chat_models import ChatOpenAI
from langchain.schema.document import Document
from langchain.chains.llm import LLMChain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.prompts import PromptTemplate
from dotenv import load_dotenv

from engine.constants import Podcast, LEAST_ACCEPTED_SIMILARITY
from engine.data_handler.get import get_text
from engine.utils import attach_summaries, extract_episode_from_docs
from engine.data_handler.get import get_link, get_title


load_dotenv()
DB_PATH = os.sep.join("./data/vectorDB".split("/"))


class VectorDB:
    _db = None

    @classmethod
    def _get_db(cls) -> Chroma:
        
        if cls._db is None:
            cls._db = Chroma(persist_directory=DB_PATH, embedding_function=OpenAIEmbeddings())
        return cls._db

    @classmethod
    def similarity_search_with_score(cls, prompt, k):
        db = cls._get_db()
        return db.similarity_search_with_score(prompt, k)


def get_similar_docs(prompt: str, k: int = 20) -> List[Tuple[Document, float]]:
    """
    Retrieves a list of documents similar to the given prompt, along with their similarity scores.

    This function performs a similarity search in the Chroma database for the given prompt.
    It filters out documents with a similarity score below the least accepted similarity threshold.

    Args:
        prompt (str): The prompt text used for finding similar documents.
        k (int, optional): The number of similar documents to retrieve. Defaults to 20.

    Returns:
        List[Tuple[Document, float]]: A list of tuples, each containing a Document and its similarity score.
    """

    docs_with_score = VectorDB.similarity_search_with_score(prompt, k)
    docs = [
        (data, score)
        for data, score in docs_with_score
        if score < LEAST_ACCEPTED_SIMILARITY
    ]
    return docs


def suggest_me_episodes(prompt: str, k: int = 8) -> List:
    """
    Suggests podcast episodes that are similar to the given prompt.

    This function finds episodes that are most similar to the provided prompt text by leveraging
    a similarity search in the database. It returns the top 'k' similar episodes.

    Args:
        prompt (str): The text prompt used for finding similar episodes.
        k (int, optional): The number of episodes to return. Defaults to 8.

    Returns:
        List: A list of tuples, where each tuple contains the episode number
                               and the podcast name of a suggested episode.
    """
    epis = get_similar_docs(prompt, k)
    epis = extract_episode_from_docs(epis)
    return epis

@functools.lru_cache(maxsize=4096)
def is_related(episode: Tuple[int, str], prompt: str) -> bool:
    """
    Determines if the content of a podcast episode is related to a given prompt.

    This function uses a language model to assess whether the content of a specified
    podcast episode is relevant to a given question or hint (prompt). It does so by
    generating a response based on the episode content and the prompt.

    Args:
        episode (Tuple[int, str]): A tuple containing the episode number and the podcast title.
        prompt (str): The question or hint to be considered in relation to the episode content.

    Returns:
        bool: True if the episode content is related to the prompt, False otherwise.
    """
    prompt_template = (
        """ Look at the following content, and answer my question only based on this content.
        CONTENT: "{text}"
        """
        + f"""
        Question: "{prompt}"
        
        Does the CONTENT have some info regarding the QUESTION?
        Respond only Yes or No
        Answer (Yes/No): """
    )

    prompt = PromptTemplate.from_template(prompt_template)

    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text"
    )
    
    podcast_title = episode[1]

    text = get_text(episode[0], podcast_title.value)[0][0]
    docs = [Document(page_content=text)]

    llm_output = stuff_chain.run(docs)
    if "yes" in llm_output.lower():
        return True

    return False

@functools.lru_cache(maxsize=4096)
def find_episodes(prompt, k=12, TOP_K=6):
    """
    Finds and returns podcast episodes related to a given prompt.

    The function searches for episodes similar to the prompt, filters them based on relevance,
    and then fetches their titles, texts, and links. It returns a list of dictionaries,
    each containing information about a relevant episode.

    Args:
        prompt (str): The prompt or query to find related podcast episodes.
        k (int, optional): The number of episodes to initially fetch for similarity assessment. Defaults to 12.
        TOP_K (int, optional): The number of top relevant episodes to return. Defaults to 3.

    Returns:
        List[Dict]: A list of dictionaries, each containing information about an episode
                    (number, title, text, link, and podcast title).
    """

    most_common_epis = suggest_me_episodes(prompt, k=k)
    # separate episode num, podcast name

    def clean_up(epis):
        def _convert(input_string):
            return "".join([char.lower() for char in input_string if char.isalpha()])

        return [
            (
                num,
                Podcast.PHILOSOPHIZE_THIS
                if _convert(p) == "philosophizethis"
                else Podcast.UNKNOWN,
            )
            for num, p in epis
        ]

    # most_common_epis = [i for i, _ in most_common_epis][:TOP_K]
    most_common_epis = most_common_epis[:TOP_K]

    most_common_epis = clean_up(most_common_epis)

    try:
        if len(most_common_epis) == 0 or not is_related(
            most_common_epis[0], prompt
        ):  # NOTE: pick the first episode to checking only
            return []
    except Exception as e:
        # fixme: if the document is too long we get an error, 
        # hiding the error here. We have to figure out a systematic solution.
        pass

    most_common_epis = attach_summaries(most_common_epis, exclude_episodes=[])

    episodes = [
        {
            "episode_number": epi_info[0],
            "episode_title": get_title(epi_info[0], epi_info[1]),
            "podcast_title": epi_info[1].value,
            "episode_text": epi_text[0][0],
            "episode_link": get_link(epi_info[0], epi_info[1]),
        }
        for epi_info, epi_text in most_common_epis
    ]

    return episodes
