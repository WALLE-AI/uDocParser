
import os
from llm import ChatModel
from llm.llm import LLMApi
from llm.llm_config import MODEL_NAME_LIST
from loguru import  logger

api_key = os.environ.get("OPENROUTER_API_KEY")
base_url = "https://openrouter.ai/api/v1"
llm_name = MODEL_NAME_LIST['openrouter']["openai/gpt-4o"]
llm_name_openrouter = MODEL_NAME_LIST['openrouter']['openai/gpt-4o']


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
