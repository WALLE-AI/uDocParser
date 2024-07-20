import loguru

from llm import RerankModel


def  test_embedding_model():
    texts = ["你是谁","我是谁","我爱中国"]
    model = RerankModel['BAAI'](key = "key",model_name = "BAAI/bge-large-zh-v1.5")
    vec,tokens = model.encode(texts=texts)
    loguru.logger.info(f"tokens {tokens}")
    query_vec = model.encode_queries(texts[0])
    loguru.logger.info(f"query embedding {len(query_vec[0])}")