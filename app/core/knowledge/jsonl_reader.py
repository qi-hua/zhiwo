# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 14:21
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: pdf_parser.py
from pathlib import Path
from typing import List, Optional, Dict

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class JsonlReader(Reader):
    """jsonl reader."""

    def load_data(self, file: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the jsonl file.

        Note:
            `datasets` is required to read jsonl files: `pip install datasets`
        """
        try:
            from datasets import Dataset
        except ImportError:
            raise ImportError(
                "datasets is required to read PDF files: `pip install datasets`"
            )
        
        # {"id": "1", "question": "莫妮卡·贝鲁奇的代表作？", "sparql": "select ?x where { <莫妮卡·贝鲁奇> <代表作品> ?x. }", "answer": "<西西里的美丽传说>"}

        ds = Dataset.from_json(file)
        docs = []

        for data in ds:
            metadata = data
            if ext_info is not None:
                metadata.update(ext_info)
            docs.append(Document(metadata=metadata))
        return docs
