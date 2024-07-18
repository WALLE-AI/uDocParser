##参考阿里云的oss服务客户端来进行集成，目前采用minio的local对象存储的方案
import sys
from collections.abc import Generator
from contextlib import closing

import oss2 as aliyun_s3
from flask import Flask

from conf.database_config import ALIYUNSTORGE_CONFIG

class AliYunOSSClient():
    """Implementation for aliyun storage.
    """

    def __init__(self):
        self.bucket_name = ALIYUNSTORGE_CONFIG['ALIYUN_OSS_BUCKET_NAME']
        oss_auth_method = aliyun_s3.Auth
        region =ALIYUNSTORGE_CONFIG['ALIYUN_OSS_REGION']
        oss_auth = oss_auth_method(ALIYUNSTORGE_CONFIG['ALIYUN_OSS_ACCESS_KEY'], ALIYUNSTORGE_CONFIG['ALIYUN_OSS_SECRET_KEY'])
        self.client = aliyun_s3.Bucket(
            oss_auth,
            ALIYUNSTORGE_CONFIG['ALIYUN_OSS_ENDPOINT'],
            self.bucket_name,
            connect_timeout=30,
            region=region,
        )

    def percentage(self,consumed_bytes, total_bytes):
        if total_bytes:
            rate = int(100 * (float(consumed_bytes) / float(total_bytes)))
            print('\r{0}% '.format(rate), end='')
            sys.stdout.flush()
    def save(self, filename, data):
        '''
        这是流式方式上传https://help.aliyun.com/zh/oss/developer-reference/simple-upload-1?spm=a2c4g.11186623.0.0.57934c1dUWbpv4
        '''
        return self.client.put_object(filename, data)
    def save_local_file(self,filename,file_local_path):
        return self.client.put_object_from_file(filename,file_local_path)

    def get_file_url(self,filename):
        return self.client.sign_url('GET', filename, 3600, slash_safe=True)

    def load_once(self, filename: str) -> bytes:
        with closing(self.client.get_object(filename)) as obj:
            data = obj.read()
        return data

    def load_stream(self, filename: str) -> Generator:
        def generate(filename: str = filename) -> Generator:
            with closing(self.client.get_object(filename)) as obj:
                while chunk := obj.read(4096):
                    yield chunk

        return generate()

    def download(self, filename, target_filepath):
        self.client.get_object_to_file(filename, target_filepath)

    def exists(self, filename):
        return self.client.object_exists(filename)

    def delete(self, filename):
        self.client.delete_object(filename)
