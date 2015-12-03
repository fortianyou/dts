#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import random
import tornado.log
from bson.objectid import ObjectId
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
        self._logs['beg_id'] = self.get_argument('beg_id', '0')

    def __get_albums(self):
        """从服务器中获取写真集列表
        """
        albums_info = {}
        # 最大张数
        try:
            max_albums = int(self.get_argument('max', 10))
        except:
            max_albums = 10

        # 起始位置
        try:
            albums_info = {
                '_id': {
                    '$lt': ObjectId(self.get_argument('beg_id')),
                }
            }
        except:
            pass

        self._rets['albums'] = []
        albums = self.__db.get_albums(albums_info).limit(max_albums)
        last_id = None
        for album in albums:
            last_id = album['_id']
            del album['_id']
            del album['date']
            # 为图片添加域名, 这样比较灵活
            cover_url = '{0}/{1}!thumb'.format(
                self.__cdn_domain,
                album['cover_url']
            )
            album['cover_url'] = cover_url
            self._rets['albums'].append(album)
        self._rets['last_id'] = str(last_id)

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
