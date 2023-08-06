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
"""Implements a neural keyword assignment model using Transformer embeddings.

  Typical usage example:

  document = \""" Your document...

          \""" or

  document = "path_to_txt_file"

  # Initialize transformer model.
  model = NKA()

  # Keyword extraction.
  keywords = model.extract_keywords(document)

  # Keyword assignement.
  oot_candidates = ["List", "of", "add.", "out", "of", "text", "candidates"]
  blacklist = ["List", "of", "words", "to", "exclude"]
  keywords = model.assign_keywords(document=document,
                  oot_candidates=oot_candidates, blacklist=blacklist)
"""
from typing import List, Tuple

import spacy
import torch
import numpy as np

from sentence_transformers import util

from nka._input_pipeline import preprocessor
from nka._mmr import maximal_marginal_relevance
from nka._proposals import proposal_of_candidates
from nka.backend._utils import select_backend


class NKA:
    """Neural keyword assignement using transformers and linguistic approaches.

  NKA offers two functions: extract_keywords() and assign_keywords():
    - extract_keywords: Exclusively uses the words in the document. All
      proposed candidates and finally keywords are extracted from the
      text body. Usefull as a initial default strategy.

    - assign_keywords: Combines extracted candidates and out-of-text
      canidates, which are given by the user to enhance the performance.
      Additionally the user can specify a blacklist of words that cannot
      be proposed as candidates. Optionally, the user might want to propose
      his own canidates which are then ranked.

  Attributes:
      model: Transfomer model to be used for the embeddings.
      max_seq_length: An integer count of maximal word length to be used.
  """

    def __init__(self,
                 model: str = "paraphrase-multilingual-mpnet-base-v2",
                 max_seq_length: int = 128):
        """Neural Keyword Assignement initialization.

        Args:
            model: Transformer model.
                   The following backends are currently supported:
                        - SentenceTransformers
                        - Spacy (TODO)
                        - TF-Hub (TODO)

            max_seq_length: An integer count of maximal word length to be used.
        """
        self.model = select_backend(model)
        self.max_seq_length = max_seq_length
        self.model.model.max_seq_length = max_seq_length

    def return_doc(self,
                   document: str,
                   pos_tag: List[str] = None,
                   language: str = "de_dep_news_trf",
                   exclude: List[str] = None) -> spacy.tokens.Doc:
        """Returns the spacy.tokens.Doc class for a given document which is
        generated during the preprocessing steps.

        Args:
            document: String or path to txt file. The body of text from which
                the keywords are generated.
            pos_tag: List of POS-Tags(spacy) that candidates must fall into.
                Defaults to ["PROPN", "ADJ", "NOUN"].
            language: Spacy langugage class. EN: en_core_web_sm, defaults to
                german.
            exclude: List of spacy pipeline compononets to exclude.
                Defaults to ["lemmatizer"].

        Returns:
            A spacy Doc object containing the file.
        """
        # Use a sentinel value instead of a mutable default value as an
        # argument.
        if exclude is None:
            exclude = ["lemmatizer"]
        if pos_tag is None:
            pos_tag = ["PROPN", "ADJ", "NOUN"]
        # Step 1: Spacy and python regex input pipeline transformations.
        doc = preprocessor(document=document,
                           language=language,
                           exclude=exclude)
        return doc

    def _bucketize(self, doc: spacy.tokens.Doc) -> List[str]:
        """Returns a partioned doc as multiple buckets with smaller token size.
        The sentence transformers used define the max_seq_length of each bucket.

        Args:
            doc (spacy.tokens.doc)): _description_

        Returns:
            A list of strings.
        """
        # Splitt doc into max_seq_length chunks to use with transformers.
        buckets = []
        chunk = ""
        token_counter = 0
        for sentence in doc.sents:
            token_counter += len(sentence)
            if token_counter >= self.max_seq_length:
                buckets.append(chunk)
                token_counter = 0
                chunk = ""
            else:
                chunk += str(sentence)
        if len(chunk) != 0:
            buckets.append(chunk)

        return buckets

    def _embedding_phase(
            self, buckets: List[str],
            candidates: List[str]) -> Tuple[torch.Tensor, torch.Tensor]:
        """Returns the numeric embedding of the document and potential
        candidates done by the sentence transformer.

        Args:
            buckets (List[str]): List of strings containing the doc as buckets.
            candidates (List[str]): List of strings containing the candidates.

        Returns:
            A Tuple containing the document and candidate embeddings.
        """
        # Document embedding.
        doc_embedding = self.model.embed(buckets)

        # Candidates embedding.
        candidate_embeddings = self.model.embed(candidates)

        # Convert to PyTorch Tensor for cos sim function.
        doc_embedding = torch.from_numpy(doc_embedding)
        candidate_embeddings = torch.from_numpy(candidate_embeddings)

        return doc_embedding, candidate_embeddings

    def _diversify(self, cosine_scores, candidate_embeddings, candidates, top_n,
                   diversity):
        if len(candidates) > top_n:
            # Similarity between candidates is needed for mmr.
            candidates_sim = util.cos_sim(candidate_embeddings,
                                          candidate_embeddings).numpy()

            keywords = maximal_marginal_relevance(
                candidates_doc_sim=cosine_scores,
                candidates_sim=candidates_sim,
                candidates=candidates,
                top_n=top_n,
                diversity=diversity)
        else:
            keywords = [(candidates[index],
                         round(float(cosine_scores[0][index]), 4))
                        for index in cosine_scores.argsort()[0][-top_n:]][::-1]

        return keywords

    def extract_keywords(self,
                         document: str,
                         pos_tag: List[str] = None,
                         top_n: int = 7,
                         diversity: float = 0.4,
                         language: str = "de_dep_news_trf",
                         exclude: List[str] = None) -> List[Tuple[str, float]]:
        """Extracts keywords from document.

        Retrives keywords only from the text body using POS-Tags for candidate
        proposial and cosine-similarity for embedded ranking. Maximal Marginal
        Relevance is used if and only if the number of proposed candidates is
        larger than top_n.

        Args:
            document: String or path to txt file. The body of text from which
                the keywords are generated.
            pos_tag: List of POS-Tags(spacy) that candidates must fall into.
                Defaults to ["PROPN", "ADJ", "NOUN"].
            top_n: Max number of proposed keywords.
            diversity: How diverse the select keywords are. Values between 0 and
                1 with 0 being not diverse at all and 1 being most diverse.
            language: Spacy langugage class. EN: en_core_web_sm, defaults to
                german.
            exclude: List of spacy pipeline compononets to exclude.
                Defaults to ["lemmatizer"].

        Returns:
            Top_n keywords with their cosine similarities. List can be smaller,
            if the number of proposed candidates is smaller than top_n.
        """
        # Use a sentinel value instead of a mutable default value as an
        # argument.
        if exclude is None:
            exclude = ["lemmatizer"]
        if pos_tag is None:
            pos_tag = ["PROPN", "ADJ", "NOUN"]
        # Step 1: Spacy and python regex input pipeline transformations.
        doc = preprocessor(document=document,
                           language=language,
                           exclude=exclude)

        # Step 2: Proposal of candidates.
        candidates = proposal_of_candidates(doc=doc, pos_tag=pos_tag)

        if not candidates:
            # List of candidates is empty.
            return []

        # Step 3: Bucketize
        buckets = self._bucketize(doc)

        # Step 4: Ranking with transformer embeddings and cosine similarity.
        # Document embedding.
        doc_embedding, candidate_embeddings = self._embedding_phase(
            buckets, candidates)

        # Step 5: Maximum similarity: compute cosine-similarities for each
        # sentence with each other sentence.
        cosine_scores = util.cos_sim(doc_embedding, candidate_embeddings)
        if len(buckets) > 1:
            # Compute max similarities for each candidate with every bucket.
            cosine_scores = np.amax(cosine_scores.numpy(), axis=0)

        # Step 6: Diversify using mmr if and only if number of
        # candidates > top_n.
        keywords = self._diversify(cosine_scores, candidate_embeddings,
                                   candidates, top_n, diversity)

        return keywords

    def assign_keywords(self,
                        document: str,
                        oot_candidates: List[str] = None,
                        blacklist: List[str] = None,
                        candidates: List[str] = None,
                        pos_tag: List[str] = None,
                        top_n: int = 7,
                        diversity: float = 0.4,
                        language: str = "de_dep_news_trf",
                        exclude: List[str] = None) -> List[Tuple[str, float]]:
        """Assign keywords to a document.

        Retrives keywords from the text body using POS-Tags for candidate
        proposial in addition to out-of-text candidates given by the user
        and cosine-similarity for embedded ranking. Maximal Marginal
        Relevance is used if and only if the number of proposed candidates is
        larger than top_n.

        Args:
            document: String or path to txt file. The body of text from which
                the keywords are generated.
            oot_candidates: List of candidates that should be considered.
            blacklist: List of words, that cannot be proposed as candidates.
            candidates: If set, only these candidates are used as proposals.
            pos_tag: List of POS-Tags(spacy) that candidates must fall into.
                Defaults to ["PROPN", "ADJ", "NOUN"].
            top_n: Max number of proposed keywords.
            diversity: How diverse the select keywords are. Values between 0 and
                1 with 0 being not diverse at all and 1 being most diverse.
            language: Spacy langugage class. EN: en_core_web_sm, defaults to
                german.
            exclude: List of spacy pipeline compononets to exclude.
                Defaults to: ["lemmatizer"]

        Returns:
            Top_n keywords with their cosine similarities. List can be smaller,
            if the number of proposed candidates is smaller than top_n.
        """
        # Use a sentinel value instead of a mutable default value as an
        # argument.
        if exclude is None:
            exclude = ["lemmatizer"]
        if pos_tag is None:
            pos_tag = ["PROPN", "ADJ", "NOUN"]

        # Step 1: Spacy and python regex input pipeline transformations.
        doc = preprocessor(document=document,
                           language=language,
                           exclude=exclude)

        # Step 2: Proposal of candidates.
        if candidates is None:
            # Extract candidates from text.
            candidates = proposal_of_candidates(doc=doc, pos_tag=pos_tag)

        if oot_candidates is not None:
            # If oot_candidates is given, append it to canidates list.
            candidates = candidates + oot_candidates

        if blacklist is not None:
            # Remove canidates in blacklist from proposed candidates.
            cleaned_candidates = [
                candidate for candidate in candidates
                if candidate not in blacklist
            ]
            candidates = cleaned_candidates

        if not candidates:
            # List of candidates is empty.
            return []

        ## Step 3: Bucketize
        buckets = self._bucketize(doc)

        # Step 4: Ranking with transformer embeddings and cosine similarity.
        # Document embedding.
        doc_embedding, candidate_embeddings = self._embedding_phase(
            buckets, candidates)

        # Step 5: Maximum similarity: ompute cosine-similarities for each
        # sentence with each other sentence.
        cosine_scores = util.cos_sim(doc_embedding, candidate_embeddings)
        if len(buckets) > 1:
            # Compute max similarities for each candidate with every bucket.
            cosine_scores = np.amax(cosine_scores.numpy(), axis=0)

        # Step 6 Diversify using mmr if and only if number of
        # candidates > top_n.
        keywords = self._diversify(cosine_scores, candidate_embeddings,
                                   candidates, top_n, diversity)

        return keywords
