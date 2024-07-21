
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

    @classmethod
    def model_instance(cls, uuid_id, llm_type,
                       llm_name=None, lang="Chinese"):


        '''

        该函数提供的模型单例服务，根据当前用户ID 现在模型类型和模型名称

        '''

        if llm_type == LLMType.EMBEDDING.value:
            mdlnm = uuid_id.embd_id if not llm_name else llm_name
        elif llm_type == LLMType.SPEECH2TEXT.value:
            mdlnm = uuid_id.asr_id
        elif llm_type == LLMType.IMAGE2TEXT.value:
            mdlnm = uuid_id.img2txt_id if not llm_name else llm_name
        elif llm_type == LLMType.CHAT.value:
            mdlnm = uuid_id.llm_id if not llm_name else llm_name
        elif llm_type == LLMType.RERANK:
            mdlnm = uuid_id.rerank_id if not llm_name else llm_name
        else:
            assert False, "LLM type error"

        model_config = cls.get_api_key(uuid_id, mdlnm)
        if model_config: model_config = model_config.to_dict()
        if not model_config:
            if llm_type in [LLMType.EMBEDDING, LLMType.RERANK]:
                llm = LLMService.query(llm_name=llm_name if llm_name else mdlnm)
                if llm and llm[0].fid in ["Youdao", "FastEmbed", "BAAI"]:
                    model_config = {"llm_factory": llm[0].fid, "api_key": "",
                                    "llm_name": llm_name if llm_name else mdlnm, "api_base": ""}
            if not model_config:
                if llm_name == "flag-embedding":
                    model_config = {"llm_factory": "Tongyi-Qianwen", "api_key": "",
                                    "llm_name": llm_name, "api_base": ""}
                else:
                    if not mdlnm:
                        raise LookupError(f"Type of {llm_type} model is not set.")
                    raise LookupError("Model({}) not authorized".format(mdlnm))

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
    def __init__(self, tenant_id, llm_type, llm_name=None, lang="Chinese"):
        self.tenant_id = tenant_id
        self.llm_type = llm_type
        self.llm_name = llm_name
        self.mdl = LLMService.model_instance(
            tenant_id, llm_type, llm_name, lang=lang)
        assert self.mdl, "Can't find mole for {}/{}/{}".format(
            tenant_id, llm_type, llm_name)
        self.max_length = 512
        for lm in LLMService.query(llm_name=llm_name):
            self.max_length = lm.max_tokens
            break

    def encode(self, texts: list, batch_size=32):
        emd, used_tokens = self.mdl.encode(texts, batch_size)
        if not LLMService.increase_usage(
                self.tenant_id, self.llm_type, used_tokens):
            loguru.logger.error(
                "Can't update token usage for {}/EMBEDDING".format(self.tenant_id))
        return emd, used_tokens

    def encode_queries(self, query: str):
        emd, used_tokens = self.mdl.encode_queries(query)
        if not LLMService.increase_usage(
                self.tenant_id, self.llm_type, used_tokens):
            loguru.logger.error(
                "Can't update token usage for {}/EMBEDDING".format(self.tenant_id))
        return emd, used_tokens

    def similarity(self, query: str, texts: list):
        sim, used_tokens = self.mdl.similarity(query, texts)
        if not LLMService.increase_usage(
                self.tenant_id, self.llm_type, used_tokens):
            loguru.logger.error(
                "Can't update token usage for {}/RERANK".format(self.tenant_id))
        return sim, used_tokens

    def describe(self, image, max_tokens=300):
        txt, used_tokens = self.mdl.describe(image, max_tokens)
        if not LLMService.increase_usage(
                self.tenant_id, self.llm_type, used_tokens):
            loguru.logger.error(
                "Can't update token usage for {}/IMAGE2TEXT".format(self.tenant_id))
        return txt

    def chat(self, system, history, gen_conf):
        txt, used_tokens = self.mdl.chat(system, history, gen_conf)
        if not LLMService.increase_usage(
                self.tenant_id, self.llm_type, used_tokens, self.llm_name):
            loguru.logger.error(
                "Can't update token usage for {}/CHAT".format(self.tenant_id))
        return txt

    def chat_streamly(self, system, history, gen_conf):
        for txt in self.mdl.chat_streamly(system, history, gen_conf):
            if isinstance(txt, int):
                if not LLMService.increase_usage(
                        self.tenant_id, self.llm_type, txt, self.llm_name):
                    loguru.logger.error(
                        "Can't update token usage for {}/CHAT".format(self.tenant_id))
                return
            yield txt





