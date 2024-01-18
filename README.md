# Philosophy Episode Finder

## Introduction

The Philosophy Episode Finder is a Retrieval Augmented Generation (RAG) project designed to redefine how we engage with philosophical content. Moving beyond the limits of traditional search engines, it offers a novel approach for efficiently pinpointing precise philosophical insights.

At the heart of this application lie advanced technologies such as LangChain, OpenAI models, and ChromaDB. Working collaboratively, these tools meticulously parse through the "Philosophize This!" podcast, providing accurate and relevant answers to user queries. Our aim is to simplify the exploration of philosophical content, directly catering to specific questions and interests. Adding other podcasts to this project is work in progress.

### Use Case

The Philosophy Episode Finder addresses a common challenge in exploring philosophical podcasts: deciphering the essence of episodes from often abstract titles and summaries. Titles like "The Creation of Meaning - The Denial of Death" or "The Ethics of Ambiguity" offer little insight into their actual content. Our project bridges this gap. By understanding and analyzing user queries, it recommends the most relevant episodes, specifically those that contain answers to the users' philosophical questions, thus making the discovery of meaningful content more intuitive and accessible.

### Key Features

- **AI-Powered Episode Summaries**: Utilizing AI, each episode of "Philosophize This!" is concisely summarized, offering quick and insightful access to its content.
- **Custom Benchmarking Dataset**: A tailor-made dataset underpins the system's benchmarking, achieving an recall@4 exceeding 97%.
- **Focused Philosophical Search**: Users can pose their philosophical questions and receive recommendations for podcast episodes that most closely align with their inquiries.

### Future Directions

- **Broadening Podcast Coverage**: Future updates aim to incorporate a wider range of philosophical podcasts, enhancing the diversity of accessible content.
- **Podcast Transcription via Whisper**: A forthcoming feature involves transcribing podcast episodes using OpenAI's Whisper technology, further augmenting the platform's functionality.

This project stands at the crossroads of cutting-edge AI technology and the vast world of philosophy, striving to make the journey through philosophical learning as targeted and accessible as possible.

### Installation Guide and Usage

To ensure a smooth setup and operation of the Philosophy Episode Finder, please follow these steps:

1. **Python Version**: Make sure you have `Python 3.9.17` installed. This version is recommended for optimal compatibility with the project dependencies.

2. **Install Dependencies**: Run the following command to install the necessary libraries and frameworks: `pip install -r requirements.txt`

**Note on Compatibility with Python 3.11**: The application has been tested and works fine with `Python 3.11`. However, if you choose to use this version, you may need to install different versions of some dependencies, which are not listed in the current `requirements.txt`. Please adjust accordingly based on compatibility requirements of the libraries with Python 3.11.

## License

Philosophy Episode Finder is open source and licensed under the GNU General Public License v3.0. For more details, please refer to the [LICENSE](LICENSE) file included in this repository. This license allows for modification, distribution, and private use, while ensuring that improvements are shared with the community.

## Acknowledgments

Special thanks to "Philosophize This!" and its creator, Stephen West, for their invaluable contributions to making philosophy more accessible to a wider audience. This project draws inspiration from their work and aims to further extend the reach of philosophical education and discourse through technology.
