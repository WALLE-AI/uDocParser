import loguru

from database import DatabaseConnector


def test_upload_oss():
    pdf_file = "D:\\LLM\\project\\uDocParser\\examples\\rename_pdf_test\\北京市地方标准：房屋建筑使用安全检查技术规程.pdf"
    file_name = "北京市地方标准：房屋建筑使用安全检查技术规程.pdf"
    ossclient = DatabaseConnector['AliyunOSSClient']()
    ##upload file
    if ossclient.exists(file_name):
        result = ossclient.delete(file_name)
        loguru.logger.info(f"request_id: {result.request_id}")
    result = ossclient.save_local_file("北京市地方标准：房屋建筑使用安全检查技术规程.pdf",pdf_file)
    # 请求ID。请求ID是本次请求的唯一标识，强烈建议在程序日志中添加此参数。
    print('request_id: {0}'.format(result.request_id))
    # ETag是put_object方法返回值特有的属性，用于标识一个Object的内容。
    print('ETag: {0}'.format(result.etag))
    # HTTP响应头部。
    print('date: {0}'.format(result.headers['date']))
    url = ossclient.get_file_url(file_name)
    loguru.logger.info(f"file url {url}")


