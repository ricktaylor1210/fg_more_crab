# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyGameServerApi as GameApi
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *

DelaySetEntityQueryTimerDict = {}


def SetEntityQueryAndNotifyToClient(entity_id, query_name, query_value):
    """
    根据传入的entity_id, query_name, query_value进行Query设置

    :param entity_id: entity_id
    :type: str
    :param query_name: query_name
    :type: str
    :param query_value: query_value
    :type: float or int
    """
    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name
    if query_name in DelaySetEntityQueryTimerDict.setdefault(entity_id,{}):
        GameApi.CancelTimer(DelaySetEntityQueryTimerDict[entity_id][query_name])
        DelaySetEntityQueryTimerDict[entity_id].pop(query_name)
    ServerMain.ServerMobInstancesController.OnChangeEntityQueryToAllClientEvent({"entity_id": entity_id, "query_name": query_name, "query_value": query_value})


def SetEntityQueryAndNotifyToClientAndAutoRecover(entity_id, query_name, query_value, recover_time=0.05, recover_value=0):
    """
    根据传入的entity_id, query_name, query_value进行Query设置，并且在recover_time后自动恢复

    :param entity_id: entity_id
    :type: str
    :param query_name: query_name
    :type: str
    :param query_value: query_value
    :type: float or int
    :param recover_time: recover_time
    :type: float or int
    :param recover_value: recover_value
    :type: float or int
    """
    DelaySetEntityQueryTimerDict.setdefault(entity_id, {})
    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name
    SetEntityQueryAndNotifyToClient(entity_id, query_name, query_value)
    DelaySetEntityQueryTimerDict[entity_id][query_name] = GameApi.AddTimer(recover_time, SetEntityQueryAndNotifyToClient, entity_id, query_name, recover_value)
