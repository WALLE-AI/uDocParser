##RAG采用管道式封装common function
from api.utils.api_utils import get_json_result, server_error_response


@manager.route('/info', methods=['GET'])
def rag_info():
    '''
    获取现有rag服务中所有LLM vllm embedding reranker 信息
    '''
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/embedding', methods=['POST'])
def rag_embedding():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/reranker', methods=['POST'])
def rag_reranker():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/llm', methods=['POST'])
def rag_llm():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/vlm', methods=['POST'])
def rag_vlm():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)



@manager.route('/llm_chat', methods=['POST'])
def rag_llm_chat():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/vlm_chat', methods=['POST'])
def rag_vlm_chat():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


