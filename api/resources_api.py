from flask import request

from api.utils import generator_md5
from api.utils.api_utils import get_json_result, server_error_response

@manager.route('/info', methods=['GET'])
def resource_info():
    '''
    获取现有rag服务中所有LLM vllm embedding reranker 信息
    '''
    try:
        return get_json_result(data={"test": "我是starVLM"})
    except Exception as e:
        return server_error_response(e)


@manager.route('/image/upload', methods=['POST'])
def resource_image_upload():
    '''
    图片识图chat能力
    '''
    req = request.json
    user_id = req['user_id']
    image_path = req['image_path']
    image_id = generator_md5(image_path)
    ##upload image 导入oss服务,也可以存在localstorge中
    try:
        return get_json_result(data={"image_id":image_id,"user_id":user_id})
    except Exception as e:
        return server_error_response(e)



@manager.route('/doc/upload', methods=['POST'])
def resource_doc_upload():
    '''
    图片识图chat能力
    '''
    req = request.json
    user_id = req['user_id']
    doc_path = req['doc_path']
    kb_id = generator_md5("默认需要根据生成一个知识库的唯一ID")
    doc_id = generator_md5(doc_path)
    ##upload doc 导入oss服务,也可以存在localstorge中
    try:
        return get_json_result(data={"image_id":doc_path,"user_id":user_id})
    except Exception as e:
        return server_error_response(e)


@manager.route('/doc/chunk_id', methods=['POST'])
def resource_doc_chunk_id():
    '''
    获取现有rag服务中所有LLM vllm embedding reranker 信息
    '''
    req = request.json
    chunk_id = req['chunk_id']
    try:
        return get_json_result(data={"test": chunk_id})
    except Exception as e:
        return server_error_response(e)


@manager.route('/doc/parser', methods=['POST'])
def resource_doc_parser():
    '''
    图片识图chat能力
    '''
    req = request.json
    user_id = req['user_id']
    doc_id = req['doc_id']
    kb_id = req['kb_id']
    parser_id = generator_md5("解析ID")
    ##根据doc_id从oss服务中找到对应的文件流，从数据库找到文件相关的信息
    try:
        return get_json_result(data={"doc_id":doc_id,"user_id":user_id})
    except Exception as e:
        return server_error_response(e)