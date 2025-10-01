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

from langchain_community.document_transformers import EmbeddingsRedundantFilter
from langchain_community.document_transformers import LongContextReorder
from langchain_community.document_transformers import EmbeddingsClusteringFilter
# from langchain_community.embeddings import VertexAIEmbeddings
from langchain_google_vertexai import VertexAIEmbeddings
from langchain.retrievers import ContextualCompressionRetriever
from google.cloud.logging_v2.logger import Logger
from langchain.retrievers.document_compressors import DocumentCompressorPipeline
from langchain.retrievers.merger_retriever import MergerRetriever
from langchain.text_splitter import CharacterTextSplitter
from langchain.retrievers.document_compressors import LLMChainFilter
from langchain_google_vertexai import VertexAI
from typing import Any, Mapping

llm = VertexAI(model_name="gemini-1.0-pro-002")

def combine_retriever(retrievers: list, logger:Logger, log_id: str, filter_embeddings: VertexAIEmbeddings)->Mapping[Any, Any]:
    """
    Takes list of retrievrs as input and returns merged retriever.
    Args:
        retrievers: List of retrievers.
    Returns:
        Single retriever object.
    """
    lotr = MergerRetriever(retrievers=retrievers)
    try:
        # splitter = CharacterTextSplitter(chunk_size=300, chunk_overlap=0, separator=". ")
        llm_filter = LLMChainFilter.from_llm(llm)
        filter_em = EmbeddingsRedundantFilter(embeddings=filter_embeddings)
        relevant_filter = EmbeddingsFilter(embeddings=embeddings, similarity_threshold=0.8)
        reordering = LongContextReorder()
        pipeline = DocumentCompressorPipeline(transformers=[llm_filter, filter_em, relevant_filter, 
                                                            reordering])
        compression_retriever = ContextualCompressionRetriever(
            base_compressor=pipeline, base_retriever=lotr,
        )
        log = "Run: " + log_id + \
            " Retriever Clustering & sorting process successful"
        logger.log_text(log, severity="INFO")
    except Exception as e:
        log = "Run: " + log_id + " Retriever Clustering & sorting " + \
            f"process failed | Standard operating procedure initiated: {e}"
        logger.log_text(log, severity="INFO")
        return lotr, lotr
    return compression_retriever, lotr
