# -*- coding: utf-8 -*-
from ..ClientBaseUtils import *

def GetHealthPercentage(entity_id):
    """
    获取传入实体的生命值百分比。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 生命值百分比
    :rtype: int or float
    """
    comp_attr=CompFactory.CreateAttr(entity_id)

    health_value = comp_attr.GetAttrValue(MinecraftEnum.AttrType.HEALTH)

    max_health = comp_attr.GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)

    if max_health:
        return health_value/float(max_health)*100.0

    return 0

def GetEntityDir(entity_id):
    """
    获取entity_id的方向

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 方向
    :rtype: tuple[float,float,float] or None
    """
    entity_rot = CompFactory.CreateRot(entity_id).GetRot()
    if entity_rot:
        entity_dir = ClientApi.GetDirFromRot(entity_rot)
        if entity_dir:
            return entity_dir
    return None


def GetEntityCenterPos(entity_id):
    """
    获取entity_id的中间位置

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 中间位置
    :rtype: tuple[float,float,float] or None
    """
    comp_pos = CompFactory.CreatePos(entity_id)
    entity_pos = comp_pos.GetPos()
    entity_foot_pos = comp_pos.GetFootPos()
    if entity_pos is None or entity_foot_pos is None:
        return None
    x1, y1, z1 = entity_pos
    x2, y2, z2 = entity_foot_pos
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0, (z1 + z2) / 2.0

AutoUnlockJumpTimer = None
AutoUnlockAllControlTimer = None

def LockMove(is_lock):
    """
    锁定或解锁实体的移动能力。

    :param is_lock: True表示锁定，False表示解锁
    :type is_lock: bool
    """
    GetCompOperation().SetCanMove(not is_lock)

def LockMoveAndJump(is_lock):
    """
    锁定或解锁实体的移动和跳跃能力。

    :param is_lock: True表示锁定，False表示解锁
    :type is_lock: bool
    """
    global AutoUnlockJumpTimer
    if AutoUnlockJumpTimer:
        GetCompGameLevel().CancelTimer(AutoUnlockJumpTimer)
    GetCompOperation().SetCanMove(not is_lock)
    GetCompOperation().SetCanJump(not is_lock)


def LockMoveAndJumpAndAutoUnlock(un_lock_time=2.0):
    """
    锁定实体的移动和跳跃能力，在un_lock_time之后自动解锁。

    :param un_lock_time: 自动解锁的时间
    :type un_lock_time: float
    """
    LockMoveAndJump(True)
    global AutoUnlockJumpTimer
    if AutoUnlockJumpTimer:
        GetCompGameLevel().CancelTimer(AutoUnlockJumpTimer)
    AutoUnlockJumpTimer = GetCompGameLevel().AddTimer(un_lock_time, LockMoveAndJump, False)


def LockPlayerAllControl(is_lock):
    """
    锁定玩家的所有控制能力

    :param is_lock: True表示锁定，False表示解锁
    :type is_lock: bool
    """
    global AutoUnlockAllControlTimer
    comp_action_motion=CompFactory.CreateActorMotion(GetLocalPlayerId())
    if AutoUnlockAllControlTimer:
        GetCompGameLevel().CancelTimer(AutoUnlockAllControlTimer)
        AutoUnlockAllControlTimer = None
    LockMoveAndJump(is_lock)
    GetCompOperation().SetCanDrag(not is_lock)
    GetCompOperation().SetCanAttack(not is_lock)
    GetCompOperation().SetCanInair(not is_lock)
    GetCompOperation().SetCanPause(not is_lock)
    GetCompOperation().SetCanOpenInv(not is_lock)
    GetCompOperation().SetCanPerspective(not is_lock)
    GetCompOperation().SetCanScreenShot(not is_lock)
    GetCompOperation().SetCanWalkMode(not is_lock)
    GetCompOperation().SetMoveLock(not is_lock)
    if is_lock:
        comp_action_motion.LockInputVector((0, 0))
        comp_action_motion.LockVerticalMove(True)
    else:
        comp_action_motion.UnlockInputVector()
        comp_action_motion.UnLockVerticalMove()


def LockPlayerAllControlAndAutoUnlock(un_lock_time=2.0):
    """
    锁定玩家的所有控制能力，在un_lock_time之后自动解锁。

    :param un_lock_time: 自动解锁的时间
    :type un_lock_time: float or int
    """
    LockPlayerAllControl(True)
    global AutoUnlockAllControlTimer
    if AutoUnlockAllControlTimer:
        GetCompGameLevel().CancelTimer(AutoUnlockAllControlTimer)
        AutoUnlockAllControlTimer = None
    AutoUnlockAllControlTimer = GetCompGameLevel().AddTimer(un_lock_time, LockPlayerAllControl, False)

# <editor-fold desc="实体类型">

def GetEngineType(entity_id):
    """
    获取entity_id的类型

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 类型
    :rtype: int or None
    """
    entity_type = CompFactory.CreateEngineType(entity_id).GetEngineType()
    return entity_type if entity_type else None


def CheckEngineTypeIsSelectType(entity_id, select_type):
    """
    检测entity是否是select_type,注意,此接口不一定能返回正确的结果,例如一个mob可能会属于item,可以用其他方式来判定,例如tag和family

    :param entity_id: 实体ID
    :type: str

    :param select_type: select_type
    :type: MinecraftEnum.EntityType

    :return: 是否是select_type
    :rtype: bool
    """
    return GetEngineType(entity_id) & select_type == select_type


def CheckEntityIsItemEntity(entity_id):
    """
    检查实体是否是ItemEntity
    :param entity_id:entity_id
    :type entity_id: str
    :rtype: bool
    """
    return GetEngineType(entity_id) == MinecraftEnum.EntityType.ItemEntity


def CheckEntityIsXpOrb(entity_id):
    """
    检查实体是否是经验球
    :param entity_id:entity_id
    :type entity_id: str
    :rtype: bool
    """
    return GetEngineType(entity_id) == MinecraftEnum.EntityType.Experience


def CheckEntityIsTntEntity(entity_id):
    """
    检查实体是否是TntEntity
    :param entity_id:entity_id
    :type entity_id: str
    :rtype: bool
    """
    return GetEngineType(entity_id) == MinecraftEnum.EntityType.PrimedTnt


def CheckEntityIsMinecraftTntEntity(entity_id):
    """
    检查实体是否是MinecraftTntEntity
    :param entity_id:entity_id
    :type entity_id: str
    :rtype: bool
    """
    return GetEngineType(entity_id) == MinecraftEnum.EntityType.MinecartTNT


def CheckEntityIsProject(entity_id):
    """
    检查实体是否是Project
    :param entity_id:entity_id
    :type entity_id: str
    :rtype: bool
    """
    return CheckEngineTypeIsSelectType(entity_id, MinecraftEnum.EntityType.Projectile)


def CheckEntityIsMoveBlock(entity_id):
    """
    检查实体是否是MoveBlock
    :param entity_id:entity_id
    :type entity_id: str
    :rtype: bool
    """
    return GetEngineType(entity_id) in [MinecraftEnum.EntityType.FallingBlock, MinecraftEnum.EntityType.MovingBlock]


def CheckEntityIsMob(entity_id):
    """
    获取实体是否是生物
    :param entity_id: entity_id
    :type entity_id: str
    :return: 是否是生物
    :rtype: bool
    """
    return CheckEngineTypeIsSelectType(entity_id, MinecraftEnum.EntityType.Mob)

def _normalize_entity_type_targets(target_types):
    """
    内部工具方法：
    把“单个目标 / 多个目标 / None”统一归一化成一个可迭代的容器，方便主逻辑使用。

    约定：
    - None            -> 返回空 tuple，表示没有任何匹配目标
    - list/tuple/set  -> 原样返回（不复制，交给调用方保证是只读/常量）
    - frozenset       -> 原样返回
    - 其他任意类型     -> 认为是“单个目标”，包装成 (target_types,) 返回
      （包括单个枚举值 int、单个字符串 "minecraft:zombie" 等）
    """
    if target_types is None:
        return ()

    if isinstance(target_types, (list, tuple, set, frozenset)):
        return target_types

    # 注意：str 不在上面的判断里，所以会走到这里，被当成“单个目标”，
    # 这样可以统一兼容单个字符串 / 单个枚举值的写法。
    return (target_types,)


def IsEntityTypeInSet(entity_id, target_types):
    """
    使用按位枚举（GetEngineType）判断实体是否属于给定类型集合中的任意一种。

    :param entity_id: 实体 id（客户端拿到的 entityId）
    :param target_types:
        - 单个 EntityType 枚举值，例如：EntityType.ItemEntity
        - 或可迭代的枚举集合，例如：
          {EntityType.ItemEntity, EntityType.Experience, EntityType.Projectile}
    :return: bool，属于其中任意一种则为 True，否则 False
    """
    engine_type_comp = CompFactory.CreateEngineType(entity_id)
    if engine_type_comp is None:
        # 一般来说正常实体不会为 None，这里防御式写法避免潜在崩溃
        return False

    # 只获取一次类型值，避免在循环中重复访问组件
    entity_type_value = engine_type_comp.GetEngineType()

    # 统一归一化入参，兼容“单个枚举值 / 容器 / None”
    normalized_targets = _normalize_entity_type_targets(target_types)
    if not normalized_targets:
        # 无匹配目标，直接判定为 False
        return False

    # 统一用“按位与”判断：
    # - 对于 Mob / Projectile 这种“类别标志”，& 判断是“是否包含该类别”
    # - 对于 ItemEntity / Experience 这种“具体类型”，因为不会再被 OR 组合，
    #   & 判断退化成“是否等于该值”，语义仍然正确
    #
    # 这样调用方完全不用区分“传进来的是大类还是具体类型”，逻辑统一，
    # 未来如果官方把某个具体类型改成组合型也不用改这里的判断。
    for target_type in normalized_targets:
        if entity_type_value & target_type == target_type:
            return True

    return False


def IsEntityTypeStrIn(entity_id, target_type_names):
    """
    使用 GetEngineTypeStr() 判断某个实体的“类型名称字符串”
    是否属于给定名称集合 / 单个名称。

    :param entity_id: 实体 id（客户端拿到的 entityId）
    :param target_type_names:
        - 单个 str: "minecraft:husk"
        - 或包含若干 str 的容器（set/list/tuple/frozenset）：
          {"minecraft:husk", "minecraft:zombie", ...}
    :return: bool，名称相等则为 True，否则 False
    """
    engine_type_comp = CompFactory.CreateEngineType(entity_id)
    if engine_type_comp is None:
        # 理论上正常实体不会为 None，这里做防御，避免后面调用方法崩掉
        return False

    entity_type_name = engine_type_comp.GetEngineTypeStr()
    if not entity_type_name:
        # 极端情况下拿不到名字（空串 / None），直接视为不匹配
        return False

    # 同样用归一化工具，兼容“单个字符串 / 多个字符串 / None”
    normalized_targets = _normalize_entity_type_targets(target_type_names)
    if not normalized_targets:
        return False

    # 字符串这边是纯等值比较，不做前缀魔改：
    # - 调用方传什么就比什么，规则清晰
    # - 真要支持省略 "minecraft:" 之类前缀，可以在外层再封一层语义方法单独处理
    for type_name in normalized_targets:
        if entity_type_name == type_name:
            return True

    return False

def IsEntityTypeMatch(entity_id, enum_targets=None, name_targets=None):
    """
    实体类型综合判断主方法。

    支持两种维度的匹配：
    1. 按枚举（位标志）匹配：通过 GetEngineType() + bitmask 判断
    2. 按字符串名称匹配：通过 GetEngineTypeStr() 判断

    只要其中任意一个维度匹配，就返回 True。

    :param entity_id: 实体 id（客户端拿到的 entityId）

    :param enum_targets:
        - 单个 EntityType 枚举值：
            EntityTypeEnum.Projectile
        - 或可迭代的枚举集合：
            {EntityTypeEnum.ItemEntity, EntityTypeEnum.Experience, ...}
        - 为 None 时表示“忽略枚举维度判断”

    :param name_targets:
        - 单个 str：
            "minecraft:husk"
        - 或包含若干 str 的容器（set / list / tuple / frozenset）：
            {"minecraft:husk", "minecraft:zombie", ...}
        - 为 None 时表示“忽略名称维度判断”

    :return: bool，只要某一维度命中任意一个目标就为 True，否则 False。
    """

    
    # 两个都没给，等价于“没有任何判定条件”，直接 False
    if enum_targets is None and name_targets is None:
        return False

    # 先按枚举位标志检查
    if enum_targets is not None:
        if IsEntityTypeInSet(entity_id, enum_targets):
            return True

    # 再按字符串名称检查
    if name_targets is not None:
        if IsEntityTypeStrIn(entity_id, name_targets):
            return True

    return False

# </editor-fold>