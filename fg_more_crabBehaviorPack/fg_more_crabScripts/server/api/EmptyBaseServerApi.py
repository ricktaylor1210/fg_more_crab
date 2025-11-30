# -*- coding: utf-8 -*-
from fg_more_crabScripts.ModBaseApi import *
from fg_more_crabScripts.modMain import GetServerMain

ServerMain = GetServerMain()
GlobalTickCount = ServerMain.GlobalTickCount
LevelId = ServerApi.GetLevelId()
CompFactory = ServerApi.GetEngineCompFactory()

# 初始化组件
CompItem = CompFactory.CreateItem(LevelId)
CompBlockInfo = CompFactory.CreateBlockInfo(LevelId)
CompBlock = CompFactory.CreateBlock(LevelId)
CompHttp = CompFactory.CreateHttp(LevelId)
ExtraDataCompLevel = CompFactory.CreateExtraData(LevelId)
ExplosionCompLevel = CompFactory.CreateExplosion(LevelId)
GameCompLevel = CompFactory.CreateGame(LevelId)
CommandCompLevel = CompFactory.CreateCommand(LevelId)
CompChunkSource = CompFactory.CreateChunkSource(LevelId)

MinecraftEnum = ServerApi.GetMinecraftEnum()

# 统一组件缓存
component_cache = {}

# 手动列出所有可能的组件类型及其对应的方法名称
component_methods = {
    'Effect': 'CreateEffect',
    'ModAttr': 'CreateModAttr',
    'Attr': 'CreateAttr',
    'Action': 'CreateAction',
    'Breath': 'CreateBreath',
    'ActionMotion': 'CreateActorMotion',
    'Dimension': 'CreateDimension',
    'Pos': 'CreatePos',
    'Rot': 'CreateRot',
    'EngineType': 'CreateEngineType',
    'Tag': 'CreateTag',
    'EntityComponent': 'CreateEntityComponent',
    'Player': 'CreatePlayer',
    'Lv': 'CreateLv',
    'Msg': 'CreateMsg',
    'Tame': 'CreateTame',
    'ActorOwner': 'CreateActorOwner',
    'Hurt': 'CreateHurt',
    'ControlAi': 'CreateControlAi',
    'ExtraData': 'CreateExtraData',
    'Game': 'CreateGame',
    'Gravity': 'CreateGravity',
    'Item': 'CreateItem',
    'EntityDefinitions': 'CreateEntityDefinitions',
    'EntityEvent': 'CreateEntityEvent',
    'Ride': 'CreateRide',
    'Explosion': 'CreateExplosion',
    'Command': 'CreateCommand'
}


def get_component(comp_type, entity_id):
    key = (comp_type, entity_id)
    if key not in component_cache:
        method_name = component_methods[comp_type]
        create_method = getattr(CompFactory, method_name)
        component_cache[key] = create_method(entity_id)
    return component_cache[key]


def GetEffectComp(entity_id):
    return get_component('Effect', entity_id)


def GetModAttrComp(entity_id):
    return get_component('ModAttr', entity_id)


def GetAttrComp(entity_id):
    return get_component('Attr', entity_id)


def GetBreathComp(entity_id):
    return get_component('Breath', entity_id)


def GetActionComp(entity_id):
    return get_component('Action', entity_id)


def GetActionMotionComp(entity_id):
    return get_component('ActionMotion', entity_id)


def GetDimensionComp(entity_id):
    return get_component('Dimension', entity_id)


def GetPosComp(entity_id):
    return get_component('Pos', entity_id)


def GetEntityRotComp(entity_id):
    return get_component('Rot', entity_id)


def GetEntityTypeComp(entity_id):
    return get_component('EngineType', entity_id)


def GetTagComp(entity_id):
    return get_component('Tag', entity_id)


def GetEntityComponentComp(entity_id):
    return get_component('EntityComponent', entity_id)


def GetPlayerComp(entity_id):
    return get_component('Player', entity_id)


def GetLvComp(entity_id):
    return get_component('Lv', entity_id)


def GetExpComp(entity_id):
    return get_component('Exp', entity_id)


def GetMsgComp(entity_id):
    return get_component('Msg', entity_id)


def GetTameComp(entity_id):
    return get_component('Tame', entity_id)


def GetActorOwnerComp(entity_id):
    return get_component('ActorOwner', entity_id)


def GetHurtComp(entity_id):
    return get_component('Hurt', entity_id)


def GetAiComp(entity_id):
    return get_component('ControlAi', entity_id)


def GetExtraDataComp(entity_id):
    return get_component('ExtraData', entity_id)


def GetGameComp(entity_id):
    return get_component('Game', entity_id)


def GetGravityComp(entity_id):
    return get_component('Gravity', entity_id)


def GetItemComp(entity_id):
    return get_component('Item', entity_id)


def GetEntityDefinitionsComp(entity_id):
    return get_component('EntityDefinitions', entity_id)


def GetEntityEventComp(entity_id):
    return get_component('EntityEvent', entity_id)


def GetRideComp(entity_id):
    return get_component('Ride', entity_id)
