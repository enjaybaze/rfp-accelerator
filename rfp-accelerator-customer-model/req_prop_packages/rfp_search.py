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
Comphrehsive search module with all integrated functionalities.
"""
# import string
# import traceback
import time
import datetime
import warnings
import vertexai
import pandas as pd
from google.cloud import logging
from sqlalchemy import create_engine
from langchain.chains import RetrievalQA
from langchain.prompts import PromptTemplate
from langchain_google_vertexai import VertexAIEmbeddings
from req_prop_packages.retrievers import get_all_retrievers
from req_prop_packages.config import (LOG_NAME, PROJECT_ID, REGION, SEARCH_EMBEDDING_MODEL,DB_API)
from req_prop_packages.merge_retriever import combine_retriever
from req_prop_packages.google_translate import translate_text
from req_prop_packages.custom_llm import get_llm
from req_prop_packages.status_output import print_status
import requests

warnings.filterwarnings("ignore")


logging_client = logging.Client()
logger = logging_client.logger(LOG_NAME)
embeddings = VertexAIEmbeddings(model_name=SEARCH_EMBEDDING_MODEL)  # Vertex AI embeddings
filter_embeddings = VertexAIEmbeddings(model_name=SEARCH_EMBEDDING_MODEL)
vertexai.init(project=PROJECT_ID, location=REGION)
# text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=150)
MAIN_URL = DB_API.strip()

#Backend API to save the responses
save_model_response = f"{MAIN_URL}/save_model_response"



def escape_special_chars_maketrans(result_str: str)->str:
    """
    Preprocessing to remove escape charectors from
    string data for database.
    
    Args:
        string_data: String data
    Return:
        Processed string
    """
    table = str.maketrans({
       "'": "''",
       '"': '""',
       "\\": "\\\\",
       "%": "\\%",
       "_": "\\_",
       # "\n": "\\n",
       "\r": "\\r",
       "\t": "\\t",
       "|": "\\|",
       "&": "\\&",
    })
    #Translate the string using the translation table.
    escaped_string = result_str.translate(table)
    # Return the escaped string.
    return escaped_string

#Database insertion
def save_response(action: str, resp_param: dict):
    
    
    payload = {"expert_request_id":f"{resp_param['exp_id']}","action": action,
                   "data":[{"question_id":f"{resp_param['qid']}",
                            "response":f"{resp_param['response']}",
                            "dependency": f"{resp_param['dependency']}",
                            "run_status":f"{resp_param['status']}",
                            "context":f"{resp_param['context']}",
                            "process_status": f"{resp_param['process_status']}"}],
              }
    response = requests.post(save_model_response,json=payload, timeout=90)
    return response

def info_logger(search_parameters: dict, translate_service: str,
                model_parameters: dict, log_id: str)->None:
    """
    Log all initial function parameters.
    Args:
        search_parameters: Search configuration parameters.
        llm: Large language model object.
        page_size: The amount of information to be extracted.
        log_id: For logging purposes.

    Returns:
        List of retrievers.
    """
    config_logs = [
        ("query", search_parameters['query']),
        # ("spider_version", search_parameters['spider_version']),
        ("translate_service", translate_service),
        ("project", PROJECT_ID),
        ("preview_model", model_parameters['preview_model']),
        ("model_name", model_parameters['model_name']),
        ("temperature", model_parameters['temperature']),
        ("top_p", model_parameters['top_p']),
        ("top_k", model_parameters['top_k']),
        ("page_size", search_parameters['page_size']),
    ]
    for var, value in config_logs:
        log = f"Run: {log_id} {var}: {value}"
        logger.log_text(log, severity="INFO")
    return None


def llm_model(model_parameters: dict):
    """
    Choose llm object as per definitions.
    Args:
        model_parameters: Model configuration parameters.
    Returns:
        llm object.
    """
    return get_llm(model_parameters)




def search_qa(log_id: str, search_parameters: dict,
                    translate_service: str, model_parameters: dict)->None:
    """
    Comphrensive search implementation.
    Args:
        search_parameters: Search configuration parameters.
        llm: List of selected sources.
        translate_service: Type of translation services.
        model_parameters: The model configuration parameters.

    Returns:
        Full results with, context information.
    """
    info_logger(search_parameters, translate_service, model_parameters, log_id)
    print_status("Information logged successfully.")
    try:
        llm = llm_model(model_parameters)
        print_status("LLM initialized successfully.")
        query_value = str(search_parameters['query']['query'])
        translator = translate_text("en", str(search_parameters['query']['query']))
        search_parameters['query']['query'] = translator['translatedText']
        language = translator['detectedSourceLanguage']
        print_status("Translater initialized successfully.")
        log = "Run: " + log_id + " Detected Language: " + language
        logger.log_text(log, severity="INFO")
        if translate_service == 'gt':
            language = 'en'
        elif translate_service == 'mt':
            pass
        else:
            print_status("Translate service(gt/mt) should be specified.", stat="WARNING")
        retrievers = get_all_retrievers(search_parameters, logger, log_id)
        print_status("Retrievers working initialized successfully")
        if not retrievers:
            print_status("No relevant information found")
            raise ValueError('Retrivers not found')
        # lotr
        compression_retriever, compression_retriever_lotr = combine_retriever(retrievers,
                                                  logger, log_id,
                                                  filter_embeddings)
        log = "Run: " + log_id + " Retriever merging process successful"
        logger.log_text(log, severity="INFO")
        with open("prompts/qa_template.txt", "r", encoding="utf-8") as f:
            prompt_template = f.read()
        log = "Run: " + log_id + " Initializing prompt"
        logger.log_text(log, severity="INFO")
        prompt_template = prompt_template.replace("\n  ", "\n")
        final_prompt = PromptTemplate(
            template=prompt_template, input_variables=["context", "question"],
            partial_variables={"language": f"'{language}'",
                        "prev_questions": str(search_parameters['query']['prev_ques']),
                        "search_refinement": str(search_parameters['query']['search_refinement']),
                        "date": str(datetime.date.today())
                        }
        )
        log = "Run: " + log_id + " Initializing prompt template"
        logger.log_text(log, severity="INFO")
        chain_type_kwargs = {"prompt": final_prompt}
        for i in range(0,5):
            try:
                qa = RetrievalQA.from_chain_type(llm=llm, chain_type="stuff",
                                             retriever=compression_retriever,
                                             chain_type_kwargs=chain_type_kwargs,
                                             return_source_documents=True, verbose=False)
                qa.combine_documents_chain.verbose = False
                qa.combine_documents_chain.llm_chain.verbose = False
                qa.combine_documents_chain.llm_chain.llm.verbose = False
                result = qa.invoke(query_value)
                break
            except ValueError as e:
                compression_retriever = compression_retriever_lotr
                print_status(f"Retry initiated (Value error) for {log_id}: Ensemble answer generation: {e}")
                print(f"Retry initiated (Value error) for {log_id}: Ensemble answer generation: {e}")
            except Exception as e:
                # print(e)
                # print(f"{type(e).__name__} was raised: {e}")
                print_status(f"Retry initiated for {log_id}: Ensemble answer generation, {e}")
                print(f"Retry initiated for {log_id}: Ensemble answer generation, {e}")
                time.sleep(2)
                continue
        context_retrieved = ""
        for src in result['source_documents']:
            context_retrieved += src.page_content
        if translate_service == 'gt':
            language = translator['detectedSourceLanguage']
            translator = translate_text(
                language, result['result'])
            result['result'] = translator['translatedText']
            log = "Run: " + log_id + " gt: final traslation process completed successfully"
            logger.log_text(log, severity="INFO")
        log = "Run: " + log_id + f" Result: {result['result']}"
        logger.log_text(log, severity="INFO")
        log = "Run: " + log_id + " Completed successfully"
        logger.log_text(log, severity="INFO")
        print_status("Process successfully completed")
        sources = ""
        sources = [i.metadata['source'] for i in result['source_documents']]
        sources =  "\n #### References\n" + "\n".join(list(set(sources)))
        formatted_ans = escape_special_chars_maketrans(result['result'])
        if (formatted_ans.find('cannot determine') == -1):
            formatted_ans = formatted_ans + "\n" + sources   
        context_retrieved = escape_special_chars_maketrans(context_retrieved)
        db_data_api = {"exp_id": search_parameters['query']['expert_request_id'],
                       "qid": search_parameters['query']['question_id'],
                       "response":formatted_ans,
                       "dependency":str(search_parameters['query']['prev_ques']),
                       "status": "processed",
                       "context": context_retrieved,
                       "process_status": "pa_review"

                        }      
        save_response("update_model_response", db_data_api)
    except Exception as e:
        print(e)

        db_data_api = {"exp_id": search_parameters['query']['expert_request_id'],
                       "qid": search_parameters['query']['question_id'],
                       "response":"Unable to generate model response",
                       "dependency":str(search_parameters['query']['prev_ques']),
                       "status": "error",
                       "context": '',
                       "process_status": "pa_review"
                        }      
        save_response("update_model_response", db_data_api)