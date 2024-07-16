##参考阿里云的oss服务客户端来进行集成，目前采用minio的local对象存储的方案


class AliYunOSSClient(object):
    def __init__(self):
         self.desc = " aliyun oss client connector"

    def __str__(self):
        return self.desc