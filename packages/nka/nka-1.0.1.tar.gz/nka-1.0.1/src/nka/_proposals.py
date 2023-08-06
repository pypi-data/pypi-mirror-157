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
"""This module implements the linguistic characteristics for neural keyword
assignment. TODO In Future we include words out of Doc to generalize from
keyword extraction to keyword assignement.
"""
from typing import List
import spacy


def proposal_of_candidates(doc: spacy.tokens.Doc,
                           pos_tag: List[str] = None) -> List[str]:
    """Proposal of candidates using linguistic characteristics.

    The proposal of candidates is a list containing single words like:
    - proper noun
    - adjectives
    - noun

    These POS-Characeristics can be controlled using pos_tag. Furthermore, we
    extract adjective + noun combinations from the given Doc.

    Args:
        doc: A spacy Doc object.
        pos_tag: spacy pos_tags to extract as single_word_length canidates.


    Returns:
        A List containing candidates for keyword assignement.
    """
    if pos_tag is None:
        # Only use POS-Tags: proper noun, adjective and noun as canidates.
        pos_tag = ["PROPN", "ADJ", "NOUN"]

    single_candidates = []
    for token in doc:
        # Check if Stopword and POS, single candidate
        if not token.is_stop and token.pos_ in pos_tag:
            single_candidates.append(token.text)
    # Remove duplicates.
    single_candidates = list(set(single_candidates))

    if "ADJ" in pos_tag:
        multiple_candidates = []
        for chunk in doc.noun_chunks:
            adj = []
            noun = ""
            for tok in chunk:
                if tok.pos_ == "NOUN":
                    noun = tok.text
                if tok.pos_ == "ADJ":
                    adj.append(tok.text)
            if noun:
                if adj:
                    for i in adj:
                        multiple_candidates.append(i + " " + noun)
        # Remove duplicates.
        multiple_candidates = list(set(multiple_candidates))
        return single_candidates + multiple_candidates
    else:
        return single_candidates
