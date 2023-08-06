# MIT License
#
# Copyright (c) 2022 Tobias Höfer
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.
# ==============================================================================
"""Defines a Rest API using fastapi and nka."""
from typing import List, Optional

from fastapi import FastAPI
from nka import NKA
from pydantic import BaseModel

app = FastAPI()


class RequestExtract(BaseModel):
    document: str
    model: Optional[str] = "paraphrase-multilingual-mpnet-base-v2"
    max_seq_length: Optional[int] = 512
    pos_tag: Optional[List[str]] = ["PROPN", "ADJ", "NOUN"]
    top_n: Optional[int] = 7
    diversity: Optional[float] = 0.4
    language: Optional[str] = "de_dep_news_trf"
    exclude: Optional[List[str]] = ["lemmatizer"]


class RequestAssign(BaseModel):
    document: str
    oot_candidates: Optional[List[str]] = None
    blacklist: Optional[List[str]] = None
    candidates: Optional[List[str]] = None
    model: Optional[str] = "paraphrase-multilingual-mpnet-base-v2"
    max_seq_length: Optional[int] = 512
    pos_tag: Optional[List[str]] = ["PROPN", "ADJ", "NOUN"]
    top_n: Optional[int] = 7
    diversity: Optional[float] = 0.4
    language: Optional[str] = "de_dep_news_trf"
    exclude: Optional[List[str]] = ["lemmatizer"]


@app.post("/de/1/extract-keywords")
def extract_keywords(request: RequestExtract):
    model = NKA(model=request.model, max_seq_length=request.max_seq_length)
    keywords = model.extract_keywords(document=request.document,
                                      pos_tag=request.pos_tag,
                                      top_n=request.top_n,
                                      diversity=request.diversity,
                                      language=request.language,
                                      exclude=request.exclude)

    if keywords:
        # Parse to specific JSON-Format.
        result = {
            "keywords": {
                "keywords": [{
                    "keyword": key,
                    "score": value
                } for key, value in dict(keywords).items()]
            }
        }
    else:
        result = []
    return result


@app.post("/de/1/assign-keywords")
def assign_keywords(request: RequestAssign):
    model = NKA(model=request.model, max_seq_length=request.max_seq_length)
    keywords = model.assign_keywords(document=request.document,
                                     oot_candidates=request.oot_candidates,
                                     blacklist=request.blacklist,
                                     candidates=request.candidates,
                                     pos_tag=request.pos_tag,
                                     top_n=request.top_n,
                                     diversity=request.diversity,
                                     language=request.language,
                                     exclude=request.exclude)

    if keywords:
        # Parse to specific JSON-Format.
        result = {
            "keywords": {
                "keywords": [{
                    "keyword": key,
                    "score": value
                } for key, value in dict(keywords).items()]
            }
        }
    else:
        result = []
    return result
