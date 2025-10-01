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
Vertex search data extraction module.
"""
# Discovery search wrapper
import datetime
from typing import List
from google.api_core.client_options import ClientOptions
from google.cloud import discoveryengine_v1 as discoveryengine
from google.cloud import discoveryengine_v1beta as discoveryengine
from langchain.docstore.document import Document
from langchain_community.vectorstores import DocArrayInMemorySearch
from langchain_google_vertexai import VertexAIEmbeddings
from req_prop_packages.config import SEARCH_EMBEDDING_MODEL
from req_prop_packages.status_output import print_status


def vx_search(
    project_id: str,
    location: str,
    data_store_id: str,
    search_query: str,
    page_size: int,
    content_type="extractive_segments",
    ) -> List[discoveryengine.SearchResponse]:
    """Search for documents in a data store.

    For more information, refer to:
    https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store

    Args:
        project_id: The ID of the project.
        location: The location of the data store.
        data_store_id: The ID of the data store.
        search_query: The search query.

    Returns:
        A list of search results.
    """
    #  For more information, refer to:
    # https://cloud.google.com/generative-ai-app-builder/docs/locations#specify_a_multi-region_for_your_data_store
    with open("prompts/vertex_search_preamble.txt", encoding='UTF-8') as f:
        prompt = f.read()
    preamble = prompt.format(prev_questions=str(search_query['prev_ques']),
                           search_refinement=str(search_query['search_refinement']),
                           date=str(datetime.date.today())
                          )
    # print(preamble)
    embeddings = VertexAIEmbeddings(model_name=SEARCH_EMBEDDING_MODEL)
    print_status(f"Present query: {search_query['query']}")
    client_options = (
        ClientOptions(api_endpoint=f"{location}-discoveryengine.googleapis.com")
        if location != "global"
        else None
    )
    client = discoveryengine.SearchServiceClient(client_options=client_options)
    # The full resource name of the search engine serving config
    # print("INFO:     Search app debugging -2")
    serving_config = client.serving_config_path(
        project=project_id,
        location=location,
        data_store=data_store_id,
        serving_config="default_config",
    )
    content_search_spec = discoveryengine.SearchRequest.ContentSearchSpec(
        # For information about snippets, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/snippets
        snippet_spec=discoveryengine.SearchRequest.ContentSearchSpec.SnippetSpec(
            return_snippet=True
        ),
        extractive_content_spec =
          discoveryengine.SearchRequest.ContentSearchSpec.ExtractiveContentSpec(
            max_extractive_segment_count=4
        ),
        # For information about search summaries, refer to:
        # https://cloud.google.com/generative-ai-app-builder/docs/get-search-summaries
        summary_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec(
            summary_result_count=1,
            include_citations=True,
            ignore_adversarial_query=True,
            model_prompt_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelPromptSpec(
                preamble=preamble
            ),
            ignore_non_summary_seeking_query=True,
            model_spec=discoveryengine.SearchRequest.ContentSearchSpec.SummarySpec.ModelSpec(
                # version="gemini-1.0-pro-002/answer_gen/v1",
                version="stable",
            ),
        ),
    )
    query = ("Previous questions" +
             "".join(search_query['prev_ques']) + 
             "\n Present Question:" + search_query['query'])
    request = discoveryengine.SearchRequest(
        serving_config=serving_config,
        query=query,
        page_size=page_size,
        content_search_spec=content_search_spec,
        query_expansion_spec=discoveryengine.SearchRequest.QueryExpansionSpec(
            condition=discoveryengine.SearchRequest.QueryExpansionSpec.Condition.AUTO,
        ),
        spell_correction_spec=discoveryengine.SearchRequest.SpellCorrectionSpec(
            mode=discoveryengine.SearchRequest.SpellCorrectionSpec.Mode.AUTO
        ),
    )
    
    response = client.search(request)
    
    # print("error in search app client resp")
    sources = []
    docs = []
    retriever=None
    for document in response.results:
        title = "[" + str(document.document.derived_struct_data.get('title')) + "]"
        src_link = "(" + str(document.document.derived_struct_data.get('link')) + ")"
        md_link =  title + src_link
        fields = document.document.derived_struct_data.items()
        # sources.append(document.document.derived_struct_data.get('link'))
        for i in fields:
            # print(i)
            if i[0] == 'extractive_answers' and content_type=='extractive_answers':
                for extractive_ans in i[1]:
                    # print(dir(extractive_ans))
                    doc =  Document(page_content=str(extractive_ans.get('content')),
                    metadata={"source": str(document.document.derived_struct_data.get('link'))})
                    docs.append(doc)
            if i[0] == 'snippets' and content_type=='snippets':
                for extractive_ans in i[1]:
                    # print(dir(extractive_ans))
                    # print(extractive_ans.get('snippet'))
                    doc =  Document(page_content=str(extractive_ans.get('snippet')),
                    metadata={"source": str(document.document.derived_struct_data.get('link'))})
                    docs.append(doc)
            if i[0] == 'extractive_segments' and content_type=='extractive_segments':
                for extractive_ans in i[1]:
                    # print(dir(extractive_ans))
                    # print(extractive_ans.get('content'))
                    doc =  Document(page_content=str(extractive_ans.get('content')),
                    metadata={"source": md_link})
                    docs.append(doc)
    if response.summary.summary_text!='':
        doc =  Document(page_content=str("[rfp-summary] " + response.summary.summary_text),
          metadata={"source": "Vertex search response Candidate"})
        docs.append(doc)
    else:
        print_status("Vertex search returned empty string")
    if docs:
        retriever = DocArrayInMemorySearch.from_documents(docs,
          embeddings).as_retriever(search_kwargs={"k": page_size})
    return sources, retriever
