from api.utils.api_utils import get_json_result, server_error_response
from test.test_cv_llm import test_cv_llm


@manager.route('/info', methods=['GET'])
def chat_info():
    '''
    获取现有rag服务中所有LLM vllm embedding reranker 信息
    '''
    try:
        return get_json_result(data={"test":"我是starVLM"})
    except Exception as e:
        return server_error_response(e)
    

@manager.route('/cv_completion', methods=['GET'])
def chat_cv_completion():
    '''
    图片识图chat能力
    '''
    response,use_tokens = test_cv_llm()
    try:
        return get_json_result(data={"llm_repsonse":response,"use_tokens":use_tokens})
    except Exception as e:
        return server_error_response(e)


@manager.route('/completion', methods=['POST'])
def chat_completion():
    '''
    获取现有rag服务中所有LLM vllm embedding reranker 信息
    '''
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)