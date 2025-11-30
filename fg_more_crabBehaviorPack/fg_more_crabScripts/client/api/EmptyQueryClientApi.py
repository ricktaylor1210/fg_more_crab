# coding=utf-8
from fg_more_crabScripts.client.api import EmptyGameClientApi as GameApi
from fg_more_crabScripts.client.api.EmptyBaseClientApi import *

DelaySetEntityQueryTimerDict = {}
RegisterQueryList = []


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
        CompQueryLevel.Register(query_name, query_value)
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
    query_comp = GetEntityQueryComp(entity_id) if entity_id != LocalPlayerId else CompQueryLocalPlayer
    return query_comp.Get(query_name)


client_main_mob_query_value_map_initialized = False


def check_client_main_mob_query_value_map_initialization():
    """
    检查 ClientMain 的 MobQueryValueMap 是否已初始化
    """
    global client_main_mob_query_value_map_initialized
    try:
        if hasattr(ClientMain, 'ClientMobInstancesController') and hasattr(ClientMain.ClientMobInstancesController, 'MobQueryValueMap'):
            client_main_mob_query_value_map_initialized = True
    except AttributeError:
        pass


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
    global client_main_mob_query_value_map_initialized
    if not client_main_mob_query_value_map_initialized:
        check_client_main_mob_query_value_map_initialization()
        if not client_main_mob_query_value_map_initialized:
            return

    if "query.mod." not in query_name:
        query_name = "query.mod." + query_name

    query_comp = GetEntityQueryComp(entity_id) if entity_id != LocalPlayerId else CompQueryLocalPlayer
    current_value = query_comp.Get(query_name)
    if current_value != query_value:
        query_comp.Set(query_name, query_value)

        try:
            entity_map = ClientMain.ClientMobInstancesController.MobQueryValueMap.setdefault(entity_id, {})
            if entity_map.get(query_name) != query_value:
                entity_map[query_name] = query_value
        except AttributeError:
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
        GameApi.CancelTimer(DelaySetEntityQueryTimerDict[entity_id][query_name])
        DelaySetEntityQueryTimerDict[entity_id].pop(query_name)
    SetQuery(entity_id, query_name, query_value)
    ClientMain.NotifyToServer("OnChangeEntityQueryToAllClientEvent", {"entity_id": entity_id, "query_name": query_name, "query_value": query_value})


def SetEntityQueryAndNotifyToServerAndAutoRecover(entity_id, query_name, query_value, recover_time=0.05, recover_value=0):
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
    DelaySetEntityQueryTimerDict[entity_id][query_name] = GameApi.AddTimer(recover_time, SetEntityQueryAndNotifyToServer, entity_id, query_name,
                                                                           recover_value)


def SetLocalPlayerQuery(query_name, query_value):
    """
    根据传入的query_name, query_value进行本地玩家Query设置

    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    """
    SetQuery(LocalPlayerId, query_name, query_value)


def SetLocalPlayerQueryAndNotifyToServer(query_name, query_value):
    """
    根据传入的query_name, query_value进行本地玩家Query设置

    :param query_name: query_name
    :type query_name: str
    :param query_value: query_value
    :type query_value: float or int
    """
    SetEntityQueryAndNotifyToServer(LocalPlayerId, query_name, query_value)


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
    SetEntityQueryAndNotifyToServerAndAutoRecover(LocalPlayerId, query_name, query_value, recover_time, recover_value)
