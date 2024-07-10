# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/28 19:28
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: demo_knowledge.py

from typing import Optional, Dict, List, Any
from agentuniverse.agent.action.knowledge.knowledge import Knowledge
from agentuniverse.agent.action.knowledge.store.chroma_store import ChromaStore
from agentuniverse.agent.action.knowledge.store.document import Document
from agentuniverse.agent.action.knowledge.store.query import Query
from pathlib import Path

from agentuniverse.base.util.logging.logging_util import LOGGER

from ..ollama_embedding import OllamaEmbedding
from ..jsonl_reader import JsonlReader

from ..text_reader import TextReader


class SparqlTrainKnowledge(Knowledge):
    """The demo knowledge."""

    def __init__(self, **kwargs):
        """The __init__ method.

        Some parameters, such as name and description,
        are injected into this class by the demo_knowledge.yaml configuration.


        Args:
            name (str): Name of the knowledge.

            description (str): Description of the knowledge.

            store (Store): Store of the knowledge, store class is used to store knowledge
            and provide retrieval capabilities, such as ChromaDB store or Redis Store,
            demo knowledge uses ChromaDB as the knowledge storage.

            reader (Reader): Reader is used to load data,
            the demo knowledge uses WebPdfReader to load pdf files from web.
        """
        super().__init__(**kwargs)
        self.store = ChromaStore(
            collection_name="sparql_train_store",
            # persist_path="../../DB/sparql_train.db",
            persist_path="/home/qihua/study/zhiwo/DB/sparql_train.db",
            embedding_model=OllamaEmbedding(
                embedding_model_name='shaw/dmeta-embedding-zh'
            ),
            dimensions=768)
        self.reader = JsonlReader()
        # Initialize the knowledge
        # self.insert_knowledge()
 
    def insert_knowledge(self, **kwargs) -> None:
        """
        Load criminal law pdf and save into vector database.
        """
        # doc_list = self.reader.load_data('https://www.sfu.ca/~poitras/BUFFET.pdf')
        sparql_train_docs = self.reader.load_data('/home/qihua/study/python/CCKS2024——开放领域知识图谱问答评测/round1_train_and_test/train.jsonl')
        for doc in sparql_train_docs:
            # 问题：谁是《湖上草》的主要作者？SPARQL查询语句：select ?x where {{ ?x <主要作品> <湖上草>. }}
            doc.embedding = self.store.embedding_model.get_embeddings([doc.metadata['question']])[0]
            doc.text = "问题：{}\tSPARQL查询语句：{}".format(doc.metadata.pop('question'),doc.metadata.pop('sparql'))
            doc.id = doc.metadata['id']
            del(doc.metadata['answer'])

            # self.store.collection.add(
            #     documents=[doc.text],
            #     metadatas=[doc.metadata],
            #     embeddings=[doc.embedding],
            #     ids=[doc.id]
            # )
            self.store.insert_documents([doc])

    def query_knowledge(self, **kwargs) -> List[Document]:
        """Query the knowledge.

        Query documents from the store and return the results.
        """
        # similarity_top_k = 5
        # if 'similarity_top_k' in kwargs:
        #     similarity_top_k = kwargs['similarity_top_k']
        # LOGGER.info("____________--------------------",kwargs)

        # query = Query(text=kwargs['text'], similarity_top_k=similarity_top_k)
        query = Query(**kwargs)
        return self.store.query(query)
    