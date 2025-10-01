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

from langchain_google_vertexai import VertexAI
from vertexai.preview.tuning import sft
from vertexai.generative_models import GenerativeModel, Part, FinishReason
import vertexai.preview.generative_models as generative_models
import random
import tqdm
import re
import traceback
import json
from google.cloud import storage
import pandas as pd
import numpy as np
import time
import inspect
import logging
import warnings
import pandas as pd
import sqlite3
import pandas as pd
import math
from google.cloud import aiplatform
import configparser
import subprocess
from req_prop_packages.config import (PROJECT_ID, REGION)
project_id = PROJECT_ID
region = REGION
config_file_path = "../rfp-model/config.ini" #Replace with your config.ini file path


def get_latest_endpoint(project_id, location):
  """
  Get latest deployed endpoint for replacement  
  """  
  aiplatform.init(project=project_id, location=location)
  endpoints = aiplatform.Endpoint.list()
  if not endpoints:
    raise ValueError("No endpoints found.")
  latest_endpoint = sorted(endpoints, key=lambda x: x.create_time, reverse=True)[0]  
  return latest_endpoint.resource_name



def update_model_name_in_config(config_file: str, section: str, key: str, value: str):
    """
    Update a specific key's value(model_name) in a given section of the config.ini file.
    """
    config = configparser.ConfigParser()
    config.read(config_file) 
    if section in config:
        config[section][key] = value
        with open(config_file, 'w') as configfile:
            config.write(configfile)
        print(f"Updated {key} in section [{section}] to {value}.")
    else:
        print(f"Section [{section}] not found in {config_file}.") 
#---------------------------------------------------------------------------------------------------#
#--------Placeholder code to push only config.ini changes to git to trigger the CI/CD pipeline------#
def push_config_to_git(repo_path: str, file_to_commit: str, commit_message: str, branch: str = "main"):
    
    try:
        # Navigate to the repository
        subprocess.run(["git", "-C", repo_path, "add", file_to_commit], check=True)
        subprocess.run(["git", "-C", repo_path, "commit", "-m", commit_message], check=True)
        subprocess.run(["git", "-C", repo_path, "push", "origin", branch], check=True)
        print("Config changes pushed to Git successfully.")
    except subprocess.CalledProcessError as e:
        print(f"Error during Git operations: {e}")

#----------------------------------------------------------------------------------------------------#
 
# Fetch the latest endpoint
latest_endpoint = get_latest_endpoint(project_id, region)
if latest_endpoint:
    # Update the model_name in the config file
    update_model_name_in_config(config_file_path, "search-model-parameters", "model_name", latest_endpoint)        
    
    # Replace below variables with your actual values
    repo_path = "/path/to/your/git/repository"
    config_file_path = config_file_path 
    commit_message = "Update model_name to latest deployed endpoint"
    branch_name = "branch_name"  # Adjust as per your repository
    
    # Push the changes
    #push_config_to_git(repo_path, config_file_path, commit_message, branch_name) 