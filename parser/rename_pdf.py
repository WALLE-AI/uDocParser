import os
import sys
# sys.path.insert(
#     0,
#     os.path.abspath(
#         os.path.join(
#             os.path.dirname(
#                 os.path.abspath(__file__)),
#             '../../')))
import pdfplumber
from loguru import logger
from llm.llm import LLMApi
from llm.prompt.prompt_pdf_parser import PROMPT_RENAME_TEMPLATE, STANDARD_LABEL, FILE_PDF_JSON_FORMATH
from vision import OCR
import numpy as np
import pandas as pd
import json



def list_pdf_files_in_directory(directory_path):
    try:
        # 获取目录中的所有文件和子目录
        entries = os.listdir(directory_path)
        
        # 过滤并只保留 PDF 文件
        pdf_files = [entry for entry in entries if entry.lower().endswith('.pdf') and os.path.isfile(os.path.join(directory_path, entry))]  
        pdf_files_path = {pdf_name:directory_path + "/" + pdf_name for pdf_name in pdf_files }    
        return pdf_files_path
    except Exception as e:
        print(f"An error occurred: {e}")
        return []


class RenamePDF():

    def __init__(self,pdf_file_path) -> None:
        self.pdf = pdfplumber.open(pdf_file_path)
        self.ocr = OCR()
        self.rename_prompt = PROMPT_RENAME_TEMPLATE
        
    def is_pdf_edit(self):
        '''
            判断当前pdf文件是否可以编辑，由于直接抽取文字出现乱码和字符问题，均采用vlm和OCR的策略来抽取
        '''
        ##抽取当前文本前五页均为空，判断为无法编辑pdf文档,true无法编辑，false能够编辑
       
        text_list = [text.extract_text() for text in self.pdf.pages[0:5]]
        return all(element == "" for element in text_list)
    
    def get_page_text_ocr(self,page_num,zoomin=3):
        images = [p.to_image(resolution=72 * zoomin).annotated for i, p in
                            enumerate(self.pdf.pages[0:page_num])]
        return self.ocr_extract(images)
    
    def ocr_extract(self,images):
        ocr_text = []
        for i, img in enumerate(images):
            bxs = self.ocr(np.array(img))
            bxs = [(line[0], line[1][0]) for line in bxs]
            bxs = [{
            "text": t,
            "bbox": [b[0][0], b[0][1], b[1][0], b[-1][1]],
            "type": "ocr",
            "score": 1} for b, t in bxs if b[0][0] <= b[1][0] and b[0][1] <= b[-1][1]]
            ocr_text.append("\n".join([o["text"] for o in bxs]))
        return ocr_text
    
    def get_text(self,page_num):
        '''
        根据页面抽取对应的文本信息
        '''
        # if self.is_pdf_edit():
        logger.info(f"pdf no edit extract text information. please use ocr method")
        bxs = self.get_page_text_ocr(page_num)
        return bxs
        # else:
        #     return [text.extract_text() for text in self.pdf.pages[0:page_num]]
    @classmethod
    def rename_pdf(cls,pdf_file_path):
        '''
        pdf文件名标准化
        名称_标准号_国标/地方表_实施时间
        使用LLM来抽取出结构化信息
        '''
        cls = cls(pdf_file_path=pdf_file_path)
        text = "\n".join(page_text for page_text in cls.get_text(page_num=3))
        standard_label_str = ";".join(label for label in STANDARD_LABEL)
        file_rename_json_format = json.dumps(FILE_PDF_JSON_FORMATH,ensure_ascii=False)
        prompt_input = cls.rename_prompt.format(standard_label=standard_label_str,text=text,file_rename_json_format=file_rename_json_format)
        result_response = LLMApi.call_llm(prompt_input)
        logger.info(f"prompt input:{prompt_input}")
        return  LLMApi.llm_result_postprocess(result_response)

def test_rename_pdf():
    test_pdf = "D:/LLM/需求梳理/datasets/建筑行业施工与安全标准/2、GB50108-2008地下工程防水技术规范.pdf"
    pdf_dir = "examples/rename_pdf_test"
    local_test = "D:/LLM/project/uDocParser/rename_pdf_test/江苏省工程建设标准 DGJ32TJ60-2007.pdf"
    save_path = "examples/rename_pdf_test/test.csv"
    pdf_files_path_dict= list_pdf_files_in_directory(pdf_dir)
    save_data_list = []
    for key,values in pdf_files_path_dict.items():
        logger.info(f"pdf file name {values}")
        response_result = RenamePDF.rename_pdf(values)
        ##json格式校验
        # assert type(response_result) == dict
        if isinstance(response_result,dict):
            response_result['文件原名称'] = key
            save_data_list.append(response_result)
    save_data = pd.DataFrame(save_data_list)
    save_data.to_csv(save_path,index=False)
    
if __name__ =="__main__":
    test_rename_pdf()

            
            
            