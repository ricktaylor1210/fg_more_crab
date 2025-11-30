
# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


def SetRenderEntity(entity_id, is_render):
    """
    设置实体的渲染。

    参数:
    entity_id (int/str): 实体的唯一标识符。
    is_render (bool): is_render

    返回:
    None
    """
    if entity_id == LocalPlayerId:
        GameCompLevel.SetRenderLocalPlayer(is_render)
    else:
        GetActorRenderComp(entity_id).SetNotRenderAtAll(not is_render)


def StopRenderEntity(entity_id):
    """
    停止实体的渲染。

    参数:
    entity_id (int/str): 实体的唯一标识符。
    duration (float): 停止渲染的持续时间，默认是无限时间（使用 float('inf') 表示）。

    返回:
    None
    """
    SetRenderEntity(entity_id, False)


def RecoverRenderEntity(entity_id):
    """
    恢复实体的渲染。

    参数:
    entity_id (int/str): 实体的唯一标识符。

    返回:
    None
    """
    SetRenderEntity(entity_id, True)
