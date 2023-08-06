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
"""This module implements MMR as a way to diversify chosen candidates. """
from typing import List, Tuple

import numpy as np


def maximal_marginal_relevance(
        candidates_doc_sim: np.ndarray,
        candidates_sim: np.ndarray,
        candidates: List[str],
        top_n: int = 7,
        diversity: float = 0.4) -> List[Tuple[str, float]]:
    """Calculate Maximal Marginal Relevance (MMR) between candidate keywords
    and the document.

    MMR considers the similarity of keywords/keyphrases with the
    document, along with the similarity of already selected
    keywords and keyphrases. This results in a selection of keywords
    that maximize their within diversity with respect to the document.

    Args:
        candidates_doc_sim: Cosine scores between the doc and the candidates.
        candidates_sim: Cosine scores within the candidates itself.
        candidates: The selected candidates.
        top_n: The number of keywords to return.
        diversity: How diverse the select keywords/keyphrases are.
                   Values between 0 and 1 with 0 being not diverse at all
                   and 1 being most diverse.

    Returns:
        List[Tuple[str, float]]: Keywords with their doc similarities.
    """

    # Get index for best candidate which is the first keyword.
    keywords_idx = [np.argmax(candidates_doc_sim)]
    # Initialize candidates List and exclude best index.
    candidates_idx = [i for i in range(len(candidates)) if i != keywords_idx[0]]

    for _ in range(top_n - 1):
        # Extract similarities within candidates and
        # between candidates and selected keywords/phrases
        candidate_similarities = candidates_doc_sim[candidates_idx]
        candidate_similarities = candidate_similarities.reshape(-1, 1)
        # Similarities between candidates and best candidate.
        target_similarities = np.max(
            candidates_sim[candidates_idx][:, keywords_idx],
            axis=1)  # (num_candidates - 1)

        # Calculate MMR
        mmr = (
            1 - diversity
        ) * candidate_similarities - diversity * target_similarities.reshape(
            -1, 1)
        mmr_idx = candidates_idx[np.argmax(mmr)]

        # Update keywords & candidates
        keywords_idx.append(mmr_idx)
        candidates_idx.remove(mmr_idx)

    # Format top_n keywords for return.
    keywords = [(candidates[idx],
                 round(float(candidates_doc_sim.reshape(1, -1)[0][idx]), 4))
                for idx in keywords_idx]
    return keywords
