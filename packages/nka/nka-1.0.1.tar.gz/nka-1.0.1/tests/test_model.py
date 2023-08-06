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
import os
import pytest
from nka import NKA
from nka.backend._sentencetransformers import SentenceTransformerBackend
from sentence_transformers import SentenceTransformer


@pytest.fixture
def doc_string_large() -> str:
    # String.
    doc_string = """Ludwig II. Otto Friedrich Wilhelm, König von Bayern
    (* 25. August 1845 auf Schloss Nymphenburg, Nymphenburg, heute München;
    13. Juni 1886 im Würmsee, heute Starnberger See, bei Schloss Berg),
    aus dem Haus Wittelsbach stammend, war vom 10. März 1864 bis zu seinem
    Tod König von Bayern. Nach seiner Entmündigung am 9. Juni 1886 übernahm
    sein Onkel Luitpold als Prinzregent die Regierungsgeschäfte im
    Königreich Bayern, da Ludwigs jüngerer Bruder Otto wegen einer
    Geisteskrankheit regierungsunfähig war. Ludwig II. hat sich in der
    Geschichte Bayerns als leidenschaftlicher Schlossbauherr, vor allem der
    Schlösser Neuschwanstein, Herrenchiemsee und Linderhof, ein Denkmal
    gesetzt; er wird auch als Märchenkönig bezeichnet. Mit seinem Namen
    untrennbar verbunden ist auch die großzügige Förderung Richard Wagners.
    Während Ludwigs Regentschaft verlor Bayern den Deutschen Krieg und
    vollzog 1870/71 den Eintritt in das Deutsche Reich."""
    return doc_string


@pytest.fixture
def doc_string_small() -> str:
    # String.
    doc_string = """The unittest unit testing framework was originally
        inspired by JUnit and has a similar flavor as major unit testing
        frameworks in other languages. It supports test automation, sharing of
        setup and shutdown code for tests, aggregation of tests into
        collections, and independence of the tests from the reporting framework.
        """
    return doc_string


@pytest.fixture
def doc_file() -> str:
    # Path to file.
    doc_txt_file = os.path.join(os.path.dirname(__file__), "input.txt")
    return doc_txt_file


def test_backup_sentence_transformers():
    # Default settings.
    model = NKA()
    assert model.model.model.max_seq_length == 128
    assert isinstance(model.model, SentenceTransformerBackend)

    model = NKA(max_seq_length=256)
    assert model.model.model.max_seq_length == 256
    assert isinstance(model.model, SentenceTransformerBackend)

    # Method 1
    model = NKA(model="paraphrase-MiniLM-L6-v2")
    assert model.model.model.max_seq_length == 128
    assert isinstance(model.model, SentenceTransformerBackend)

    # Method 2
    sentence_model = SentenceTransformerBackend(
        "paraphrase-multilingual-mpnet-base-v2")
    model = NKA(model=sentence_model)
    assert model.model.model.max_seq_length == 128
    assert isinstance(model.model, SentenceTransformerBackend)

    # Method 3
    embedding_model = SentenceTransformer(
        "paraphrase-multilingual-mpnet-base-v2")
    sentence_model = SentenceTransformerBackend(embedding_model)
    model = NKA(model=sentence_model)
    assert model.model.model.max_seq_length == 128
    assert isinstance(model.model, SentenceTransformerBackend)

    # Test wrong string for sentence transformer TODO
    #model = NKA(model="i-do-not-exist")
    #self.assertRaises(ValueError)


def test_extract_keywords(doc_file):
    model = NKA()
    keywords = model.extract_keywords(doc_file, language="de_dep_news_trf")
    # Test deafult top_n
    assert len(keywords) == 7


def test_assign_keywords(doc_file):
    model = NKA()
    keywords = model.assign_keywords(doc_file, language="de_dep_news_trf")
    # Test deafult top_n
    assert len(keywords) == 7

    # Test oot_candidates.
    assert (model.assign_keywords("hi du",
                                  oot_candidates=["Hi"],
                                  language="de_dep_news_trf")[0][0] == "Hi")
    assert (len(
        model.assign_keywords("hi du",
                              oot_candidates=["Hi", "du"],
                              language="de_dep_news_trf")) == 2)
    assert (len(
        model.assign_keywords("Apple",
                              oot_candidates=["Hi", "du"],
                              language="de_dep_news_trf")) == 3)

    # Test blacklist.
    assert (len(
        model.assign_keywords("hi du",
                              oot_candidates=["Hi", "du"],
                              blacklist=["Hi"],
                              language="de_dep_news_trf")) == 1)

    # Test candidates.
    assert (len(
        model.assign_keywords("Apple",
                              candidates=["Hi", "du"],
                              language="de_dep_news_trf")) == 2)


def test_special_docs():
    model = NKA()
    # Extract keywords.
    # Empty document.
    assert ([] == model.extract_keywords("", language="de_dep_news_trf"))
    # Document conaining no pos_tags / candidates.
    assert ([] == model.extract_keywords("hi du.", language="de_dep_news_trf"))
    # Short but valid document.
    assert (model.extract_keywords("Apple", language="de_dep_news_trf")
            is not None)
    assert (model.extract_keywords(["Apple", "is", "fine"],
                                   language="de_dep_news_trf") is not None)

    # Assign keywords.
    # Empty document.
    assert ([] == model.assign_keywords("", language="de_dep_news_trf"))
    # Document conaining no pos_tags / candidates.
    assert ([] == model.assign_keywords("hi du.", language="de_dep_news_trf"))
    # Short but valid document.
    assert (model.assign_keywords("Apple", language="de_dep_news_trf")
            is not None)
    assert (model.assign_keywords(["Apple", "is", "fine"],
                                  language="de_dep_news_trf") is not None)
