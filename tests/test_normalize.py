"""norm_v1 and the indicative tags."""

import unicodedata

from bdsl.text.normalize import normalize, tokens
from bdsl.text.tags import NEGATION_WORDS, QUESTION_WORDS, length_bucket, stratum


def test_nfc_makes_equal_sentences_equal():
    decomposed = "আমি বই পড়ি"                      # ড + nukta
    composed = unicodedata.normalize("NFC", decomposed)
    assert normalize(decomposed) == normalize(composed)


def test_punctuation_and_spaces():
    assert normalize("  আমি  ভাত খাই।  ") == "আমি ভাত খাই"
    assert normalize("হ্যাঁ, আমি যাব! কে?") == "হ্যাঁ আমি যাব কে"
    assert normalize("। . , ! ?") == ""


def test_spelling_digits_latin_hyphen_zwnj_kept():
    s = "e-mail ২০২৪ 2024 র‌বি"
    assert normalize(s) == unicodedata.normalize("NFC", s)


def test_idempotent_and_tokens():
    s = "তুমি কোথায় যাও ।"
    assert normalize(normalize(s)) == normalize(s)
    assert tokens(s) == ["তুমি", "কোথায়", "যাও"]
    assert tokens(" । ") == []


def test_word_lists_are_normalised():
    assert all(w == normalize(w) for w in QUESTION_WORDS | NEGATION_WORDS)


def test_stratum_priority_and_buckets():
    assert stratum(tokens("তুমি কোথায় যাও")) == "question"
    assert stratum(tokens("আমি যাব না")) == "negation"
    assert stratum(tokens("আমার ২টা বই")) == "number_time"
    assert stratum(tokens("ধন্যবাদ")) == "short"
    assert stratum(tokens("এক দুই তিন চার পাঁচ ছয় সাত")) == "long"
    assert stratum(tokens("আমি ভাত খাই")) == "other"
    assert [length_bucket(n) for n in (1, 3, 6, 9)] == ["1-2", "3-4", "5-6", "7+"]
