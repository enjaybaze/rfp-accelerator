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
Custom retriever implementation using langchain.
"""
from typing import List
from langchain.schema.retriever import BaseRetriever
from langchain.callbacks.manager import CallbackManagerForRetrieverRun
from langchain.docstore.document import Document


class CustomizedRetriever(BaseRetriever):
    """
    A customized retriever that wraps another retriever and adds additional functionality.

    Args:
        c_retriever (BaseRetriever): The retriever to wrap.
        c_source (str): The source of the documents retrieved by the wrapped retriever.
    """
    c_retriever: BaseRetriever
    c_source: str
    def _get_relevant_documents(
        self, query: str, *, run_manager: CallbackManagerForRetrieverRun
    ) -> List[Document]:
        """
        Get relevant documents for a given query.

        Args:
            query (str): The query to search for.
            run_manager (CallbackManagerForRetrieverRun): The callback manager for 
            the retriever run.

        Returns:
            List[Document]: A list of relevant documents.
        """
        # Get the relevant documents from the wrapped retriever
        documents = self.c_retriever.get_relevant_documents(query,
                                                callbacks=run_manager.get_child())
        # Add additional information to the documents
        for doc in documents:
            doc.page_content = f"Source: {self.c_source} \n" + \
                "REFERENCE\n---------\n" + doc.page_content
        # Sort the documents by source
        try:
            documents = sorted(documents, key=lambda doc: doc.metadata.get('source'))
        except Exception as e:
            print(f"[INFO] {e}")
        return documents
