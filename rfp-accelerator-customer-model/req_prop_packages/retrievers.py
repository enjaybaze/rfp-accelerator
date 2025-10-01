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
Create multiple retrievers for ensembling process.
"""
from typing import Any, Mapping
from req_prop_packages.config import (PROJECT_ID, LOCATION_ID, DATA_STORE_LIST)
from req_prop_packages.custom_retriever import CustomizedRetriever
from req_prop_packages.search_app import vx_search
from req_prop_packages.status_output import print_status


def get_search_data(search_parameters, dstore)->Mapping[list, Any]:
    """
    Function for searching using grounding or vertex search as per configurations.
    Args:
        search_parameters: Search configuration parameters.
        embeddings: Vertex ai embedding object, for embedding the retrieved contents.
        dstore: Vertex search data store.
    Returns:
        List of retrievers.
    """
    urls, search_retriever = vx_search(PROJECT_ID, LOCATION_ID,
        dstore,
        search_parameters['query'],
        search_parameters['page_size'],)
    return urls,search_retriever


def get_all_retrievers(search_parameters, logger, log_id)->list:
    """
    Selects all the necessary parameters to create a list of retrievers as per source definitions.
    Args:
        sources: list of selected sources.
        search_parameters: Search configuration parameters.
        llm: Large language model object.
        page_size: The amount of information to be extracted.
        log_id: For logging purposes.
    Returns:
        List of retrievers.
    """
    retrievers = []
    for ds in DATA_STORE_LIST:
        _, retr = get_search_data(
                                search_parameters, ds)
        if retr is not None:
            custom_req_prop_static_retriever = CustomizedRetriever(
                c_retriever=retr, c_source=f"{ds}")
            retrievers.append(custom_req_prop_static_retriever)
            log = "Run: " + log_id + f"{ds} static extracted successfully"
            # print_status(log)
            logger.log_text(log, severity="INFO")
    return retrievers
