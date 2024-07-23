from api.utils.api_utils import get_json_result, server_error_response


@manager.route('/info', methods=['GET'])
def docparser_info():
    '''
    获取现有rag服务中所有LLM vllm embedding reranker 信息
    '''
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)

@manager.route('/doc', methods=['POST'])
def docparser_doc():
    '''
    支持多种非结构文档解析
    '''
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)

@manager.route('/bulk_doc', methods=['POST'])
def docparser_bulk_doc():
    '''
    批量解析
    '''
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/doc_id', methods=['POST'])
def docparser_get_doc():
    '''
    根据文件名称或者doc_id,获取文档名称、chunk数等文件属性信息
    '''
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)

@manager.route('/doc_chunk_id', methods=['POST'])
def docparser_get_chunk_doc():
    '''
    根据chunk_id,获取文档名称、chunk数等文件属性信息
    '''
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)

