import os


ALIYUNSTORGE_CONFIG = {
    "ALIYUN_OSS_BUCKET_NAME":"architecturehandbook",
    "ALIYUN_OSS_REGION":"cn-beijing",
    "ALIYUN_OSS_ACCESS_KEY":os.environ.get("ALIYUN_OSS_ACCESS_KEY"),
    "ALIYUN_OSS_SECRET_KEY":os.environ.get("ALIYUN_OSS_SECRET_KEY"),
    "ALIYUN_OSS_ENDPOINT":os.environ.get("ALIYUN_OSS_ENDPOINT")

}

ES_CLIENT_CONFIG = {
    
    "ES_HOST_LOCAL":"XXX",
    "ES_CLOUD_ID":"", 
    "ES_USER":"",
    "ES_PASSWORD":"",
    "ES_API_KEY":"",
    "ES_CONNECT_PARAMS":"",
    "ES_SIGNATURE":"",
    "ES_BM25_SEARCH_SIZE":100
    
}

