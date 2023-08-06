# MIT License
#
# Copyright (c) 2021 Tobias Höfer
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
"""Implements a neural keyword assignment model using sentence transformers API.

    Typical usage example:

    To create a model, you can load in a string pointing to a
    sentence-transformers model:

    from nka.backend import SentenceTransformerBackend
    sentence_model =
        SentenceTransformerBackend("paraphrase-multilingual-mpnet-base-v2")

    or you can instantiate a model yourself:
    from nka.backend import SentenceTransformerBackend
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer("paraphrase-MiniLM-L6-v2")
    sentence_model = SentenceTransformerBackend(embedding_model)
"""
from typing import List, Union

import numpy as np
from sentence_transformers import SentenceTransformer
from nka.backend._abc_embedder import ABCEmbedder


class SentenceTransformerBackend(ABCEmbedder):
    """ Sentence-transformers embedding model.

    This class accepts a string pointing to a specific transorfer model oder a
    sentence_transformer object to be used as an embedding model.
    """

    def __init__(self, model: Union[str, SentenceTransformer]):
        super().__init__()

        if isinstance(model, SentenceTransformer):
            self.model = model
        elif isinstance(model, str):
            self.model = SentenceTransformer(model)
        else:
            raise ValueError(
                "Please select viable sentence transformer, e.g \n"
                "`from sentence_transformers import SentenceTransformer` \n"
                "`model = SentenceTransformer('paraphrase-MiniLM-L6-v2')`")

    def embed(self, documents: List[str], verbose: bool = False) -> np.ndarray:
        """ Embed a list of n documents/words into an n-dimensional matrix of
        embeddings.

        Args:
            documents: A list of documents or words to be embedded.
            verbose: Controls the verbosity of the process.

        Returns:
            Document/words embeddings with shape (n, m) with "n" documents/words
            that each have an embeddings size of "m".
        """
        embeddings = self.model.encode(documents, show_progress_bar=verbose)
        return embeddings
