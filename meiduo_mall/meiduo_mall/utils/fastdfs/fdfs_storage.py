from django.conf import settings
from django.core.files.storage import Storage
from fdfs_client.client import Fdfs_client


class FastDFSStorage(Storage):
    def __init__(self, base_url=None, client_conf=None):
        """
        初始化
        :param base_url: 用于构造图片完整路径使用，图片服务器的域名
        :param client_conf: FastDFS客户端配置文件的路径
        """
        if base_url is None:
            base_url = settings.FDFS_URL
        self.base_url = base_url
        if client_conf is None:
            client_conf = settings.FDFS_CLIENT_CONF
        self.client_conf = client_conf

    def _open(self, name, mode='rb'):
        # 打开文件
        pass

    def _save(self, name, content):
        # 保存文件
        # 连接fastDFS 连接七牛云
        client=Fdfs_client(self.client_conf)

        # 文件上传
        ret=client.upload_by_buffer(content.read())

        # 判断返回结果 是否上传成功
        if ret['Status'] != 'Upload successed.':
            raise Exception('upload errors')

        # 获取file_id
        file_id=ret['Remote file_id']

        # 返回file_id
        return file_id

    def url(self, name):
        # 拼接完整路径

        return self.base_url+name

    def exists(self, name):
        # 判断文件是否重复
        return False



