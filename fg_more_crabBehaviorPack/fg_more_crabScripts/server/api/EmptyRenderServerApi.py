# -*- coding: utf-8 -*-

from fg_more_crabScripts.server.api.EmptyBaseServerApi import *


def StopRenderEntity(entity_id, duration=float('inf')):
    """
    停止实体的渲染。

    参数:
    entity_id (int/str): 实体的唯一标识符。
    duration (float): 停止渲染的持续时间，默认是无限时间（使用 float('inf') 表示）。

    返回:
    None
    """
    ServerMain.BroadcastToAllClient("ServerStopRenderEntityEvent", {"entity_id": entity_id, "duration": duration})


def RecoverRenderEntity(entity_id):
    """
    恢复实体的渲染。

    参数:
    entity_id (int/str): 实体的唯一标识符。

    返回:
    None
    """
    ServerMain.BroadcastToAllClient("ServerRecoverRenderEntityEvent", {"entity_id": entity_id})
