import os


ALIYUNSTORGE_CONFIG = {
    "ALIYUN_OSS_BUCKET_NAME":"architecturehandbook",
    "ALIYUN_OSS_REGION":"cn-beijing",
    "ALIYUN_OSS_ACCESS_KEY":os.environ.get("ALIYUN_OSS_ACCESS_KEY"),
    "ALIYUN_OSS_SECRET_KEY":os.environ.get("ALIYUN_OSS_SECRET_KEY"),
    "ALIYUN_OSS_ENDPOINT":os.environ.get("ALIYUN_OSS_ENDPOINT")

}

ES_CLIENT_CONFIG = {
    
    "ES_HOST_LOCAL":"http://localhost:9200",
    "ES_CLOUD_ID":"", 
    "ES_USER":"root",
    "ES_PASSWORD":"csce_gaojing",
    "ES_API_KEY":"",
    "ES_CONNECT_PARAMS":"",
    "ES_SIGNATURE":"",
    "ES_BM25_SEARCH_SIZE":100
    
}

llm_client_key_url_info = [{
    "OpenRouter":"OpenRouter",
    "api_key":os.environ.get("OPENROUTER_API_KEY"),
    "base_url":"https://openrouter.ai/api/v1"
    },
    {
    "Siliconflow":"Siliconflow",
    "api_key": os.environ.get("SILICONFLOW_API_KEY"),
    "base_url": "https://api.siliconflow.cn/v1"
    },
    {
        "Dashscope":"Dashscope",
        "api_key": os.environ.get("DASHSCOPE_API_KEY"),
        "base_url": "xxx"  
    }
]


