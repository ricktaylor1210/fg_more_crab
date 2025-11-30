# coding=utf-8
from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


def SendMessageToClient(message_text):
    CompTextNotifyClient.SetLeftCornerNotify(message_text)


def SetTipMessage(message_text):
    GetGameComp(LocalPlayerId).SetTipMessage(message_text)


def GetLocalDimensionId():
    """

    获取entity_id的CompGame

    :return: 维度id。客户端未登录完成或正在切维度时返回-1
    :rtype: int or None
    """
    current_dimension_id = GameCompLevel.GetCurrentDimension()
    return current_dimension_id if current_dimension_id != -1 else None


def GetAllPlayerList():
    """
    获取所有玩家list
    由于引擎中的玩家id是无序存储的，所以该接口返回列表的先后顺序没有实际意义，仅为在多平台下表现一致。

    :return:所有玩家list
    :rtype:list[str]
    """
    return ClientApi.GetPlayerList()


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
    return ClientApi.GetEngineActor()


def GetEntityIsAlive(entity_id):
    """
    判断生物实体是否存活或非生物实体是否存在
    注意，如果检测的实体所在的区块被卸载，则该接口返回False。因此，需要注意实体所在的区块是否被加载。
    区块卸载：游戏只会加载玩家周围的区块，玩家移动到别的区域时，原来所在区域的区块会被卸载，参考区块介绍

    :param entity_id: 实体的entity_id。
    :type entity_id: str

    :return: bool  false表示生物实体已死亡或非生物实体已销毁，true表示生物实体存活或非生物实体存在
    :rtype: bool
    """
    return GameCompLevel.IsEntityAlive(entity_id) and GameCompLevel.HasEntity(entity_id)


def AddTimer(delay, func, *args, **kwargs):
    """
    添加客户端触发的定时器，非重复。

    :param delay: 定时器的延迟时间（秒）。
    :type delay: float
    :param func: 定时器触发时调用的函数。
    :return: Timer组件。
    """
    return GameCompLevel.AddTimer(delay, func, *args, **kwargs)


def AddRepeatedTimer(delay, func, *args, **kwargs):
    """
    添加客户端触发的定时器，重复。

    :param delay: 定时器的延迟时间（秒）。
    :type delay: float
    :param func: 定时器触发时调用的函数。
    :param args: 传递给函数的位置参数。
    :param kwargs: 传递给函数的关键字参数。

    :return: Timer组件。
    """
    return GameCompLevel.AddRepeatedTimer(delay, func, *args, **kwargs)


def CancelTimer(timer):
    """
    取消定时器。

    :param timer: 要取消的定时器。

    """
    GameCompLevel.CancelTimer(timer)
