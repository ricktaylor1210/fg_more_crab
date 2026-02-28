# -*- coding: utf-8 -*-

from ..ServerBaseUtils import *


def StopRenderEntity(entity_id, duration=float('inf'), only_client_id=None, exclude_client_id=None):
    """
    停止实体的渲染。

    参数:
    entity_id (int/str): 实体的唯一标识符。
    duration (float): 停止渲染的持续时间，默认是无限时间（使用 float('inf') 表示）。

    only_client_id (str/None/list[str]): 若设置此参数,则只对该客户端进行渲染控制。
    exclude_client_id (str/None/list[str]): 若设置此参数,则只排除该客户端的渲染控制。

    only_client_id和exclude_client_id参数冲突,请只设置一个

    返回:
    None
    """
    GetServerMainSystem().BroadcastToAllClient("ServerStopRenderEntityEvent",
                                    {"entity_id": entity_id, "duration": duration, "only_client_id": only_client_id, "exclude_client_id": exclude_client_id})


def RecoverRenderEntity(entity_id, only_client_id=None, exclude_client_id=None):
    """
    恢复实体的渲染。

    参数:
    entity_id (int/str): 实体的唯一标识符。

    only_client_id (str/None/list[str]): 若设置此参数,则只对该客户端进行渲染控制。
    exclude_client_id (str/None/list[str]): 若设置此参数,则只排除该客户端的渲染控制。

    only_client_id和exclude_client_id参数冲突,请只设置一个

    返回:
    None
    """
    GetServerMainSystem().BroadcastToAllClient("ServerRecoverRenderEntityEvent",
                                    {"entity_id": entity_id, "only_client_id": only_client_id, "exclude_client_id": exclude_client_id})
