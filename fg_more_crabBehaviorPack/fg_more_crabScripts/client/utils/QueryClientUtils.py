# -*- coding: utf-8 -*-

from ..ClientBaseUtils import *

DelaySetEntityQueryTimerDict = {}
RegisterQueryList = []
MobQueryValueMap = {}


def RegisterQuery(query_name, query_value):
    """
    根据传入的query_name, query_value进行Query注册

    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    """
    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name
    if query_name not in RegisterQueryList:
        GetCompQueryLevel().Register(query_name, query_value)
        RegisterQueryList.append(query_name)


def RegisterQueryByMap(query_map):
    """
    根据传入的query_map进行Query注册

    :param query_map: query_map
    :type query_map: dict[str,int or float]
    """
    for query_name, query_value in query_map.iteritems():
        RegisterQuery(query_name, query_value)


def GetQuery(entity_id, query_name):
    """
    根据传入的entity_id, query_name获取Query

    :param entity_id: entity_id
    :type entity_id: str
    :param query_name: query_name
    :type query_name: str
    :return query_value
    :rtype int or float or None
    """
    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name
    query_comp = CompFactory.CreateQueryVariable(entity_id)
    return query_comp.Get(query_name)


def SetQuery(entity_id, query_name, query_value):
    """
    根据传入的entity_id, query_name, query_value进行Query设置

    :param entity_id: entity_id
    :type entity_id: str
    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    """

    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name

    query_comp = CompFactory.CreateQueryVariable(entity_id)
    current_value = query_comp.Get(query_name)
    if current_value != query_value:
        query_comp.Set(query_name, query_value)

        try:
            entity_map = MobQueryValueMap.setdefault(entity_id, {})
            if entity_map.get(query_name) != query_value:
                entity_map[query_name] = query_value
        except AttributeError:
            if IN_DEVELOPMENT:
                # 开发模式：直接抛出，便于发现问题
                raise
            else:
                pass


def SetEntityQueryAndNotifyToServer(entity_id, query_name, query_value):
    """
    根据传入的entity_id, query_name, query_value进行Query设置

    :param entity_id: entity_id
    :type entity_id: str
    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    """
    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name
    if query_name in DelaySetEntityQueryTimerDict.setdefault(entity_id, {}):
        GetCompGameLevel().CancelTimer(DelaySetEntityQueryTimerDict[entity_id][query_name])
        DelaySetEntityQueryTimerDict[entity_id].pop(query_name)
    SetQuery(entity_id, query_name, query_value)
    GetClientMainSystem().NotifyToServer("OnChangeEntityQueryToAllClientEvent",
                                         {"entity_id": entity_id, "query_name": query_name, "query_value": query_value})


def SetEntityQueryAndNotifyToServerAndAutoRecover(entity_id, query_name, query_value, recover_time=0.05,
                                                  recover_value=0):
    """
    根据传入的entity_id, query_name, query_value进行Query设置，并且在recover_time后自动恢复

    :param entity_id: entity_id
    :type entity_id: str
    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    :param recover_time: recover_time
    :type recover_time: float or int
    :param recover_value: recover_value
    :type recover_value: float or int
    """
    DelaySetEntityQueryTimerDict.setdefault(entity_id, {})
    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name
    SetEntityQueryAndNotifyToServer(entity_id, query_name, query_value)
    DelaySetEntityQueryTimerDict[entity_id][query_name] = GetCompGameLevel().AddTimer(recover_time,
                                                                                 SetEntityQueryAndNotifyToServer,
                                                                                 entity_id, query_name,
                                                                                 recover_value)


def SetEntityQueryAndAutoRecover(entity_id, query_name, query_value, recover_time=0.05, recover_value=0):
    """
    根据传入的entity_id, query_name, query_value进行Query设置，并且在recover_time后自动恢复

    :param entity_id: entity_id
    :type entity_id: str
    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    :param recover_time: recover_time
    :type recover_time: float or int
    :param recover_value: recover_value
    :type recover_value: float or int
    """
    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name
    if query_name in DelaySetEntityQueryTimerDict.setdefault(entity_id, {}):
        GetCompGameLevel().CancelTimer(DelaySetEntityQueryTimerDict[entity_id][query_name])
        DelaySetEntityQueryTimerDict[entity_id].pop(query_name)
    SetQuery(entity_id, query_name, query_value)

    DelaySetEntityQueryTimerDict[entity_id][query_name] = GetCompGameLevel().AddTimer(recover_time, SetQuery, entity_id,
                                                                                 query_name,
                                                                                 recover_value)


def SetLocalPlayerQueryAndNotifyToServer(query_name, query_value):
    """
    根据传入的query_name, query_value进行本地玩家Query设置

    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    """
    SetEntityQueryAndNotifyToServer(GetLocalPlayerId(), query_name, query_value)


def SetLocalPlayerQueryAndNotifyToServerAndAutoRecover(query_name, query_value, recover_time=0.05, recover_value=0):
    """
    根据传入的query_name, query_value进行本地玩家Query设置，并且在recover_time后自动恢复

    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    :param recover_time: recover_time
    :type recover_time: float or int
    :param recover_value: recover_value
    :type recover_value: float or int
    """
    SetEntityQueryAndNotifyToServerAndAutoRecover(GetLocalPlayerId(), query_name, query_value, recover_time, recover_value)
