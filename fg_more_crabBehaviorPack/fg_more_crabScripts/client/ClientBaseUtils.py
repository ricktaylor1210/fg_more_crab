# -*- coding: utf-8 -*-
from ..ModMainConfig import *
import mod.client.extraClientApi as ClientApi
import mod.common.minecraftEnum as MinecraftEnum

# UI Path
BasePanelPath0 = "/variables_button_mappings_and_controls/safezone_screen_matrix/inner_matrix"
BasePanelPath = BasePanelPath0 + "/safezone_screen_panel/root_screen_panel"

UITextureBasePath = "textures/ui/"

ButtonTouchEventToCallbacksMap = {
    7: "ScreenExit",
    0: "TouchUp",
    3: "TouchCancel",
    1: "TouchDown",
    5: "TouchMoveIn",
    4: "TouchMove",
    6: "TouchMoveOut"
}

# ClientSystem
ClientSystem = ClientApi.GetClientSystemCls()
ClientEngineNamespace = ClientApi.GetEngineNamespace()
ClientEngineSystemName = ClientApi.GetEngineSystemName()

ScreenNode = ClientApi.GetScreenNodeCls()
ViewBinder = ClientApi.GetViewBinderCls()
ViewRequest = ClientApi.GetViewViewRequestCls()
CustomUIScreenProxy = ClientApi.GetUIScreenProxyCls()
NativeScreenManager = ClientApi.GetNativeScreenManagerCls()

# 0：Window；1：IOS；2：Android；-1：其他
PlatForm = ClientApi.GetPlatform()

# 延迟获取，避免在导入阶段就固定 / 失效
_LevelId = None
_LocalPlayerId = None

# 工厂本身与关卡无关，仍然可以在导入时拿一次
CompFactory = ClientApi.GetEngineCompFactory()

# 所有组件先占位为 None，真正用时再懒加载（前缀下划线避免对外暴露）
_CompOperation = None
_CompPostProcess = None
_CompGameLevel = None
_CompConfigClientLevel = None
_CompPlayerViewLevel = None
_CompPlayerLocal = None
_CompSoundLevel = None
_CompQueryLevel = None
_CompBlockGeometryLevel = None
_CompBlockInfoLevel = None
_CompBlockLevel = None
_CompParticleSystem = None
_CompCameraLevel = None
_CompTextNotifyClientLevel = None
_CompTimeLevel = None
_CompItemLocalPlayer = None
_CompTextBoard = None

def GetLevelId():
    """
    获取当前关卡 Id，每次调用都从 ClientApi 获取最新值并缓存到模块级缓存。
    使用前缀下划线的全局变量，避免对外暴露实现细节。
    """
    global _LevelId
    _LevelId = ClientApi.GetLevelId()
    return _LevelId


def GetLocalPlayerId():
    """
    获取当前本地玩家 Id，每次调用都从 ClientApi 获取最新值并缓存到模块级缓存。
    同样使用带下划线的全局变量，约束外部代码不要直接访问。
    """
    global _LocalPlayerId
    _LocalPlayerId = ClientApi.GetLocalPlayerId()
    return _LocalPlayerId



def _check_create_result(component_name, result, key_name, key_value):
    """
    统一处理组件创建结果：

    设计原因：
    - 所有组件创建逻辑集中到一个函数里做安全检查，避免到处写重复的 if result is None；
    - 开发环境（IN_DEVELOPMENT=True）下，创建失败直接抛出 RuntimeError，
      可以让问题在调试阶段尽早暴露；
    - 非开发环境则直接放行（可能返回 None），避免因为临时失败导致玩家直接崩溃。
    """
    if result is None and IN_DEVELOPMENT:
        raise RuntimeError(
            "%s creation failed, %s=%r" % (component_name, key_name, key_value)
        )
    return result
# ---------------------------------------------------------------------------
# 各种组件 Getter（懒加载 + 缓存）
# ---------------------------------------------------------------------------

def GetCompOperation():
    """
    获取 Operation 组件。

    设计要点：
    - 懒加载：仅当 _CompOperation 为 None 时创建并缓存；
    - 为恢复自动补全：CreateOperation(...) 的返回值先落到局部变量 result；
    - 开发期校验：创建失败抛 RuntimeError，提示包含关键入参（LevelId）。
    """
    global _CompOperation
    if _CompOperation is None:
        level_id = GetLevelId()

        # 先落变量，给 IDE/语言服务器建立类型推断链路
        result = CompFactory.CreateOperation(level_id)

        # 做开发期校验
        _check_create_result("Operation", result, "LevelId", level_id)

        _CompOperation = result

    return _CompOperation


def GetCompPostProcess():
    """
    获取 PostProcess 组件（后处理）。

    设计要点：
    - 懒加载 + 缓存；
    - CreatePostProcess(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompPostProcess
    if _CompPostProcess is None:
        level_id = GetLevelId()

        result = CompFactory.CreatePostProcess(level_id)
        _check_create_result("PostProcess", result, "LevelId", level_id)

        _CompPostProcess = result

    return _CompPostProcess


def GetCompGameLevel():
    """
    获取 Game 组件（关卡维度）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateGame(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompGameLevel
    if _CompGameLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateGame(level_id)
        _check_create_result("Game", result, "LevelId", level_id)

        _CompGameLevel = result

    return _CompGameLevel


def GetCompConfigClientLevel():
    """
    获取 ConfigClient 组件（客户端配置）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateConfigClient(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompConfigClientLevel
    if _CompConfigClientLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateConfigClient(level_id)
        _check_create_result("ConfigClient", result, "LevelId", level_id)

        _CompConfigClientLevel = result

    return _CompConfigClientLevel


def GetCompPlayerViewLevel():
    """
    获取 PlayerView 组件（与关卡绑定的视角相关组件）。

    设计要点：
    - 懒加载 + 缓存；
    - CreatePlayerView(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompPlayerViewLevel
    if _CompPlayerViewLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreatePlayerView(level_id)
        _check_create_result("PlayerView", result, "LevelId", level_id)

        _CompPlayerViewLevel = result

    return _CompPlayerViewLevel


def GetCompPlayerLocal():
    """
    获取当前本地玩家对应的 Player 组件。

    设计要点：
    - 与关卡无关，使用 LocalPlayerId 创建；
    - CreatePlayer(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LocalPlayerId。
    """
    global _CompPlayerLocal
    if _CompPlayerLocal is None:
        local_player_id = GetLocalPlayerId()

        result = CompFactory.CreatePlayer(local_player_id)
        _check_create_result("PlayerLocal", result, "LocalPlayerId", local_player_id)

        _CompPlayerLocal = result

    return _CompPlayerLocal


def GetCompSoundLevel():
    """
    获取 CustomAudio 组件（音频）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateCustomAudio(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompSoundLevel
    if _CompSoundLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateCustomAudio(level_id)
        _check_create_result("CustomAudio", result, "LevelId", level_id)

        _CompSoundLevel = result

    return _CompSoundLevel


def GetCompQueryLevel():
    """
    获取 QueryVariable 组件（查询变量 / 状态）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateQueryVariable(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompQueryLevel
    if _CompQueryLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateQueryVariable(level_id)
        _check_create_result("QueryVariable", result, "LevelId", level_id)

        _CompQueryLevel = result

    return _CompQueryLevel


def GetCompBlockGeometryLevel():
    """
    获取 BlockGeometry 组件（方块几何信息）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateBlockGeometry(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompBlockGeometryLevel
    if _CompBlockGeometryLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateBlockGeometry(level_id)
        _check_create_result("BlockGeometry", result, "LevelId", level_id)

        _CompBlockGeometryLevel = result

    return _CompBlockGeometryLevel


def GetCompBlockLevel():
    """
    获取 Block 组件（方块读写相关）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateBlock(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompBlockLevel
    if _CompBlockLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateBlock(level_id)
        _check_create_result("Block", result, "LevelId", level_id)

        _CompBlockLevel = result

    return _CompBlockLevel


def GetCompBlockInfoLevel():
    """
    获取 BlockInfo 组件（方块信息查询）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateBlockInfo(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompBlockInfoLevel
    if _CompBlockInfoLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateBlockInfo(level_id)
        _check_create_result("BlockInfo", result, "LevelId", level_id)

        _CompBlockInfoLevel = result

    return _CompBlockInfoLevel


def GetCompParticleSystem():
    """
    获取 ParticleSystem 组件（粒子系统）。

    设计要点：
    - 原逻辑 CreateParticleSystem(None) 保持不变；
    - 为恢复自动补全：先落 result 变量；
    - 开发期校验失败抛错，提示包含 Arg=None。
    """
    global _CompParticleSystem
    if _CompParticleSystem is None:
        # 先落变量，避免类型在包装函数返回值上丢失
        result = CompFactory.CreateParticleSystem(None)

        _check_create_result("ParticleSystem", result, "Arg", None)

        _CompParticleSystem = result

    return _CompParticleSystem


def GetCompCameraLevel():
    """
    获取 Camera 组件（摄像机）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateCamera(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompCameraLevel
    if _CompCameraLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateCamera(level_id)
        _check_create_result("Camera", result, "LevelId", level_id)

        _CompCameraLevel = result

    return _CompCameraLevel


def GetCompTextNotifyClientLevel():
    """
    获取 TextNotifyClient 组件（文本提示）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateTextNotifyClient(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompTextNotifyClientLevel
    if _CompTextNotifyClientLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateTextNotifyClient(level_id)
        _check_create_result("TextNotifyClient", result, "LevelId", level_id)

        _CompTextNotifyClientLevel = result

    return _CompTextNotifyClientLevel


def GetCompTimeLevel():
    """
    获取 Time 组件（时间相关接口）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateTime(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompTimeLevel
    if _CompTimeLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateTime(level_id)
        _check_create_result("Time", result, "LevelId", level_id)

        _CompTimeLevel = result

    return _CompTimeLevel


def GetCompItemLocalPlayer():
    """
    获取本地玩家的 Item 组件（物品栏 / 物品操作）。

    设计要点：
    - 与关卡无关，使用 LocalPlayerId 创建；
    - CreateItem(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LocalPlayerId。
    """
    global _CompItemLocalPlayer
    if _CompItemLocalPlayer is None:
        local_player_id = GetLocalPlayerId()

        result = CompFactory.CreateItem(local_player_id)
        _check_create_result("ItemLocalPlayer", result, "LocalPlayerId", local_player_id)

        _CompItemLocalPlayer = result

    return _CompItemLocalPlayer


def GetCompTextBoard():
    """
    获取 TextBoard 组件（文本牌子 / 看板）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateTextBoard(...) 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompTextBoard
    if _CompTextBoard is None:
        level_id = GetLevelId()

        result = CompFactory.CreateTextBoard(level_id)
        _check_create_result("TextBoard", result, "LevelId", level_id)

        _CompTextBoard = result

    return _CompTextBoard

_client_main_system_instance = None

# ---------------------------------------------------------------------------
# ClientMainSystem 自动补全辅助
# ---------------------------------------------------------------------------

def GetClientMainSystem():
    """
    这个方法本身没有实际逻辑，仅用于 IDE 代码自动补全：

    - 返回的是模块级的 _client_main_system_instance；
    - 真正的实例由外部通过 SetClientMainSystem 注入；
    - 通过类型注解 / 引用路径，让 IDE 能识别到 ClientMainSystem 上的方法。
    :return: ClientMainSystem
    :rtype: fg_more_crabScripts.client.ClientMainSystem.ClientMainSystem
    """
    return _client_main_system_instance


def SetClientMainSystem(client_main_system):
    """
    由外部在客户端主系统初始化时调用，用于注入 ClientMainSystem 实例。

    设计原因：
    - 不在这里直接创建 ClientMainSystem，而是由上层控制生命周期；
    - 本模块只负责保存引用，给其他地方做自动补全和访问入口。
    """
    global _client_main_system_instance
    _client_main_system_instance = client_main_system



# ===== Mirror Dimension 分配配置（最大玩家=20，Custom池=128）=====
# 维度 ID 对应你生成的配置文件：
# - Overworld: 12469~12488 (20)
# - Nether:    12489~12508 (20)
# - End:       12509~12528 (20)
# - Flat:  12529~12549 (20)
# - Custom池:  12550~12676 (128)
MAX_MIRROR_PLAYERS = 20
OVERWORLD_MIRROR_BASE = 12469
NETHER_MIRROR_BASE = OVERWORLD_MIRROR_BASE + MAX_MIRROR_PLAYERS
END_MIRROR_BASE = NETHER_MIRROR_BASE + MAX_MIRROR_PLAYERS
FLAT_MIRROR_BASE = END_MIRROR_BASE + MAX_MIRROR_PLAYERS

CUSTOM_MIRROR_POOL_BASE = FLAT_MIRROR_BASE + MAX_MIRROR_PLAYERS
CUSTOM_MIRROR_POOL_SIZE = 128


def _build_mirror_dimension_id_list():
    ids = []
    ids.extend(range(OVERWORLD_MIRROR_BASE, OVERWORLD_MIRROR_BASE + MAX_MIRROR_PLAYERS))
    ids.extend(range(NETHER_MIRROR_BASE, NETHER_MIRROR_BASE + MAX_MIRROR_PLAYERS))
    ids.extend(range(END_MIRROR_BASE, END_MIRROR_BASE + MAX_MIRROR_PLAYERS))
    ids.extend(range(FLAT_MIRROR_BASE, FLAT_MIRROR_BASE + MAX_MIRROR_PLAYERS))
    ids.extend(range(CUSTOM_MIRROR_POOL_BASE, CUSTOM_MIRROR_POOL_BASE + CUSTOM_MIRROR_POOL_SIZE))
    return ids


# 注意：这个 list 用于“占用态”(in_use) 管理与合法性校验，不要再拿它做“挑一个 dst 去 Mirror”。
_mirror_dimension_id_list = _build_mirror_dimension_id_list()

def GetDimensionIdIsMirror(dimension_id):
    return dimension_id in _mirror_dimension_id_list

