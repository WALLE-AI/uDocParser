from api.service.llm_service import LLMBundle


def test_llm_serivices():
    texts = ["hello world","我爱中国"]
    model = LLMBundle("embedding")
    em_text = model.encode(texts)
    print(em_text)
