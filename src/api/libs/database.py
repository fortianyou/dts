#!/usr/bin/env python
# -*- encoding: utf-8 -*-
"""
其实原本我是想用 motor 的, 但是我不会用, 而且感觉不优雅.
"""
import random
import pymongo
import datetime
import utils
import config


@utils.singleton
class Database(object):
    """数据储存的类, 封装了几个函数
    """

    def __init__(self):
        self.__albums, self.__photos = self.__init_db()

    def __init_db(self):
        """初始化数据库以及对应的 collections
        """
        conf = config.get_config()
        host = conf.get('mongodb', 'host')
        port = conf.getint('mongodb', 'port')
        db_name = conf.get('mongodb', 'db_name')
        client = pymongo.MongoClient(host, port)
        db = client[db_name]

        # 初始化 `写真集` collection
        albums = db.albums
        # 建立索引, 同一出版社一个名字只能属于一本写真集
        albums.create_index(
            [('name', pymongo.ASCENDING), ('press', pymongo.ASCENDING)],
            unique=True,
        )
        # 日期, 选取数据使用, 不用唯一
        albums.create_index(
            [('date', pymongo.ASCENDING)],
            unique=False,
        )

        # 初始化 `照片` collection
        photos = db.photos
        # 建立索引, 为写真集名字建立索引, 不唯一.
        photos.create_index(
            [('album_name', pymongo.ASCENDING), ('press', pymongo.ASCENDING)],
            unique=False,
        )
        # 用 _id 唯一标识一张图片, 可用于点赞等
        photos.create_index(
            [('_id', pymongo.DESCENDING)],
            unique=True,
        )
        return albums, photos

    def insert_albums(self, albums_info):
        """插入一本写真集信息

        参数:
            albums_info: 写真集的各种参数信息, 格式必须为:
            {
                'name': 写真集名称,
                'press': 出版社, 和写真集名称一起唯一,
                'models': [模特1, 模特2, ...],
                'tags': [tag1, tag2, ...],
                'date': 出版日期, 如果找不到我会记作加入日期, 精度到日,
                'cover_url': 封面 URL,
                'description': 描述文字,
                'photos': 照片数目,
                'views': 浏览次数, 定时求和照片的浏览次数,
                'likes': 点赞数目, 定时求和照片的点赞次数,
                'rand': 0 ~ 1 之间的一个随机数. 可以定期更新, 索引!
            }
            也支持上述结构的列表.

        返回:
            成功返回 id, 否则抛出异常.

        异常:
            pymongo.errors.DuplicateKeyError: 已存在
        """
        for album in albums_info:
            if 'date' not in album:
                album['date'] = datetime.datetime.utcnow()
        return self.__albums.insert(albums_info)

    def shuffle_albums(self):
        """重新打乱写真集, 让随机更加随机点
        """
        albums = self.__albums.find()
        for album in albums:
            album['rand'] = random.random()
            self.__albums.save(album)

    def get_albums(self, albums_info):
        """可以通过任意维度来查询, 但是只对 `name` 和 `press` 建了索引

        参数:
            albums_info: 请看 `insert_album` 的注释.

        返回:
            返回迭代器, 出错抛出异常
        """
        return self.__albums.find(albums_info).sort('_id', pymongo.DESCENDING)

    def insert_photos(self, photos_info):
        """插入图片信息

        参数:
            photos_info: 照片信息, 如下信息是必要的:
            {
                'press': 出版社,
                'album_name': 写真集名称,
                'url': 图片的 URL,
                'views': 图片被浏览的次数,
                'likes': 图片被点赞的次数,
            }
            也支持上述结构的列表.

        返回:
            成功返回 id, 否则抛出异常.
        """
        return self.__photos.insert(photos_info)

    def get_photos(self, photos_info):
        """可以通过任意维度来查询, 但是只对 `album_name` 建了索引

        参数:
            photos_info: 请看 `insert_photos` 的注释.

        返回:
            返回迭代器, 出错抛出异常.
        """
        return self.__photos.find(photos_info)


if __name__ == '__main__':
    db = Database()
    #db.shuffle_albums()
    #db.get_albums({})
