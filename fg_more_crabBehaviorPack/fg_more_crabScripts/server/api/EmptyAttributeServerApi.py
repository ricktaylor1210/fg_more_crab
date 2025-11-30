# -*- coding: utf-8 -*-

from fg_more_crabScripts.server.api import EmptyGameServerApi, EmptyDataServerApi
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *


def GetPlayerGameModeType(player_id):
    """
    获取指定玩家的游戏模式

    :param player_id: 玩家ID
    :type player_id: str

    :return GameModeType: GameModeType
    Undefined = -1            # 未定义类型
    Survival = 0              # 生存模式
    Creative = 1              # 创造模式
    Adventure = 2             # 冒险模式
    Spectator = 6             # 旁观模式
    Default = Survival        # 默认类型，默认为生存模式
    :rtype GameModeType: int
    """
    return GameCompLevel.GetPlayerGameType(player_id)


def GetEmptyEntityTag(entity_id, tag_name):
    """
    获取实体的特定标签状态及其过期时间。

    :param entity_id: 实体ID
    :param tag_name: 标签名称
    :return: 如果标签存在且未过期，返回True，否则返回False
    """
    data = GetExtraDataComp(entity_id).GetExtraData("tag_%s" % tag_name)
    if data:
        expiration_time = data.get("expiration_time", 0.0)
        if time.time() < expiration_time or expiration_time == float('inf'):
            return True
    return False


def SetEmptyEntityTag(entity_id, tag_name, state=True, duration_time=0):
    """
    设置实体的特定标签状态及其过期时间。

    :param entity_id: 实体ID
    :param tag_name: 标签名称
    :param state: 标签状态，True表示设置标签，False表示移除标签
    :param duration_time: 标签的有效时间（秒），0表示永久有效
    """
    if state is None or state is False:
        # 如果state为False或None，清除对应的标签
        GetExtraDataComp(entity_id).CleanExtraData("tag_%s" % tag_name)
        if DEVELOPMENT:
            print("清除了实体 {} 的标签：{}".format(entity_id, tag_name))
    else:
        expiration_time = float('inf') if duration_time == 0 else time.time() + duration_time

        data = {
            "expiration_time": expiration_time
        }

        GetExtraDataComp(entity_id).SetExtraData("tag_%s" % tag_name, data)

        if DEVELOPMENT:
            print("设置了实体 {} 的标签：{}，过期时间：{}".format(entity_id, tag_name, expiration_time))


def CleanUpEmptyExpiredTags():
    """
    清理所有实体中过期的标签数据。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("tag_"):
                expiration_time = value.get("expiration_time", 0.0)
                if expiration_time != float('inf') and current_time >= expiration_time:
                    keys_to_delete.append(key)

        # 删除过期的标签
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期标签: {}".format(entity_id, keys_to_delete))


def AddEffectList(entity_id, effect_list):
    """
    为指定实体添加一组效果（effect_list）。

    :param entity_id: 实体的唯一标识符
    :type entity_id: str

    :param effect_list: 要添加的效果列表，每个效果通过字典定义。字典包含以下键：
        - effect_name: 效果名称
        - add_time: 效果持续时间
        - add_level: 效果等级
        - can_show_particle: 是否显示粒子效果（可选，默认为True）
    :type effect_list: list[dict]

    该方法遍历effect_list中的每个效果字典，并将其效果添加到指定实体上。
    """
    for effect_dict in effect_list:
        AddEffect(entity_id, effect_dict["effect_name"], effect_dict["effect_time"], effect_dict["effect_level"],
                  effect_dict.get("can_show_particle", True))


def AddEffect(entity_id, effect_name, add_time=5, add_level=0, can_show_particle=True):
    """
    为实体添加指定状态效果，如果添加的状态已存在则有以下集中情况：
        1、等级大于已存在则更新状态等级及持续时间；
        2、状态等级相等且剩余时间duration大于已存在则刷新剩余时间；
        3、等级小于已存在则不做修改；
        4、粒子效果以新的为准

    :param entity_id: 实体ID
    :type entity_id: str

    :param effect_name: effect_name
    :type effect_name: str

    :param add_time: add_time
    :type add_time: int

    :param add_level: add_level
    :type add_level: int

    :param can_show_particle: can_show_particle
    :type can_show_particle: bool

    """
    GetEffectComp(entity_id).AddEffectToEntity(effect_name, add_time, add_level, can_show_particle)


def GetEntityAllEffects(entity_id):
    """
    获取实体当前所有状态效果

    状态效果信息字典 effectDict
        关键字	数据类型	说明
        effectName	str	状态效果名称
        duration	int	状态效果剩余持续时间，单位秒
        duration_f	float	状态效果剩余持续时间(浮点型)，单位秒
        amplifier	int	状态效果额外等级

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 状态效果信息字典的list。无状态效果时返回None
    :rtype: list[dict] or None
    """
    return GetEffectComp(entity_id).GetAllEffects()


def EntityHasEffects(entity_id, effect_name):
    """
    获取实体是否存在当前状态效果

    :param entity_id: 实体ID
    :type entity_id: str

    :param effect_name: 状态效果名称字符串，包括自定义状态效果和原版状态效果，原版状态效果可在wiki查询
    :type effect_name: str

    :return: 返回是否存在状态效果

    :rtype: bool
    """
    return GetEffectComp(entity_id).HasEffect(effect_name)


def RemoveEntityEffect(entity_id, effect_name):
    """
    为实体删除指定状态效果

    :param entity_id: 实体ID
    :type entity_id: str
    :param effect_name: 状态效果名称字符串，包括自定义状态效果和原版状态效果，原版状态效果可在wiki查询
    :type effect_name: str

    :return: True表示删除成功
    :rtype: bool
    """
    return GetEffectComp(entity_id).RemoveEffectFromEntity(effect_name)


def GetEntityModAttr(entity_id, attr_name, default_value=None, attr_mod_name=ModName):
    """
    获取entity自定义的mod属性
    :param entity_id: entity_id
    :type entity_id: str
    :param attr_name: attr_name
    :type attr_name: str
    :param default_value: default_value
    :type default_value: any
    :param attr_mod_name: get_mod_name
    :type attr_mod_name: str
    :return: 自定义的mod属性
    :rtype: any
    """
    return GetModAttrComp(entity_id).GetAttr(attr_mod_name + attr_name, default_value)


def SetEntityModAttr(entity_id, attr_name, attr_value, need_restore=True, auto_save=True, attr_mod_name=ModName):
    """
    获取entity自定义的mod属性
    :param entity_id: entity_id
    :type entity_id: str
    :param attr_name: attr_name
    :type attr_name: str
    :param attr_value: default_value
    :type attr_value: any
    :param need_restore: 该属性是否需要存档，默认为False。
    :type need_restore: bool
    :param auto_save: 是否需要立刻存档，当needRestore为True时生效。调用接口频繁时，可设置为False时，再另调用SaveAttr进行统一存储，减少开销
    :type auto_save: bool
    :param attr_mod_name: get_mod_name
    :type attr_mod_name: str
    """
    GetModAttrComp(entity_id).SetAttr(attr_mod_name + attr_name, attr_value, need_restore, auto_save)


def SaveEntityModAttr(entity_id):
    """
    SaveEntityModAttr
    :param entity_id: entity_id
    :type entity_id: str
    :return: 自定义的mod属性
    :rtype: any
    """
    GetModAttrComp(entity_id).SaveAttr()


def GetEntityAttr(entity_id, attr_type):
    """
    获取实体的引擎属性
    damage，knockback_resistance，jump_strength这三个值目前实现中并不会同步给客户端，因此这几个值通过客户端获取的为默认值。只有通过服务端的GetAttr才能获取到准确值
    当生物不存在该属性时，返回-1。部分属性的最大值默认为1，可通过entity的json配置来设置，详见attrType连接

    :param entity_id: 实体ID
    :type entity_id: str

    :param attr_type: attr_type
    :type attr_type: int

    :return: 属性结果
    :rtype: float or None
    """
    attr_value = GetAttrComp(entity_id).GetAttrValue(attr_type)
    return attr_value if attr_value else None


def SetEntityAttr(entity_id, attr_type, attr_value):
    """
    设置实体的引擎属性

    设置接口暂不支持 ABSORPTION
    在设置属性的时候，需要注意判断是否超过原版的值范围或是当前属性的值范围，如果设置的数值超过原版值的范围，则返回False。
    如果超过当前属性的最大值，则需要先调用SetAttrMaxValue接口来扩充该属性的最大值，否则设置的值过大时会由于超过该属性的最大值而被截取成该最大值。如果设置的值低于当前属性的最小值，则会被设置成原版的最小值。
    关于基础属性的原版最大值或最小值限制，可查看AttrType枚举
    需要注意的是护甲值由身上的护甲累计计算所得，并不能通过该接口直接修改

    :param entity_id: 实体ID
    :type entity_id: str

    :param attr_type: attr_type
    :type attr_type: int

    :param attr_value: attr_value
    :type attr_value: int or float

    :return: 设置结果
    :rtype: bool
    """
    attr_set_res = GetAttrComp(entity_id).SetAttrValue(attr_type, attr_value)
    return attr_set_res


def SetEntityAttrByDiff(entity_id, attr_type, diff_value):
    """
    设置实体的引擎属性

    设置接口暂不支持 ABSORPTION
    在设置属性的时候，需要注意判断是否超过原版的值范围或是当前属性的值范围，如果设置的数值超过原版值的范围，则返回False。
    如果超过当前属性的最大值，则需要先调用SetAttrMaxValue接口来扩充该属性的最大值，否则设置的值过大时会由于超过该属性的最大值而被截取成该最大值。如果设置的值低于当前属性的最小值，则会被设置成原版的最小值。
    关于基础属性的原版最大值或最小值限制，可查看AttrType枚举
    需要注意的是护甲值由身上的护甲累计计算所得，并不能通过该接口直接修改

    :param entity_id: 实体ID
    :type entity_id: str

    :param attr_type: attr_type
    :type attr_type: int

    :param diff_value: diff_value
    :type diff_value: int or float

    :return: 设置结果
    :rtype: bool
    """
    attr_current_value = GetEntityAttr(entity_id, attr_type)
    new_value = attr_current_value + diff_value
    attr_set_res = SetEntityAttr(entity_id, attr_type, new_value)
    return attr_set_res


def GetEntityMaxAttr(entity_id, attr_type):
    """
    获取实体的最大引擎属性

    attack_damage，knockback_resistance，jump_strength这三个值目前实现中并不会同步给客户端，因此这几个值通过客户端获取的为默认值。只有通过服务端的GetAttr才能获取到准确值
    因为护甲为身上盔甲总防御值，因此目前不支持获取护甲的最大值

    :param entity_id: 实体ID
    :type entity_id: str

    :param attr_type: attr_type
    :type attr_type: int

    :return: 属性结果
    :rtype: float or None
    """
    attr_max_value = GetAttrComp(entity_id).GetAttrMaxValue(attr_type)
    return attr_max_value if attr_max_value else None


def SetEntityMaxAttr(entity_id, attr_type, attr_max_value):
    """
    设置实体的最大引擎属性

    设置接口暂不支持 ABSORPTION
    在设置属性的时候，需要注意判断是否超过原版的值范围，如果设置的数值超过原版值的范围，则返回False。
    设置的最大饱和度不能超过当前的饥饿值; 食用食物后，最大饱和度会被原版游戏机制修改
    需要注意的是护甲值由身上的护甲累计计算所得，并不能通过该接口直接修改

    :param entity_id: 实体ID
    :type entity_id: str

    :param attr_type: attr_type
    :type attr_type: int

    :param attr_max_value: attr_max_value
    :type attr_max_value: int or float

    :return: 设置结果
    :rtype: bool
    """
    attr_set_res = GetAttrComp(entity_id).SetAttrMaxValue(attr_type, attr_max_value)
    return attr_set_res


def SetEntityMaxAttrByDiff(entity_id, attr_type, diff_value):
    """
    根据差值设置实体的最大引擎属性

    设置接口暂不支持 ABSORPTION
    在设置属性的时候，需要注意判断是否超过原版的值范围，如果设置的数值超过原版值的范围，则返回False。
    设置的最大饱和度不能超过当前的饥饿值; 食用食物后，最大饱和度会被原版游戏机制修改
    需要注意的是护甲值由身上的护甲累计计算所得，并不能通过该接口直接修改

    :param entity_id: 实体ID
    :type entity_id: str

    :param attr_type: attr_type
    :type attr_type: int

    :param diff_value: diff_value
    :type diff_value: int or float

    :return: 设置结果
    :rtype: bool
    """
    attr_current_max_value = GetEntityMaxAttr(entity_id, attr_type)
    new_max_value = attr_current_max_value + diff_value
    attr_set_res = SetEntityMaxAttr(entity_id, attr_type, new_max_value)
    return attr_set_res


def GetMaxAirSupply(entity_id):
    """
    获取最大氧气值
    注意：该值返回的是最大氧气储备的支持的逻辑帧数 = 氧气储备值 * 逻辑帧数（每秒20帧数）

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 最大氧气值
    :rtype: int
    """
    return GetBreathComp(entity_id).GetMaxAirSupply()


def SetMaxAirSupply(entity_id, max_air_value):
    """
    设置最大氧气值
    注意：该值设置的是当前氧气储备的支持的逻辑帧数 = 氧气储备值 * 逻辑帧数（每秒20帧数）

    :param entity_id: 实体ID
    :type entity_id: str

    :param max_air_value: air_value
    :type max_air_value: int

    :return: 设置结果
    :rtype: bool
    """
    return GetBreathComp(entity_id).SetMaxAirSupply(max_air_value)


def GetCurrentAirSupply(entity_id):
    """
    获取当前氧气值
    注意：该值设置的是当前氧气储备的支持的逻辑帧数 = 氧气储备值 * 逻辑帧数（每秒20帧数）

    :param entity_id: 实体ID
    :type entity_id: str


    :return: 当前氧气值
    :rtype: int
    """
    return GetBreathComp(entity_id).GetCurrentAirSupply()


def SetCurrentAirSupply(entity_id, air_value):
    """
    设置当前氧气值
    注意：该值设置的是当前氧气储备的支持的逻辑帧数 = 氧气储备值 * 逻辑帧数（每秒20帧数）

    :param entity_id: 实体ID
    :type entity_id: str

    :param air_value: air_value
    :type air_value: int

    :return: 设置结果
    :rtype: bool
    """
    return GetBreathComp(entity_id).SetCurrentAirSupply(air_value)


def SetCurrentAirSupplyToMaxAirSupply(entity_id):
    """
    设置当前氧气值为最大氧气值

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 设置结果
    :rtype: bool
    """
    current_air_supply = GetCurrentAirSupply(entity_id)
    max_air_supply = GetMaxAirSupply(entity_id)
    if current_air_supply == max_air_supply:
        return True
    return SetCurrentAirSupply(entity_id, max_air_supply)


def GetUnitBubbleAirSupply(entity_id):
    """
    单位气泡数对应的氧气储备值

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 单位气泡数对应的氧气储备值
    :rtype: int
    """
    return GetBreathComp(entity_id).GetUnitBubbleAirSupply()


def IsConsumingAirSupply(entity_id):
    """
    获取生物当前是否在消耗氧气

    :param entity_id: 实体ID
    :type entity_id: str


    :return: 是否在消耗氧气
    :rtype: bool
    """
    return GetBreathComp(entity_id).IsConsumingAirSupply()


def SetRecoverTotalAirSupplyTime(entity_id, time_sec):
    """
    设置恢复最大氧气量的时间，单位秒
    注意：当设置的最大氧气值小于（timeSec*10）时，生物每帧恢复氧气量的值为0

    :param entity_id: 实体ID
    :type entity_id: str

    :param time_sec: 恢复生物最大氧气值的时间，单位秒
    :type time_sec: float

    :return: 设置结果
    :rtype: bool
    """
    return GetBreathComp(entity_id).SetRecoverTotalAirSupplyTime(time_sec)


def ResetAttackTarget(entity_id):
    """
    清除仇恨目标

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 设置结果
    :rtype: bool
    """
    return GetActionComp(entity_id).ResetAttackTarget()


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
    attack_target = GetActionComp(entity_id).GetAttackTarget()
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
    return GetActionComp(entity_id).SetAttackTarget(target_id)


def GetEntityMotion(entity_id):
    """
    获取entity_id的Motion

    :param entity_id: 实体ID
    :type entity_id: str

    :return: Motion
    :rtype: tuple[float,float,float] or None
    """
    entity_motion = GetActionMotionComp(entity_id).GetMotion()
    return entity_motion if entity_motion else None


def GetEntityDimension(entity_id):
    """
    获取entity_id的维度ID

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 维度ID
    :rtype: int or None
    """
    dimension_id = GetDimensionComp(entity_id).GetEntityDimensionId()
    return dimension_id


def SetPlayerDimension(player_id, dimension_id, pos):
    """
    设置玩家的维度ID
    该接口在成功切换维度时pos位置为玩家头的位置，即比设定位置低1.62

    :param player_id: 玩家ID
    :type player_id: str

    :param dimension_id: 维度ID
    :type dimension_id: int

    :param pos: pos
    :type pos: tuple[float,float,float]

    :return: 是否设置成功
    :rtype: bool
    """
    return GetDimensionComp(player_id).ChangePlayerDimension(dimension_id, pos)


def SetEntityDimension(entity_id, dimension_id, pos):
    """
    设置entity_id的维度ID

    :param entity_id: 实体ID
    :type entity_id: str

    :param dimension_id: 维度ID
    :type dimension_id: int

    :param pos: pos
    :type pos: tuple[float,float,float]

    :return: 是否设置成功
    :rtype: bool
    """
    if CheckEntityIsPlayer(entity_id):
        return SetPlayerDimension(entity_id, dimension_id, pos)
    else:
        return GetDimensionComp(entity_id).ChangeEntityDimension(dimension_id, pos)


def GetEntityPos(entity_id):
    """
    对于非玩家，获取到的是脚底部位的位置
    对于玩家，如果处于行走，站立，游泳，潜行，滑翔状态，获得的位置比脚底位置高1.62；如果处于睡觉状态，获得的位置比最低位置高0.2
    类似接口有GetFootPos，对任何实体都是获取脚底部位的位置

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 位置
    :rtype: tuple[float,float,float] or None
    """
    entity_pos = GetPosComp(entity_id).GetPos()
    return entity_pos if entity_pos else None


def GetEntityFootPos(entity_id):
    """
    获取实体脚底的位置（除了睡觉时）

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 脚部位置
    :rtype: tuple[float,float,float] or None
    """
    entity_foot_pos = GetPosComp(entity_id).GetFootPos()
    return entity_foot_pos if entity_foot_pos else None


def GetEntityCenterPos(entity_id):
    """
    获取entity_id的中间位置

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 中间位置
    :rtype: tuple[float,float,float] or None
    """
    entity_pos = GetEntityPos(entity_id)
    entity_foot_pos = GetEntityFootPos(entity_id)
    if entity_pos is None or entity_foot_pos is None:
        return None
    x1, y1, z1 = entity_pos
    x2, y2, z2 = entity_foot_pos
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0, (z1 + z2) / 2.0


def SetEntityPos(entity_id, pos):
    """
    设置entity_id的位置

    :param entity_id: 实体ID
    :type entity_id: str

    :param pos: pos
    :type pos: tuple[float,float,float]

    :return: set_res
    :rtype: bool

    """
    return GetPosComp(entity_id).SetPos(pos)


def SetEntityFootPos(entity_id, foot_pos):
    """
    设置entity_id的脚底位置

    :param entity_id: 实体ID
    :type entity_id: str

    :param foot_pos: pos
    :type foot_pos: tuple[float,float,float]

    :return: set_res
    :rtype: bool

    """
    return GetPosComp(entity_id).SetFootPos(foot_pos)


def GetEntityRot(entity_id):
    """
    获取实体头与水平方向的俯仰角度和竖直方向的旋转角度

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 俯仰角度及绕竖直方向旋转的角度,单位是角度而不是弧度
    :rtype: tuple[float,float] or None
    """
    entity_rot = GetEntityRotComp(entity_id).GetRot()
    return entity_rot if entity_rot else None


def SetEntityRot(entity_id, rot):
    """
    设置entity_id的旋转角度

    :param entity_id: 实体ID
    :type entity_id: str

    :param rot: rot
    :type rot: tuple[float,float]

    :return: set_res
    :rtype: bool
    """
    return GetEntityRotComp(entity_id).SetRot(rot)


def GetEntityDir(entity_id):
    """
    获取entity_id的方向

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 方向
    :rtype: tuple[float,float,float] or None
    """
    entity_rot = GetEntityRot(entity_id)
    if entity_rot:
        entity_dir = ServerApi.GetDirFromRot(entity_rot)
        if entity_dir:
            return entity_dir
    return None


def GetEngineTypeStr(entity_id):
    """
    获取entity_id的类型字符串

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 类型字符串
    :rtype: str or None
    """
    entity_type_str = GetEntityTypeComp(entity_id).GetEngineTypeStr()
    return entity_type_str if entity_type_str else None


def GetEngineType(entity_id):
    """
    获取entity_id的类型

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 类型
    :rtype: int or None
    """
    entity_type = GetEntityTypeComp(entity_id).GetEngineType()
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


def GetEntitySize(entity_id):
    """
    获取entity_id的尺寸

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 尺寸
    :rtype: tuple[float,float] or None
    """

    entity_size = CompFactory.CreateCollisionBox(entity_id).GetSize()

    return entity_size


def SetEntitySize(entity_id, entity_size):
    """
    设置entity_id的尺寸
    对新生产的实体需要经过5帧之后再设置包围盒的大小才会生效


    :param entity_id: 实体ID
    :type entity_id: str

    :param entity_size: entity_size
    :type entity_size: tuple(float,float)

    :return: 设置结果
    :rtype: bool
    """

    return CompFactory.CreateCollisionBox(entity_id).SetSize(entity_size)


def HasTag(entity_id, tag):
    """
    检测实体是否含有tag

    :param entity_id: 实体ID
    :type entity_id: str

    :param tag: tag
    :type tag: str

    :return: 是否含有
    :rtype: bool
    """
    return GetTagComp(entity_id).EntityHasTag(tag)


def GetEntityTag(entity_id):
    """
    检测实体是否含有tag

    :param entity_id: 实体ID
    :type entity_id: str

    :return: tag_list
    :rtype: list[str] or None
    """
    entity_tag_list = GetTagComp(entity_id).GetEntityTags()
    return entity_tag_list if entity_tag_list else None


AddEntityTagRetryTimerMap = {}
AddEntityTagRetryCountMap = {}


def AddEntityTag(entity_id, tag, need_auto_retry=False):
    """
    为实体增加tag

    :param entity_id: 实体ID
    :type entity_id: str

    :param tag: tag
    :type tag: str

    :param need_auto_retry: 添加失败是否自动重试
    :type need_auto_retry: bool

    :return: 是否成功
    :rtype: bool
    """
    if HasTag(entity_id, tag):
        return True
    AddEntityTagRetryCountMap.setdefault(tag, {})
    AddEntityTagRetryTimerMap.setdefault(tag, {})

    def clear_retry_data():
        """
        清除重试相关的数据
        """
        if AddEntityTagRetryTimerMap[tag].get(entity_id, None):
            EmptyGameServerApi.CancelTimer(AddEntityTagRetryTimerMap[tag][entity_id])
            AddEntityTagRetryTimerMap[tag].pop(entity_id)

    res = GetTagComp(entity_id).AddEntityTag(tag)
    if not res and need_auto_retry:
        retry_count = AddEntityTagRetryCountMap[tag].setdefault(entity_id, 0)
        if retry_count > 10:
            clear_retry_data()
            return False
        AddEntityTagRetryTimerMap[tag][entity_id] = EmptyGameServerApi.AddTimer(0.03, AddEntityTag, entity_id, tag, need_auto_retry)
        AddEntityTagRetryCountMap[tag][entity_id] += 1
        return False
    clear_retry_data()
    return res


RemoveEntityTagRetryTimerMap = {}
RemoveEntityTagRetryCountMap = {}


def RemoveEntityTag(entity_id, tag, need_auto_retry=False):
    """
    为实体删除tag

    :param entity_id: 实体ID
    :type entity_id: str

    :param tag: tag
    :type tag: str

    :param need_auto_retry: 删除失败是否自动重试
    :type need_auto_retry: bool

    :return: 是否成功
    :rtype: bool
    """
    if not HasTag(entity_id, tag):
        return True
    RemoveEntityTagRetryCountMap.setdefault(tag, {})
    RemoveEntityTagRetryTimerMap.setdefault(tag, {})

    def clear_retry_data():
        """
        清除重试相关的数据
        """
        if RemoveEntityTagRetryTimerMap[tag].get(entity_id, None):
            EmptyGameServerApi.CancelTimer(RemoveEntityTagRetryTimerMap[tag][entity_id])
            RemoveEntityTagRetryTimerMap[tag].pop(entity_id, None)

    res = GetTagComp(entity_id).RemoveEntityTag(tag)
    if not res and need_auto_retry:
        retry_count = RemoveEntityTagRetryCountMap[tag].setdefault(entity_id, 0)
        if retry_count > 10:
            clear_retry_data()
            return False
        RemoveEntityTagRetryTimerMap[tag][entity_id] = EmptyGameServerApi.AddTimer(0.03, RemoveEntityTag, entity_id, tag, need_auto_retry)
        RemoveEntityTagRetryCountMap[tag][entity_id] += 1
        return False
    clear_retry_data()
    return res


def GetAllComponentsName(entity_id):
    """
    获取实体所拥有的原版组件list
    :param entity_id: 实体ID
    :type entity_id: str

    :return: 原版组件名list，EntityComponentType枚举
    :rtype: list[str] or None
    """
    all_components = GetEntityComponentComp(entity_id).GetAllComponentsName()
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
        return GetEntityComponentComp(entity_id).HasComponent(component_name)
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
    navigation_type_list = ["navigation_walk", "navigation_generic", "navigation_climb", "navigation_fly", "navigation_float", "navigation_hover"]
    for navigation_type in navigation_type_list:
        if CheckEntityHasComponents(entity_id, navigation_type):
            return navigation_type
    return None


def GetPlayerOperation(player_id):
    """
    获取玩家权限类型信息

    :return: 权限类型，Visitor为0，Member为1，Operator为2，Custom为3
    :rtype: int
    """
    return GetPlayerComp(player_id).GetPlayerOperation()


def CheckEntityIsPlayer(entity_id):
    """
    检测传入的entity_id是否是玩家

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 是否是玩家
    :rtype: bool
    """
    return entity_id in EmptyGameServerApi.GetAllPlayerList()


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


def GetLoadMobMessageList():
    """
    获取所有维度中已加载的所有生物列表（不包含玩家）。

    :return:当前地图中的所有实体信息，key：实体id，value：实体信息字典
        实体信息字典:
            dimensionId	int	维度id
            entityType	int	实体类型
            identifier	str	实体identifier
    :rtype:dict[str,dict]
    """
    engine_actor_dict = EmptyGameServerApi.GetEngineActor()
    mob_dict = {}
    if engine_actor_dict:
        for entity_id, entity_dict in engine_actor_dict.iteritems():
            if CheckEntityIsItemEntity(entity_id):
                continue
            elif CheckEntityIsMoveBlock(entity_id):
                continue
            elif CheckEntityIsProject(entity_id):
                continue
            elif CheckEntityIsMob(entity_id):
                mob_dict[entity_id] = {"identifier": entity_dict["identifier"], "dimensionId": entity_dict["dimensionId"]}
                continue
    return mob_dict


def GetEntityOwner(entity_id):
    """
    获取实体的属主（包括可驯服生物的主人，或者掉落物的丢弃者，弹射物的发射者等）

    :param entity_id: entity_id
    :type entity_id: str
    :return: Owner
    :rtype: str or None
    """
    return GetActorOwnerComp(entity_id).GetEntityOwner()


def GetOwnerId(entity_id):
    """
    获取驯服生物的主人id

    :param entity_id: entity_id
    :type entity_id: str
    :return: Owner
    :rtype: str or None
    """
    return GetTameComp(entity_id).GetOwnerId()


def SetEntityOwner(entity_id, owner_id):
    """
    设置实体的属主（包括可驯服生物的主人，或者掉落物的丢弃者，弹射物的发射者等）

    :param entity_id: entity_id
    :type entity_id: str
    :param owner_id: entity_id
    :type owner_id: str or None
    :return: 设置是否成功
    :rtype: bool
    """
    return GetActorOwnerComp(entity_id).SetEntityOwner(owner_id)


def GetTypeFamily(entity_id):
    """
    获取生物行为包字段 type_family

    :param entity_id: entity_id
    :type entity_id: str
    :return: type_family列表，例['cow', 'mob']
    :rtype: list[str] or None
    """
    type_family = GetAttrComp(entity_id).GetTypeFamily()
    return type_family if type_family else None
