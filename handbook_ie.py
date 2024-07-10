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

class ChunkTextData(BaseModel):
    '''
    main table information
    {
      chunk_ID:语义块的ID
      chunk_method: 分块策略,字符分块，递归分块、语义分块
      text:块文本信息
      bbox：[xxxx]，目标检测框的坐标信息，便于定位与高亮  
      chunk_bbox:List=[] 当前chunk 高亮部分
      file_name:文件名
      file_path_url:文档存储的服务位置地址，使用pdf.js即可打开
      position_standard:当前文件属于地方标准还是国家标准，["国家标准","省","市"],可以根据工地所在区域进行，搜索过滤
      page_num:所在的页码,存在跨页面的情况
      images：文本块关联的图片信息
      text_embedding_id:文本向量ID  --对应向量数据库
      similarity_question:[question1,question2,xxxx]--根据块生成最相似的问题，并且当前块存在该问题的答案信息
      simi_question_embedding_id:相似问题向量ID --对应向量数据库
    }
    '''
    chunk_id: int=11232323432
    chunk_method: dict={"default":"character","recursive":"recursive"}
    text: str='''我是中国人'''
    bbox:List=[801.0, 38.0, 1026.0, 55.0]
    chunk_bbox:List=[]
    file_name:str="广东省市政基础设施工程竣工验收技术资料统一用表（2019版）"
    file_path_url:str="http:10.5.12.45/pdf/广东省市政基础设施工程竣工验收技术资料统一用表（2019版）.pdf"
    position_standard:List[str]=["广东省"]
    page_num:List[int]=[3]
    images:List[str]=['01.png']
    text_embedding_id:int=153545325436
    similarity_question:List[str]=["我爱中国"]
    simi_question_embedding_id:int=26246374732747
    
    
class FileData(BaseModel):
    '''
    File Data Obeject
    {
      file_id:文件名的md5数据
      file_name:文件名
      file_path_url:文档存储的服务位置地址，使用pdf.js即可打开
      position_standard:当前文件属于地方标准还是国家标准，["国家标准","省","市"],可以根据工地所在区域进行，搜索过滤
      total_page_num:总页码数
      stadard_label:属于建筑那个大类，比如防水工程、建筑电气
    }
    '''
    file_id:int
    file_name:str="广东省市政基础设施工程竣工验收技术资料统一用表（2019版）"
    file_path_url:str="http:10.5.12.45/pdf/广东省市政基础设施工程竣工验收技术资料统一用表（2019版）.pdf"
    position_standard:List[str]=["广东省"]
    total_page_num:int
    
  
class FileDataInforation(BaseModel):
    '''
    File Data Information
    {
        file_name:"厂矿道路设计规范"
        standard_num: GB50108—2008
        standard_position_label:"国家标准"
        effective_date: "2009年4月1日"
        discard_data:"GB50108—2001"
    }
    '''
    file_name:str = "厂矿道路设计规范"
    standard_num: str = "GB50108—2008"
    standard_position_label: str = "国家标准"
    effective_date: str = "2009年4月1日"
    discard_standard_num: str = "GB50108—2001"
    
    
    
    


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
        
        