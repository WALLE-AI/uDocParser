import loguru

from llm import RerankModel


def  test_rerank_model():
    texts = ["你是谁","我是谁","我爱中国"]
    query="中国属于亚洲"
    model = RerankModel['BAAI'](key = "key",model_name = "BAAI/bge-reranker-v2-m3")
    score,tokens = model.similarity(query,texts)
    loguru.logger.info(f"score {score}")
    loguru.logger.info(f"tokens {tokens}")