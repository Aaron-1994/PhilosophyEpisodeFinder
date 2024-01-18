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
import os
import shutil
import time
from langchain.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.embeddings import OpenAIEmbeddings
from langchain.vectorstores import Chroma
from loguru import logger
from dotenv import load_dotenv
from engine.constants import Podcast

load_dotenv()


def remove_old_data():
    # Ask user for confirmation before proceeding
    user_response = input(
        "Are you sure you want to remove all contents in the vectorDB folder? (yes/no): "
    )
    if user_response.lower() != "yes":
        print("Operation aborted.")
        exit()

    # Delete contents of the vectorDB folder
    db_path = os.sep.join("./data/vectorDB".split("/"))
    if os.path.exists(db_path):
        shutil.rmtree(db_path)
    os.makedirs(db_path)  # Recreate the empty folder


def build_new_db():
    db_path = os.sep.join("./data/vectorDB".split("/"))
    PT_episodes_path = os.sep.join(
        "./data/philosophize_this/episode_transcripts".split("/")
    )
    PT_episodes = [
        f"{PT_episodes_path}{os.sep}{f}"
        for f in os.listdir(PT_episodes_path)
        if ".txt" in f
    ]

    # PB_episodes_path = os.sep.join("./data/philosophy_bites/episode_transcripts_merged".split("/"))
    # PB_episodes = [f"{PB_episodes_path}{os.sep}{f}" for f in os.listdir(PB_episodes_path) if ".txt" in f]

    episodes = []

    # episodes = episodes.extend(PB_episodes)
    episodes.extend(PT_episodes)

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=300)
    logger.info(f"total of {len(episodes)} episodes")
    for idx, epi in enumerate(episodes):
        logger.info(f"Starting on episode {idx}, {epi}")
        time.sleep(3)
        loader = TextLoader(epi.replace(os.sep, "/"), encoding="UTF-8")

        data = loader.load()

        all_splits = text_splitter.split_documents(data)
        for doc in all_splits:
            podcast_title = (
                Podcast.PHILOSOPHIZE_THIS
                if "philosophize_this" in doc.metadata["source"]
                else "Philosophy Bites"
            )

            if podcast_title == Podcast.PHILOSOPHIZE_THIS:
                epi_num = int(doc.metadata["source"][-10:][3:6])
            else:
                episode_name_ind = doc.metadata["source"].rfind("/")
                episode_name = doc.metadata["source"][episode_name_ind + 1 :]
                first_ = episode_name.find("_")
                epi_num = episode_name[:first_]

            doc.metadata["epi_num"] = epi_num
            doc.metadata["podcast"] = podcast_title

        if len(all_splits) == 0:
            logger.warning(f"{idx}:{epi} has an empty text file")
            continue

        try:
            vector_storage = Chroma.from_documents(
                documents=all_splits,
                embedding=OpenAIEmbeddings(),
                persist_directory=db_path,
            )
        except Exception as e:
            logger.warning(
                "Failed Vectorizing Episode with id, title: {idx} - {epi} Error: {error}",
                idx=idx,
                epi=epi,
                error=e,
            )


if __name__ == "__main__":
    remove_old_data()
    build_new_db()
