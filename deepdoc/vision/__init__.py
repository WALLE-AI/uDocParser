#  Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
#  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS,
#  WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#  See the License for the specific language governing permissions and
#  limitations under the License.
#

import threading
import httpx
import pdfplumber

from .ocr import OCR
from .recognizer import Recognizer
from .layout_recognizer import LayoutRecognizer
from .table_structure_recognizer import TableStructureRecognizer

import openai
import os

# def local_client(llm_type):
#         """
#         Gets a thread-local client, so in case openai clients are not thread safe,
#         each thread will have its own client.
#         """
#     thread_local = threading.local()
#     try:
#         return thread_local.client
#     except AttributeError:
#         if llm_type == "openrouter":
#             base_url = "https://openrouter.ai/api/v1"
#             api_key  = os.environ.get("OPENROUTER_API_KEY")
#         elif llm_type =='siliconflow':
#             base_url = "https://api.siliconflow.cn/v1"
#             api_key = os.environ.get("SILICONFLOW_API_KEY")
#         else:
#             base_url = "https://api.openai.com/v1"
#             api_key  = os.environ.get("OPENAI_API_KEY")
        
#         thread_local.client = openai.OpenAI(
#             base_url=base_url,
#             api_key=api_key,
#                 # We will set the connect timeout to be 10 seconds, and read/write
#                 # timeout to be 120 seconds, in case the inference server is
#                 # overloaded.
#             timeout=httpx.Timeout(connect=10, read=120, write=120, pool=10),
#         )
#         return thread_local.client



class RenamePDF():
    def __init__(self,pdf_file_path) -> None:
        self.pdf = pdfplumber.open(pdf_file_path)
        self.rename_prompt = '''
        你能够根据用户的提供的内容，高质量的信息抽取出结构化知识，如下为用户输入：{text}\n
        采用json格式信息抽取出 {文件名称："xxx",标准号："xxx","国标/地方标准："xxx",实施时间："xxx"} 格式的内容，如果没有相关信息，输出为""
        '''
        self.text_list = []
        
    def is_pdf_edit(self):
        '''
            判断当前pdf文件是否可以编辑
        '''
        ##抽取当前文本前五页均为空，判断为无法编辑pdf文档,true无法编辑，false能够编辑
       
        self.text_list = [text.extract_text() for text in self.pdf.pages[0:5]]
        return all(element == "" for element in self.text_list)


    def rename_pdf(self,llm_client):
        '''
        pdf文件名标准化
        名称_标准号_国标/地方表_实施时间
        使用LLM来抽取出结构化信息
        '''
        text = "\n".join(page_text for page_text in self.text_list)
        prompt_input = self.rename_prompt.format(text)
        llm_response = llm_client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt_input}],
                max_tokens=1024,
                stream=False,
                temperature=0.2,
            )
        return llm_response
    
        
        
    


def init_in_out(args):
    from PIL import Image
    import os
    import traceback
    from utils.file_utils import traversal_files
    images = []
    outputs = []
    if not os.path.exists(args.output_dir):
        os.mkdir(args.output_dir)

    def pdf_pages(fnm, zoomin=3):
        import pdb
        pdb.set_trace()
        nonlocal outputs, images
        pdf = pdfplumber.open(fnm)
        images = [p.to_image(resolution=72 * zoomin).annotated for i, p in
                            enumerate(pdf.pages)]

        for i, page in enumerate(images):
            outputs.append(os.path.split(fnm)[-1] + f"_{i}.jpg")

    def images_and_outputs(fnm):
        nonlocal outputs, images
        if fnm.split(".")[-1].lower() == "pdf":
            pdf_pages(fnm)
            return
        try:
            images.append(Image.open(fnm))
            outputs.append(os.path.split(fnm)[-1])
        except Exception as e:
            traceback.print_exc()

    if os.path.isdir(args.inputs):
        for fnm in traversal_files(args.inputs):
            images_and_outputs(fnm)
    else:
        images_and_outputs(args.inputs)

    for i in range(len(outputs)): outputs[i] = os.path.join(args.output_dir, outputs[i])

    return images, outputs