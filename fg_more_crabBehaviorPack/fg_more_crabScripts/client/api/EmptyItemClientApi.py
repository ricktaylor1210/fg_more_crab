# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


def UnwrapUserData(data):
    if isinstance(data, dict) and '__type__' in data and '__value__' in data:
        return data['__value__']
    return data


def WrapUserData(data, data_type=None):
    if isinstance(data, bool):  # Byte (True/False)
        return {'__type__': 1, '__value__': data}
    elif isinstance(data, int):
        if -(2 ** 15) <= data < (2 ** 15):  # Short
            return {'__type__': 2, '__value__': data}
        elif -(2 ** 31) <= data < (2 ** 31):  # Int
            return {'__type__': 3, '__value__': data}
        elif -(2 ** 63) <= data < (2 ** 63):  # Int64
            return {'__type__': 4, '__value__': data}
    elif isinstance(data, float):
        if data_type == 5:  # Float
            return {'__type__': 5, '__value__': data}
        else:  # Double
            return {'__type__': 6, '__value__': data}
    elif isinstance(data, list):
        if all(isinstance(i, int) for i in data):  # IntArray or ByteArray
            if data_type == 7:  # ByteArray
                return {'__type__': 7, '__value__': data}
            else:  # IntArray
                return {'__type__': 11, '__value__': data}
        else:  # List (recursive conversion)
            return {'__type__': 9, '__value__': [WrapUserData(i) for i in data]}
    elif isinstance(data, dict):  # Compound (recursive conversion)
        return {'__type__': 10, '__value__': {k: WrapUserData(v) for k, v in data.items()}}
    elif isinstance(data, str):  # String
        return {'__type__': 8, '__value__': data}
    else:
        raise ValueError("Unsupported data type")


def GetCarriedItem(get_user_data=False):
    """
    获取右手物品的信息
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品信息字典，没有物品则返回None
    :rtype:dict or None
    """
    return CompItem.GetCarriedItem(get_user_data)


def GetCarriedItemName(get_user_data=False):
    """
    获取右手物品的名称
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品名称
    :rtype:str or None
    """
    item_dict = GetCarriedItem(get_user_data)
    return item_dict["newItemName"] if item_dict else None


def GetOffhandItem(get_user_data=False):
    """
    获取左手物品的信息
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品信息字典，没有物品则返回None
    :rtype:dict or None
    """
    return CompItem.GetOffhandItem(get_user_data)


def GetOffhandItemName(get_user_data=False):
    """
    获取左手物品的名称
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品名称
    :rtype:str or None
    """
    item_dict = GetOffhandItem(get_user_data)
    return item_dict["newItemName"] if item_dict else None
