# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/12 11:43
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: ollama_embedding.py
import aiohttp
import requests
from typing import List, Generator, Optional
from pydantic import Field
import json

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding


OLLAMA_EMBEDDING_URL = "http://localhost:11434/api/embeddings"


class OllamaEmbedding(Embedding):
    """The Ollama embedding class."""
    # ollama_api_key: Optional[str] = Field(
    #     default_factory=lambda: get_from_env("OLLAMA_API_KEY")
    # )

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts.

        This function interfaces with the ollama embedding API to obtain
        embeddings for a batch of input texts. It handles batching of input texts
        to ensure efficient API calls. Each text is processed using the specified
        embedding model.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call to ollama fails, an exception is raised with
                       the respective error code and message.
        """
        def post(post_params):
            response = requests.post(
                url=OLLAMA_EMBEDDING_URL,
                headers={
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {self.ollama_api_key}"
                },
                data=json.dumps(post_params, ensure_ascii=False).encode(
                    "utf-8"),
                timeout=120
            )
            resp_json = response.json()
            return resp_json
        # if not self.ollama_api_key:
        #     raise Exception("No OLLAMA_API_KEY in your environment.")
        result = []
        post_params = {
            "model": self.embedding_model_name,
            "prompt": "",
        }

        for text in texts:
            post_params["prompt"] = text
            resp_json: dict = post(post_params)
            data = resp_json.get("embedding")
            if data:
                result.append(data)
            else:
                error_message = resp_json.get("error", "")
                raise Exception(f"Failed to call ollama embedding api, "
                                f"error message:{error_message}")
        return result

    async def async_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Async version of get_embeddings.

        This function interfaces with the ollama embedding API to obtain
        embeddings for a batch of input texts. It handles batching of input texts
        to ensure efficient API calls. Each text is processed using the specified
        embedding model.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call to ollama fails, an exception is raised with
                       the respective error code and message.
        """
        async def async_post(post_params):
            async with aiohttp.ClientSession() as session:
                async with await session.post(
                        url=OLLAMA_EMBEDDING_URL,
                        headers={
                            "Content-Type": "application/json",
                            # "Authorization": f"Bearer {self.ollama_api_key}"
                        },
                        data=json.dumps(post_params, ensure_ascii=False).encode(
                            "utf-8"),
                        timeout=120,
                ) as resp:
                    resp_json = await resp.json()
            return resp_json
        # if not self.ollama_api_key:
        #     raise Exception("No OLLAMA_API_KEY in your environment.")
        result = []
        post_params = {
            "model": self.embedding_model_name,
            "prompt": "",
        }

        for text in texts:
            post_params["prompt"] = text
            resp_json: dict = await async_post(post_params)
            data = resp_json.get("embedding")
            if data:
                result.append(data)
            else:
                error_message = resp_json.get("error", "")
                raise Exception(f"Failed to call ollama embedding api, "
                                f"error message:{error_message}")
        return result