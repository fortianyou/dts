#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import random
import tornado.log
import base_handler
import api.libs.database
import api.libs.log



class AlbumsHandler(base_handler.BaseHandler):
    """写真集 URI
    """

    def __init__(self, *args, **kwargs):
        super(AlbumsHandler, self).__init__(*args, **kwargs)
        self.__db = api.libs.database.Database()
        self.__cdn_domain = self._conf.get('cdn', 'domain')

    def __log_arguments(self):
        """获取需要记录日志的参数, 包括:

            uid: 用户 ID
            os: 操作系统 (android/ios)
            ver: 客户端版本号
            max: 最大加载数目 (默认: 10)
        """
        self._logs['uid'] = self.get_argument('uid', None)
        self._logs['os'] = self.get_argument('os', None)
        self._logs['ver'] = self.get_argument('ver', None)
        self._logs['max'] = self.get_argument('max', '10')

    def __get_albums(self):
        """从服务器中获取写真集列表
        """
        left = int(self.get_argument('max', 10))
        # 记录请求数据库次数
        self._logs['db_req'] = 0
        self._rets['albums'] = []
        while left > 0:
            # 请求一次数据库
            self._logs['db_req'] += 1
            rand = random.random()
            albums = self.__db.get_albums({'rand': {'$gt': rand}}).limit(left)
            for album in albums:
                del album['_id']
                del album['rand']
                # 为图片添加域名, 这样比较灵活
                cover_url = self.__cdn_domain + "/" + album['cover_url']
                album['cover_url'] = cover_url
                self._rets['albums'].append(album)
                left -= 1

    def get(self):
        logger_level = 'info'
        try:
            logger = api.libs.log.get_logger('albums')
            self.__log_arguments()
            self.__get_albums()
        except Exception as e:
            self._errno = api.libs.define.ERR_FAILURE
            self._logs['msg'] = str(e)
            logger_level = 'warning'
        finally:
            self._logs['errno'] = self._errno
            logger.flush(logger_level, self._logs)
            self._write()
