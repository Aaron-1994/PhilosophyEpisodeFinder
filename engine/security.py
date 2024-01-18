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
This module provides functionality to detect gibberish text using a pre-trained model.

Classes:
- GibberishDetector: A class that encapsulates the functionality for detecting gibberish in text inputs.
"""
from typing import ClassVar
from loguru import logger
from transformers import pipeline, Pipeline


class GibberishDetector:
    """
    A class for detecting gibberish or nonsensical text.

    This class uses a pre-trained text classification model to determine whether a given text input is gibberish.
    It is designed as a singleton, initializing and using a shared pipeline instance for text classification.

    Class Attributes:
        _pipe: A private class-level attribute that holds the pipeline instance for text classification.
    """

    _pipe: ClassVar[Pipeline] = None

    @classmethod
    def get_pipe(cls) -> Pipeline:
        """
        Retrieves or initializes the text classification pipeline.

        This method ensures that the pipeline is instantiated only once and reused for subsequent calls.

        Returns:
            A pipeline object for text classification.
        """
        if cls._pipe is None:
            cls._pipe = pipeline(
                "text-classification", model="wajidlinux99/gibberish-text-detector"
            )
        return cls._pipe

    @classmethod
    def detect(cls, user_input: str) -> bool:
        """
        Determines if the given user input is gibberish.

        Args:
            user_input (str): The text input to be analyzed.

        Returns:
            bool: True if the input is classified as 'noise' (gibberish), False otherwise.
        """
        pipe: Pipeline = cls.get_pipe()
        result = pipe(user_input)
        label = result[0]["label"]
        logger.info(
            "[GIBBER CHECK] Request: {req} is classified as {label}",
            req=user_input,
            label=label,
        )
        return label != "clean"
        # return label == "noise" or label == "mild gibberish"
