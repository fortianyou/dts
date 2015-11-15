#!/usr/bin/env python
# -*- encoding: utf-8 -*-


def singleton(cls, *args, **kwargs):
    """单例模式装饰器

    参数:
        cls: 类的对象
        *args, **kwargs: 需要带入的其他参数
    """
    instances = {}

    def __func(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]
    return __func
