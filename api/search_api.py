##使用fastapi来封装，整个RAG采用管道式封装
from api.utils.api_utils import get_json_result, server_error_response


@manager.route('/query', methods=['GET'])
def factories():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)
    