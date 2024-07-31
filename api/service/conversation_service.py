import os
import json
import re
from copy import deepcopy

import loguru

from api.service.llm_service import LLMService, LLMBundle
from api.utils.setting_utils import LLMType
from api.utils.settings import chat_logger, retrievaler
from handbook.resume import forbidden_select_fields4resume
from llm.nlp import keyword_extraction
from llm.nlp.search import index_name
from utils import rmSpace, num_tokens_from_string, encoder
from utils.file_utils import get_project_base_directory


def message_fit_in(msg, max_length=4000):
    def count():
        nonlocal msg
        tks_cnts = []
        for m in msg:
            tks_cnts.append(
                {"role": m["role"], "count": num_tokens_from_string(m["content"])})
        total = 0
        for m in tks_cnts:
            total += m["count"]
        return total

    c = count()
    if c < max_length:
        return c, msg

    msg_ = [m for m in msg[:-1] if m["role"] == "system"]
    msg_.append(msg[-1])
    msg = msg_
    c = count()
    if c < max_length:
        return c, msg

    ll = num_tokens_from_string(msg_[0]["content"])
    l = num_tokens_from_string(msg_[-1]["content"])
    if ll / (ll + l) > 0.8:
        m = msg_[0]["content"]
        m = encoder.decode(encoder.encode(m)[:max_length - l])
        msg[0]["content"] = m
        return max_length, msg

    m = msg_[1]["content"]
    m = encoder.decode(encoder.encode(m)[:max_length - l])
    msg[1]["content"] = m
    return max_length, msg


def llm_id2llm_type(llm_id):
    fnm = os.path.join(get_project_base_directory(), "uDocParser\\conf")
    llm_factories = json.load(open(os.path.join(fnm, "llm_factories.json"), "r"))
    for llm_factory in llm_factories["llm_factory"]:
        for llm in llm_factory["llm"]:
            if llm_id == llm["llm_name"]:
                return llm["model_type"].strip(",")[-1]


class DialogConfig():
    def __init__(self):
        self.rerank_id = "BAAI/bge-reranker-v2-m3"
        self.llm_id = "perplexity/llama-3-sonar-large-32k-chat"
        self.emb_id = "BAAI/bge-large-zh-v1.5"
        self.tenant_id=""
        self.kb_ids = ""
        self.similarity_threshold = ""
        self.vector_similarity_weight=0.3
        self.self_rag = True
        self.prompt_config =  {
        "system": """你是一个智能助手，请总结知识库的内容来回答问题，请列举知识库中的数据详细回答。当所有知识库内容都与问题无关时，你的回答必须包括“知识库中未找到您要的答案！”这句话。回答需要考虑聊天历史。
以下是知识库：
{knowledge}
以上是知识库。""",
        "prologue": "您好，我是您的助手小樱，长得可爱又善良，can I help you?",
        "parameters": [
            {"key": "knowledge", "optional": False}
        ],
        "empty_response": "Sorry! 知识库中未找到相关内容！"
    }
        self.llm_setting = {


        }

def chat(dialog, messages, stream=False, **kwargs):
    assert messages[-1]["role"] == "user", "The last content of this conversation is not from user."
    # llm = LLMService.query(llm_name=dialog.llm_id)
    # if not llm:
    #     llm = TenantLLMService.query(tenant_id=dialog.tenant_id, llm_name=dialog.llm_id)
    #     if not llm:
    #         raise LookupError("LLM(%s) not found" % dialog.llm_id)
    max_tokens = 8192
    # else:
    #     max_tokens = llm[0].max_tokens
    # kbs = KnowledgebaseService.get_by_ids(dialog.kb_ids)
    # embd_nms = list(set([kb.embd_id for kb in kbs]))
    # if len(embd_nms) != 1:
    #     yield {"answer": "**ERROR**: Knowledge bases use different embedding models.", "reference": []}
    #     return {"answer": "**ERROR**: Knowledge bases use different embedding models.", "reference": []}

    questions = [m["content"] for m in messages if m["role"] == "user"]
    embd_mdl = LLMBundle(LLMType.EMBEDDING, dialog.emb_id)
    ##这里判断是否有图片输入 TODO:这个地方可以做双向支持
    # if llm_id2llm_type(dialog.llm_id) == "image2text":
    #     chat_mdl = LLMBundle(LLMType.IMAGE2TEXT, dialog.llm_id)
    # else:
    chat_mdl = LLMBundle(LLMType.CHAT, dialog.llm_id)

    prompt_config = dialog.prompt_config
    # field_map = KnowledgebaseService.get_field_map(dialog.kb_ids)
    # try to use sql if field mapping is good to go
    # if field_map:
    #     chat_logger.info("Use SQL to retrieval:{}".format(questions[-1]))
    #     ans = use_sql(questions[-1], field_map, dialog.tenant_id, chat_mdl, prompt_config.get("quote", True))
    #     if ans:
    #         yield ans
    #         return

    # for p in prompt_config["parameters"]:
    #     if p["key"] == "knowledge":
    #         continue
    #     if p["key"] not in kwargs and not p["optional"]:
    #         raise KeyError("Miss parameter: " + p["key"])
    #     if p["key"] not in kwargs:
    #         prompt_config["system"] = prompt_config["system"].replace(
    #             "{%s}" % p["key"], " ")
    #
    # rerank_mdl = None
    # if dialog.rerank_id:
    #     rerank_mdl = LLMBundle(LLMType.RERANK, dialog.rerank_id)

    for _ in range(len(questions) // 2):
        questions.append(questions[-1])
    if "knowledge" not in [p["key"] for p in prompt_config["parameters"]]:
        kbinfos = {"total": 0, "chunks": [], "doc_aggs": []}
    # else:
    #     if prompt_config.get("keyword", False):
    questions[-1] += keyword_extraction(chat_mdl, questions[-1])
    kbinfos = retrievaler.retrieval(" ".join(questions), embd_mdl, dialog.tenant_id, dialog.kb_ids, 1,5,aggs=False, rerank_mdl=None)
    knowledges = [ck["content_with_weight"] for ck in kbinfos["chunks"]]
    # self-rag
    if dialog.prompt_config.get("self_rag") and not relevant(dialog.tenant_id, dialog.llm_id, questions[-1],
                                                             knowledges):
        ##question改写
        questions[-1] = rewrite(dialog.tenant_id, dialog.llm_id, questions[-1])
        kbinfos = retrievaler.retrieval(" ".join(questions), embd_mdl, dialog.tenant_id, dialog.kb_ids, 1,
                                        5,aggs=False, rerank_mdl=None)
        knowledges = [ck["content_with_weight"] for ck in kbinfos["chunks"]]

    chat_logger.info(
        "{}->{}".format(" ".join(questions), "\n->".join(knowledges)))

    if not knowledges and prompt_config.get("empty_response"):
        yield {"answer": prompt_config["empty_response"], "reference": kbinfos}
        return {"answer": prompt_config["empty_response"], "reference": kbinfos}

    kwargs["knowledge"] = "\n".join(knowledges)
    gen_conf = dialog.llm_setting

    msg = [{"role": "system", "content": prompt_config["system"].format(**kwargs)}]
    msg.extend([{"role": m["role"], "content": m["content"]}
                for m in messages if m["role"] != "system"])
    used_token_count, msg = message_fit_in(msg, int(max_tokens * 0.97))
    assert len(msg) >= 2, f"message_fit_in has bug: {msg}"

    if "max_tokens" in gen_conf:
        gen_conf["max_tokens"] = min(
            gen_conf["max_tokens"],
            max_tokens - used_token_count)

    def decorate_answer(answer):
        nonlocal prompt_config, knowledges, kwargs, kbinfos
        refs = []
        if knowledges and (prompt_config.get("quote", True) and kwargs.get("quote", True)):
            answer, idx = retrievaler.insert_citations(answer,
                                                       [ck["content_ltks"]
                                                        for ck in kbinfos["chunks"]],
                                                       [ck["vector"]
                                                        for ck in kbinfos["chunks"]],
                                                       embd_mdl,
                                                       tkweight=1 - dialog.vector_similarity_weight,
                                                       vtweight=dialog.vector_similarity_weight)
            idx = set([kbinfos["chunks"][int(i)]["doc_id"] for i in idx])
            recall_docs = [
                d for d in kbinfos["doc_aggs"] if d["doc_id"] in idx]
            if not recall_docs: recall_docs = kbinfos["doc_aggs"]
            kbinfos["doc_aggs"] = recall_docs

            refs = deepcopy(kbinfos)
            for c in refs["chunks"]:
                if c.get("vector"):
                    del c["vector"]

        if answer.lower().find("invalid key") >= 0 or answer.lower().find("invalid api") >= 0:
            answer += " Please set LLM API-Key in 'User Setting -> Model Providers -> API-Key'"
        return {"answer": answer, "reference": refs}

    if stream:
        answer = ""
        for ans in chat_mdl.chat_streamly(msg[0]["content"], msg[1:], gen_conf):
            answer = ans
            yield {"answer": answer, "reference": {}}
        yield decorate_answer(answer)
    else:
        answer = chat_mdl.chat(
            msg[0]["content"], msg[1:], gen_conf)
        chat_logger.info("User: {}|Assistant: {}".format(
            msg[-1]["content"], answer))
        yield decorate_answer(answer)


def use_sql(question, field_map, tenant_id, chat_mdl, quota=True):
    sys_prompt = "你是一个DBA。你需要这对以下表的字段结构，根据用户的问题列表，写出最后一个问题对应的SQL。"
    user_promt = """
表名：{}；
数据库表字段说明如下：
{}

问题如下：
{}
请写出SQL, 且只要SQL，不要有其他说明及文字。
""".format(
        index_name(tenant_id),
        "\n".join([f"{k}: {v}" for k, v in field_map.items()]),
        question
    )
    tried_times = 0

    def get_table():
        nonlocal sys_prompt, user_promt, question, tried_times
        sql = chat_mdl.chat(sys_prompt, [{"role": "user", "content": user_promt}], {
            "temperature": 0.06})
        print(user_promt, sql)
        chat_logger.info(f"“{question}”==>{user_promt} get SQL: {sql}")
        sql = re.sub(r"[\r\n]+", " ", sql.lower())
        sql = re.sub(r".*select ", "select ", sql.lower())
        sql = re.sub(r" +", " ", sql)
        sql = re.sub(r"([;；]|```).*", "", sql)
        if sql[:len("select ")] != "select ":
            return None, None
        if not re.search(r"((sum|avg|max|min)\(|group by )", sql.lower()):
            if sql[:len("select *")] != "select *":
                sql = "select doc_id,docnm_kwd," + sql[6:]
            else:
                flds = []
                for k in field_map.keys():
                    if k in forbidden_select_fields4resume:
                        continue
                    if len(flds) > 11:
                        break
                    flds.append(k)
                sql = "select doc_id,docnm_kwd," + ",".join(flds) + sql[8:]

        print(f"“{question}” get SQL(refined): {sql}")

        chat_logger.info(f"“{question}” get SQL(refined): {sql}")
        tried_times += 1
        return retrievaler.sql_retrieval(sql, format="json"), sql

    tbl, sql = get_table()
    if tbl is None:
        return None
    if tbl.get("error") and tried_times <= 2:
        user_promt = """
        表名：{}；
        数据库表字段说明如下：
        {}

        问题如下：
        {}

        你上一次给出的错误SQL如下：
        {}

        后台报错如下：
        {}

        请纠正SQL中的错误再写一遍，且只要SQL，不要有其他说明及文字。
        """.format(
            index_name(tenant_id),
            "\n".join([f"{k}: {v}" for k, v in field_map.items()]),
            question, sql, tbl["error"]
        )
        tbl, sql = get_table()
        chat_logger.info("TRY it again: {}".format(sql))

    chat_logger.info("GET table: {}".format(tbl))
    print(tbl)
    if tbl.get("error") or len(tbl["rows"]) == 0:
        return None

    docid_idx = set([ii for ii, c in enumerate(
        tbl["columns"]) if c["name"] == "doc_id"])
    docnm_idx = set([ii for ii, c in enumerate(
        tbl["columns"]) if c["name"] == "docnm_kwd"])
    clmn_idx = [ii for ii in range(
        len(tbl["columns"])) if ii not in (docid_idx | docnm_idx)]

    # compose markdown table
    clmns = "|" + "|".join([re.sub(r"(/.*|（[^（）]+）)", "", field_map.get(tbl["columns"][i]["name"],
                                                                        tbl["columns"][i]["name"])) for i in
                            clmn_idx]) + ("|Source|" if docid_idx and docid_idx else "|")

    line = "|" + "|".join(["------" for _ in range(len(clmn_idx))]) + \
           ("|------|" if docid_idx and docid_idx else "")

    rows = ["|" +
            "|".join([rmSpace(str(r[i])) for i in clmn_idx]).replace("None", " ") +
            "|" for r in tbl["rows"]]
    if quota:
        rows = "\n".join([r + f" ##{ii}$$ |" for ii, r in enumerate(rows)])
    else:
        rows = "\n".join([r + f" ##{ii}$$ |" for ii, r in enumerate(rows)])
    rows = re.sub(r"T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+Z)?\|", "|", rows)

    if not docid_idx or not docnm_idx:
        chat_logger.warning("SQL missing field: " + sql)
        return {
            "answer": "\n".join([clmns, line, rows]),
            "reference": {"chunks": [], "doc_aggs": []}
        }

    docid_idx = list(docid_idx)[0]
    docnm_idx = list(docnm_idx)[0]
    doc_aggs = {}
    for r in tbl["rows"]:
        if r[docid_idx] not in doc_aggs:
            doc_aggs[r[docid_idx]] = {"doc_name": r[docnm_idx], "count": 0}
        doc_aggs[r[docid_idx]]["count"] += 1
    return {
        "answer": "\n".join([clmns, line, rows]),
        "reference": {"chunks": [{"doc_id": r[docid_idx], "docnm_kwd": r[docnm_idx]} for r in tbl["rows"]],
                      "doc_aggs": [{"doc_id": did, "doc_name": d["doc_name"], "count": d["count"]} for did, d in
                                   doc_aggs.items()]}
    }


def relevant(tenant_id, llm_id, question, contents: list):
    # if llm_id2llm_type(llm_id) == "image2text":
    #     chat_mdl = LLMBundle(tenant_id, LLMType.IMAGE2TEXT, llm_id)
    # else:
    chat_mdl = LLMBundle(LLMType.CHAT, "perplexity/llama-3-sonar-large-32k-chat")
    prompt = """
        You are a grader assessing relevance of a retrieved document to a user question. 
        It does not need to be a stringent test. The goal is to filter out erroneous retrievals.
        If the document contains keyword(s) or semantic meaning related to the user question, grade it as relevant. 
        Give a binary score 'yes' or 'no' score to indicate whether the document is relevant to the question.
        No other words needed except 'yes' or 'no'.
    """
    if not contents: return False
    contents = "Documents: \n" + "   - ".join(contents)
    contents = f"Question: {question}\n" + contents
    if num_tokens_from_string(contents) >= chat_mdl.max_length - 4:
        contents = encoder.decode(encoder.encode(contents)[:chat_mdl.max_length - 4])
    ans = chat_mdl.chat(prompt, [{"role": "user", "content": contents}], {"temperature": 0.01})
    if "yes" in ans: return True
    return False


def rewrite(tenant_id, llm_id, question):
    # if llm_id2llm_type(llm_id) == "image2text":
    #     chat_mdl = LLMBundle(tenant_id, LLMType.IMAGE2TEXT, llm_id)
    # else:
    chat_mdl = LLMBundle(LLMType.CHAT, "perplexity/llama-3-sonar-large-32k-chat")
    prompt = """
        You are an expert at query expansion to generate a paraphrasing of a question.
        I can't retrieval relevant information from the knowledge base by using user's question directly.     
        You need to expand or paraphrase user's question by multiple ways such as using synonyms words/phrase, 
        writing the abbreviation in its entirety, adding some extra descriptions or explanations, 
        changing the way of expression, translating the original question into another language (English/Chinese), etc. 
        And return 5 versions of question and one is from translation.
        Just list the question. No other words are needed.
    """
    ans = chat_mdl.chat(prompt, [{"role": "user", "content": question}], {"temperature": 0.8})
    return ans



def test_chat():
    dialog_config = DialogConfig()
    question = "工程建设标准全文信息系统"
    message_info = [{"role":"user","content":question}]
    response_generator = chat(dialog_config,message_info)
    for text in response_generator:
        loguru.logger.info(f"response :{text}")
