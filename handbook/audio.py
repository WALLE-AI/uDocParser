import io
import re
import numpy as np

from api.service.llm_service import LLMBundle
from api.utils.setting_utils import LLMType
from llm.nlp import rag_tokenizer
from llm.nlp import tokenize


def chunk(filename, binary, tenant_id, lang, callback=None, **kwargs):
    doc = {
        "docnm_kwd": filename,
        "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename))
    }
    doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])

    # is it English
    eng = lang.lower() == "english"  # is_english(sections)
    try:
        callback(0.1, "USE Sequence2Txt LLM to transcription the audio")
        seq2txt_mdl = LLMBundle(LLMType.SPEECH2TEXT, lang=lang)
        ans = seq2txt_mdl.transcription(binary)
        callback(0.8, "Sequence2Txt LLM respond: %s ..." % ans[:32])
        tokenize(doc, ans, eng)
        return [doc]
    except Exception as e:
        callback(prog=-1, msg=str(e))

    return []