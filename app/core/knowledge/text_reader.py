# !/usr/bin/env python3
# -*- coding:utf-8 -*-

# @Time    : 2024/3/18 14:21
# @Author  : wangchongshi
# @Email   : wangchongshi.wcs@antgroup.com
# @FileName: pdf_parser.py
from pathlib import Path
from typing import List, Optional, Dict, Set

from agentuniverse.agent.action.knowledge.reader.reader import Reader
from agentuniverse.agent.action.knowledge.store.document import Document


class TextReader(Reader):
    """jsonl reader."""

    def load_data(self, file: str, ext_info: Optional[Dict] = None) -> List[Document]:
        """Parse the jsonl file.

        Note:
            `datasets` is required to read jsonl files: `pip install datasets`
        """
        
        """表姨
        学生
        表弟"""
        with open(file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        docs = []

        for text in lines:
            docs.append(Document(text=text))
        return docs

    def load_to_list(self, file: str, ext_info: Optional[Dict] = None) -> List[str]:
        """Parse the jsonl file."""
        with open(file, "r", encoding="utf-8") as f:
            lines = [line.strip() for line in f.readlines()]
        return lines
    
    def load_to_set(self, file: str, ext_info: Optional[Dict] = None) -> Set[str]:
        """Parse the jsonl file."""
        with open(file, "r", encoding="utf-8") as f:
            lines = {line.strip() for line in f.readlines()}
        return lines