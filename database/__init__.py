from database.database_aliyun_oss_connector import AliYunOSSClient
from database.database_es_connector import ElasticsearchClient
from database.database_milvus_connector import MilvusClient
from database.database_minio_connector import MinioClient
from database.database_mysql_connector import MysqlClient

DatabaseConnector = {
    "MysqlClient": AliYunOSSClient,
    "ElasticsearchClient": ElasticsearchClient,
    "MilvusClient": MilvusClient,
    "MinioClient": MinioClient,
    "AliyunOSSClient": MysqlClient
}