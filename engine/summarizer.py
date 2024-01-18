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
import functools
from langchain.chains.llm import LLMChain
from langchain.prompts import PromptTemplate
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.schema.document import Document
from langchain.chat_models import ChatOpenAI

@functools.lru_cache(maxsize=512)
def make_summary(episode_text: str, hint: str = "") -> str:
    """
    Generates a concise summary of a podcast episode text, optionally considering a hint or question.

    This function creates a prompt for a language model (LLM), which is then used to summarize the episode text.
    If a hint is provided, it's included in the prompt to guide the summary generation.

    Args:
        episode_text (str): The text content of the podcast episode to be summarized.
        hint (str, optional): An optional hint or question to tailor the summary. Defaults to an empty string.

    Returns:
        str: The generated summary of the episode.
    """
    if len(hint) > 0:
        prompt_template = (
            f"""Write a concise summary of the following content with respect to the following hint/question "{hint}":
        """
            + """"{text}"
        CONCISE SUMMARY: """
        )
    else:
        prompt_template = """Write a concise summary of the following, do not include any dash - or other unnecessary signs at the end:
        "{text}"
        CONCISE SUMMARY: """
    prompt = PromptTemplate.from_template(prompt_template)

    # Define LLM chain
    llm = ChatOpenAI(temperature=0, model_name="gpt-3.5-turbo-16k")
    llm_chain = LLMChain(llm=llm, prompt=prompt)

    # Define StuffDocumentsChain
    stuff_chain = StuffDocumentsChain(
        llm_chain=llm_chain, document_variable_name="text"
    )

    docs = [Document(page_content=episode_text)]
    summary = stuff_chain.run(docs)
    return summary
