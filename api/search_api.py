from api.utils.api_utils import get_json_result, server_error_response


@manager.route('/info', methods=['GET'])
def get_search_info():
    try:
        return get_json_result(data={"test": "hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/general_query', methods=['POST'])
def ai_general_search():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/libary_query', methods=['POST'])
def ai_libary_search():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/hybrid_query', methods=['POST'])
def ai_hybrid_search():
    try:
        return get_json_result(data={"test":"hello world"})
    except Exception as e:
        return server_error_response(e)
    