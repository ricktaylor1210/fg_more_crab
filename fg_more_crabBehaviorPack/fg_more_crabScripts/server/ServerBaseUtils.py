# -*- coding: utf-8 -*-
from collections import deque

from ..ModMainConfig import *
import mod.server.extraServerApi as ServerApi
import mod.common.minecraftEnum as MinecraftEnum

from fg_more_crabScripts.utils.singleton import singleton

# ServerSystem
ServerSystem = ServerApi.GetServerSystemCls()
ServerEngineNameSpace = ServerApi.GetEngineNamespace()
ServerEngineSystemName = ServerApi.GetEngineSystemName()

# 0：Windows平台；1：IOS；2：Android；-1：其他，例如联机大厅，阿波罗等linux服务器
PlatForm = ServerApi.GetPlatform()

# LevelId 延迟初始化（避免导入阶段取不到有效值）
# 使用前缀下划线标记为模块内部实现，外部只通过 GetLevelId() 访问。
_LevelId = None

# 工厂本身与关卡无强依赖，可以在导入时拿一次并缓存。
CompFactory = ServerApi.GetEngineCompFactory()

# 所有组件先置为 None，占位以便 IDE 补全 & 惰性初始化。
# 统一使用前缀下划线，避免在其它模块自动补全时被误用。
_CompGameLevel = None
_CompExtraDataLevel = None
_CompBlockInfoLevel = None
_CompBlockEntityLevel = None
_CompExplosionLevel = None
_CompProjectileLevel = None
_CompCommandLevel = None
_CompItemLevel = None
_CompTimeLevel = None
_CompWeatherLevel = None
_CompDimensionLevel = None
_CompChunkSourceLevel = None


def GetLevelId():
    """
    每次调用从 ServerApi 获取最新 LevelId，并写入模块级缓存。

    设计原因：
    - 不在导入阶段绑定 LevelId，避免早期调用拿到无效数据；
    - 缓存到 _LevelId，方便调试时查看最近一次的关卡 Id。
    """
    global _LevelId
    _LevelId = ServerApi.GetLevelId()
    return _LevelId



def _check_create_result(component_name, result, key_name, key_value):
    """
    内部工具函数：统一处理组件创建结果。

    设计原因：
    - 把所有组件创建失败的处理逻辑集中到一处，避免每个 Getter 里都写一遍 if result is None。
    - 开发环境 (IN_DEVELOPMENT=True) 时，创建失败直接抛 RuntimeError，
      防止问题被静默吞掉，方便在测试阶段尽早发现配置 / 调用错误。
    - 非开发环境下，不强行中断流程，原样返回 result（可能为 None），
      交给上层逻辑决定是否以及如何兜底处理。
    """
    if result is None and IN_DEVELOPMENT:
        raise RuntimeError(
            "%s creation failed, %s=%r" % (component_name, key_name, key_value)
        )
    return result


def GetCompGameLevel():
    """
    获取 Game 组件（关卡级别）。

    设计要点：
    - 使用 _CompGameLevel 做懒加载缓存；
    - 先把 CreateGame 的返回值落到一个变量上，IDE/语言服务器能沿着赋值推断类型，从而恢复自动补全；
    - 开发期校验：创建失败直接抛 RuntimeError，错误信息包含关键入参，便于定位。
    """
    global _CompGameLevel
    if _CompGameLevel is None:
        level_id = GetLevelId()

        # 先把 CreateGame 的返回值落到一个变量上，IDE/语言服务器能沿着这个赋值推断出类型，从而自动补全
        result = CompFactory.CreateGame(level_id)

        # 做开发期校验
        _check_create_result("Game", result, "LevelId", level_id)

        _CompGameLevel = result

    return _CompGameLevel


def GetCompExtraDataLevel():
    """
    获取 ExtraData 组件（附加数据读写）。

    设计要点：
    - 使用 _CompExtraDataLevel 做懒加载缓存；
    - 先落到 result 变量上以恢复 IDE 自动补全；
    - 开发期校验失败会抛错（包含 LevelId）。
    """
    global _CompExtraDataLevel
    if _CompExtraDataLevel is None:
        level_id = GetLevelId()

        # 先把 CreateExtraData 的返回值落到一个变量上, IDE/语言服务器能沿着这个赋值推断出类型，从而自动补全
        result = CompFactory.CreateExtraData(level_id)

        # 做开发期校验
        _check_create_result("ExtraData", result, "LevelId", level_id)

        _CompExtraDataLevel = result

    return _CompExtraDataLevel


def GetCompBlockInfoLevel():
    """
    获取 BlockInfo 组件（方块信息查询）。

    设计要点：
    - 懒加载 + 缓存；
    - CreateBlockInfo 先落本地变量，保证语言服务器可推断类型；
    - 开发期创建失败抛错，提示包含 LevelId。
    """
    global _CompBlockInfoLevel
    if _CompBlockInfoLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateBlockInfo(level_id)
        _check_create_result("BlockInfo", result, "LevelId", level_id)

        _CompBlockInfoLevel = result

    return _CompBlockInfoLevel


def GetCompBlockEntityLevel():
    """
    获取 BlockEntity 组件（方块实体相关操作）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompBlockEntityLevel
    if _CompBlockEntityLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateBlockEntity(level_id)
        _check_create_result("BlockEntity", result, "LevelId", level_id)

        _CompBlockEntityLevel = result

    return _CompBlockEntityLevel


def GetCompExplosionLevel():
    """
    获取 Explosion 组件（爆炸相关逻辑）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompExplosionLevel
    if _CompExplosionLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateExplosion(level_id)
        _check_create_result("Explosion", result, "LevelId", level_id)

        _CompExplosionLevel = result

    return _CompExplosionLevel


def GetCompProjectileLevel():
    """
    获取 Projectile 组件（投射物相关逻辑）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompProjectileLevel
    if _CompProjectileLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateProjectile(level_id)
        _check_create_result("Projectile", result, "LevelId", level_id)

        _CompProjectileLevel = result

    return _CompProjectileLevel


def GetCompCommandLevel():
    """
    获取 Command 组件（命令执行相关）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompCommandLevel
    if _CompCommandLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateCommand(level_id)
        _check_create_result("Command", result, "LevelId", level_id)

        _CompCommandLevel = result

    return _CompCommandLevel


def GetCompItemLevel():
    """
    获取 Item 组件（物品相关操作，服务端关卡维度）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompItemLevel
    if _CompItemLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateItem(level_id)
        _check_create_result("Item", result, "LevelId", level_id)

        _CompItemLevel = result

    return _CompItemLevel


def GetCompTimeLevel():
    """
    获取 Time 组件（时间控制）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompTimeLevel
    if _CompTimeLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateTime(level_id)
        _check_create_result("Time", result, "LevelId", level_id)

        _CompTimeLevel = result

    return _CompTimeLevel


def GetCompWeatherLevel():
    """
    获取 Weather 组件（天气控制）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompWeatherLevel
    if _CompWeatherLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateWeather(level_id)
        _check_create_result("Weather", result, "LevelId", level_id)

        _CompWeatherLevel = result

    return _CompWeatherLevel


def GetCompDimensionLevel():
    """
    获取 Dimension 组件（维度 / 世界相关操作）。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompDimensionLevel
    if _CompDimensionLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateDimension(level_id)
        _check_create_result("Dimension", result, "LevelId", level_id)

        _CompDimensionLevel = result

    return _CompDimensionLevel


def GetCompChunkSourceLevel():
    """
    获取 ChunkSource 组件。

    设计要点：
    - 懒加载 + 缓存；
    - 先落变量以恢复自动补全；
    - 开发期校验失败抛错，提示包含 LevelId。
    """
    global _CompChunkSourceLevel
    if _CompChunkSourceLevel is None:
        level_id = GetLevelId()

        result = CompFactory.CreateChunkSource(level_id)
        _check_create_result("ChunkSource", result, "LevelId", level_id)

        _CompChunkSourceLevel = result

    return _CompChunkSourceLevel


_server_main_system_instance = None


def GetServerMainSystem():
    """
    这个方法本身没有实际业务逻辑，只用于：
    - 为 IDE 提供 ServerMainSystem 的代码自动补全入口；
    - 对外统一获取服务端主系统实例的方式。

    :return: ServerMainSystem
    :rtype: fg_more_crabScripts.server.ServerMainSystem.ServerMainSystem
    """
    return _server_main_system_instance


def SetServerMainSystem(server_main_system):
    """
    由上层在 ServerMainSystem 初始化完成后调用，用于注入实例。

    设计原因：
    - 生命周期仍由主系统控制，这里只负责保存引用；
    - 避免在这里直接 new，保持模块职责单一。
    """
    global _server_main_system_instance
    _server_main_system_instance = server_main_system



def DoProfile(second):
    ServerApi.StartProfile()

    def finishProfile():
        timestamp = int(time.time())
        filename = "profile_%d.svg" % timestamp
        ServerApi.StopProfile(filename)

    comp = ServerApi.GetEngineCompFactory().CreateGame(ServerApi.GetLevelId())
    comp.AddTimer(second, finishProfile)


def DoProfileEvent(second):
    ServerApi.StartRecordEvent()

    def finishProfile():
        result = ServerApi.StopRecordEvent()
        for eventName, data in result.iteritems():
            head = "event[{}]".format(eventName)
            head = head.ljust(20)
            SetDevelopmentMessage(logging.INFO, "{} sendNum={} sendSize={} recvNum={} recvSize={}", head, data["send_num"], data["send_size"],
                                  data["recv_num"], data["recv_size"])

    comp = ServerApi.GetEngineCompFactory().CreateGame(ServerApi.GetLevelId())
    comp.AddTimer(second, finishProfile)


def DoProfilePacket(second):
    ServerApi.StartRecordPacket()

    def finishProfile():
        result = ServerApi.StopRecordPacket()
        for packetName, data in result.iteritems():
            head = "packet[{}]".format(packetName)
            head = head.ljust(20)
            SetDevelopmentMessage(logging.INFO, "{} sendNum={} sendSize={} recvNum={} recvSize={}", head, data["send_num"], data["send_size"],
                                  data["recv_num"], data["recv_size"])

    comp = ServerApi.GetEngineCompFactory().CreateGame(ServerApi.GetLevelId())
    comp.AddTimer(second, finishProfile)



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
_in_use_mirror_dimension_id_list = []


# ====== 玩家 slot + Custom 独占映射（按 (player_id, src_custom_dim)）======
# 设计要点：
# - Overworld/Nether/End：每玩家固定 3 个镜像维度（用 slot 公式计算），天然隔离
# - Custom：共享一个 128 的目标维度池，但分配粒度是 (player, src_custom_dim) → dst_dim
#   因此玩家 A/B 的 custom(7) 会拿到不同 dst，互不污染；不用到 custom 的玩家不占资源

_player_slot_by_player_id = {}          # player_id -> slot [0..MAX_MIRROR_PLAYERS-1]
_slot_in_use_flags = [False] * MAX_MIRROR_PLAYERS

_custom_key_to_mirror_id = {}           # (player_id, src_custom_dim) -> dst_dim
_custom_mirror_id_to_key = {}           # dst_dim -> (player_id, src_custom_dim)  反查，便于排错
_custom_free_pool = deque(range(CUSTOM_MIRROR_POOL_BASE, CUSTOM_MIRROR_POOL_BASE + CUSTOM_MIRROR_POOL_SIZE))

_custom_lru_by_player_id = {}           # player_id -> [key0(oldest), ..., keyN(newest)]

_initialized_mirror_dst_set = set()     # 本次开服周期内，哪些 dst_dim 已经 MirrorDimension 初始化过
# ===== MirrorDimension 初始化失败容错 =====
# 设计原因：
# - 你已经遇到：dst_dim 在一次开服周期内 MirrorDimension 只能成功一次，甚至可能首次也失败（引擎/配置/源维度特殊）
# - 我们的目标：失败时不要卡死技能；至少保证后续 palette 覆盖写入 + 传送还能跑
_mirror_init_failed_dst_set = set()

# mirror id 集合，用于快速判断“这个维度是不是我们镜像体系里的”
# 注意：_mirror_dimension_id_list 是启动后固定不变的（你配置文件固定），所以 set 可以常驻
_mirror_dimension_id_set = set(_mirror_dimension_id_list)


def IsFlatDimension(dimension_id,pos):
    int_pos=ServerApi.GetIntPos(pos)

    comp_chunk_level = GetCompChunkSourceLevel()

    chunk_pos = comp_chunk_level.GetChunkPosFromBlockPos(int_pos)

    chunk_min_pos = comp_chunk_level.GetChunkMinPos(chunk_pos)
    chunk_max_pos = comp_chunk_level.GetChunkMaxPos(chunk_pos)

    for x in range(chunk_min_pos[0],chunk_max_pos[0]):
        for z in range(chunk_min_pos[2],chunk_min_pos[2]):
            check_pos=(x,-64,z)
            block_dict=GetCompBlockInfoLevel().GetBlockNew(check_pos, dimension_id)
            if block_dict:
                if block_dict.get("name", None)!="minecraft:bedrock":
                    return False
            return False
    return True


def WasMirrorDimensionInitFailed(mirror_dimension_id):
    if mirror_dimension_id is None:
        return False
    return int(mirror_dimension_id) in _mirror_init_failed_dst_set


def IsMirrorDimensionId(dimension_id):
    if dimension_id is None:
        return False
    return int(dimension_id) in _mirror_dimension_id_set


def EnsurePlayerSlotAllocated(player_id):
    """
    给玩家预先占一个 slot。
    设计原因：
    - 你要做“禁止进入别人镜像维度”，那就必须在玩家触发维度变化时能立刻知道他自己的 3 个固定镜像维度。
    """
    return _allocate_player_slot(player_id) is not None


def IsPlayerAllowedInMirrorDimension(player_id, dimension_id):
    """
    权限隔离：
    - 非镜像维度：永远允许
    - 镜像维度：
      - fixed(0/1/2)：只允许该玩家自己的 slot 对应 3 个维度
      - custom：只允许该玩家当前已分配到的 custom dst
    """
    if not IsMirrorDimensionId(dimension_id):
        return True

    slot = _allocate_player_slot(player_id)
    if slot is None:
        # 超过 MAX_MIRROR_PLAYERS 的玩家，不应该进入任何镜像维度
        return False

    dim_id = int(dimension_id)
    if dim_id == OVERWORLD_MIRROR_BASE + slot:
        return True
    if dim_id == NETHER_MIRROR_BASE + slot:
        return True
    if dim_id == END_MIRROR_BASE + slot:
        return True
    if dim_id == FLAT_MIRROR_BASE + slot:
        return True

    # custom：检查 (player_id, src_custom_dim) 映射的值里是否包含这个 dst
    for (pid, _src_dim), dst_dim in _custom_key_to_mirror_id.iteritems():
        if pid == player_id and int(dst_dim) == dim_id:
            return True

    return False


def ReallocateCustomMirrorDimensionId(player_id, src_custom_dimension_id):
    """
    custom 专用：当某个 dst 初始化 MirrorDimension 一直失败时，把这个 key 换绑到池里的另一个 dst。
    设计取舍：
    - 只对 custom 做，因为 custom 有 pool；fixed 没有候选就只能“容错降级为 palette-only”
    - 释放旧 dst 回池：dst 本次开服不再 MirrorDimension，只靠 palette 覆盖刷新，复用不会破坏一致性
    """
    key = (player_id, int(src_custom_dimension_id))

    old_mirror_id = _custom_key_to_mirror_id.get(key)
    if old_mirror_id is not None:
        _custom_key_to_mirror_id.pop(key, None)
        _custom_mirror_id_to_key.pop(old_mirror_id, None)
        _custom_free_pool.append(old_mirror_id)

        # LRU 移除该 key（避免残留导致“抢占错误对象”）
        lru = _custom_lru_by_player_id.get(player_id) or []
        try:
            lru.remove(key)
        except ValueError:
            pass

    return GetOrAllocateCustomMirrorDimensionId(player_id, src_custom_dimension_id)


def EnsureMirrorDimensionInitialized(dimension_level_comp, src_dimension_id, mirror_dimension_id, allow_degrade_to_palette=True):
    """
    dst_dim 在“本次开服周期”只 MirrorDimension 一次。

    容错策略：
    - 若 MirrorDimension 失败：
      - 记录到 _mirror_init_failed_dst_set
      - 如果 allow_degrade_to_palette=True：返回 True（继续走 palette 覆盖写入），避免技能硬失败
      - 否则返回 False（由上层决定怎么兜底）
    """
    if mirror_dimension_id is None:
        return False

    mirror_dimension_id = int(mirror_dimension_id)

    # 已初始化 or 已确认 init 失败：都不再重复 MirrorDimension
    if mirror_dimension_id in _initialized_mirror_dst_set:
        return True
    if mirror_dimension_id in _mirror_init_failed_dst_set:
        return True

    res = dimension_level_comp.MirrorDimension(int(src_dimension_id), mirror_dimension_id)
    if not res:
        _mirror_init_failed_dst_set.add(mirror_dimension_id)
        return bool(allow_degrade_to_palette)

    _initialized_mirror_dst_set.add(mirror_dimension_id)
    return True


def _touch_custom_key(player_id, key):
    """更新该玩家的 custom LRU（避免 full-pool 时只能全服硬失败）"""
    lru = _custom_lru_by_player_id.setdefault(player_id, [])
    try:
        lru.remove(key)
    except ValueError:
        pass
    lru.append(key)


def _allocate_player_slot(player_id):
    """懒分配 slot：第一次需要镜像维度时分配；服务器应在玩家离线时释放。"""
    if player_id in _player_slot_by_player_id:
        return _player_slot_by_player_id[player_id]

    for slot_idx, used in enumerate(_slot_in_use_flags):
        if used:
            continue
        _slot_in_use_flags[slot_idx] = True
        _player_slot_by_player_id[player_id] = slot_idx
        return slot_idx

    # 超过 MAX_MIRROR_PLAYERS：不给镜像维度，调用方需要兜底（例如禁用技能/降级共享）
    return None


def ReleasePlayerMirrorResources(player_id):
    """玩家离线时调用：释放 slot & custom 映射，避免 custom 池被长时间占满。"""
    # 释放 slot
    slot = _player_slot_by_player_id.pop(player_id, None)
    if slot is not None and 0 <= slot < len(_slot_in_use_flags):
        _slot_in_use_flags[slot] = False

    # 释放 custom 映射（注意：dst_dim 不再 Mirror，只会被 palette 覆盖刷新；归还到池中可复用）
    keys_to_remove = [k for k in _custom_key_to_mirror_id.keys() if k[0] == player_id]
    for key in keys_to_remove:
        mirror_id = _custom_key_to_mirror_id.pop(key, None)
        if mirror_id is None:
            continue
        _custom_mirror_id_to_key.pop(mirror_id, None)
        _custom_free_pool.append(mirror_id)

    _custom_lru_by_player_id.pop(player_id, None)
    return True


def GetPlayerFixedMirrorDimensionId(player_id, src_dimension_id, is_flat_src=False):
    """Overworld/Flat/Nether/End：每玩家固定 4 个镜像维度（slot 公式）。"""
    slot = _allocate_player_slot(player_id)
    if slot is None:
        return None

    if src_dimension_id == 0:
        if is_flat_src:
            return FLAT_MIRROR_BASE + slot
        return OVERWORLD_MIRROR_BASE + slot
    if src_dimension_id == 1:
        return NETHER_MIRROR_BASE + slot
    if src_dimension_id == 2:
        return END_MIRROR_BASE + slot
    return None


def GetOrAllocateCustomMirrorDimensionId(player_id, src_custom_dimension_id):
    """Custom：按 (player_id, src_custom_dim) 独占分配 dst。"""
    key = (player_id, int(src_custom_dimension_id))
    existing = _custom_key_to_mirror_id.get(key)
    if existing is not None:
        _touch_custom_key(player_id, key)
        return existing

    mirror_id = None
    if _custom_free_pool:
        mirror_id = _custom_free_pool.popleft()
    else:
        # 池满：优先抢占“该玩家自己”最久未用的 custom 映射，避免一个玩家把全服池吃光
        lru = _custom_lru_by_player_id.get(player_id) or []
        if lru:
            old_key = lru.pop(0)
            mirror_id = _custom_key_to_mirror_id.pop(old_key, None)
            if mirror_id is not None:
                _custom_mirror_id_to_key.pop(mirror_id, None)

    if mirror_id is None:
        return None

    _custom_key_to_mirror_id[key] = mirror_id
    _custom_mirror_id_to_key[mirror_id] = key
    _touch_custom_key(player_id, key)
    return mirror_id


def GetOrAllocateMirrorDimensionIdForPlayer(player_id, src_dimension_id, is_flat_src=False):
    """统一入口：根据 src_dimension_id 选择 fixed or custom。"""
    fixed_id = GetPlayerFixedMirrorDimensionId(player_id, src_dimension_id, is_flat_src=is_flat_src)
    if fixed_id is not None:
        return fixed_id
    return GetOrAllocateCustomMirrorDimensionId(player_id, src_dimension_id)

def _build_in_use_id_set():
    """
    用 set 加速 membership 判断。
    注意：这里每次从 list 生成 set，保证即使外部直接改了 list，也不会出现状态不同步。
    """
    if not _in_use_mirror_dimension_id_list:
        return set()
    return set(_in_use_mirror_dimension_id_list)


def GetFirstUnUsedMirrorDimensionId():
    """
    1) 获取索引最前面的未使用 id
    找不到则返回 None
    """
    if not _mirror_dimension_id_list:
        return None

    in_use_id_set = _build_in_use_id_set()
    for mirror_id in _mirror_dimension_id_list:
        if mirror_id not in in_use_id_set:
            return mirror_id
    return None


def IsMirrorDimensionIdInUse(mirror_dimension_id):
    """
    2) 判断一个 id 是否已使用
    """
    if mirror_dimension_id is None:
        return False
    return mirror_dimension_id in _build_in_use_id_set()


def SetMirrorDimensionIdInUse(mirror_dimension_id):
    """
    3) 设置一个 id 正在使用中
    - id 不在 _mirror_dimension_id_list 中：返回 False
    - 已在使用中：返回 True（幂等）
    - 成功加入：返回 True
    """
    if mirror_dimension_id is None:
        return False
    if mirror_dimension_id not in _mirror_dimension_id_list:
        return False
    if IsMirrorDimensionIdInUse(mirror_dimension_id):
        return True

    _in_use_mirror_dimension_id_list.append(mirror_dimension_id)
    return True


def DeleteMirrorDimensionInUseId(mirror_dimension_id):
    """
    4) 删除一个正在使用中的 id
    - 不存在：返回 False
    - 删除成功：返回 True
    """
    if mirror_dimension_id is None:
        return False
    if not _in_use_mirror_dimension_id_list:
        return False

    # 只移除一次；如果你希望移除所有重复项，把 break 去掉即可
    for idx, used_id in enumerate(_in_use_mirror_dimension_id_list):
        if used_id == mirror_dimension_id:
            del _in_use_mirror_dimension_id_list[idx]
            return True
    return False


def DeleteAllMirrorDimensionInUseIds():
    """
    5) 删除所有正在使用的 id
    """
    # 用切片清空，保持 list 对象本身不变（外部引用也能看到更新）
    del _in_use_mirror_dimension_id_list[:]

def GetDimensionIdIsMirror(dimension_id):
    return dimension_id in _mirror_dimension_id_list
