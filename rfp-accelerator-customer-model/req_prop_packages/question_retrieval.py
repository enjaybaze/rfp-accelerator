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

import json
import jwt
import ast
import time
import configparser
import requests
import pandas as pd
from google.cloud import secretmanager
from req_prop_packages.status_output import print_status
from req_prop_packages.config_check import get_config_file_name
from req_prop_packages.config import (LOG_NAME, PROJECT_ID, REGION, SEARCH_EMBEDDING_MODEL,DB_API,SECRET_ID,SECRETS_NAME)
import warnings


warnings.filterwarnings("ignore")

MAIN_URL = DB_API.strip()
#Backend API to fetch data from database
get_questions_to_predict = f"{MAIN_URL}/run_model_question"


PROJECT_ID = PROJECT_ID
SECRET_ID = SECRET_ID
SECRETS_NAME = str(SECRETS_NAME)
client = secretmanager.SecretManagerServiceClient()
PARENT = client.secret_path(PROJECT_ID, SECRET_ID)
response = client.access_secret_version(request={"name": SECRETS_NAME})
jwt_secret_key = response.payload.data.decode("UTF-8")


def get_questions_by_req_id_by_status(exp_id: str, exp_status: str, token: str, user_ldap:str):
    """
    This function gets a list of questions to run from the 
    database based on the expert request ID and the run status.

    Args:
        exp_id (str): The expert request ID.
        exp_status (str): The run status of the questions.

    Returns:
        tuple: Length and set of questions in dataframe format.
    """
    ## Request API to get list of questions to run [status = "waiting"]
    json_response = {}
    payload_req_id_and_status =  {"expert_request_id":f"{exp_id}",
                                  "run_status":f"{exp_status}", "token": token, "user_ldap": user_ldap}
    response = requests.post(get_questions_to_predict,json=payload_req_id_and_status, timeout=30)
    if response.status_code==200:
        json_response = json.loads(response.text)
        if json_response.get('questions') is None:
            return 0, []
        return len(json_response['questions']), pd.DataFrame(json_response['questions'])
    print("DB error")
    return 0, []