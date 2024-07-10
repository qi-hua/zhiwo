# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/6/12 11:43
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: minirbt256_embedding.py
import aiohttp  
import requests
from typing import List, Generator, Optional
from pydantic import Field
import json

from agentuniverse.base.annotation.singleton import singleton
from agentuniverse.base.util.logging.logging_util import LOGGER
from agentuniverse.base.util.env_util import get_from_env
from agentuniverse.agent.action.knowledge.embedding.embedding import Embedding

@singleton
class Minirbt256Model:

    try:
        from transformers import BertTokenizer, BertModel
    except ImportError:
        LOGGER.error("Please install transformers")
        exit(1)
    model_path = "/home/qihua/computer/models/minirbt-h256"
    tokenizer = BertTokenizer.from_pretrained(model_path)
    model = BertModel.from_pretrained(model_path)

    def generate_embeddings(self, text: str) -> List[float]:
        """
        Generate embeddings for a text.
        """
        # return self.model(**self.tokenizer(text, return_tensors="pt")).last_hidden_state.mean(dim=1).squeeze().tolist()
        return self.model(**self.tokenizer(text, return_tensors="pt")).pooler_output[0].tolist()


class Minirbt256Embedding(Embedding):
    """The Minirbt256 embedding class."""
    # minirbt256_api_key: Optional[str] = Field(
    #     default_factory=lambda: get_from_env("OLLAMA_API_KEY")
    # )

    def get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """
        Retrieve text embeddings for a list of input texts.

        This function interfaces with the minirbt256 embedding API to obtain
        embeddings for a batch of input texts. It handles batching of input texts
        to ensure efficient API calls. Each text is processed using the specified
        embedding model.

        Args:
            texts (List[str]): A list of input texts to be embedded.

        Returns:
            List[List[float]]: A list of embeddings corresponding to the input texts.

        Raises:
            Exception: If the API call to minirbt256 fails, an exception is raised with
                       the respective error code and message.
        """
        result = []
        for text in texts:
            data = Minirbt256Model().generate_embeddings(text)
            if data:
                result.append(data)
            else:
                raise Exception(f"Failed to call minirbt256 generate_embeddings")
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
        return self.get_embeddings(texts)