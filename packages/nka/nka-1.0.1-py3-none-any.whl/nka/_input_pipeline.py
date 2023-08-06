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
"""Defines input pipeline specific text transformations and input cleaning.
Using a spacy nlp pipeline the preprocessor returns a spacy Doc object.

It is necessary to remove non-useful information from a text, e.g emojis,
single characters, spelling, special symbols, etc.
"""
import os
import io
import re
from typing import List

import spacy


def _read_doc(document: str) -> str:
    # Check if list of strings and concatenate them via space.
    if isinstance(document, List):
        document = " ".join(document)

    # Read txt from file
    if os.path.isfile(document):
        # txt files.
        with io.open(document, "r", encoding="utf-8") as f:
            text = f.read()

    # Take input as text.
    elif isinstance(document, str):
        text = document
    return text


def _pre_process(txt: str) -> str:
    # TODO search for best possible solution. Eliminate Code sections,
    # normalize words to root ?
    # Lowercase ?
    #text = text.lower()

    # Remove tags
    text = re.sub("&lt;/?.*?&gt", " &lt;&gt; ", txt)

    # Remove special characters and digits
    text = re.sub("(\\d|\\W)+", " ", text)

    # Remove single characters
    text = re.sub(r"\b[a-zA-Z]\b", "", text)

    # Remove leading and ending spaces
    text = text.strip()

    return text


def preprocessor(document: str,
                 language: str = "de_dep_news_trf",
                 exclude: List[str] = None) -> spacy.tokens.Doc:
    """Reads document and remove non-useful information from a text.

    This preprocessor uses a spacy nlp pipeline to transfrom its input to a
    Doc object. When you call preprocessor on a text, we will clean and
    eliminate non-useful information using regex, then spacy will internally
    first tokenizes the text to produce a Doc object, The Doc is then processed
    in several different steps - this is also referred to as the processing
    pipeline. The pipeline typically includes a tagger, a lammatizer, a parser,
    and an entity recognizer. Each pipeline component returns the processed Doc,
    which is then passed on to the next component.

    Args:
        document: Path to a txt File or text as string.
        language: Spacy langugage class. EN: en_core_web_sm, defaults to german.
        exclude: Spacy pipeline components which should not be used.

    Returns:
        A spacy Doc object containing the file.
    """
    if exclude is None:
        exclude = ["lemmatizer"]

    # Install language model from spacy if not available.
    try:
        nlp = spacy.load(language)
    except OSError:
        from spacy.cli import download  # pylint: disable=C0415
        download(language)

    # Read document type
    text = _read_doc(document)
    # Pre-Processing
    text = _pre_process(text)
    # Init spacy nlp pipeline.
    nlp = spacy.load(language, exclude=exclude)
    # Convert to doc.
    doc = nlp(text)
    return doc
