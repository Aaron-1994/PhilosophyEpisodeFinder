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
This Flask application module provides a web interface for interacting with podcast data. 
It includes routes for searching podcast episodes, generating summaries, and managing requests and responses.

Key Features:
- Search Functionality: Processes search queries to find relevant podcast episodes and returns the results in JSON format.
- Summary Generation: Creates summaries for podcast episodes based on user input.
- Request Logging: Captures details of incoming requests and logs them, including IP address, request method, and URL.
- Response Logging: Logs the details of the responses sent back to the client.
- Error Handling: Includes a custom handler for internal server errors (500) with logging support.

Routes:
- `/`: Renders the home page of the web application.
- `/search`: Handles search requests for podcast episodes and returns results in JSON format.
- `/make_summary`: Generates a summary for a specified podcast episode and returns the data in JSON format.

The module utilizes several external libraries, including `loguru` for logging, `json` for JSON parsing, and custom modules like `engine.similarity_retrieval` and `engine.security` for specific functionalities related to podcast data processing and security.

Usage of this module requires a running Flask environment and is intended to be accessed through a web interface.
"""
from urllib.parse import unquote
import json
from flask import Flask, request, jsonify, render_template, Response
from flask_cors import CORS
from werkzeug.exceptions import HTTPException
from loguru import logger

from engine.similiarty_retrieval import find_episodes
import engine.summarizer as summarizer
from engine.security import GibberishDetector
from engine.data_handler.get import get_episode


app = Flask(__name__)
logger.add("app.log", rotation="1 day", format="{time} {level} {message}")

# Enable CORS (Cross-Origin Resource Sharing) for all routes


CORS(app)


@app.before_request
def log_request() -> None:
    """
    Logs details about each incoming request.

    Captures and logs the IP address, request method, URL, and request data.
    Attempts to parse request data as JSON; if parsing fails, raw data is logged.

    Returns:
        None
    """
    ip = request.remote_addr
    method = request.method
    url = request.url
    logger.info("Request from {ip}: {method} {url}", ip=ip, method=method, url=url)
    try:
        # Attempt to parse request data as JSON
        request_data = json.loads(request.data.decode())
    except json.JSONDecodeError:
        # If parsing fails, use the raw data
        request_data = request.data.decode()
    logger.info(
        "Request: path: {path}, json: {json}",
        path=request.path,
        json=request_data,
    )


@app.after_request
def log_response(response: Response) -> Response:
    """
    Logs details about the response after processing a request.

    This function logs the response status code and the response data.
    It attempts to parse the request data as JSON; if parsing fails, it logs the raw request data.

    Args:
        response (Response): The response object to be logged.

    Returns:
        Response: The same response object for further processing by Flask.
    """
    try:
        # Attempt to parse request data as JSON
        request_data = json.loads(request.data.decode())
    except json.JSONDecodeError:
        # If parsing fails, use the raw data
        request_data = request.data.decode()
    logger.info("Request Data: {data}", data=request_data)
    logger.info("Response: Status: {response}", response=response.status_code)
    logger.info("Response: {response}", response=response.data)
    return response


@app.errorhandler(500)
def handle_500_error(exception: HTTPException) -> tuple:
    """
    Handles internal server errors (HTTP status code 500).

    Logs the exception details and returns a standard error message to the client.

    Args:
        exception (HTTPException): The exception that triggered the error handler.

    Returns:
        tuple: A response tuple containing the error message and HTTP status code.
    """
    logger.exception("Server error: {exception}", exception=exception)
    return jsonify({"error": "Internal Server Error"}), 500


@app.route("/")
def index():
    """
    Render the home page.
    """
    return render_template("home.html")


@app.route("/search", methods=["POST"])
def search():
    """
    Handle search requests and return results as JSON.

    This function processes POST requests by extracting user input,
    checking for gibberish using the GibberishDetector, and then
    searching for relevant episodes using the 'find_episodes' function.
    The results are returned as a JSON response.

    Returns:
        Any: A Flask response object containing the search results in JSON format.
    """

    data = request.get_json()

    if request.method == "POST":
        data = request.get_json()
        user_input = data["user_input"]
        user_input = unquote(user_input)

        if GibberishDetector.detect(user_input):
            return jsonify({"results": []})

        user_response = find_episodes(user_input)
        response_data = {"results": user_response}

        return jsonify(response_data)


@app.route("/make_summary", methods=["POST"])
def make_summary():
    """
    Creates and returns a summary for a specified podcast episode based on user input.

    This function processes POST requests by extracting the episode number, hint/question, and podcast title from the request.
    It retrieves the episode data, generates a summary using the 'summarizer' module, and returns this information in JSON format.
    """

    data = request.get_json()

    if request.method == "POST":
        data = request.get_json()

        episode_number = data["epi_num"]
        hint = data["question"]
        podcast_title = data["podcast_title"]
        episode_data = get_episode(episode_number, podcast_title)

        episode_number, episode_title, episode_text = (
            episode_data[0][0],
            episode_data[0][1],
            episode_data[0][2],
        )

        summary = summarizer.make_summary(episode_text=episode_text, hint=hint)

        response_data = {
            "results": {
                "episode_number": episode_number,
                "episode_title": episode_title,
                "episode_summary": summary,
                "podcast_title": podcast_title,
            }
        }

        return jsonify(response_data)


if __name__ == "__main__":
    logger.info("starting the app!")
    app.run(host="0.0.0.0", port=5500, debug=True)
