import copy
import datetime
import hashlib
import json
import os
import re
import sys
from functools import partial
from io import BytesIO

import loguru
import numpy as np
import pdfplumber
from elasticsearch_dsl import Q

from api.service.llm_service import LLMBundle
from api.utils.setting_utils import LLMType
from api.utils.settings import retrievaler
from database.database_es_ragflow_connector import ELASTICSEARCH
from db import ParserType
from handbook import naive, paper, presentation, manual, laws, qa, table, picture, one, book, audio
from llm.nlp import rag_tokenizer,search
from utils import rmSpace, num_tokens_from_string
from utils.file_utils import get_project_base_directory
from utils.settings import DOC_MAXIMUM_SIZE, cron_logger
from timeit import default_timer as timer
from llm.nlp.raptor import RecursiveAbstractiveProcessing4TreeOrganizedRetrieval as Raptor
BATCH_SIZE = 64

FACTORY = {
    "general": naive,
    ParserType.NAIVE.value: naive,
    ParserType.PAPER.value: paper,
    ParserType.BOOK.value: book,
    ParserType.PRESENTATION.value: presentation,
    ParserType.MANUAL.value: manual,
    ParserType.LAWS.value: laws,
    ParserType.QA.value: qa,
    ParserType.TABLE.value: table,
    ParserType.PICTURE.value: picture,
    ParserType.ONE.value: one,
    ParserType.AUDIO.value: audio
}

def set_progress(task_id, from_page=0, to_page=-1,
                 prog=None, msg="Processing..."):
    if prog is not None and prog < 0:
        msg = "[ERROR]" + msg
    cancel = False
    if cancel:
        msg += " [Canceled]"
        prog = -1

    if to_page > 0:
        if msg:
            msg = f"Page({from_page + 1}~{to_page + 1}): " + msg
    d = {"progress_msg": msg}
    if prog is not None:
        d["progress"] = prog
    try:
        "TaskService.update_progress(task_id, d)"
    except Exception as e:
        cron_logger.error("set_progress:({}), {}".format(task_id, str(e)))

    "close_connection()"
    if cancel:
        sys.exit()


def build(row):
    if row["size"] > DOC_MAXIMUM_SIZE:
        set_progress(row["id"], prog=-1, msg="File size exceeds( <= %dMb )" %
                                             (int(DOC_MAXIMUM_SIZE / 1024 / 1024)))
        return []

    callback = partial(
        set_progress,
        row["id"],
        row["from_page"],
        row["to_page"])
    def dummy(prog=None, msg=""):
        pass
    chunker = FACTORY[row["parser_id"].lower()]
    try:
        st = timer()
        ##可以从oss服务获取
        # bucket, name = "File2DocumentService.get_minio_address(doc_id=row[""doc_id""])"
        # binary = "get_minio_binary(bucket, name)"
        # loguru.logger.info(
        #     "From minio({}) {}/{}".format(timer() - st, row["location"], row["name"]))
        cks = chunker.chunk(row['file_full_path'], from_page=row["from_page"],
                            to_page=row["to_page"], lang=row["language"], callback=dummy)
        loguru.logger.info(
            "Chunkking({}) {}".format(timer() - st, row["file_name"]))
    except TimeoutError as e:
        callback(-1, f"Internal server error: Fetch file timeout. Could you try it again.")
        loguru.logger.error(
            "Chunkking({}) {}".format(timer() - st, row["file_name"]))
        return
    except Exception as e:
        if re.search("(No such file|not found)", str(e)):
            callback(-1, "Can not find file <%s>" % row["file_name"])
        else:
            callback(-1, f"Internal server error: %s" %
                     str(e).replace("'", ""))
        # traceback.print_exc()

        loguru.logger.error(
            "Chunkking {}: {}".format( row["file_name"], str(e)))

        return

    docs = []
    doc = {
        "doc_id": row["id"]
    }
    el = 0
    for ck in cks:
        d = copy.deepcopy(doc)
        d.update(ck)
        md5 = hashlib.md5()
        md5.update((ck["content_with_weight"] +
                    str(d["doc_id"])).encode("utf-8"))
        d["_id"] = md5.hexdigest()
        d["create_time"] = str(datetime.datetime.now()).replace("T", " ")[:19]
        d["create_timestamp_flt"] = datetime.datetime.now().timestamp()
        if not d.get("image"):
            docs.append(d)
            continue

        output_buffer = BytesIO()
        if isinstance(d["image"], bytes):
            output_buffer = BytesIO(d["image"])
        else:
            d["image"].save(output_buffer, format='JPEG')

        st = timer()
        # MINIO.put(row["kb_id"], d["_id"], output_buffer.getvalue())
        el += timer() - st
        d["img_id"] = "{}".format(d["_id"])
        del d["image"]
        docs.append(d)
    loguru.logger.info("MINIO PUT({}):{}".format(row["file_name"], el))

    return docs


def init_kb(row):
    idxnm = search.index_name(row["id"])
    if ELASTICSEARCH.indexExist(idxnm):
        return
    return ELASTICSEARCH.createIdx(idxnm, json.load(
        open(os.path.join(get_project_base_directory(), "uDocParser\\conf", "mapping.json"), "r")))


def embedding(docs, mdl, parser_config={}, callback=None):
    batch_size = 32
    tts, cnts = [rmSpace(d["title_tks"]) for d in docs if d.get("title_tks")], [
        re.sub(r"</?(table|td|caption|tr|th)( [^<>]{0,12})?>", " ", d["content_with_weight"]) for d in docs]
    tk_count = 0
    if len(tts) == len(cnts):
        tts_ = np.array([])
        for i in range(0, len(tts), batch_size):
            vts, c = mdl.encode(tts[i: i + batch_size])
            if len(tts_) == 0:
                tts_ = vts
            else:
                tts_ = np.concatenate((tts_, vts), axis=0)
            tk_count += c
            # callback(prog=0.6 + 0.1 * (i + 1) / len(tts), msg="")
        tts = tts_

    cnts_ = np.array([])
    for i in range(0, len(cnts), batch_size):
        vts, c = mdl.encode(cnts[i: i + batch_size])
        if len(cnts_) == 0:
            cnts_ = vts
        else:
            cnts_ = np.concatenate((cnts_, vts), axis=0)
        tk_count += c
        # callback(prog=0.7 + 0.2 * (i + 1) / len(cnts), msg="")
    cnts = cnts_
    ##文件名称在chunk中权重
    title_w = float(parser_config.get("filename_embd_weight", 0.1))

    vects = (title_w * tts + (1 - title_w) *
             cnts) if len(tts) == len(cnts) else cnts

    assert len(vects) == len(docs)
    for i, d in enumerate(docs):
        v = vects[i].tolist()
        d["q_%d_vec" % len(v)] = v
    return tk_count


def get_pdf_info_with_pdfplumber(pdf_path):
    # 打开PDF文件
    with pdfplumber.open(pdf_path) as pdf:
        # 获取页面总数
        num_pages = len(pdf.pages)

        # 获取文件大小（字节）
        file_size = os.path.getsize(pdf_path)

    return num_pages, file_size


def run_raptor(row, chat_mdl, embd_mdl, callback=None):
    vts, _ = embd_mdl.encode(["ok"])
    vctr_nm = "q_%d_vec"%len(vts[0])
    chunks = []
    for d in retrievaler.chunk_list(row["doc_id"], row["tenant_id"], fields=["content_with_weight", vctr_nm]):
        chunks.append((d["content_with_weight"], np.array(d[vctr_nm])))

    raptor = Raptor(
        row["parser_config"]["raptor"].get("max_cluster", 64),
        chat_mdl,
        embd_mdl,
        row["parser_config"]["raptor"]["prompt"],
        row["parser_config"]["raptor"]["max_token"],
        row["parser_config"]["raptor"]["threshold"]
    )
    original_length = len(chunks)
    raptor(chunks, row["parser_config"]["raptor"]["random_seed"], callback)
    doc = {
        "doc_id": row["doc_id"],
        "kb_id": [str(row["kb_id"])],
        "docnm_kwd": row["name"],
        "title_tks": rag_tokenizer.tokenize(row["name"])
    }
    res = []
    tk_count = 0
    for content, vctr in chunks[original_length:]:
        d = copy.deepcopy(doc)
        md5 = hashlib.md5()
        md5.update((content + str(d["doc_id"])).encode("utf-8"))
        d["_id"] = md5.hexdigest()
        d["create_time"] = str(datetime.datetime.now()).replace("T", " ")[:19]
        d["create_timestamp_flt"] = datetime.datetime.now().timestamp()
        d[vctr_nm] = vctr.tolist()
        d["content_with_weight"] = content
        d["content_ltks"] = rag_tokenizer.tokenize(content)
        d["content_sm_ltks"] = rag_tokenizer.fine_grained_tokenize(d["content_ltks"])
        res.append(d)
        tk_count += num_tokens_from_string(content)
    return res, tk_count


def file_generator_md5(text):
    md5 = hashlib.md5()
    md5.update((text).encode("utf-8"))
    return md5.hexdigest()

def read_pdf_files(pdf_path):
    '''
    读取文件夹中所有pdf文件或者pdf文件
    '''
    import os
    import re

    pattern = re.compile(r'.*\.pdf$', re.IGNORECASE)  # 匹配以.pdf结尾的文件名
    file_info_list = []
    if os.path.isfile(pdf_path):
        pdf_files_dict = {}
        # 如果是PDF文件，直接添加到词典中 TODO 如何直接判断出相对路径和绝对路径
        file_name = pdf_path.split('\\')[-1].split(".pdf")
        pdf_files_dict['file_name'] = file_name[0]
        pdf_files_dict["file_full_path"] = pdf_path
        num_pages, file_size = get_pdf_info_with_pdfplumber(pdf_path)
        file_md5 = file_generator_md5(file_name[0])
        pdf_files_dict['id'] = file_md5
        pdf_files_dict["from_page"] = 1
        pdf_files_dict["to_page"] = 5
        pdf_files_dict['total_page'] = num_pages
        pdf_files_dict["size"] = file_size
        pdf_files_dict['llm_id'] = "perplexity/llama-3-sonar-large-32k-chat"
        pdf_files_dict["embd_id"] = "BAAI/bge-large-zh-v1.5"
        pdf_files_dict["language"] = "Chinese"
        pdf_files_dict['parser_id'] = "book"
        pdf_files_dict['parser_config'] = {"filename_embd_weight":0.1}
        file_info_list.append(pdf_files_dict)
    elif os.path.isdir(pdf_path):
        for root, dirs, files in os.walk(pdf_path):
            for file in files:
                pdf_files_dict = {}
                if pattern.match(file):
                    file_name = file.split('.pdf')
                    full_path = os.path.join(root, file)
                    pdf_files_dict['file_name'] = file_name[0]
                    pdf_files_dict["file_full_path"] = full_path
                    num_pages, file_size = get_pdf_info_with_pdfplumber(pdf_path)
                    pdf_files_dict['total_page'] = num_pages
                    pdf_files_dict["size"] = file_size
                    file_md5 =file_generator_md5(file_name[0])
                    pdf_files_dict['id'] = file_md5
                    pdf_files_dict["from_page"] = 1
                    pdf_files_dict["to_page"] = 5
                    pdf_files_dict['llm_id'] = "perplexity/llama-3-sonar-large-32k-chat"
                    pdf_files_dict["embd_id"] = "BAAI/bge-large-zh-v1.5"
                    pdf_files_dict["language"] = "Chinese"
                    pdf_files_dict['parser_id'] = "book"
                    pdf_files_dict['parser_config'] = {"filename_embd_weight": 0.1}
                    file_info_list.append(pdf_files_dict)
    return file_info_list


def document_parser(file_path_or_dir):
    file_info_list = read_pdf_files(file_path_or_dir)
    if len(file_info_list) == 0:
        return

    for r in file_info_list:
        callback = partial(set_progress, r["id"], r["from_page"], r["to_page"])
        try:
            embd_mdl = LLMBundle(LLMType.EMBEDDING, llm_name=r["embd_id"], lang=r["language"])
        except Exception as e:
            callback(-1, msg=str(e))
            cron_logger.error(str(e))
            continue

        if r.get("task_type", "") == "raptor":
            try:
                chat_mdl = LLMBundle(LLMType.CHAT, llm_name=r["llm_id"], lang=r["language"])
                cks, tk_count = run_raptor(r, chat_mdl, embd_mdl, callback)
            except Exception as e:
                callback(-1, msg=str(e))
                cron_logger.error(str(e))
                continue
        else:
            st = timer()
            cks = build(r)
            loguru.logger.info("Build chunks({}): {}".format(r["file_name"], timer() - st))
            if cks is None:
                continue
            if not cks:
                callback(1., "No chunk! Done!")
                continue
            # TODO: exception handler
            ## set_progress(r["did"], -1, "ERROR: ")
            callback(
                msg="Finished slicing files(%d). Start to embedding the content." %
                    len(cks))
            st = timer()
            try:
                tk_count = embedding(cks, embd_mdl, parser_config=r['parser_config'],callback=callback)
            except Exception as e:
                callback(-1, "Embedding error:{}".format(str(e)))
                cron_logger.error(str(e))
                tk_count = 0
            cron_logger.info("Embedding elapsed({}): {:.2f}".format(r["file_name"], timer() - st))
            callback(msg="Finished embedding({:.2f})! Start to build index!".format(timer() - st))

        init_kb(r)
        chunk_count = len(set([c["_id"] for c in cks]))
        st = timer()
        es_r = ""
        es_bulk_size = 16
        for b in range(0, len(cks), es_bulk_size):
            es_r = ELASTICSEARCH.bulk(cks[b:b + es_bulk_size], search.index_name(r["id"]))
            if b % 128 == 0:
                callback(prog=0.8 + 0.1 * (b + 1) / len(cks), msg="")

        cron_logger.info("Indexing elapsed({}): {:.2f}".format(r["file_name"], timer() - st))
        if es_r:
            callback(-1, "Index failure!")
            ELASTICSEARCH.deleteByQuery(
                Q("match", doc_id=r["doc_id"]), idxnm=search.index_name(r["id"]))
            cron_logger.error(str(es_r))
        else:
            # if TaskService.do_cancel(r["id"]):
            #     ELASTICSEARCH.deleteByQuery(
            #         Q("match", doc_id=r["doc_id"]), idxnm=search.index_name(r["tenant_id"]))
            #     continue
            callback(1., "Done!")
            # DocumentService.increment_chunk_num(
            #     r["doc_id"], r["kb_id"], tk_count, chunk_count, 0)
            cron_logger.info(
                "Chunk doc({}), token({}), chunks({}), elapsed:{:.2f}".format(
                    r["id"], tk_count, len(cks), timer() - st))