from typing import List
import time
import pytest
import pandas as pd

from langchain.schema.document import Document

from loguru import logger

from engine.similiarty_retrieval import suggest_me_episodes
from engine.utils import attach_summaries
from engine.similiarty_retrieval import find_episodes
from tests.utils import table_print


########################## prompts ##############################

prompt_camus = "I want to learn about Albert Camus?", (170, 105, 104, 103, 88, 87, 86)
prompt_camus_sartre = "What happened between Camus and Sartre?", (88, 87, 86)
prompt_freedom = "I am curious to understand freedom better", (151, 141, 86, 140, 66)


########################## prompt End ###########################

tests = [
    prompt_camus,
    prompt_camus_sartre,
    prompt_freedom,
    
]


def sort_for_print(l1: List, l2: List):
    # this method will sort both lists for print
    # common values will come first, and then rest of the

    l1 = sorted(l1, reverse=True)
    l2 = sorted(l2, reverse=True)
    s1 = set(l1)
    s2 = set(l2)
    s_intersect = s1.intersection(s2)
    l_intersect = sorted(list(s_intersect), reverse=True)
    rl1 = list(l_intersect)
    rl2 = list(l_intersect)
    rl1.extend([i for i in l1 if i not in s_intersect])
    rl2.extend([i for i in l2 if i not in s_intersect])
    return rl1, rl2, l_intersect


@pytest.mark.parametrize(
    "prompt, potential_responses",
    tests,
    ids=[
        "prompt_camus",
        "prompt_camus_sartre",
        "prompt_freedom",
    ],
)
def test_1(prompt, potential_responses):
    logger.info("Testing: {prompt}", prompt=prompt)
    
    most_common_epis = find_episodes(prompt=prompt, k=8)
    logger.info(
        "Suggested Episodes: {most_common_epis}", most_common_epis=most_common_epis
    )
    
    ranked_suggested_epis = [int(i["episode_number"]) for i in most_common_epis]
    
    logger.info(f"returned episodes: {ranked_suggested_epis}" )
    logger.info(f"expected episodes: {potential_responses}")

    for c in ranked_suggested_epis:
        if c in potential_responses:
            return 
    assert False, "No common episodes are found"



def abstract_smart(p_series):
    return p_series.Abstract

def person_smart(p_series):
    return p_series.Person


K = 12
TOP_K = 6

@pytest.mark.parametrize("get_question, file_path, k, top_k", [(person_smart, "./tests/questions.csv", K, TOP_K) , (abstract_smart,  "./tests/questions.csv", K, TOP_K)])
def test_philosophize_this(
    get_question,
    file_path,
    k,
    top_k,
):
    logger.info("Testing for Philosophize This")
    logger.info(f"K={k}, TOP_K={top_k}, {get_question.__qualname__}")
    INDEX = 0
    df = pd.read_csv(file_path)
    correct = 0
    total = 0

    for INDEX in range(len(df)):
        time.sleep(3)
        source_episode = df.iloc[INDEX].EPI_NUM
        question = get_question(df.iloc[INDEX])
        if len(question) < 3:
            continue
        total += 1
        most_common_epis = find_episodes(prompt=question, k=k, TOP_K=top_k)
        

        if most_common_epis == []:
            logger.warning(f"Prompt: {question} - Nothing was found!")
            continue

        ranked_suggested_epis = [int(i["episode_number"]) for i in most_common_epis]
        logger.info(f"returned epis: {ranked_suggested_epis}" )
        logger.info(f"{len(ranked_suggested_epis)}")
        logger.info(f"source: {source_episode}")
        if source_episode in ranked_suggested_epis:
            logger.info(f"Passed - Question: {question}")
            correct += 1
        else:
            logger.warning(f"question {question}: was not found; index: {INDEX}")

    logger.info(f"total: {total}")
    logger.info(f"correct: {correct}")
    logger.info(f"recall: {correct/total * 100}")