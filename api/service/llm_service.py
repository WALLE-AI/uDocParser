import json
import os

import loguru

from api.utils.setting_utils import LLMType
from conf.database_config import llm_client_key_url_info
from llm import EmbeddingModel, RerankModel, CvModel, ChatModel
from utils.file_utils import get_project_base_directory


class LLMService(object):
    def __init__(self):
        pass

    @classmethod
    def get_api_key(cls, user_uuid, model_name):
        '''
        根据user_uuid和模型名称获取对应key值，这里需要查询数据认证，是否该模型权限
        '''
        pass

    def get_model_config(self,llm_type,llm_name):
        result_dict = {
            "llm_factory":"BAAI",
            "api_key":"xxx",
            "llm_name":llm_name,
            "api_base":"xxxx",
            "model_type":"xxxx"
        }
        factory_llm_infos = json.load(
            open(
                os.path.join(get_project_base_directory(), "uDocParser"+"\\conf", "llm_factories.json"),
                "r",
            )
        )
        model_list = factory_llm_infos['llm_factory']
        for llm_type_dict in model_list:
            for llm_dict in llm_type_dict.get('llm'):
                if llm_name == llm_dict.get("llm_name"):
                    result_dict['llm_factory']=llm_type_dict.get("name")
                    key_url = [key_url for key_url in  llm_client_key_url_info if llm_type_dict.get("name") in key_url]
                    if key_url:
                        result_dict["api_key"] = key_url[0]['api_key']
                        result_dict['api_base'] = key_url[0]['base_url']
                    result_dict['model_type'] = llm_dict.get("model_type")
                    result_dict['llm_name'] = llm_dict.get("llm_name")
        return result_dict

    @classmethod
    def model_instance(cls, llm_type,
                       llm_name=None, lang="Chinese"):

        '''
        该函数提供的模型单例服务，根据当前用户ID 现在模型类型和模型名称,在想想这块怎么写
        '''
        ##通过获取配置文件来进行集成
        model_config = cls().get_model_config(llm_type,llm_name)

        if llm_type == LLMType.EMBEDDING.value:
            return EmbeddingModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], base_url=model_config["api_base"])

        if llm_type == LLMType.RERANK:
            return RerankModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], base_url=model_config["api_base"])

        if llm_type == LLMType.IMAGE2TEXT.value:
            return CvModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], lang,
                base_url=model_config["api_base"]
            )

        if llm_type == LLMType.CHAT.value:
            return ChatModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], base_url=model_config["api_base"])



##还需要改造这两个类
class LLMBundle(object):
    def __init__(self,llm_type, llm_name=None, lang="Chinese"):
        self.llm_type = llm_type
        self.llm_name = llm_name
        self.mdl = LLMService.model_instance(llm_type, llm_name, lang=lang)
        assert self.mdl, "Can't find mole for {}/{}/{}".format(llm_type, llm_name)
        self.max_length = 512

    def encode(self, texts: list, batch_size=32):
        emd, used_tokens = self.mdl.encode(texts, batch_size)
        return emd, used_tokens

    def encode_queries(self, query: str):
        emd, used_tokens = self.mdl.encode_queries(query)
        return emd, used_tokens

    def similarity(self, query: str, texts: list):
        sim, used_tokens = self.mdl.similarity(query, texts)
        return sim, used_tokens

    def describe(self, image, max_tokens=300):
        txt, used_tokens = self.mdl.describe(image, max_tokens)
        return txt,used_tokens

    def chat(self, system, history, gen_conf):
        txt, used_tokens = self.mdl.chat(system, history, gen_conf)
        return txt,used_tokens

    def chat_streamly(self, system, history, gen_conf):
        for txt in self.mdl.chat_streamly(system, history, gen_conf):
            yield txt





