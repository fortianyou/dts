#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
上传文件到 CDN
暂时使用的是七牛的 CDN 服务. http://www.qiniu.com
"""
import qiniu
import config


class CDN(object):
    """
    CDN 的类.
    """

    def __init__(self):
        self.__client = self.__init_client()
        conf = config.get_config()
        self.__bucket = conf.get('cdn', 'bucket_name')

    def __init_client(self):
        conf = config.get_config()
        client = qiniu.Auth(conf.get('cdn', 'access_key'),
                            conf.get('cdn', 'secret_key'))
        return client

    def upload_file(self, key, filename):
        """上传文件到 CDN

        参数:
            key: 储存在 CDN 上的文件名, 可以包含 "/", 访问时会有层级感.
            filename: 本地文件的路径

        返回:
            返回成功与否.
        """
        token = self.__client.upload_token(self.__bucket, key)
        ret, info = qiniu.put_file(
            token, key, filename, mime_type='image/jpeg', check_crc=True
        )
        return ret['key'] == key and ret['hash'] == qiniu.etag(filename)


if __name__ == '__main__':
    cdn = CDN()
    import sys
    import os
    for line in sys.stdin:
        line = line.strip()
        press, title, models, local = line.split("\t")
        filename = os.path.split(local)[-1]
        vol = title.split("-")[0]
        remote = "{}/{}/{}".format(press, vol, filename)
        local = "../../ysweb/{}".format(local)
        ret = cdn.upload_file(remote, local)
        print "{}\t{}".format(ret, local)
