#!/usr/bin/env python
# -*- encoding: utf-8 -*-
import base_handler
import api.libs.database


class PhotosHandler(base_handler.BaseHandler):
    """照片 URI
    """

    def __init__(self, *args, **kwargs):
        super(PhotosHandler, self).__init__(*args, **kwargs)
        self.__db = api.libs.database.Database()
        self.__cdn_domain = self._conf.get('cdn', 'domain')

    def __log_arguments(self):
        """获取需要记录日志的参数, 包括:

            uid: 用户 ID
            os: 操作系统 (androdi/os)
            ver: 客户端版本
            max: 最大加载数目 (默认: 10)
            beg: 起始位置 (从0开始, 默认0)
            press: 出版社
            album_name: 写真集名字
        """
        self._logs['uid'] = self.get_argument('uid', None)
        self._logs['os'] = self.get_argument('os', None)
        self._logs['ver'] = self.get_argument('ver', None)
        self._logs['max'] = self.get_argument('max', '10')
        self._logs['beg'] = self.get_argument('beg', '0')
        self._logs['press'] = self.get_argument('press', None)
        self._logs['album_name'] = self.get_argument('album_name', None)

    def __get_photos(self):
        skip = int(self.get_argument('beg', 0))
        max_photos = int(self.get_argument('max', 10))
        self._rets['photos'] = []

        photos = self.__db.get_photos({
            'album_name': self.get_argument('album_name', None),
            'press': self.get_argument('press', None),
        }).skip(skip).limit(max_photos)

        for photo in photos:
            self._rets['photos'].append({
                "url": "{0}/{1}!thumb".format(self.__cdn_domain, photo['url']),
                "id": str(photo['_id']),
            })

    def __get_album_info(self):
        album_gen = self.__db.get_albums({
            'name': self.get_argument('album_name', None),
            'press': self.get_argument('press', None),
        })

        album = album_gen.next()
        self._rets['album_name'] = album['name']
        self._rets['press'] = album['press']
        self._rets['models'] = album['models']

    def get(self):
        logger_level = 'info'
        try:
            logger = api.libs.log.get_logger('photos')
            self.__log_arguments()
            self.__get_photos()
            self.__get_album_info()
        except Exception as e:
            self._errno = api.libs.define.ERR_FAILURE
            self._logs['msg'] = str(e)
            logger_level = 'warning'
        finally:
            self._logs['errno'] = self._errno
            logger.flush(logger_level, self._logs)
            self._write()
