
import loguru

from api.utils.setting_utils import LLMType
from llm import EmbeddingModel, RerankModel, CvModel, ChatModel


class LLMService(object):
    def __init__(self):
        pass

    @classmethod
    def get_api_key(cls, user_uuid, model_name):
        '''
        根据user_uuid和模型名称获取对应key值，这里需要查询数据认证，是否该模型权限
        '''
        pass
        # objs = cls.query(tenant_id=tenant_id, llm_name=model_name)
        # if not objs:
        #     return
        # return objs[0]

    def get_model_config(self,llm_type,llm_name=None):

        return {}

    @classmethod
    def model_instance(cls, uuid_id, llm_type,
                       llm_name=None, lang="Chinese"):

        '''
        该函数提供的模型单例服务，根据当前用户ID 现在模型类型和模型名称,在想想这块怎么写
        '''
        ##通过获取配置文件来进行集成
        model_config = cls().get_model_config(llm_type=llm_type,llm_name=llm_name)

        if llm_type == LLMType.EMBEDDING.value:
            if model_config["llm_factory"] not in EmbeddingModel:
                return
            return EmbeddingModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], base_url=model_config["api_base"])

        if llm_type == LLMType.RERANK:
            if model_config["llm_factory"] not in RerankModel:
                return
            return RerankModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], base_url=model_config["api_base"])

        if llm_type == LLMType.IMAGE2TEXT.value:
            if model_config["llm_factory"] not in CvModel:
                return
            return CvModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], lang,
                base_url=model_config["api_base"]
            )

        if llm_type == LLMType.CHAT.value:
            if model_config["llm_factory"] not in ChatModel:
                return
            return ChatModel[model_config["llm_factory"]](
                model_config["api_key"], model_config["llm_name"], base_url=model_config["api_base"])



##还需要改造这两个类
class LLMBundle(object):
    def __init__(self, user_uuid, llm_type, llm_name=None, lang="Chinese"):
        self.tenant_id = user_uuid
        self.llm_type = llm_type
        self.llm_name = llm_name
        self.mdl = LLMService.model_instance(
            user_uuid, llm_type, llm_name, lang=lang)
        assert self.mdl, "Can't find mole for {}/{}/{}".format(
            user_uuid, llm_type, llm_name)
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





