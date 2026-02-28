# -*- coding: utf-8 -*-
from ..ClientBaseUtils import *


def CheckPlayerItemApi(item_name, item_aux=0, count=1):
    """
    检查指定玩家是否拥有特定属性的物品。

    :param item_name: 物品名称。
    :type item_name: str
    :param item_aux: 物品的附加属性值。
    :type item_aux: int
    :param count: 需要检查的物品数量。
    :type count: int

    :return: 返回物品所在的位置类型和索引，如果没有找到则返回None。
    :rtype: tuple[int, int] or tuple[None, None]
    """
    for pos_type in range(4):
        item_dict_list = GetCompItemLocalPlayer().GetPlayerAllItems(pos_type)
        for index, item_dict in enumerate(item_dict_list):
            if item_dict and item_dict["newItemName"] == item_name and item_dict["newAuxValue"] == item_aux and item_dict["count"] >= count:
                return pos_type, index
    return None, None


def GetCarriedItem(get_user_data=False):
    """
    获取右手物品的信息
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品信息字典，没有物品则返回None
    :rtype:dict or None
    """
    return GetCompItemLocalPlayer().GetCarriedItem(get_user_data)


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
    return GetCompItemLocalPlayer().GetOffhandItem(get_user_data)


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