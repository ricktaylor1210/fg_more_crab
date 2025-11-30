# -*- coding: utf-8 -*-

from fg_more_crabScripts.server.api.EmptyBaseServerApi import *


def GetRelevantPlayer(player_id, except_list=None):
    """
    获取附近玩家id列表

    :param player_id: player_id
    :type player_id: str
    :param except_list: 排除的玩家id列表,默认值为None,不排除其他玩家及自身
    :type except_list: list[str]
    :return:附近玩家id列表
    :rtype:list[str]
    """
    return GetPlayerComp(player_id).GetRelevantPlayer(except_list if except_list else [player_id])


def GetAllPlayerList():
    """
    获取所有玩家list
    由于引擎中的玩家id是无序存储的，所以该接口返回列表的先后顺序没有实际意义，仅为在多平台下表现一致。

    :return:所有玩家list
    :rtype:list[str]
    """
    return ServerApi.GetPlayerList()


def GetEngineActor():
    """
    获取所有维度中已加载的所有实体（不包含玩家）。

    :return:当前地图中的所有实体信息，key：实体id，value：实体信息字典
        实体信息字典:
            dimensionId	int	维度id
            entityType	int	实体类型
            identifier	str	实体identifier
    :rtype:dict[str,dict]
    """
    return ServerApi.GetEngineActor()


def GetEngineActorList():
    """
    获取所有维度中已加载的所有实体（不包含玩家）。

    :rtype:list[str]
    """
    return list(GetEngineActor().keys())


def GetEntityIsAlive(entity_id):
    """
    判断生物实体是否存活或非生物实体是否存在
    注意，如果检测的实体所在的区块被卸载，则该接口返回False。因此，需要注意实体所在的区块是否被加载。
    区块卸载：游戏只会加载玩家周围的区块，玩家移动到别的区域时，原来所在区域的区块会被卸载，参考区块介绍

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 是否存活
    :rtype: bool
    """
    return GameCompLevel.IsEntityAlive(entity_id)


def AddTimer(delay, func, *args, **kwargs):
    """
    添加一个服务端触发的一次性定时器。

    :param delay: 定时器的延迟时间。
    :type delay: float or int
    :param func: 定时器触发时要执行的函数。

    :return: 返回创建的定时器。
    """
    return GameCompLevel.AddTimer(delay, func, *args, **kwargs)


def AddRepeatedTimer(delay, func, *args, **kwargs):
    """
    添加一个服务端触发的重复定时器。

    :param delay: 定时器的延迟时间。
    :type delay: float or int
    :param func: 定时器触发时要执行的函数。

    :return: 返回创建的定时器。
    """
    return GameCompLevel.AddRepeatedTimer(delay, func, *args, **kwargs)


def CancelTimer(timer):
    """
    取消一个已经设置的定时器。

    :param timer: 需要取消的定时器。

    :return: 取消定时器的操作结果。
    :rtype: bool or None
    """
    return GameCompLevel.CancelTimer(timer)
