# How to Prep Philosophize This! data

1. run `data_preparation/scrappers/philosophize_this/scrapper_philosohpize_this.py` to download all the data from Philosophize This.
2. Data will be located under `data/philosophize_this/`
   1. episode_transcripts
3. Next use summarizer under data_preparation to create summaries and put them under `data/philosophize_this/shorts` - use: `python -m data_preparation.scrappers.philosophize_this.summarizer`
4. Use `merger_script.py` to create `merged_data.csv` from episode_transcripts and shorts - `data_preparation\scrappers\philosophize_this\merger_script.py`
5. Finally we should be able to use merged_data.csv to build our vector database!
6. convert all the csv files to sqlite using `data_preparation\scrappers\philosophize_this\save_sqlite.py`
7. merge all the metadata databases created from all the podcasts
8. Remove everything under `data/vectorDB`
9. run `data_preparation/build_database.py` - NOTE: you have to prepare all your data for all the podcasts before running this!

Note: transcription_processed under `data/philosophize_this` are cleaned up transcripts used for building up a test dataset.
transcription_processed is extra cleaned up content, it is not required to make the project work.
