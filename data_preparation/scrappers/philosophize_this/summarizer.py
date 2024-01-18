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
import time
from dotenv import load_dotenv
from loguru import logger
from engine.summarizer import make_summary

load_dotenv()

transcripts_path = ".\data\philosophize_this\episode_transcripts"
summary_path = ".\data\philosophize_this\shorts"

transcripts = os.listdir(transcripts_path)

for transcript_name in transcripts:
    logger.info(f"Summarizing {transcript_name}")
    transcript_path = f"{transcripts_path}/{transcript_name}"
    transcript = open(transcript_path, "r").read()
    dot_index = transcript_name.find(".txt")
    name = transcript_name[:dot_index]
    output_path = f"{summary_path}/{name}summary.txt"
    if not os.path.exists(output_path):
        try:
            summary = make_summary(transcript)
            with open(output_path, "w") as f:
                f.write(summary)
            logger.info("Created Summary {summary}", summary=summary)
        except Exception as e:
            logger.warning(e)
            logger.warning("Failed to Make Summary For {name}", name=name)
        time.sleep(5)
    else:
        logger.info("Summary Already Existed For {name}", name=name)
