
import os
from llm import ChatModel
from llm.llm import LLMApi
from llm.llm_config import MODEL_NAME_LIST
from loguru import  logger

api_key = os.environ.get("OPENROUTER_API_KEY")
api_key_siliconflow = os.environ.get("SILICONFLOW_API_KEY")
base_url = "https://openrouter.ai/api/v1"
llm_name = MODEL_NAME_LIST['openrouter']["openai/gpt-4o"]
llm_name_openrouter = MODEL_NAME_LIST['openrouter']['openai/gpt-4o']
llm_name_siliconflow = MODEL_NAME_LIST['siliconflow']['Qwen/Qwen2-7B-Instruct']
base_url_siliconflow = "https://api.siliconflow.cn/v1"


def test_openrouter_llm():
    result = LLMApi.call_llm("你是谁",llm_type="openrouter",model_name="openai/gpt-4o")
    print(result)
    result = LLMApi.llm_result_postprocess(result)
    print(result)

def test_llm_chat():
    mdl = ChatModel['Openrouter'](api_key,
    llm_name_openrouter,base_url)
    try:
        m, tc = mdl.chat(None, [{"role": "user", "content": "Hello! How are you doing!"}], {
                                 "temperature": 0.9})
        logger.info(f"response {m}")
        if not tc:
            raise Exception(m)
    except Exception as e:
            logger.info(f"\nFail to access model({llm_name_openrouter}) using this api key.")


def test_llm_siliconflow_chat():
    mdl = ChatModel['Siliconflow'](key=api_key_siliconflow,
    model_name=llm_name_siliconflow,base_url=base_url_siliconflow)
    try:
        m, tc = mdl.chat(None, [{"role": "user", "content": "Hello! How are you doing!"}], {
                                 "temperature": 0.9})
        logger.info(f"response {m}")
        if not tc:
            raise Exception(m)
    except Exception as e:
            logger.info(f"\nFail to access model({llm_name_openrouter}) using this api key.")