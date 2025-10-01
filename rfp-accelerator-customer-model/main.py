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
Entry point - Fast API
"""
import json
import uuid
import ast
import configparser
import jwt
import pandas as pd
from PyPDF2 import PdfReader
from fastapi import BackgroundTasks, FastAPI, HTTPException, Body, Request, Depends
from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from io import BytesIO
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, validator, root_validator
from google.auth.transport import requests as g_requests
from google.oauth2 import id_token
from google.cloud import secretmanager
from req_prop_packages.rfp_search import search_qa
from req_prop_packages.deps_extractor import deps_process
from req_prop_packages.config_check import get_config_file_name
from req_prop_packages.status_output import print_status
from req_prop_packages.validation_package.validate import validate_dict_values
from req_prop_packages.question_retrieval import get_questions_by_req_id_by_status



app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins="*",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


class StringQuery(BaseModel):
    """
    A query object represents a query parameters that is used to search for text data.

    Fields:
        model_parameters: A dictionary of model parameters.
        search_parameters: A dictionary of search parameters.
        language_translation: The language to translate the query & results into.
        sources: A list of sources to search.
    """
    model_parameters: dict
    search_parameters: dict
    language_translation: str

    @root_validator(pre=True)
    def root_validate(cls, v):
        """
        input parameter validation function
        """
        expected_types = {"model_parameters": dict,
                         "search_parameters": dict,
                         "language_translation": str,
                         }
        if validate_dict_values(v, expected_types):
            raise HTTPException(status_code=400, detail="Invalid root parameter")
        return v

    @validator("model_parameters")
    def validate_model_parameters(cls, v):
        """
        input parameter validation function
        """
        expected_types = {
            "model_name": str,
            "temperature": float,
            "max_output_tokens": int,
            "top_p": float,
            "top_k": int,
            "preview_model": bool,
        }
        if validate_dict_values(v, expected_types):
            raise HTTPException(status_code=400, detail="Invalid model parameter")
        return v

    @validator("search_parameters")
    def validate_search_parameters(cls, v):
        """
        input parameter validation function
        """
        expected_types = {"query": dict,
                          "page_size": int}
        expected_types_query = {"query": str,
                                "prev_ques": list,
                                "question_id": int,
                                "expert_request_id": str,
                                "search_refinement": str,
                                "run_id": str
                               
                               }
        if validate_dict_values(v['query'], expected_types_query):
            raise HTTPException(status_code=400,
                                detail="Invalid search:query parameter")
        if validate_dict_values(v, expected_types):
            raise HTTPException(status_code=400,
                                detail="Invalid search parameter")
        return v


class DepsExtract(BaseModel):
    """
    The pydantic class to store the file id request.
    
    Fields:
        expert_request_id: File id.
    """
    expert_request_id: str
    user_name: str
    token: str

    @root_validator(pre=True)
    def root_validate(cls, v):
        """
        input parameter validation function
        """
        expected_types = {"expert_request_id": str,
                         "user_name": str,
                         "token": str}
        if validate_dict_values(v, expected_types):
            raise HTTPException(status_code=400, detail="Invalid root parameter")
        return v


@app.post("/string-query")
async def string_query(background_tasks: BackgroundTasks,
    string_query_data: StringQuery = Body(...))->dict:
    """
    FastAPI post request route function for single query.
    
    Fields:
        background task: The background task object, used for triggering new background tasks.
        string query object: A query object represents a query parameters that is used to 
        search for text data.
    """
    try:
        query = string_query_data.search_parameters['query']['query']
        if query is None:
            raise HTTPException(status_code=400, detail="String query is required")
        print_status(f"Query request: {query[0:15]}.....")
        log_id = str(uuid.uuid4())
        background_tasks.add_task(search_qa, log_id,
                  string_query_data.search_parameters,
                  string_query_data.language_translation,
                  string_query_data.model_parameters)
        return {"answer_id": f"{log_id}", "status":"logged"}
    except Exception as e:
        print(f"string query error {e}")

@app.post("/deps-query")
async def deps_query(background_tasks: BackgroundTasks,
    deps_query_data: DepsExtract, request: Request)->dict:
    """
    FastAPI post request route function for file (multiple section).
    
    Fields:
        background task: The background task object, used for triggering new background tasks.
        deps query object: Object that contains parameters for file processing.
    """
    query_url = str(request.base_url) + "string-query/"
    ######################## input file logic ###################################
    calc_deps = True
    user_ldap = deps_query_data.user_name
    token = deps_query_data.token
    exp_id = deps_query_data.expert_request_id
    if exp_id is None:
        raise HTTPException(status_code=400, detail="Exp id required")
    _, dta = get_questions_by_req_id_by_status(exp_id,'waiting',token, user_ldap)   
    dta.fillna('', inplace=True)    
    #############################################################################
    if len(dta)==0:
        print_status("Invalid Request, No questions under this expert_request_id")
        raise HTTPException(status_code=400,
                            detail="Invalid request, No question under provided expert_request_id")
    

    log_id = str(uuid.uuid4())
    background_tasks.add_task(deps_process,
                              dta,
                              query_url, calc_deps, log_id)
    return {"status":"queued", "id": log_id}


@app.get("/")
async def home():
    """
    Home endpoint
    """
    return {"message":"Now you are in genai model"}
