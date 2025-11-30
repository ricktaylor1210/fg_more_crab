# coding=utf-8

from fg_more_crabScripts.ModBaseApi import *
from fg_more_crabScripts.modMain import GetClientMain

ClientMain = GetClientMain()
GlobalTickCount = ClientMain.GlobalTickCount
LevelId = ClientApi.GetLevelId()
CompFactory = ClientApi.GetEngineCompFactory()
LocalPlayerId = ClientApi.GetLocalPlayerId()

# 初始化组件
ConfigClient = CompFactory.CreateConfigClient(LevelId)
CompBlock = CompFactory.CreateBlock(LevelId)
CompSound = CompFactory.CreateCustomAudio(LevelId)
CompCamera = CompFactory.CreateCamera(LevelId)
CompOperation = CompFactory.CreateOperation(LevelId)
CompTextNotifyClient = CompFactory.CreateTextNotifyClient(LevelId)
CompPostProcess = CompFactory.CreatePostProcess(LevelId)
CompBlockGeometry = CompFactory.CreateBlockGeometry(LevelId)
CompTextBoard = CompFactory.CreateTextBoard(LevelId)
CompTime = CompFactory.CreateTime(LevelId)
CompQueryLevel = CompFactory.CreateQueryVariable(LevelId)
CompParticleSystem = CompFactory.CreateParticleSystem(None)
MinecraftEnum = ClientApi.GetMinecraftEnum()
GameCompLevel = CompFactory.CreateGame(LevelId)

CompItem = CompFactory.CreateItem(LocalPlayerId)
CompPlayerView = CompFactory.CreatePlayerView(LocalPlayerId)
CompPlayer = CompFactory.CreatePlayer(LocalPlayerId)
CompQueryLocalPlayer = CompFactory.CreateQueryVariable(LocalPlayerId)

# 0：Window；1：IOS；2：Android；-1：其他
PlatForm = ClientApi.GetPlatform()

ScreenNode = ClientApi.GetScreenNodeCls()
ViewBinder = ClientApi.GetViewBinderCls()
ViewRequest = ClientApi.GetViewViewRequestCls()
CustomUIScreenProxy = ClientApi.GetUIScreenProxyCls()
NativeScreenManager = ClientApi.GetNativeScreenManagerCls()

# 统一组件缓存
component_cache = {}

# 手动列出所有可能的组件类型及其对应的方法名称
component_methods = {
    "pos": "CreatePos",
    "mod_attr": "CreateModAttr",
    "tame": "CreateTame",
    "action_motion": "CreateActorMotion",
    "entity_rot": "CreateRot",
    "entity_type": "CreateEngineType",
    "collision_box": "CreateCollisionBox",
    "frame_ani_control": "CreateFrameAniControl",
    "frame_ani_trans": "CreateFrameAniTrans",
    "game": "CreateGame",
    "query": "CreateQueryVariable",
    "actor_render": "CreateActorRender",
    "model": "CreateModel"
}


def get_component(comp_type, entity_id):
    key = (comp_type, entity_id)
    if key not in component_cache:
        method_name = component_methods[comp_type]
        create_method = getattr(CompFactory, method_name)
        component_cache[key] = create_method(entity_id)
    return component_cache[key]


def GetPosComp(entity_id):
    return get_component("pos", entity_id)


def GetModAttrComp(entity_id):
    return get_component("mod_attr", entity_id)


def GetTameComp(entity_id):
    return get_component("tame", entity_id)


def GetActionMotionComp(entity_id):
    return get_component("action_motion", entity_id)


def GetEntityRotComp(entity_id):
    return get_component("entity_rot", entity_id)


def GetEntityTypeComp(entity_id):
    return get_component("entity_type", entity_id)


def GetCollisionBoxComp(entity_id):
    return get_component("collision_box", entity_id)


def GetFrameAniControlComp(entity_id):
    return get_component("frame_ani_control", entity_id)


def GetFrameAniTransComp(entity_id):
    return get_component("frame_ani_trans", entity_id)


def GetGameComp(entity_id):
    return get_component("game", entity_id)


def GetEntityQueryComp(entity_id):
    return get_component("query", entity_id)


def GetActorRenderComp(entity_id):
    return get_component("actor_render", entity_id)


def GetModelComp(entity_id):
    return get_component("model", entity_id)

# 测试函数，打印所有组件
# def test_print_all_components():
#     print ("============================================")
#     print("ConfigClient:", ConfigClient)
#     print("CompItem:", CompItem)
#     print("CompBlock:", CompBlock)
#     print("CompSound:", CompSound)
#     print("CompCamera:", CompCamera)
#     print("CompPlayerView:", CompPlayerView)
#     print("CompOperation:", CompOperation)
#     print("CompTextNotifyClient:", CompTextNotifyClient)
#     print("CompPostProcess:", CompPostProcess)
#     print("CompPlayer:", CompPlayer)
#     print("CompBlockGeometry:", CompBlockGeometry)
#     print("CompTextBoard:", CompTextBoard)
#     print("CompTime:", CompTime)
#     print("CompQueryLevel:", CompQueryLevel)
#     print("CompQueryLocalPlayer:", CompQueryLocalPlayer)
#     print("MinecraftEnum:", MinecraftEnum)
#     print("PlatForm:", PlatForm)
#     print("ScreenNode:", ScreenNode)
#     print("ViewBinder:", ViewBinder)
#     print("ViewRequest:", ViewRequest)
#     print("CustomUIScreenProxy:", CustomUIScreenProxy)
#     print("NativeScreenManager:", NativeScreenManager)
#     print("PosComp:", GetPosComp(LocalPlayerId))
#     print("ModAttrComp:", GetModAttrComp(LocalPlayerId))
#     print("TameComp:", GetTameComp(LocalPlayerId))
#     print("ActionMotionComp:", GetActionMotionComp(LocalPlayerId))
#     print("EntityRotComp:", GetEntityRotComp(LocalPlayerId))
#     print("EntityTypeComp:", GetEntityTypeComp(LocalPlayerId))
#     print("CollisionBoxComp:", GetCollisionBoxComp(LocalPlayerId))
#     print("FrameAniControlComp:", GetFrameAniControlComp(LocalPlayerId))
#     print("GameComp:", GetGameComp(LocalPlayerId))
#     print("EntityQueryComp:", GetEntityQueryComp(LocalPlayerId))
#     print("ActorRenderComp:", GetActorRenderComp(LocalPlayerId))
#     print("ModelComp:", GetModelComp(LocalPlayerId))
#     print("GameCompLevel:", GameCompLevel)

# 执行测试函数
# test_print_all_components()
