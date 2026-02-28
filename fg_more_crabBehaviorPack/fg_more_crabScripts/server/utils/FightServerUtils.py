# -*- coding: utf-8 -*-
from . import EntitySpatialMotionServerUtils, AttributeServerUtils
from ..ServerBaseUtils import *


def is_backstab(main_id, target_id, accept_angle=60.0, max_distance=5.0):
    main_foot_pos = Vector3(CompFactory.CreatePos(main_id).GetFootPos())
    target_foot_pos = Vector3(CompFactory.CreatePos(target_id).GetFootPos())

    main_rot = CompFactory.CreateRot(main_id).GetRot()
    target_rot = CompFactory.CreateRot(target_id).GetRot()

    main_dir = Vector3(ServerApi.GetDirFromRot((0, main_rot[1])))
    target_dir = Vector3(ServerApi.GetDirFromRot((0, target_rot[1])))

    to_main = main_foot_pos - target_foot_pos

    # 距离判定（含零距防护）
    dist = to_main.Length()
    if dist <= 1e-6:
        # 几乎重合：可按需要直接视为 False 或 True
        # 这里更保守，认为不是背刺
        return False
    if dist > max_distance:
        return False

    # 归一化得到方向
    dir_to_main = to_main
    dir_to_main.Normalize()

    # -------- 条件 1：main 是否处于 target 背后锥 --------
    # 与 target 正前方向相反即“背后”；用点积阈值判断
    # target_dir · dir_to_main <= -cos(max_back_angle)
    cos_back = math.cos(math.radians(accept_angle))
    dot_back = Vector3.Dot(target_dir, dir_to_main)
    if dot_back > -cos_back:
        return False  # 不够“在背后”

    # -------- 条件 2：main 与 target 朝向是否大致一致 --------
    # main_dir · target_dir >= cos(facing_tol)
    cos_face = math.cos(math.radians(accept_angle))
    dot_face = Vector3.Dot(main_dir, target_dir)
    if dot_face < cos_face:
        return False  # 朝向不够一致

    # --------（可选）附加：main 是否基本面向 target 的背部方向 --------
    # 这一步通常不用再加，但若你想更严格，可检查 main_dir 与 (-target_dir) 的夹角接近 180°
    # 例如要求 main_dir 与 target_dir 的反方向至少 > 90 - 某阈值
    # 这里保持简单，不再加第三个角度约束

    return True


def HurtEntity(entity_list, **kwargs):
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
        max_damage (int or float, default=None) : max_damage
        check_backstab (bool, default=False) : 是否需要检查背刺
        check_backstab_id (str, default=None) : 需要检查背刺的伤害来源id
        backstab_multiple (int or float, default=1.0) : 背刺伤害加成
        backstab_accept_angle (int or float, default=60.0) : 背刺检测角度
        backstab_max_distance (int or float, default=1.5) : 背刺检测距离
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
    attack_id = kwargs.get("attack_id", None)
    is_percent_damage = kwargs.get("is_percent_damage", False)
    critical_hit_chance = kwargs.get("critical_hit_chance", 0.0)
    critical_hit_bonus = kwargs.get("critical_hit_bonus", 0.5)
    force_backstab = kwargs.get("force_backstab", False)
    check_backstab = kwargs.get("check_backstab", False)
    check_backstab_id = kwargs.get("check_backstab_id", attack_id)
    backstab_multiple = kwargs.get("backstab_multiple", 1.0)
    backstab_accept_angle = kwargs.get("backstab_accept_angle", 60.0)
    backstab_max_distance = kwargs.get("backstab_max_distance", 5.0)

    def hurt_entity(entity_id):
        if not GetCompGameLevel().IsEntityAlive(entity_id):
            return
        damage = kwargs.get("damage", 10)

        max_damage = kwargs.get("max_damage", None)
        if max_damage:
            damage=min(damage,max_damage)
        delay_time = kwargs.get("delay_time", None)
        if delay_time:
            custom_cause_tag = "delay_%s" % delay_time
            attack_cause = MinecraftEnum.ActorDamageCause.Custom
        else:
            custom_cause_tag = kwargs.get("custom_cause_tag", None)
            attack_cause = (
                MinecraftEnum.ActorDamageCause.Custom if custom_cause_tag else kwargs.get(
                    "attack_cause") or MinecraftEnum.ActorDamageCause.EntityAttack)

        true_damage = max(AttributeServerUtils.GetHealthValueByPercentage(entity_id, damage),1) if is_percent_damage else damage
        if critical_hit_chance and random.random() < critical_hit_chance:
            true_damage = true_damage * (1 + critical_hit_bonus)
        if force_backstab:
            true_damage = true_damage * (1 + backstab_multiple)
        else:
            if check_backstab:
                if is_backstab(check_backstab_id, entity_id, backstab_accept_angle, backstab_max_distance):
                    true_damage *= (1 + backstab_multiple)

        child_attacker_id = kwargs.get("child_attacker_id", None)
        knocked = kwargs.get("default_knocked", False)


        CompFactory.CreateHurt(entity_id).Hurt(true_damage, attack_cause, attack_id, child_attacker_id, knocked,
                                               custom_cause_tag)

        if kwargs.get("need_motion", False):
            EntitySpatialMotionServerUtils.SetEntityMotion(entity_list, kwargs.get("motion", (0, 1, 0)))
        for effect_dict in kwargs.get("effect_list", []):
            CompFactory.CreateEffect(entity_id).AddEffectToEntity(effect_dict["effect_name"],
                                                                  int(effect_dict["effect_time"]),
                                                                  effect_dict["effect_level"],
                                                                  effect_dict.get("can_show_particle", True))
        if kwargs.get("can_knock_back", False):
            check_knock_back_id=kwargs.get("check_knock_back_id", attack_id)
            GetCompGameLevel().AddTimer(0.1, SetEntityKnockBackByAttacker, check_knock_back_id, entity_list,
                                   kwargs.get("knock_back_multiple", 1.0))
        if kwargs.get("attacker_need_forward", False):
            entity_forward_motion_dir = EntitySpatialMotionServerUtils.GetEntityForwardMotionDir(attack_id, kwargs.get(
                "forward_distant", 0.2))
            if entity_forward_motion_dir:
                EntitySpatialMotionServerUtils.SetEntityMotion(attack_id, entity_forward_motion_dir)

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
    around_entity_list = EntitySpatialMotionServerUtils.CheckEntitySectorAroundEntityListApi(
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
    HurtEntity(
        around_entity_list,
        attack_id=kwargs.get("attack_id", main_entity_id),
        is_percent_damage=kwargs.get("is_percent_damage", False),
        damage=kwargs.get("damage", 10),
        delay_time=kwargs.get("delay_time", None),
        can_knock_back=kwargs.get("can_knock_back", False),
        knock_back_multiple=kwargs.get("knock_back_multiple", 1.0),
        need_motion=kwargs.get("need_motion", False),
        motion=kwargs.get("motion", (0, 1.0, 0)),
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
        entity_vector = EntitySpatialMotionServerUtils.CalcVectorByDoubleEntityId(entity_id, attack_id)
        if entity_vector:
            # 根据Multiple调整方向向量的大小
            knock_back_motion = EntitySpatialMotionServerUtils.ZoomVector(entity_vector, Multiple)
            # 设置实体的运动，实现击退效果
            EntitySpatialMotionServerUtils.SetEntityMotion(entity_id, knock_back_motion)

    # 判断传入的entity_list的类型，并执行相应的操作
    if isinstance(entity_list, str):
        set_entity_knock_back(entity_list)
    else:
        for entity in entity_list:
            set_entity_knock_back(entity)


_auto_recover_ai_timer_map = {}


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
            GetCompGameLevel().CancelTimer(_auto_recover_ai_timer_map[entity_id])
            _auto_recover_ai_timer_map.pop(entity_id)
        if not GetCompGameLevel().IsEntityAlive(entity_id):
            return
        comp_ai = CompFactory.CreateControlAi(entity_id)
        if comp_ai.GetBlockControlAi():
            res = comp_ai.SetBlockControlAi(False, freeze_anim)
            if res:
                if can_auto_unlock:
                    _auto_recover_ai_timer_map[entity_id] = GetCompGameLevel().AddTimer(un_lock_time, UnBlockEntityAI,
                                                                                   entity_id)
            else:
                _auto_recover_ai_timer_map[entity_id] = GetCompGameLevel().AddTimer(0.03, block_ai, entity_id)

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
            GetCompGameLevel().CancelTimer(_auto_recover_ai_timer_map[entity_id])
            _auto_recover_ai_timer_map.pop(entity_id)
        comp_ai = CompFactory.CreateControlAi(entity_id)
        if not comp_ai.GetBlockControlAi():
            res = comp_ai.SetBlockControlAi(True, False)
            if not res:
                _auto_recover_ai_timer_map[entity_id] = GetCompGameLevel().AddTimer(0.03, un_block_ai, entity_id,
                                                                               retry_count + 1)

    if type(entity_list) == str:
        un_block_ai(entity_list)
    else:
        for entityId in entity_list:
            un_block_ai(entityId)
