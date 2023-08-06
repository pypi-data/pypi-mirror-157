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
# =============================================================================
"""This module defines some helper functions."""
from nka.backend._abc_embedder import ABCEmbedder
from nka.backend._sentencetransformers import SentenceTransformerBackend


def select_backend(model) -> ABCEmbedder:
    """ Select an embedding model based on language or a specific sentence
    transformer models. When selecting a language, we choose
    `paraphrase-MiniLM-L6-v2` for English and
    `paraphrase-multilingual-MiniLM-L12-v2` for all other languages as it
    support 100+ languages.
    Returns:
        model: Either a Sentence-Transformer or Flair model
    """
    # Nka language backend.
    if isinstance(model, ABCEmbedder):
        return model

    # Sentence Transformer embeddings.
    if "sentence_transformers" in str(type(model)):
        return SentenceTransformerBackend(model)
    # Create a Sentence Transformer model based on a string
    if isinstance(model, str):
        return SentenceTransformerBackend(model)

    # Defaults to "paraphrase-multilingual-mpnet-base-v2" sentence transformer.
    return SentenceTransformerBackend("paraphrase-multilingual-mpnet-base-v2")
