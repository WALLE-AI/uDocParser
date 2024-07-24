import loguru
from tika import parser
import re
from io import BytesIO

from api.utils import get_uuid
from llm import bullets_category, is_english, remove_contents_table, \
    hierarchical_merge, make_colon_as_title, naive_merge, random_choices, tokenize_table, tokenize_chunks, find_codec
from llm.nlp import rag_tokenizer
from parser import PdfParser, DocxParser, PlainParser, HtmlParser
from parser.excel_parser import RAGFlowExcelParser
from utils.file_utils import FileType


class Pdf(PdfParser):
    def __call__(self, filename, binary=None, from_page=0,
                 to_page=100000, zoomin=3, callback=None):
        callback(msg="OCR is running...")
        self.__images__(
            filename if not binary else binary,
            zoomin,
            from_page,
            to_page,
            callback)
        callback(msg="OCR finished")

        from timeit import default_timer as timer
        start = timer()
        self._layouts_rec(zoomin)
        callback(0.67, "Layout analysis finished")
        print("layouts:", timer() - start)
        self._table_transformer_job(zoomin)
        callback(0.68, "Table analysis finished")
        self._text_merge()
        tbls = self._extract_table_figure(True, zoomin, True, True)
        self._naive_vertical_merge()
        self._filter_forpages()
        self._merge_with_same_bullet()
        callback(0.75, "Text merging finished.")

        callback(0.8, "Text extraction finished")

        return [(b["text"] + self._line_tag(b, zoomin), b.get("layoutno", ""))
                for b in self.boxes], tbls


def chunk(filename, binary=None, from_page=0, to_page=100000,
          lang="Chinese", callback=None, **kwargs):
    """
        Supported file formats are docx, pdf, txt.
        Since a book is long and not all the parts are useful, if it's a PDF,
        please setup the page ranges for every book in order eliminate negative effects and save elapsed computing time.
    """
    doc = {
        "docnm_kwd": filename,
        "title_tks": rag_tokenizer.tokenize(re.sub(r"\.[a-zA-Z]+$", "", filename))
    }
    doc["title_sm_tks"] = rag_tokenizer.fine_grained_tokenize(doc["title_tks"])
    pdf_parser = None
    sections, tbls = [], []
    if re.search(r"\.docx$", filename, re.IGNORECASE):
        callback(0.1, "Start to parse.")
        doc_parser = DocxParser()
        # TODO: table of contents need to be removed
        sections, tbls = doc_parser(
            binary if binary else filename, from_page=from_page, to_page=to_page)
        remove_contents_table(sections, eng=is_english(
            random_choices([t for t, _ in sections], k=200)))
        tbls = [((None, lns), None) for lns in tbls]
        callback(0.8, "Finish parsing.")

    elif re.search(r"\.pdf$", filename, re.IGNORECASE):
        pdf_parser = Pdf() if kwargs.get(
            "parser_config", {}).get(
            "layout_recognize", True) else PlainParser()
        sections, tbls = pdf_parser(filename if not binary else binary,
                                    from_page=from_page, to_page=to_page, callback=callback)

    elif re.search(r"\.txt$", filename, re.IGNORECASE):
        callback(0.1, "Start to parse.")
        txt = ""
        if binary:
            encoding = find_codec(binary)
            txt = binary.decode(encoding, errors="ignore")
        else:
            with open(filename, "r") as f:
                while True:
                    l = f.readline()
                    if not l:
                        break
                    txt += l
        sections = txt.split("\n")
        sections = [(l, "") for l in sections if l]
        remove_contents_table(sections, eng=is_english(
            random_choices([t for t, _ in sections], k=200)))
        callback(0.8, "Finish parsing.")

    elif re.search(r"\.(htm|html)$", filename, re.IGNORECASE):
        callback(0.1, "Start to parse.")
        sections = HtmlParser()(filename, binary)
        sections = [(l, "") for l in sections if l]
        remove_contents_table(sections, eng=is_english(
            random_choices([t for t, _ in sections], k=200)))
        callback(0.8, "Finish parsing.")

    elif re.search(r"\.doc$", filename, re.IGNORECASE):
        callback(0.1, "Start to parse.")
        binary = BytesIO(binary)
        doc_parsed = parser.from_buffer(binary)
        sections = doc_parsed['content'].split('\n')
        sections = [(l, "") for l in sections if l]
        remove_contents_table(sections, eng=is_english(
            random_choices([t for t, _ in sections], k=200)))
        callback(0.8, "Finish parsing.")

    else:
        raise NotImplementedError(
            "file type not supported yet(doc, docx, pdf, txt supported)")

    make_colon_as_title(sections)
    bull = bullets_category(
        [t for t in random_choices([t for t, _ in sections], k=100)])
    if bull >= 0:
        chunks = ["\n".join(ck)
                  for ck in hierarchical_merge(bull, sections, 5)]
    else:
        sections = [s.split("@") for s, _ in sections]
        sections = [(pr[0], "@" + pr[1]) if len(pr) == 2 else (pr[0], '') for pr in sections ]
        chunks = naive_merge(
            sections, kwargs.get(
                "chunk_token_num", 256), kwargs.get(
                "delimer", "\n。；！？"))

    # is it English
    # is_english(random_choices([t for t, _ in sections], k=218))
    #TODO:需要chunk关联对应表格和图片
    eng = lang.lower() == "english"

    res = tokenize_table(tbls, doc, eng)
    res.extend(tokenize_chunks(chunks, doc, eng, pdf_parser))

    return res

def read_pdf_files(pdf_path):
    '''
    读取文件夹中所有pdf文件或者pdf文件
    '''
    import os
    import re
    pdf_files_dict = {}
    pattern = re.compile(r'.*\.pdf$', re.IGNORECASE)  # 匹配以.pdf结尾的文件名
    if os.path.isfile(pdf_path):
        # 如果是PDF文件，直接添加到词典中 TODO 如何直接判断出相对路径和绝对路径
        file_name = pdf_path.split('\\')[-1].split(".pdf")
        pdf_files_dict[file_name[0]] = pdf_path
    elif os.path.isdir(pdf_path):
        for root, dirs, files in os.walk(pdf_path):
            for file in files:
                if pattern.match(file):
                    file_name = file.split('.pdf')
                    full_path = os.path.join(root, file)
                    pdf_files_dict[file_name[0]] = full_path

    return pdf_files_dict

def handbook_parser(pdf_path):
    def dummy(prog=None, msg=""):
        pass
    pdf_files_dict = read_pdf_files(pdf_path)
    for pdf_name,pdf_path in pdf_files_dict.items():
        loguru.logger.info(f"pdf file name {pdf_name},pdf path {pdf_path}")
        res = chunk(pdf_path,from_page=1, to_page=5, callback=dummy)
        for text in res:
            loguru.logger.info(f"pdf_file_name:{pdf_name},parser result text {text['content_with_weight']}")


def queue_tasks(doc, bucket, name):
    def new_task():
        nonlocal doc
        return {
            "id": get_uuid(),
            "doc_id": doc["id"]
        }
    tsks = []

    if doc["type"] == FileType.PDF.value:
        file_bin = "MINIO.get(bucket, name)从阿里云oss服务段来"
        do_layout = doc["parser_config"].get("layout_recognize", True)
        pages = PdfParser.total_page_number(doc["name"], file_bin)
        page_size = doc["parser_config"].get("task_page_size", 12)
        if doc["parser_id"] == "paper":
            page_size = doc["parser_config"].get("task_page_size", 22)
        if doc["parser_id"] == "one":
            page_size = 1000000000
        if not do_layout:
            page_size = 1000000000
        page_ranges = doc["parser_config"].get("pages")
        if not page_ranges:
            page_ranges = [(1, 100000)]
        for s, e in page_ranges:
            s -= 1
            s = max(0, s)
            e = min(e - 1, pages)
            for p in range(s, e, page_size):
                task = new_task()
                task["from_page"] = p
                task["to_page"] = min(p + page_size, e)
                tsks.append(task)

    elif doc["parser_id"] == "table":
        file_bin = "MINIO.get(bucket, name)"
        rn = RAGFlowExcelParser.row_number(
            doc["name"], file_bin)
        for i in range(0, rn, 3000):
            task = new_task()
            task["from_page"] = i
            task["to_page"] = min(i + 3000, rn)
            tsks.append(task)
    else:
        tsks.append(new_task())

    bulk_insert_into_db(Task, tsks, True)
    DocumentService.begin2parse(doc["id"])


