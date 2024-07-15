# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/12 11:43
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: infinity_embedding.py
import aiohttp
import requests
from typing import List, Generator, Optional
from pydantic import Field
import json

from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding


# Infinity support max 32 string in one batch, each string max tokens is 2048.
INFINITY_MAX_BATCH_SIZE = 32

INFINITY_EMBEDDING_URL = "http://localhost:7997/embeddings"
EMBEDDING_MODEL_NAME = 'Dmeta-embedding-zh'

def batched(inputs: List,
            batch_size: int = INFINITY_MAX_BATCH_SIZE) -> Generator[List, None, None]:
    # Split input string list, due to infinity support 32 strings in one call.
    for i in range(0, len(inputs), batch_size):
        yield inputs[i:i + batch_size]


class InfinityEmbedding(Embedding):
    """The Infinity embedding class."""
    infinity_api_key: Optional[str] = None

    # def __init__(self, **kwargs):
    #     """Initialize the infinity embedding class, need infinity api key."""
    #     super().__init__(**kwargs)
    #     self.infinity_api_key = get_from_env("INFINITY_API_KEY")
    #     if not self.infinity_api_key:
    #         raise Exception("No INFINITY_API_KEY in your environment.")


    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts.

        This function interfaces with the Infinity embedding API to obtain
        embeddings for a batch of input texts. It handles batching of input texts
        to ensure efficient API calls. Each text is processed using the specified
        embedding model.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call to Infinity fails, an exception is raised with
                       the respective error code and message.
        """
        def post(post_params):
            response = requests.post(
                url=INFINITY_EMBEDDING_URL,
                headers={
                    "Content-Type": "application/json",
                    # "Authorization": f"Bearer {self.infinity_api_key}"
                },
                data=json.dumps(post_params, ensure_ascii=False).encode(
                    "utf-8"),
                timeout=20
            )
            resp_json = response.json()
            return resp_json

        result = []
        post_params = {
            "model": self.embedding_model_name,
            "input": {},
        }

        for batch in batched(texts):
            post_params["input"] = batch
            resp_json: dict = post(post_params)
            data = resp_json.get("data")
            if data:
                batch_result = [d['embedding'] for d in data if 'embedding' in d]
                result += batch_result
            else:
                error_message = resp_json.get("detail", "")
                raise Exception(f"Failed to call infinity embedding api, "
                                f"error message:{error_message}")
        return result

    async def async_get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Async version of get_embeddings.

        This function interfaces with the Infinity embedding API to obtain
        embeddings for a batch of input texts. It handles batching of input texts
        to ensure efficient API calls. Each text is processed using the specified
        embedding model.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call to Infinity fails, an exception is raised with
                       the respective error code and message.
        """
        async def async_post(post_params):
            async with aiohttp.ClientSession() as session:
                async with await session.post(
                        url=INFINITY_EMBEDDING_URL,
                        headers={
                            "Content-Type": "application/json",
                            # "Authorization": f"Bearer {self.infinity_api_key}"
                        },
                        data=json.dumps(post_params, ensure_ascii=False).encode(
                            "utf-8"),
                        timeout=20,
                ) as resp:
                    resp_json = await resp.json()
            return resp_json

        result = []
        post_params = {
            "model": self.embedding_model_name,
            "input": {},
        }

        for batch in batched(texts):
            post_params["input"] = batch
            resp_json: dict = await async_post(post_params)
            data = resp_json.get("data")
            if data:
                batch_result = [d['embedding'] for d in data if
                                'embedding' in d]
                result += batch_result
            else:
                error_message = resp_json.get("detail", "")
                raise Exception(f"Failed to call infinity embedding api, "
                                f"error message:{error_message}")
        return result