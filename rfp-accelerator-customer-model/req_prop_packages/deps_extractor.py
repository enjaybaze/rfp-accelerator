# Copyright 2024 Google LLC

# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at

#     https://www.apache.org/licenses/LICENSE-2.0

# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""
Module for File processing and dependency extraction.
"""
import ast
import time
from typing import Any
import requests
# from langchain_community.llms import VertexAI
from google.cloud import logging
from pandas import DataFrame
# import pandas as pd
from langchain_core.output_parsers import JsonOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_core.pydantic_v1 import BaseModel, Field
from req_prop_packages.config import (LOG_NAME, DEPS_LLM,
                            DEPS_TEMPERATURE, DEPS_MAX_TOKEN,
                            DEPS_MODEL_MAX_CONTEXT_LENGTH,
                            SEARCH_MODEL_NAME, SEARCH_MODEL_TEMPERATURE,
                            SEARCH_MODEL_MAX_OUTPUT_TOKENS,
                            SEARCH_MODEL_TOP_P, SEARCH_MODEL_TOP_K,
                            SEARCH_PREVIEW_MODEL,
                            SEARCH_LANGUAGE_TRANSLATION, SEARCH_PAGE_SIZE)
from req_prop_packages.custom_llm import get_llm
from req_prop_packages.status_output import print_status


logging_client = logging.Client()
logger = logging_client.logger(LOG_NAME)

deps_params = {
    "temperature": DEPS_TEMPERATURE,
    "max_output_tokens": DEPS_MAX_TOKEN
}
deps_llm = get_llm(deps_params)


class DepsQues(BaseModel):
    """
    Represents a question and its dependencies in a question-answering system.

    Args:
        present_question (str): The current question being considered.
        dependent_questions (list): A list of questions that are dependent on the present question.
        These questions should be asked or considered only after the present question is addressed.
        reason (str): A brief explanation or justification for the dependency relationship between
        the present question and its dependent questions.
    """
    present_question: str = Field(description="The present question described in the input")
    dependent_questions: list = Field(
        description="List of dependent question, dependent to present question")
    reason: str = Field(description="""Reason behind the dependency mapping.""")

def deps_extract(ques: str, prev_ques: list)->dict:
    """
    Extracts dependencies of a question given its previous question as context.

    This function leverages an LLM chain to analyze the input question and its preceding question,
    identifying and extracting relevant dependencies. The extracted dependencies are returned
    in a structured dictionary format as defined by the `DepsQues` Pydantic model.

    Args:
        ques (str): The current question to extract dependencies from.
        prev_ques (list): The list of questions preceding the current question, providing context.

    Returns:
        Dict: A dictionary containing the extracted dependencies,
              structured according to the `DepsQues` schema.
    """
    with open("prompts/dependency_prompt.txt", "r", encoding='UTF-8') as f:
        template = f.read()
    parser = JsonOutputParser(pydantic_object=DepsQues)
    prompt = PromptTemplate(
        template=template,
        input_variables=["query", "prev_ques"],
        partial_variables={"format_instructions": parser.get_format_instructions()},
    )
    chain = prompt | deps_llm | parser
    deps_result = chain.invoke({"query": ques, "prev_ques": prev_ques})
    return deps_result

def req_prop_generate(query:dict, api_url:str)->Any:
    """
    Module for triggering api for processing individual questions.
    Args:
        query: The query dictionary consist of individual questions and
               its corresponding related questions
        api_url: The route to which the api points to.
    Returns:
        Answer id/Response status
    """
    model_parameters = {"model_name":SEARCH_MODEL_NAME,
                        "temperature":SEARCH_MODEL_TEMPERATURE,
                        "max_output_tokens":SEARCH_MODEL_MAX_OUTPUT_TOKENS,
                        "top_p":SEARCH_MODEL_TOP_P,
                        "top_k":SEARCH_MODEL_TOP_K,
                        "preview_model": SEARCH_PREVIEW_MODEL,
                        }
    search_parameters = {"query": query,
                        "page_size": SEARCH_PAGE_SIZE,
                        }
    # language_translation = SEARCH_PARAMETERS['language_translation']
    request_body = {
        "model_parameters": model_parameters,
        "search_parameters": search_parameters,
        "language_translation": SEARCH_LANGUAGE_TRANSLATION,
        # "sources": sources
    }
    try:
        response = requests.post(api_url, json=request_body, timeout=30)
        if response.status_code == 200:  
            response_data = response.json()
            return response_data['answer_id']
        print(f"Error in processing: {response.status_code}")
        return None
    except Exception as e:
        print_status(e)
        return None


def deps_process(data: DataFrame,
                 query_url: str,
                 calc_deps: bool, log_id: str):
    """
    The main function responsible for processing individual files and dependency extraction.
    Args:
        data: The dataframe to be processed.
        query_url: The endpoint to which we need to create individual request to question.
        calc_deps: Boolen value specifying weather to calculate dependancy or not.
    """
    rn_expid = log_id
    print("inside deps_process")
    try:
        n = DEPS_MODEL_MAX_CONTEXT_LENGTH
        for i in range(len(data)):
            start_index = max(0, i - n)
            # Get the previous questions
            try:
                if calc_deps:
                    previous_questions = data["question"][start_index:i]
                    deps_data = deps_extract(data['question'][i], list(previous_questions))
                    prev_ques = deps_data['dependent_questions']
                else:
                    prev_ques = []
            except:
                prev_ques = []

            question_payload = {"query":data["question"][i], "prev_ques": prev_ques,
                          "question_id": int(data['id'][i]),
                          "expert_request_id": data['expert_request_id'][i],
                          "search_refinement": data['search_refinement'][i],
                          "run_id": rn_expid}
            
            req_prop_generate_resp = req_prop_generate(question_payload, query_url)
            if req_prop_generate_resp is None:
                log = f"Run: {rn_expid} Error occured for question: {question_payload}"
                print_status(log)
                logger.log_text(log, severity="ERROR")
            time.sleep(0.2)
    except Exception as e:
        log = f"Run: {rn_expid} Exception: {e}"
        logger.log_text(log, severity="ERROR")
        print_status(f"Exception {e}")
