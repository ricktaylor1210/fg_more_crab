# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyDamageServerApi, EmptyAttributeServerApi, EmptyFightServerApi, EmptyHealthServerApi
from fg_more_crabScripts.server.base_parent_class.ServerListener import *


class ServerAfterDamageController(ServerListener):
    def __init__(self):
        super(ServerAfterDamageController, self).__init__(False)
        self.engine_events.update(
            {
                # engineEventName : {func,priority}
                # 生物受到状态伤害/回复事件。
                "EntityEffectDamageServerEvent": {"func": self.EntityEffectDamageServerEvent, "priority": 0},
                # 实体实际受到伤害时触发，相比于DamageEvent，该伤害为经过护甲及buff计算后，实际的扣血量
                "ActuallyHurtServerEvent": {"func": self.ActuallyHurtServerEvent, "priority": 0},
                # 生物生命值发生变化之前触发
                "HealthChangeBeforeServerEvent": {"func": self.HealthChangeBeforeServerEvent, "priority": 0},
                # 生物生命值发生变化时触发
                "HealthChangeServerEvent": {"func": self.HealthChangeServerEvent, "priority": 0},
                # 实体死亡时触发
                "MobDieEvent": {"func": self.MobDieEvent, "priority": 0}
            }
        )
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
        })
        self.Register()

    def HealthChangeServerEvent(self, args):
        # entityId  str   实体id
        # from   float  变化前的生命值
        # to   float  变化后的生命值
        # byScript  bool  是否通过SetAttrValue或SetAttrMaxValue调用产生的变化
        entityId = args["entityId"]
        GameCompLevel.AddTimer(0.03, EmptyDamageServerApi.SyncHealthForEntity, entityId)

    def HealthChangeBeforeServerEvent(self, args):
        # entityId	str	实体id
        # from	float	变化前的生命值
        # to	float	将要变化到的生命值，cancel设置为True时可以取消该变化，但是此参数不变
        # byScript	bool	是否通过SetAttrValue或SetAttrMaxValue调用产生的变化
        # cancel	bool	是否取消该变化
        print "==============================================="
        print ("HealthChangeBeforeServerEvent Is After Active")

        if args.get("cancel", False) or (args.get("already_check_immune", False) and args.get("already_sync_damage", False)):
            return

        entityId = args["entityId"]
        diff_health = args["to"] - args["from"]
        if diff_health >= 0:
            return

        if args.get("already_check_immune", False) and EmptyDamageServerApi.GetEntityIsImmuneAllDamage(entityId, check_immune_force_damage=False):
            args["already_check_immune"] = True
            args["cancel"] = True

        if args.get("already_sync_damage", False):
            print "sync damage is ->", args.get("already_sync_damage", False)
            return
        args["already_sync_damage"] = True
        damage = -int(diff_health)

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "true_damage")
        damage_health_value = -damage
        for sync_entity_id in sync_damage_entity_list:
            if not EmptyDamageServerApi.GetEntityIsImmuneAllDamage(sync_entity_id, check_immune_force_damage=False):
                EmptyHealthServerApi.SetEntityHealthByDiff(sync_entity_id, damage_health_value)

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "true_damage_percent")
        damage_percent = EmptyHealthServerApi.GetHealthPercentage(entityId, damage)

        damage_health_percent = -damage_percent
        for sync_entity_id in sync_damage_entity_list:
            if not EmptyDamageServerApi.GetEntityIsImmuneAllDamage(sync_entity_id, check_immune_force_damage=False):
                EmptyHealthServerApi.SetEntityHealthByDiffPercentage(sync_entity_id, damage_health_percent)


    def MobDieEvent(self, args):
        # 注意：不能在该事件回调中对此玩家手持物品进行修改，如SpawnItemToPlayerCarried、ChangePlayerItemTipsAndExtraId等接口
        # id	str	实体id
        # attacker	str	伤害来源id
        # cause	str	伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        # customTag	str	使用Hurt接口传入的自定义伤害类型
        if args.get("already_deal", False):
            return
        entityId = args["id"]
        attacker = args["attacker"]
        cause = args["cause"]
        customTag = args.get("customTag", None)
        args["already_deal"] = True
        sync_death_list = EmptyDamageServerApi.GetEntitySyncDeathStatusToAnotherEntity(entityId)
        print ("2222222222222222222222222222222222222222")
        print sync_death_list
        for sync_death_entity_id in sync_death_list:
            EmptyDamageServerApi.SetEntityIsImmuneDamage(sync_death_entity_id, False, None)
            EmptyDamageServerApi.SetEntityIsImmuneToAnotherEntity(sync_death_entity_id, None, False)
        EmptyFightServerApi.HurtEntityApi(sync_death_list,
                                          **{"attack_id": attacker, "attack_cause": cause, "custom_cause_tag": customTag,
                                             "damage": EmptyHealthServerApi.GetHealthPercentage(entityId, 100), "is_percent_damage": True})

    def ActuallyHurtServerEvent(self, args):
        # 药水与状态效果造成的伤害不触发，可以使用ActorHurtServerEvent
        # 为了游戏运行效率请尽可能避免将火的伤害设置为0，因为这样会导致大量触发该事件。
        # 若要修改damage或damage_f的值，请确保修改后的值与原值不同，且需要使用原来的数据类型(int/float)，否则引擎会忽略这次修改。
        # srcId	str	伤害源id
        # projectileId	str	投射物id
        # entityId	str	被伤害id
        # damage	int	伤害值（被伤害吸收后的值），允许修改，设置为0则此次造成的伤害为0，若设置数值和原来一样则视为没有修改
        # damage_f	float	伤害值（被伤害吸收后的值），允许修改，若修改该值，则会覆盖damage的修改效果
        # cause	str	伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        # customTag	str	使用Hurt接口传入的自定义伤害类型
        print "==============================================="
        print ("ActuallyHurtServerEvent Is After Active")
        print self
        print "test_send is ->", args.get("test_send", None)

        # 如果伤害值为0，直接返回
        if args["damage"] == 0:
            return

        if args.get("already_sync_damage", False):
            print "sync damage is ->", args.get("already_sync_damage", False)
            return
        entityId = args["entityId"]
        srcId = args["srcId"]
        cause = args["cause"]
        damage = args["damage"]
        customTag = args.get("customTag", None)
        args["already_sync_damage"] = True
        EmptyDamageServerApi.SetEntityDamageLastHurtTime(entityId, cause, customTag)

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "default")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list,
                                          **{"attack_id": srcId, "attack_cause": cause, "custom_cause_tag": customTag, "damage": damage})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "default_percent")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list,
                                          **{"attack_id": srcId, "attack_cause": cause, "custom_cause_tag": customTag,
                                             "damage": EmptyHealthServerApi.GetHealthPercentage(entityId, damage), "is_percent_damage": True})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "cause_sync")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list, **{"attack_id": srcId, "custom_cause_tag": "sync_damage", "damage": damage})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "cause_sync_percent")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list,
                                          **{"attack_id": srcId, "custom_cause_tag": "sync_damage",
                                             "damage": EmptyHealthServerApi.GetHealthPercentage(entityId, damage), "is_percent_damage": True})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "force_cause_sync")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list, **{"attack_id": srcId, "custom_cause_tag": "force_damage", "damage": damage})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "force_cause_sync_percent")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list,
                                          **{"attack_id": srcId, "custom_cause_tag": "force_damage",
                                             "damage": EmptyHealthServerApi.GetHealthPercentage(entityId, damage), "is_percent_damage": True})

    def EntityEffectDamageServerEvent(self, args):
        # entityId	str	实体id
        # damage	int	伤害值（伤害吸收后实际扣血量），负数表示生命回复量
        # attributeBuffType	int	状态类型，参考AttributeBuffType
        # duration	float	状态持续时间，单位秒（s）
        # lifeTimer	float	状态生命时间，单位秒（s）
        # isInstantaneous	bool	是否为立即生效状态
        # cause	str	伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        print "==============================================="
        print ("EntityEffectDamageServerEvent Is After Active")
        entityId = args["entityId"]
        damage = args["damage"]
        cause = args["cause"]
        if damage <= 0 or (args.get("already_check_immune", False) and args.get("already_sync_damage", False)):
            return

        if args.get("already_check_immune", False) and EmptyDamageServerApi.GetEntityIsImmuneAllDamage(entityId):
            args["already_check_immune"] = True
            EmptyHealthServerApi.SetEntityHealthByDiff(entityId, damage)
            return
        if args.get("already_check_immune", False) and EmptyDamageServerApi.GetEntityIsImmuneDamage(entityId, cause):
            args["already_check_immune"] = True
            EmptyHealthServerApi.SetEntityHealthByDiff(entityId, damage)
            return
        if args.get("already_check_immune", False) and not EmptyDamageServerApi.GetEntityPastLastHurtTime(entityId, cause):
            args["already_check_immune"] = True
            EmptyHealthServerApi.SetEntityHealthByDiff(entityId, damage)
            return

        if args.get("already_sync_damage", False):
            print "sync damage is ->", args.get("already_sync_damage", False)
            return
        args["already_sync_damage"] = True
        EmptyDamageServerApi.SetEntityDamageLastHurtTime(entityId, cause)

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "default")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list, **{"attack_cause": cause, "damage": damage})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "default_percent")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list,
                                          **{"attack_cause": cause, "damage": EmptyHealthServerApi.GetHealthPercentage(entityId, damage),
                                             "is_percent_damage": True})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "cause_sync")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list, **{"custom_cause_tag": "sync_damage", "damage": damage})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "cause_sync_percent")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list,
                                          **{"custom_cause_tag": "sync_damage", "damage": EmptyHealthServerApi.GetHealthPercentage(entityId, damage),
                                             "is_percent_damage": True})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "force_cause_sync")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list, **{"custom_cause_tag": "force_damage", "damage": damage})

        sync_damage_entity_list = EmptyDamageServerApi.GetEntitiesByDamageTypeForEntity(entityId, "force_cause_sync_percent")
        EmptyFightServerApi.HurtEntityApi(sync_damage_entity_list,
                                          **{"custom_cause_tag": "force_damage", "damage": EmptyHealthServerApi.GetHealthPercentage(entityId, damage),
                                             "is_percent_damage": True})
