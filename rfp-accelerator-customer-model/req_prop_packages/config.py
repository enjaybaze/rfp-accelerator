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
Configuration handling file.
"""
import ast
import configparser
from req_prop_packages.config_check import get_config_file_name
from req_prop_packages.status_output import print_status

# reading config.ini
config = configparser.ConfigParser()
config_file_name = get_config_file_name()
print_status(f"Selected config file: {config_file_name}")
config.read(f'{config_file_name}')
# vertex search and model configurations
SEARCH_PARAMETERS = config['search-model-parameters']
SEARCH_MODEL_NAME = SEARCH_PARAMETERS['model_name']
SEARCH_MODEL_TEMPERATURE = float(SEARCH_PARAMETERS['temperature'])
SEARCH_MODEL_MAX_OUTPUT_TOKENS = int(SEARCH_PARAMETERS['max_output_tokens'])
SEARCH_MODEL_TOP_P = float(SEARCH_PARAMETERS['top_p'])
SEARCH_MODEL_TOP_K = int(SEARCH_PARAMETERS['top_k'])
SEARCH_PREVIEW_MODEL = ast.literal_eval(SEARCH_PARAMETERS['preview_model'])
SEARCH_LANGUAGE_TRANSLATION = SEARCH_PARAMETERS['language_translation']
SEARCH_PAGE_SIZE = int(SEARCH_PARAMETERS['page_size'])
SEARCH_EMBEDDING_MODEL = str(SEARCH_PARAMETERS['embedding_model'])
# general project configuration
PROJECT_CONFIG = config['project-general']
LOG_NAME = PROJECT_CONFIG['LOG_NAME']
PROJECT_ID = PROJECT_CONFIG['PROJECT_ID']
REGION = PROJECT_CONFIG['REGION']
# dependency question extraction - configuration
DEPS_PARAMETERS = config['deps-parameters']
DEPS_LLM = DEPS_PARAMETERS['llm']
DEPS_TEMPERATURE = float(DEPS_PARAMETERS['temperature'])
DEPS_MAX_TOKEN = int(DEPS_PARAMETERS['max_output_tokens'])
DEPS_MODEL_MAX_CONTEXT_LENGTH = int(DEPS_PARAMETERS['deps_context_length'])
# datastore details configurations
DATA_STORE_CONFIG = config['datastore']
PROJECT_ID = DATA_STORE_CONFIG['PROJECT_ID']
LOCATION_ID = DATA_STORE_CONFIG['LOCATION_ID']
DATA_STORE_LIST = [ds.strip() for ds in DATA_STORE_CONFIG['DATA_STORE_LIST'].split(",")]

# database api
DATABASE_CONFIG_API = config['db']
DB_API = DATABASE_CONFIG_API['DATABASE_API']

# auth credentials
AUTH_CONFIG = config['auth']
SECRET_ID = AUTH_CONFIG['SECRET_ID']
SECRETS_NAME = str(AUTH_CONFIG['SECRETS_NAME'])

# LLM provider configuration
LLM_CONFIG = config['llm']
LLM_PROVIDER = LLM_CONFIG['provider']

# Gemini configuration
GEMINI_CONFIG = config['gemini']
GEMINI_MODEL = GEMINI_CONFIG['model']

# Claude configuration
CLAUDE_CONFIG = config['claude']
CLAUDE_MODEL = CLAUDE_CONFIG['model']

# Llama configuration
LLAMA_CONFIG = config['llama']
LLAMA_MODEL = LLAMA_CONFIG['model']