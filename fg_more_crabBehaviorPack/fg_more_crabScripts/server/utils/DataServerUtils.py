# -*- coding: utf-8 -*-

from ..ServerBaseUtils import *


def GetExtraDataLevel(key):
    """
    获取世界的自定义数据某个键所对应的值。
    :param key key
    :type key str
    :rtype any
    """
    return GetCompExtraDataLevel().GetExtraData(key)


def SetExtraDataLevel(key, value, auto_save=True):
    """

    用于设置世界的自定义数据，数据以键值对的形式保存。

    :param key: key
    :type key: str
    :param value: value
    :type value: any
    :param auto_save: auto_save
    :type auto_save: bool
    :return: set_res
    :rtype: bool
    """
    return GetCompExtraDataLevel().SetExtraData(key, value, auto_save)


def CleanExtraDataLevel(key):
    """

    用于设置世界的自定义数据，数据以键值对的形式保存。

    :param key: key
    :type key: str
    :return: set_res
    :rtype: bool
    """
    return GetCompExtraDataLevel().CleanExtraData(key)


def GetExtraDataEntity(entity_id, key):
    """
    获取世界的自定义数据某个键所对应的值。
    :param entity_id: entity_id
    :type entity_id: str
    :param key key
    :type key str
    :rtype any
    """
    return CompFactory.CreateExtraData(entity_id).GetExtraData(key)


def SetExtraDataEntity(entity_id, key, value, auto_save=True):
    """

    用于设置世界的自定义数据，数据以键值对的形式保存。

    :param entity_id: entity_id
    :type entity_id: str
    :param key: key
    :type key: str
    :param value: value
    :type value: any
    :param auto_save: auto_save
    :type auto_save: bool
    :return: set_res
    :rtype: bool
    """
    return CompFactory.CreateExtraData(entity_id).SetExtraData(key, value, auto_save)


def CleanExtraDataEntity(entity_id, key):
    """

    用于设置世界的自定义数据，数据以键值对的形式保存。

    :param entity_id: entity_id
    :type entity_id: str
    :param key: key
    :type key: str
    :return: set_res
    :rtype: bool
    """
    return CompFactory.CreateExtraData(entity_id).CleanExtraData(key)


def GetEntityAllExtraData(entity_id):
    """
    :param entity_id: entity_id
    :type entity_id: str

    :return: AllExtraData
    :rtype: dict
    """
    all_extra_data = CompFactory.CreateExtraData(entity_id).GetWholeExtraData()
    if all_extra_data:
        return copy.deepcopy(all_extra_data)
    return {}
