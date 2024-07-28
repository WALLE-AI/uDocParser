import loguru

from api.service.llm_service import LLMBundle


def test_llm_serivices():
    texts = ["hello world","我爱中国"]
    model = LLMBundle("chat",'perplexity/llama-3-sonar-large-32k-chat')
    response = model.chat(None, [{"role": "user", "content": "Hello! How are you doing!"}], {
                                 "temperature": 0.9})
    loguru.logger.info(f"response:{response}")