'''
测试文本解析的工具
  - deepdoc工具--ocr技术进行信息抽取，但是无法恢复语义段落信息
  - unstructured---支持多种非结构的数据格式，可分离出对应的图片数据--OCR采用tenssrect-OCR技术、layoutparser分析工具
  - 360layoutAnalysis--针对于研报、论文信息抽取较好
  - PP-StructureV2
  
目标：
  - 获取文件中图文语义信息，chunk与图片信息对齐才行
  main table information
  {
      chunk_ID:语义块的ID
      chunk_method: 分块策略
      text:块文本信息
      bbox：[xxxx,xxxx],块中文本所在文件中坐标信息，便于定位与高亮
      file_name:文件名
      images：文本块关联的图片信息
      text_embedding_id:文本向量ID  --对应向量数据库
      similarity_question:[question1,question2,xxxx]--根据块生成最相似的问题，并且当前块存在该问题的答案信息
      simi_question_embedding_id:相似问题向量ID --对应向量数据库
  }
'''

from typing import Any, List
from loguru import logger
from unstructured.partition.pdf import partition_pdf


from abc import ABC, abstractmethod

from pydantic import BaseModel

class HandbookBase(ABC):
    def __init__(self) -> None:
        super().__init__()
    
    @abstractmethod   
    def get_text(self):
        '''
        获取抽取的所有文本
        '''
    @abstractmethod 
    def get_page_text(self):
        '''
        获取单页文本
        '''
    @abstractmethod 
    def get_all_files_infomation(self,files_dir):
        '''
        获取文件夹下面所有文件信息 名称、页码信息
        '''
    @abstractmethod  
    def get_page_images(self):
        '''
        获取当前页面中所有图片
        '''
            

class Deepdoc(HandbookBase):
    def __init__(self) -> None:
        super().__init__()
        self.files_list = []
        
class UnstructredAI(HandbookBase):
    def __init__(self) -> None:
        super().__init__()
        
    def get_text(self):
        return "获取抽取的所有文本"
    
    def get_page_text(self):
        return "获取单元文本"
    
    def get_all_files_infomation(self,files_dir):
        return "获取文件夹下面所有文件信息 名称、页码信息"
    
    def get_page_images(self):
        return "获取当前页面中所有图片"
    
        
class LayoutAnalysis360(HandbookBase):
    def __init__(self) -> None:
        super().__init__()
        
        
class PPStructureV2(HandbookBase):
    def __init__(self) -> None:
        super().__init__()
        
        
        
if __name__ == "__main__":
    logger.info("测试")
        
        