# -*- coding: utf-8 -*-
import time

from ..ServerBaseUtils import *


def SetEntityHealthByDiff(entity_id, diff_health):
    """
    根据差值设置实体的生命值

    :param entity_id: 实体ID
    :type entity_id: str

    :param diff_health: diff_health
    :type diff_health: int | float

    :return: 设置结果
    :rtype: bool
    """
    comp_attr = CompFactory.CreateAttr(entity_id)
    current_health = comp_attr.GetAttrValue(MinecraftEnum.AttrType.HEALTH)
    new_health = current_health + diff_health
    return comp_attr.SetAttrValue(MinecraftEnum.AttrType.HEALTH, new_health,0)


def SetCurrentAirSupplyByDiff(entity_id, diff):
    """
    根据传入的氧气差值调整当前氧气值

    :param entity_id: 实体ID
    :type entity_id: str

    :param diff: 要调整的氧气差值，正数增加氧气，负数减少氧气
    :type diff: int

    :return: 设置结果
    :rtype: bool
    """
    comp_breath = CompFactory.CreateBreath(entity_id)
    current_air_supply = comp_breath.GetCurrentAirSupply()
    new_air_supply = current_air_supply + diff

    # 确保新氧气值不会超过最大值或低于0
    max_air_supply = comp_breath.GetMaxAirSupply()
    new_air_supply = max(0, min(new_air_supply, max_air_supply))

    return comp_breath.SetCurrentAirSupply(new_air_supply)


# <editor-fold desc="effect">

def GetEntityEffectsLevel(entity_id, effect_name):
    """
    获取实体当前状态效果的等级

    :param entity_id: 实体ID
    :type entity_id: str

    :param effect_name: 状态效果名称字符串, 包括自定义状态效果和原版状态效果, 原版状态效果可在wiki查询
    :type effect_name: str

    :return: 返回实体当前状态效果的等级

    :rtype: int or None
    """
    comp_effect = CompFactory.CreateEffect(entity_id)
    if not comp_effect.HasEffect(effect_name):
        return None
    all_effects = comp_effect.GetAllEffects()
    for effect_dict in all_effects:
        if effect_name != effect_dict["effectName"]:
            continue
        return effect_dict["amplifier"]
    else:
        return None


def AddEffectList(entity_id, effect_list):
    """
    为指定实体添加一组效果（effect_list）。

    :param entity_id: 实体的唯一标识符
    :type entity_id: str

    :param effect_list: 要添加的效果列表，每个效果通过字典定义。字典包含以下键：
        - effect_name: 效果名称
        - effect_time: 效果持续时间
        - effect_level: 效果等级
        - can_show_particle: 是否显示粒子效果（可选，默认为True）
    :type effect_list: list[dict]

    该方法遍历effect_list中的每个效果字典，并将其效果添加到指定实体上。
    """
    comp_effect = CompFactory.CreateEffect(entity_id)
    for effect_dict in effect_list:
        comp_effect.AddEffectToEntity(effect_dict["effect_name"], effect_dict["effect_time"],
                                      effect_dict["effect_level"],
                                      effect_dict.get("can_show_particle", True))


# </editor-fold>


def CheckEntityIsPlayer(entity_id):
    """
    检测传入的entity_id是否是玩家

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 是否是玩家
    :rtype: bool
    """
    return entity_id in ServerApi.GetPlayerList()


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


def GetEntityHeadPos(entity_id):
    """
    获取entity_id的头部位置

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 头部位置
    :rtype: tuple[float,float,float] or None
    """
    comp_pos = CompFactory.CreatePos(entity_id)
    size = CompFactory.CreateCollisionBox(entity_id).GetSize()
    entity_foot_pos = comp_pos.GetFootPos()
    if size is None or entity_foot_pos is None:
        return None
    x1, y1, z1 = entity_foot_pos
    return x1, y1 + size[1], z1


def GetEntityDimensionId(entity_id):
    """
    获取entity_id的dimension

    :param entity_id: 实体ID
    :type entity_id: str

    :return: dimension
    """
    return CompFactory.CreateDimension(entity_id).GetEntityDimensionId()


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
        entity_dir = ServerApi.GetDirFromRot(entity_rot)
        if entity_dir:
            return entity_dir
    return None


def GetHealthValue(entity_id):
    """
    获取传入实体的生命值。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 生命值
    :rtype: int or float
    """
    health_value = CompFactory.CreateAttr(entity_id).GetAttrValue(MinecraftEnum.AttrType.HEALTH)
    return health_value


def GetHealthPercentage(entity_id):
    """
    获取传入实体的生命值百分比。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 生命值百分比
    :rtype: int or float
    """
    comp_attr = CompFactory.CreateAttr(entity_id)

    health_value = comp_attr.GetAttrValue(MinecraftEnum.AttrType.HEALTH)

    max_health = comp_attr.GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)

    if max_health:
        return health_value / float(max_health) * 100.0

    return 0


def GetHealthValueByPercentage(entity_id, percentage):
    """
    获取传入百分比占实体最大生命值的生命值。

    :param entity_id: 实体ID
    :type entity_id: str

    :param percentage: 百分比
    :type percentage: float

    :return: 生命值对应的实际值
    :rtype: float
    """
    max_health = CompFactory.CreateAttr(entity_id).GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)

    if max_health is None or max_health == 0:
        return 0

    health_value = (percentage / 100.0) * max_health
    return health_value


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
def CheckEntityIsNPC(entity_id):
    """
    检查实体是否是NPC
    :param entity_id:entity_id
    :type entity_id: str
    :rtype: bool
    """
    return GetEngineType(entity_id) == MinecraftEnum.EntityType.Npc


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


def IsEntityFamilyMatch(entity_id, family_targets):
    """
    使用 Attr 组件的 GetTypeFamily() 判断：
    实体是否处于给定 family_type / family_type_list 中的任意一个。

    :param entity_id: 实体 id（客户端拿到的 entityId）
    :param family_targets:
        - 单个 str，例如："cow" / "mob"
        - 或包含若干 family 名的容器（set/list/tuple/frozenset），例如：
          {"cow", "mob", "animal"}
    :return: bool，只要命中任意一个 family 即为 True，否则 False
    """
    attr_comp = CompFactory.CreateAttr(entity_id)
    if attr_comp is None:
        # 没有 Attr 组件，直接视为不匹配
        return False

    type_family_list = attr_comp.GetTypeFamily() or []
    if not type_family_list:
        # 没有任何 family 信息，直接失败
        return False

    normalized_targets = _normalize_entity_type_targets(family_targets)
    if not normalized_targets:
        # 没有目标 family，视为不匹配
        return False

    # 转成 set，加快后续查找
    type_family_set = set(type_family_list)

    for family_name in normalized_targets:
        if family_name in type_family_set:
            return True

    return False


def IsEntityTagMatch(entity_id, tag_targets, match_all=False):
    """
    使用 Tag 组件判断实体是否包含给定的标签（任一/全部）。

    内部只调用一次 GetEntityTags() 拿到标签列表，然后在 Python 里做匹配，
    避免在循环里频繁调用 EntityHasTag。

    :param entity_id: 实体 id（客户端拿到的 entityId）
    :param tag_targets:
        - 单个 str，例如："AAA"
        - 或包含若干标签名的容器（set/list/tuple/frozenset），例如：
          {"AAA", "BBB"}
    :param match_all:
        - False（默认）：只要实体拥有其中“任意一个”标签就返回 True
        - True：要求实体同时拥有“所有给定标签”才返回 True
    :return: bool，根据 match_all 模式返回是否匹配
    """
    tag_comp = CompFactory.CreateTag(entity_id)
    if tag_comp is None:
        # 没有 Tag 组件，直接视为没有任何标签
        return False

    entity_tags = tag_comp.GetEntityTags() or []
    if not entity_tags:
        # 实体本身没有标签列表，直接失败
        return False

    normalized_targets = _normalize_entity_type_targets(tag_targets)
    if not normalized_targets:
        # 没有要匹配的标签，视为不匹配（避免“空条件”误判为 True）
        return False

    entity_tag_set = set(entity_tags)

    if match_all:
        # 要求“全部命中”：有一个缺失就失败
        for tag_name in normalized_targets:
            if tag_name not in entity_tag_set:
                return False
        return True
    else:
        # 要求“任一命中”：有一个存在就成功
        for tag_name in normalized_targets:
            if tag_name in entity_tag_set:
                return True
        return False


def IsEntityTypeMatch(entity_id, enum_targets=None, name_targets=None):
    """
    为兼容旧调用保留的类型匹配方法，
    实际转发到 IsEntityMatch，只使用 enum/name 两个维度。
    """
    return IsEntityMatch(
        entity_id,
        enum_targets=enum_targets,
        name_targets=name_targets
    )


def IsEntityMatch(
        entity_id,
        enum_targets=None,
        name_targets=None,
        family_targets=None,
        tag_targets=None,
        tag_match_all=False
):
    """
    实体类型综合判断主方法。

    按“维度”划分支持 4 种判断方式：
    1. 类型枚举（位标志）：    enum_targets   -> IsEntityTypeInSet
    2. 类型名称字符串：         name_targets   -> IsEntityTypeStrIn
    3. type family：           family_targets -> IsEntityFamilyMatch
    4. tag 标签（任一/全部）： tag_targets    -> IsEntityTagMatch

    只要其中任意一个维度匹配，就返回 True。

    :param entity_id: 实体 id（客户端拿到的 entityId）

    :param enum_targets:
        - 单个 EntityType 枚举值
        - 或枚举集合（set/list/tuple/frozenset）
        - None 表示不使用“枚举类型”维度判断

    :param name_targets:
        - 单个 str（例如 "minecraft:husk"）
        - 或字符串集合
        - None 表示不使用“类型名称”维度判断

    :param family_targets:
        - 单个 str（例如 "cow" / "mob"）
        - 或字符串集合
        - None 表示不使用“family” 维度判断

    :param tag_targets:
        - 单个 str（例如 "AAA"）
        - 或字符串集合
        - None 表示不使用“标签”维度判断

    :param tag_match_all:
        - False（默认）：任一标签命中即可
        - True：要求实体包含 tag_targets 中的所有标签

    :return: bool，只要某一维度命中任意一个目标就为 True，否则 False。
    """
    # 所有条件都没给，等价于“没有任何判定条件”
    if (
            enum_targets is None
            and name_targets is None
            and family_targets is None
            and tag_targets is None
    ):
        return False

    # 类型枚举（位掩码）判断
    if enum_targets is not None:
        if IsEntityTypeInSet(entity_id, enum_targets):
            return True

    # 类型名称字符串判断
    if name_targets is not None:
        if IsEntityTypeStrIn(entity_id, name_targets):
            return True

    # family 判断
    if family_targets is not None:
        if IsEntityFamilyMatch(entity_id, family_targets):
            return True

    # tag 判断（任一 / 全部）
    if tag_targets is not None:
        if IsEntityTagMatch(entity_id, tag_targets, match_all=tag_match_all):
            return True

    return False


# </editor-fold>


def GetAllComponentsName(entity_id):
    """
    获取实体所拥有的原版组件list
    :param entity_id: 实体ID
    :type entity_id: str

    :return: 原版组件名list，EntityComponentType枚举
    :rtype: list[str] or None
    """
    all_components = CompFactory.CreateEntityComponent(entity_id).GetAllComponentsName()
    return all_components if all_components else None


def CheckEntityHasComponents(entity_id, component_name):
    """
    获取实体是否拥有的需要检测的原版组件
    :param entity_id: 实体ID
    :type entity_id: str
    :param component_name:component_name
    :type component_name:str or int
    :return: 是否拥有
    :rtype: bool
    """
    if isinstance(component_name, str):
        entity_component = GetAllComponentsName(entity_id)
        return component_name in entity_component if entity_component else False
    elif isinstance(component_name, int):
        return CompFactory.CreateEntityComponent(entity_id).HasComponent(component_name)
    else:
        return False


def GetEntityNavigationType(entity_id):
    """
    获取实体的寻路类型
    # minecraft:navigation.walk  陆地寻路，与原版僵尸的寻路相同
    # minecraft:navigation.generic  水陆寻路，支持陆地与水中，与原版溺尸的寻路相同
    # minecraft:navigation.climb  陆地寻路，但是支持爬墙，与原版蜘蛛的寻路相同。这种寻路可能会被头顶方块阻挡，一直无法抵达目的地
    # minecraft:navigation.fly 空中寻路，与原版鹦鹉的寻路相同
    # minecraft:navigation.float（如原版恶魂），
    # minecraft:navigation.hover（如原版蜜蜂）
    :param entity_id: 实体ID
    :type entity_id: str
    :return: 寻路类型
    :rtype: str or None
    """
    navigation_type_list = ["navigation_walk", "navigation_generic", "navigation_climb", "navigation_fly",
                            "navigation_float", "navigation_hover"]
    for navigation_type in navigation_type_list:
        navigation_type_num = getattr(MinecraftEnum.EntityComponentType, navigation_type, None)
        if CompFactory.CreateEntityComponent(entity_id).HasComponent(navigation_type_num):
            return navigation_type
    return None


# <editor-fold desc="target">

def ResetAttackTarget(entity_id):
    """
    清除仇恨目标

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 设置结果
    :rtype: bool
    """
    return CompFactory.CreateAction(entity_id).ResetAttackTarget()


def ClearAttackTargetIfMatched(entity_id, match_id):
    """
    如果仇恨目标是传入的目标,则清除仇恨目标

    :param entity_id: 实体ID
    :type entity_id: str

    :param match_id: match_id
    :type match_id: str

    :return: 设置结果
    :rtype: bool
    """
    if GetAttackTarget(entity_id) == match_id:
        return ResetAttackTarget(entity_id)
    return False


def GetAttackTarget(entity_id):
    """
    获取实体的仇恨目标

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 返回仇恨目标的实体id。如果传入的实体id所对应的实体没有仇恨目标，则返回-1。如果传入的实体id所对应的实体不存在，则返回None。
    :rtype: str or None
    """
    attack_target = CompFactory.CreateAction(entity_id).GetAttackTarget()
    return attack_target if attack_target and attack_target != "-1" else None


def SetAttackTarget(entity_id, target_id):
    """
    设置实体的仇恨目标

    :param entity_id: 实体ID
    :type entity_id: str
    :param target_id: target_id
    :type target_id: str

    :return: 设置结果
    :rtype: bool
    """
    if GetAttackTarget(entity_id) == target_id:
        return True
    return CompFactory.CreateAction(entity_id).SetAttackTarget(target_id)


# </editor-fold>

# <editor-fold desc="tag">

auto_remove_tag_timer = {}  # key: (entity_id, tag) -> {"timer": timer_id, "expire_time": float}


def AddEntityTagAndAutoRemove(entity_id, tag, delay_time=None):
    """
    增加实体的tag并在一定时间后自动移除
    """
    timer_key = (entity_id, tag)

    # 先给实体加 tag（这一步是无条件的）
    comp_tag = CompFactory.CreateTag(entity_id)
    comp_tag.AddEntityTag(tag)

    # 没有延时就别管自动移除的事
    if not delay_time:
        return True

    now_ts = time.time()
    old_info = auto_remove_tag_timer.get(timer_key)

    if old_info:
        old_expire = old_info["expire_time"]
        old_remaining = old_expire - now_ts

        # 老的已经过期或快过期了，视作没有
        if old_remaining <= 0:
            # 直接走下面“创建新的”流程
            pass
        else:
            # 关键逻辑：
            # 如果这次要加的 delay_time 比 旧的剩余时间 还短，就不更新
            if delay_time < old_remaining:
                # 什么都不做，沿用老的定时器
                return True

            # 否则这次的更长，需要重设：先取消旧的
            GetCompGameLevel().CancelTimer(old_info["timer"])
            auto_remove_tag_timer.pop(timer_key, None)

    # 能走到这里，说明要么：
    # 1) 原来没有定时器，或者
    # 2) 原来的过期了，或者
    # 3) 我们判断新的时间更长，准备重设
    new_timer = GetCompGameLevel().AddTimer(delay_time, comp_tag.RemoveEntityTag, tag)
    auto_remove_tag_timer[timer_key] = {
        "timer": new_timer,
        "expire_time": now_ts + delay_time,
    }

    return True
def _cancel_auto_remove_tag_timer(entity_id, tag):
    """
    内部工具函数：
    根据 (entity_id, tag) 查找并取消对应的自动移除定时器，
    同时从 auto_remove_tag_timer 字典中移除记录。
    """
    timer_key = (entity_id, tag)

    timer_info = auto_remove_tag_timer.pop(timer_key, None)
    if not timer_info:
        # 没有记录就直接返回，说明之前没设过定时器，或者已经被别的逻辑清掉了
        return False

    # 有记录就取消底层的定时器，避免后续再触发一次 RemoveEntityTag
    GetCompGameLevel().CancelTimer(timer_info["timer"])
    return True


def RemoveEntityTagAndCancelTimer(entity_id, tag):
    """
    手动移除实体的 tag，同时撤销对应的自动移除定时器。

    使用场景：
    - 想提前移除 tag，不等定时器触发
    - 并且不希望后面再有一次“迟到的”定时器回调
    """
    # 先移除 tag，本身是一个独立的业务操作
    comp_tag = CompFactory.CreateTag(entity_id)
    comp_tag.RemoveEntityTag(tag)

    # 再清理掉与这个 tag 关联的自动移除定时器（如果有的话）
    _cancel_auto_remove_tag_timer(entity_id, tag)

    return True

# </editor-fold>
