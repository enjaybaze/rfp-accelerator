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
Module for defining custom llm wrapper using langchain
"""
from typing import Optional, Dict, Any
from langchain_google_vertexai import VertexAI
from langchain_community.llms import HuggingFaceHub
from langchain_anthropic import ChatAnthropic

from req_prop_packages.config import (LLM_PROVIDER, GEMINI_MODEL, CLAUDE_MODEL,
                                      LLAMA_MODEL, SEARCH_MODEL_TEMPERATURE,
                                      SEARCH_MODEL_MAX_OUTPUT_TOKENS)

def get_llm(params: Optional[Dict[str, Any]] = None):
    """
    Returns the appropriate LLM client based on the provider specified in the config.

    Args:
        params (Optional[Dict[str, Any]]): A dictionary of parameters to configure the LLM.
                                           Overrides the default values from the config.

    Returns:
        langchain_core.language_models.llms.LLM: The LLM client.
    """
    if params is None:
        params = {}

    temperature = params.get("temperature", SEARCH_MODEL_TEMPERATURE)
    max_output_tokens = params.get("max_output_tokens", SEARCH_MODEL_MAX_OUTPUT_TOKENS)

    if LLM_PROVIDER == "gemini":
        return VertexAI(model_name=GEMINI_MODEL,
                        temperature=temperature,
                        max_output_tokens=max_output_tokens,
                        **params)
    elif LLM_PROVIDER == "claude":
        # Claude uses 'max_tokens_to_sample' instead of 'max_output_tokens'
        claude_params = params.copy()
        claude_params.pop('max_output_tokens', None) # remove to avoid conflict
        return ChatAnthropic(model=CLAUDE_MODEL,
                             temperature=temperature,
                             max_tokens_to_sample=max_output_tokens,
                             **claude_params)
    elif LLM_PROVIDER == "llama":
        # Llama from HuggingFaceHub uses 'max_new_tokens'
        llama_params = params.copy()
        llama_params.pop('max_output_tokens', None)
        return HuggingFaceHub(repo_id=LLAMA_MODEL,
                              model_kwargs={
                                  "temperature": temperature,
                                  "max_new_tokens": max_output_tokens,
                                  **llama_params
                              })
    else:
        raise ValueError(f"Unsupported LLM provider: {LLM_PROVIDER}")
