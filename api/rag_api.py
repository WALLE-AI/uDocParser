##RAG采用管道式封装common function
from api.utils.api_utils import get_json_result, server_error_response


class RAGPiPline():
    def __init__(self):
        self.desc = "rag pipline action"

    def __str__(self):
        return self.desc

@manager.route('/query', methods=['GET'])
def factories():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)
