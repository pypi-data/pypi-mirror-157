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
from nka._input_pipeline import preprocessor
import spacy


@pytest.fixture
def doc_string() -> str:
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
def doc_file() -> str:
    # Path to file.
    doc_txt_file = os.path.join(os.path.dirname(__file__), "input.txt")
    return doc_txt_file


def test_input_from_string(doc_string):
    doc = preprocessor(doc_string)
    assert isinstance(doc, spacy.tokens.Doc)


def test_input_from_string_list(doc_string):
    doc = preprocessor([doc_string, doc_string])
    assert isinstance(doc, spacy.tokens.Doc)


def test_input_from_txt_file(doc_file):
    doc = preprocessor(doc_file)
    assert isinstance(doc, spacy.tokens.Doc)
