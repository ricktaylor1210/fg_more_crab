# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyAttributeServerApi, EmptyHealthServerApi
from fg_more_crabScripts.server.api import EmptyBlockServerApi
from fg_more_crabScripts.server.api import EmptyGameServerApi
from fg_more_crabScripts.server.api import EmptyLocationDealServerApi
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *

_auto_recover_ai_timer_map = {}

def SetCameraShake(player_id, level, time):
    """
    设置窗口抖动
    :param player_id: player_id
    :type player_id: str
    :param level: level
    :type level: float or int
    :param time: time
    :type time: float or int
    """
    CompFactory.CreateCommand(player_id).SetCommand("/camerashake add @s %s %s rotational" % (level, time), player_id)


def SpawnMobFromEntity(entity_id, mob_str, is_npc=False):
    """
    根据传入的entity_id以及参数生成entity
        该方法使用给定的entity_id、mob_str和is_npc参数来生成一个新的实体。生成的实体会出现在指定entity_id所代表的实体的位置。
        如果is_npc设置为True，生成的将是一个NPC（非玩家角色）。

    :param entity_id: 需要在哪生成的实体的ID
    :type entity_id: str

    :param mob_str: 指定生成哪种类型的实体
    :type mob_str: str

    :param is_npc: 是否生成为NPC（非玩家角色）
    :type is_npc: bool

    :return: 生成的实体的ID
    :rtype: str or None
    """
    if not EmptyGameServerApi.GetEntityIsAlive(entity_id):
        return None
    entity_pos = EmptyAttributeServerApi.GetEntityFootPos(entity_id)
    if entity_pos is None:
        return
    entity_rot = EmptyAttributeServerApi.GetEntityRot(entity_id)
    if entity_rot is None:
        return
    entity_dimension_id = EmptyAttributeServerApi.GetEntityDimension(entity_id)
    if entity_dimension_id is None:
        return

    return ServerMain.CreateEngineEntityByTypeStr(mob_str, entity_pos, entity_rot, entity_dimension_id, is_npc)


def HurtEntityApi(entity_list, **kwargs):
    """
    对传入的实体id或实体id列表造成伤害
        该函数接受一个实体ID或实体ID列表，然后对这些实体应用指定的伤害值和其他可选的效果。
        伤害值、是否击退、击退的倍数、是否应用运动（motion）等都可以通过kwargs参数进行设置。

    :param entity_list: 需要受伤的实体ID或实体ID列表
    :type entity_list: list[str] or str

    :param kwargs: 其他可选参数
        attack_id (str or None, default=None) : 攻击者的ID
        critical_hit_chance (float, default=0.0) : 暴击概率
        critical_hit_bonus (float, default=0.5) : 暴击加成
        is_percent_damage (bool, default=False) : 造成百分比生命值伤害
        damage (int or float, default=10) : 如果is_percent_damage为False,那么是造成的伤害值,如果is_percent_damage为True,那么是造成的生命百分比
        can_knock_back (bool, default=False): 是否进行击退
        knock_back_multiple (float, default=1.0): 击退的倍数
        need_motion (bool, default=False): 是否需要应用运动（motion）
        motion (tuple, default=(0, 1, 0)): 运动的向量（x, y, z）
        effect_list (list, default=[]): 需要增加的effect_list
        forward_distant (int or float, default=0.2): 向前进的距离
        attacker_need_forward (bool, default=False): 攻击者是否需要向前进
        attack_cause(str, default=None): 伤害来源
        custom_cause_tag(str, default=None): 自定义伤害来源
        delay_time(int, default=None): 伤害延迟时间
        child_attacker_id(str, default=None): 伤害来源的子实体id，默认为None，比如玩家使用抛射物对实体造成伤害，该值应为抛射物Id

    """

    def hurt_entity(entity_id):
        if not EmptyGameServerApi.GetEntityIsAlive(entity_id):
            return
        attack_id = kwargs.get("attack_id", None)
        is_percent_damage = kwargs.get("is_percent_damage", False)
        critical_hit_chance = kwargs.get("critical_hit_chance", 0.0)
        critical_hit_bonus = kwargs.get("critical_hit_bonus", 0.5)
        damage = int(kwargs.get("damage", 10))
        true_damage = int(EmptyHealthServerApi.GetHealthValueByPercentage(entity_id, damage) if is_percent_damage else damage)
        if critical_hit_chance and random.random() < critical_hit_chance:
            true_damage = int(true_damage * (1 + critical_hit_bonus))
        delay_time = kwargs.get("delay_time", None)
        if delay_time:
            custom_cause_tag = "delay_%s" % delay_time
            attack_cause = MinecraftEnum.ActorDamageCause.Custom
        else:
            custom_cause_tag = kwargs.get("custom_cause_tag", None)
            attack_cause = (
                MinecraftEnum.ActorDamageCause.Custom if custom_cause_tag else kwargs.get("attack_cause") or MinecraftEnum.ActorDamageCause.EntityAttack)
        child_attacker_id = kwargs.get("child_attacker_id", None)
        knocked = kwargs.get("default_knocked", False)
        print(kwargs)

        print true_damage, attack_cause, attack_id, child_attacker_id, knocked, custom_cause_tag,type(attack_cause)
        res = GetHurtComp(entity_id).Hurt(true_damage, attack_cause, attack_id, child_attacker_id, knocked, custom_cause_tag)
        print res
        if kwargs.get("need_motion", False):
            EmptyLocationDealServerApi.SetEntityMotion(entity_list, kwargs.get("motion", (0, 1, 0)))
        if kwargs.get("effect_list", []):
            EmptyAttributeServerApi.AddEffectList(entity_id, kwargs.get("effect_list", []))
        if kwargs.get("can_knock_back", False):
            EmptyGameServerApi.AddTimer(0.1, SetEntityKnockBackByAttacker, attack_id, entity_list, kwargs.get("knock_back_multiple", 1.0))
        if kwargs.get("attacker_need_forward", False):
            entity_forward_motion_dir = EmptyLocationDealServerApi.GetEntityForwardMotionDir(attack_id, kwargs.get("forward_distant", 0.2))
            if entity_forward_motion_dir:
                EmptyLocationDealServerApi.SetEntityMotion(attack_id, entity_forward_motion_dir)

    if entity_list is None:
        return
    if isinstance(entity_list, str):
        hurt_entity(entity_list)
    else:
        for entityId in entity_list:
            hurt_entity(entityId)


def CheckEntitySectorAroundEntityListAndHurtApi(main_entity_id, **kwargs):
    """
    根据传入生物id获取扇形范围，并且进行伤害
        该函数接受一个中心生物ID，然后在其周围的扇形范围内查找其他生物并造成伤害。
        扇形的大小、伤害值、是否击退等都可以通过kwargs参数进行设置。

    :param main_entity_id: 需要检测的中心生物id
    :type main_entity_id: str

    :param kwargs: 其他可选参数
        around_radius (int or float, default=6): 扇形的长度
        radius_angle (int or float, default=60): 扇形的角度
        damage (int or float, default=6): 伤害值
        attack_id (str, default=None): 造成伤害的生物id，不传为main_entity_id
        can_knock_back (bool, default=False): 是否击退
        knock_back_multiple (int or float, default=1.0): 击退倍数
        need_motion (bool, default=False): 是否设置motion
        motion (tuple, default=(0, 1, 0)): motion
        exclude_entity_list (list, default=None): 排除的生物列表
        is_front (bool, default=False): 不考虑dir
        has_tag (str or list[str], default=""): has_tag
        has_not_tag (str or list[str], default=""): has_not_tag
        exclude_family_list: 需要排除的实体family，默认为None
        exclude_family_list: list[str]
        has_family_list: 需要拥有的实体family，默认为None
        has_family_list: list[str]
        filters: filters，默认为None
        attacker_need_forward (bool, default=False): 攻击者是否需要向前进
        forward_distant (int or float, default=0.2): 向前进的距离
        effect_list (list[str], default=[]): 需要增加的effect_list

    :return: around_entity_list
    :rtype: list[str] or None
    """
    attack_id = kwargs.get("attack_id", main_entity_id)
    around_entity_list = EmptyLocationDealServerApi.CheckEntitySectorAroundEntityListApi(
        main_entity_id,
        kwargs.get("around_radius", 6),
        kwargs.get("radius_angle", 60),
        kwargs.get("exclude_entity_list", []),
        kwargs.get("is_front", False),
        kwargs.get("has_tag", ""),
        kwargs.get("has_not_tag", ""),
        kwargs.get("exclude_family_list", []),
        kwargs.get("has_family_list", []),
        kwargs.get("filters", None),
    )
    HurtEntityApi(
        around_entity_list,
        attack_id=kwargs.get("attack_id", None),
        is_percent_damage=kwargs.get("is_percent_damage", False),
        damage=kwargs.get("damage", 10),
        delay_time=kwargs.get("delay_time", None),
        can_knock_back=kwargs.get("can_knock_back", False),
        knock_back_multiple=kwargs.get("knock_back_multiple", 1.0),
        need_motion=kwargs.get("need_motion", False),
        motion=kwargs.get("motion", (0, 1, 0)),
        effect_list=kwargs.get("effect_list", []),
        attacker_need_forward=kwargs.get("attacker_need_forward", False),
        forward_distant=kwargs.get("forward_distant", 0.2),
        attack_cause=kwargs.get("attack_cause", None),
        custom_cause_tag=kwargs.get("custom_cause_tag", None),
        child_attacker_id=kwargs.get("child_attacker_id", None)
    )
    return around_entity_list


def SetEntityKnockBackByAttacker(attack_id, entity_list, Multiple):
    """
    对传入的攻击者id以及实体id或实体id列表进行击退
        该函数通过传入攻击者ID和一个实体ID或实体ID列表，然后计算击退的动作。
        击退的方向和大小可以通过传入的参数Multiple来调节。

    :param attack_id: 攻击者id
    :type attack_id: str

    :param entity_list: 实体id或实体id列表
    :type entity_list: list[str] or str

    :param Multiple: 击退倍数
    :type Multiple: float

    """

    def set_entity_knock_back(entity_id):
        # 计算从攻击者到实体的方向向量
        entity_vector = EmptyLocationDealServerApi.CalcVectorByDoubleEntityId(entity_id, attack_id)
        if entity_vector:
            # 根据Multiple调整方向向量的大小
            knock_back_motion = EmptyLocationDealServerApi.ZoomVector(entity_vector, Multiple)
            # 设置实体的运动，实现击退效果
            EmptyLocationDealServerApi.SetEntityMotion(entity_id, knock_back_motion)

    # 判断传入的entity_list的类型，并执行相应的操作
    if isinstance(entity_list, str):
        set_entity_knock_back(entity_list)
    else:
        for entity in entity_list:
            set_entity_knock_back(entity)


def GatherSectorAroundEntityFrontMainEntity(main_entity_id, **kwargs):
    """
    将指定范围内的生物聚集到主生物面前

    :param main_entity_id: 中心生物的ID，用于确定聚集的中心点。
    :type main_entity_id: str
    :param kwargs: 额外可选参数
        - is_front (bool, default=False): 不考虑dir
        - has_tag (str, default=""): has_tag
        - has_not_tag (str, default=""): has_not_tag
        - exclude_family_list: 需要排除的实体family，默认为None
        - exclude_family_list: list[str] or None
        - has_family_list: 需要拥有的实体family，默认为None
        - has_family_list: list[str] or None
        - filters: filters，默认为None
        - around_radius: (int or float, 默认值为6) 聚集的扇形范围长度。
        - radius_angle: (int or float, 默认值为60) 聚集的扇形范围角度。
        - exclude_entity_list: (list, 默认值为[]) 需要排除的生物ID列表。
        - distant: (int or float, 默认值为1) 聚集到主生物的距离。
        - dura_time: (int or float, 默认值为0.5) 聚集持续的时间。
        - need_lock_ai: (bool, 默认值为False) 是否需要锁定生物的AI。
        - un_lock_time: (int or float, 默认值为2.0) 解锁AI的时间。
        - freeze_anim: (bool, 默认值为True) 是否冻结生物的动画。


    """
    main_entity_forward_pos = EmptyLocationDealServerApi.GetEntityForwardPos(main_entity_id, kwargs.get("distant", 1), is_center_pos=True)
    if main_entity_forward_pos is None:
        return
    around_entity_list = EmptyLocationDealServerApi.CheckEntitySectorAroundEntityListApi(main_entity_id, kwargs.get("around_radius", 6),
                                                                                         kwargs.get("radius_angle", 60),
                                                                                         kwargs.get("exclude_entity_list", []), kwargs.get("is_front", False),
                                                                                         kwargs.get("has_tag", ""), kwargs.get("has_not_tag", ""),
                                                                                         kwargs.get("exclude_family_list", None),
                                                                                         kwargs.get("has_family_list", None),
                                                                                         kwargs.get("filters", None))
    if around_entity_list:
        for entity_id in around_entity_list:
            EmptyLocationDealServerApi.AddEntityTrackMotion(entity_id, main_entity_forward_pos, kwargs.get("dura_time", 0.5))
        if kwargs.get("need_lock_ai", False):
            BlockEntityAI(around_entity_list, kwargs.get("un_lock_time", 2.0), kwargs.get("freeze_anim", True))


def GatherSectorAroundNearEntityFrontMainEntity(main_entity_id, **kwargs):
    """
    将指定范围内最近的生物聚集到主生物面前

    :param main_entity_id: 中心生物的ID，用于确定聚集的中心点。
    :type main_entity_id: str
    :param kwargs: 额外可选参数
        - has_tag (str, default=""): has_tag
        - has_not_tag (str, default=""): has_not_tag
        - exclude_family_list: 需要排除的实体family，默认为None
        - exclude_family_list: list[str] or None
        - has_family_list: 需要拥有的实体family，默认为None
        - has_family_list: list[str] or None
        - filters: filters，默认为None
        - around_radius: (int or float, 默认值为6) 聚集的扇形范围长度。
        - radius_angle: (int or float, 默认值为60) 聚集的扇形范围角度。
        - exclude_entity_list: (list, 默认值为[]) 需要排除的生物ID列表。
        - distant: (int or float, 默认值为1) 聚集到主生物的距离。
        - dura_time: (int or float, 默认值为0.5) 聚集持续的时间。
        - need_lock_ai: (bool, 默认值为False) 是否需要锁定生物的AI。
        - un_lock_time: (int or float, 默认值为2.0) 解锁AI的时间。
        - freeze_anim: (bool, 默认值为True) 是否冻结生物的动画。

    :return: 无
    :rtype: None
    """
    main_entity_forward_pos = EmptyLocationDealServerApi.GetEntityForwardPos(main_entity_id, kwargs.get("distant", 1), is_center_pos=True)
    if main_entity_forward_pos is None:
        return
    near_entity = EmptyLocationDealServerApi.CheckEntitySectorAroundNearEntityListApi(main_entity_id, kwargs.get("around_radius", 6),
                                                                                      kwargs.get("radius_angle", 60),
                                                                                      kwargs.get("exclude_entity_list", []), kwargs.get("has_tag", ""),
                                                                                      kwargs.get("has_not_tag", ""), kwargs.get("exclude_family_list", None),
                                                                                      kwargs.get("has_family_list", None), kwargs.get("filters", None))
    if near_entity:
        EmptyLocationDealServerApi.AddEntityTrackMotion(near_entity, main_entity_forward_pos, kwargs.get("dura_time", 0.5))
        if kwargs.get("need_lock_ai", False):
            BlockEntityAI(near_entity, kwargs.get("un_lock_time", 2.0), kwargs.get("freeze_anim", True))


def GatherEntityFrontMainEntity(main_entity_id, gather_entity_id, **kwargs):
    """
    将指定生物聚集到主生物面前

    :param main_entity_id: 用于确定聚集中心的主生物ID。
    :type main_entity_id: str
    :param gather_entity_id: 需要被聚集到主生物面前的目标生物ID。
    :type gather_entity_id: str
    :param kwargs: 额外可选参数
        - distant: (int or float, 默认值为1) 聚集到主生物的距离。
        - dura_time: (int or float, 默认值为0.5) 聚集操作持续的时间。
        - need_lock_ai: (bool, 默认值为False) 是否需要锁定目标生物的AI。
        - un_lock_time: (int or float, 默认值为2.0) 解锁AI的时间。
        - freeze_anim: (bool, 默认值为True) 是否冻结目标生物的动画。

    """
    main_entity_forward_pos = EmptyLocationDealServerApi.GetEntityForwardPos(main_entity_id, kwargs.get("distant", 1), is_center_pos=True)
    if main_entity_forward_pos is None:
        return
    EmptyLocationDealServerApi.AddEntityTrackMotion(gather_entity_id, main_entity_forward_pos, kwargs.get("dura_time", 0.5))
    if kwargs.get("need_lock_ai", False):
        BlockEntityAI(gather_entity_id, kwargs.get("un_lock_time", 2.0), kwargs.get("freeze_anim", True))


def BlockEntityAI(entity_list, un_lock_time=2.0, freeze_anim=True, can_auto_unlock=True):
    """
    屏蔽指定生物或生物列表的AI

    :param entity_list: 需要被屏蔽AI的生物ID或生物ID列表。
    :type entity_list: str or list[str]
    :param un_lock_time: AI解锁的延时时间，单位为秒。
    :type un_lock_time: float
    :param freeze_anim: 是否冻结生物的动画。
    :type freeze_anim: bool
    :param can_auto_unlock: can_auto_unlock。
    :type can_auto_unlock: bool

    """

    def block_ai(entity_id):
        if entity_id in _auto_recover_ai_timer_map:
            EmptyGameServerApi.CancelTimer(_auto_recover_ai_timer_map[entity_id])
            _auto_recover_ai_timer_map.pop(entity_id)
        if not EmptyGameServerApi.GetEntityIsAlive(entity_id):
            return
        if GetAiComp(entity_id).GetBlockControlAi():
            res = GetAiComp(entity_id).SetBlockControlAi(False, freeze_anim)
            if res:
                if can_auto_unlock:
                    _auto_recover_ai_timer_map[entity_id] = EmptyGameServerApi.AddTimer(un_lock_time, UnBlockEntityAI, entity_id)
            else:
                _auto_recover_ai_timer_map[entity_id] = EmptyGameServerApi.AddTimer(0.03, block_ai, entity_id)

    if type(entity_list) == str:
        block_ai(entity_list)
    else:
        for entity in entity_list:
            block_ai(entity)


def UnBlockEntityAI(entity_list):
    """
    取消屏蔽指定生物或生物列表的AI

    :param entity_list: 需要取消被屏蔽AI的生物ID或生物ID列表。
    :type entity_list: str or list[str]

    """

    def un_block_ai(entity_id, retry_count=0):
        if retry_count >= 10:
            return
        if entity_id in _auto_recover_ai_timer_map:
            EmptyGameServerApi.CancelTimer(_auto_recover_ai_timer_map[entity_id])
            _auto_recover_ai_timer_map.pop(entity_id)
        if not GetAiComp(entity_id).GetBlockControlAi():
            res = GetAiComp(entity_id).SetBlockControlAi(True, False)
            if not res:
                _auto_recover_ai_timer_map[entity_id] = EmptyGameServerApi.AddTimer(0.03, un_block_ai, entity_id, retry_count + 1)

    if type(entity_list) == str:
        un_block_ai(entity_list)
    else:
        for entityId in entity_list:
            un_block_ai(entityId)


def CreateExplosion(pos, radius, fire, breaks, source_id, player_id):
    """
    在指定位置创建爆炸效果

    :param pos: 爆炸的中心位置坐标，格式为(x, y, z)。
    :type pos: tuple(float, float, float)
    :param radius: 爆炸的威力半径，具体数值和效果可以参考相关文档或wiki。
    :type radius: int
    :param fire: 爆炸是否会产生火焰。
    :type fire: bool
    :param breaks: 爆炸是否会破坏周围的方块。
    :type breaks: bool
    :param source_id: 爆炸的伤害源实体ID。
    :type source_id: str
    :param player_id: 触发爆炸的玩家或实体ID。
    :type player_id: str

    """
    ExplosionCompLevel.CreateExplosion(pos, radius, fire, breaks, source_id, player_id)


def BreakRandomDestroyedBlocksPosListAPi(center_pos, dimension_id, radius, num_blocks, exclude_block_list=None, need_block_entity=False):
    """
    在指定中心位置、维度和范围内，随机破坏指定数量的方块

    :param center_pos: 随机破坏方块的中心位置坐标，格式为(x, y, z)。
    :type center_pos: tuple[int or float, int or float, int or float]
    :param dimension_id: 指定破坏方块的维度ID。
    :type dimension_id: int
    :param radius: 随机破坏方块的有效范围半径。
    :type radius: int
    :param num_blocks: 需要随机破坏的方块数量。
    :type num_blocks: int
    :param exclude_block_list: 需要排除的不进行破坏的方块列表。
    :type exclude_block_list: list[str] or None
    :param need_block_entity: 是否需要将破坏的方块实体化并飞出。
    :type need_block_entity: bool

    :return: 返回被破坏的方块位置列表。
    :rtype: list[tuple[int or float, int or float, int or float]]
    """
    random_block_list = EmptyBlockServerApi.GetRandomDestroyedBlocksPosListAPi(center_pos, dimension_id, radius, num_blocks, exclude_block_list)
    if need_block_entity:
        EmptyBlockServerApi.CreateBreakBlockEntity(center_pos, dimension_id, random_block_list)
    else:
        EmptyBlockServerApi.SetBlockToAirByList(random_block_list, dimension_id)
    return random_block_list


def BreakInvertedConeBlocksPosListAPi(center_pos, dimension_id, layers, initial_radius, **kwargs):
    """
    在指定的中心位置、维度、层数和初始半径基础上，执行一个倒锥形的方块破坏操作。

    :param center_pos: 需要破坏方块的中心位置坐标，格式为(x, y, z)。
    :type center_pos:  tuple[int or float, int or float, int or float]
    :param dimension_id: 指定破坏方块的维度ID。
    :type dimension_id: int
    :param layers: 需要破坏的层数。
    :type layers: int
    :param initial_radius: 初始的破坏半径。
    :type initial_radius: int
    :param kwargs: 可选的额外参数。
        - radius_decrement: 每一层的半径衰减量，默认值为1。
        - exclude_block_list: 需要排除不破坏的方块列表，默认为空列表。
        - random_remove: 是否进行随机移除方块，默认为False。
        - random_remove_count: 如果进行随机移除，移除方块的数量，默认为5。
        - need_block_entity: 是否需要将破坏的方块实体化并飞出，默认为False。
    :type kwargs: any
    :return: 返回被破坏的方块位置列表。
    :rtype:  list[tuple[int or float, int or float, int or float]]
    """
    inverted_block_list = EmptyBlockServerApi.GetInvertedConeBlocksPosListAPi(
        center_pos, dimension_id, layers, initial_radius,
        kwargs.get("radius_decrement", 1),
        kwargs.get("exclude_block_list", []),
        kwargs.get("random_remove", False),
        kwargs.get("random_remove_count", 5)
    )
    if kwargs.get("need_block_entity", False):
        EmptyBlockServerApi.CreateBreakBlockEntity(center_pos, dimension_id, inverted_block_list)
    else:
        EmptyBlockServerApi.SetBlockToAirByList(inverted_block_list, dimension_id)
    return inverted_block_list
