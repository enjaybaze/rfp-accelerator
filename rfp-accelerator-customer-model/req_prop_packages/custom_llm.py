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
from typing import Any, List, Mapping, Optional
from vertexai.preview import generative_models
from langchain.callbacks.manager import CallbackManagerForLLMRun
from langchain_core.language_models.llms import LLM
from req_prop_packages.config import (SEARCH_MODEL_TEMPERATURE,
                                   SEARCH_MODEL_MAX_OUTPUT_TOKENS,
                                   SEARCH_MODEL_TOP_P)


def generate(text: str, model: str) -> str:
    """Generates text using a generative model.

    Args:
        text: The text to generate from.
        model: The generative model to use.

    Returns:
        The generated text.
    """
    response_text = ""
    model = generative_models.GenerativeModel(model)
    responses = model.generate_content(
        text,
        generation_config={
            "max_output_tokens": SEARCH_MODEL_MAX_OUTPUT_TOKENS,
            "temperature": SEARCH_MODEL_TEMPERATURE,
            "top_p": SEARCH_MODEL_TOP_P
        },
        stream=True,
    )
    for response in responses:
        response_text += response.candidates[0].content.parts[0].text
    return response_text


class CustomLLM(LLM):
    """A custom LLM model."""
    model: str

    @property
    def _llm_type(self) -> str:
        """Get the type of the LLM."""
        return "custom"

    def _call(
        self,
        prompt: str,
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> str:
        """Call the custom LLM model.

        Args:
            prompt: The prompt to generate text from.
            stop: A list of tokens to stop generating text at.
            run_manager: A callback manager for the LLM run.
            **kwargs: Additional keyword arguments to pass to the model.

        Returns:
            The generated text.
        """
        return generate(prompt, self.model)

    @property
    def _identifying_params(self) -> Mapping[str, Any]:
        """Get the identifying parameters."""
        return {"n": self.model}
