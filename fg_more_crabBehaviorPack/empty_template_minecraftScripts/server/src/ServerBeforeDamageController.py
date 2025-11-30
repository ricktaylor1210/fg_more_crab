# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyDamageServerApi, EmptyAttributeServerApi, EmptyFightServerApi, EmptyHealthServerApi
from fg_more_crabScripts.server.base_parent_class.ServerListener import *


class ServerBeforeDamageController(ServerListener):
    def __init__(self):
        super(ServerBeforeDamageController, self).__init__(True)
        self.engine_events.update(
            {
                # engineEventName : {func,priority}
                # 玩家发送聊天信息时触发
                "ServerChatEvent": {"func": self.ServerChatEvent},
                # 实体受到伤害时触发
                "DamageEvent": {"func": self.DamageEvent, "priority": 10},
                # 生物受到火焰伤害时触发
                "OnFireHurtEvent": {"func": self.OnFireHurtEvent, "priority": 10},
                # 实体实际受到伤害时触发，相比于DamageEvent，该伤害为经过护甲及buff计算后，实际的扣血量
                "ActuallyHurtServerEvent": {"func": self.ActuallyHurtServerEvent, "priority": 10}
            }
        )
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            "KeyDownButton2TestEvent": {"func": self.KeyDownButton2TestEvent},
            "KeyDownButton3TestEvent": {"func": self.KeyDownButton3TestEvent},
            "KeyDownButton4TestEvent": {"func": self.KeyDownButton4TestEvent}
        })
        self.Register()

    def KeyDownButton2TestEvent(self, args):
        player_id = args["__id__"]
        pick_entity_id = args["pick_entity_id"]
        EmptyDamageServerApi.SetEntitySyncDamageToAnotherEntity(pick_entity_id, player_id, method_type="true_damage_percent")

    def KeyDownButton3TestEvent(self, args):
        player_id = args["__id__"]
        pick_entity_id = args["pick_entity_id"]
        EmptyDamageServerApi.SetEntitySyncDamageToAnotherEntity(pick_entity_id, player_id, sync_state=False, method_type="true_damage_percent")

    def KeyDownButton4TestEvent(self, args):
        player_id = args["__id__"]
        # pick_entity_id = args["pick_entity_id"]
        # EmptyDamageServerApi.SetEntityHealthSync(player_id, sync_state=False)
        print ("222222222222222222222222")
        # EmptyFightServerApi.HurtEntityApi(player_id, **{"attack_id": player_id, "custom_cause_tag": "delay_1", "damage": 1})

        motionComp = ServerApi.GetEngineCompFactory().CreateActorMotion(player_id)
        velocity = (0, -1, 1)
        accelerate = (0, -1, 1)
        mID = motionComp.AddPlayerVelocityMotion(velocity, accelerate, useVelocityDir=True)
        print mID
        motionComp.StartPlayerMotion(mID)

    def ServerChatEvent(self, args):
        # username	str	玩家名称
        # playerId	str	玩家id
        # message	str	玩家发送的聊天消息内容
        # cancel	bool	是否取消这个聊天事件，若取消可以设置为True
        # bChatById	bool	是否把聊天消息发送给指定在线玩家，而不是广播给所有在线玩家，若只发送某些玩家可以设置为True
        # bForbid	bool	是否禁言，仅apollo可用。true：被禁言，玩家聊天会提示“你已被管理员禁言”。
        # toPlayerIds	list(str)	接收聊天消息的玩家id列表，bChatById为True时生效
        message = args["message"]
        if str.lower(message) == "111":
            EmptyDamageServerApi.SetEntityIsImmuneDamage(args["playerId"], duration_time=10)

    def OnScriptTickServer(self):
        if GlobalTickCount() % 30 == 0:
            EmptyDamageServerApi.SyncAllEntitiesHealth()
        if GlobalTickCount() % 300 == 0:
            EmptyDamageServerApi.CleanUpAllExpiredData()

    def DamageEvent(self, args):
        # damage值会被护甲和absorption等吸收，不一定是最终扣血量。通过设置这个伤害值可以取消伤害，但不会取消由击退效果或者点燃效果带来的伤害
        # 该事件在实体受伤之前触发，由于部分伤害是在tick中处理，因此持续触发受伤时（如站在火中）会每帧触发事件（可以使用ActorHurtServerEvent来避免）。
        # 这里的damage是伤害源具有的攻击伤害值，并非实体真实的扣血量，如果需要获取真实伤害，可以使用ActuallyHurtServerEvent事件。
        # 当目标无法被击退时，knock值无效
        # 药水与状态效果造成的伤害不触发，可以使用ActorHurtServerEvent
        # 由于点燃的实现原因，此处ignite设置为false并不能取消实体的点燃效果（如果需要取消点燃效果，请通过OnFireHurtEvent事件实现）
        # srcId	str	伤害源id
        # projectileId	str	投射物id
        # entityId	str	被伤害id
        # damage	int	伤害值（被伤害吸收前的值），允许修改，设置为0则此次造成的伤害为0
        # damage_f	float	伤害值（被伤害吸收前的值），不允许修改
        # absorption	int	受到伤害时，扣除黄心前，实体拥有的黄心血量（见AttrType枚举的ABSORPTION）
        # cause	str	伤害来源，详见Minecraft枚举值文档的ActorDamageCause
        # knock	bool	是否击退被攻击者，允许修改，设置该值为False则不产生击退
        # ignite	bool	是否点燃被伤害者，允许修改，设置该值为True产生点燃效果
        # customTag	str	使用Hurt接口传入的自定义伤害类型

        # 打印调试信息
        print "==============================================="
        print "DamageEvent Is Active"
        print args["customTag"]
        print args["cause"]
        # 打印当前对象状态
        print self

        # 如果伤害值为0，直接返回
        if args["damage"] == 0 or args.get("already_check_immune", False):
            print ("0000000000000000000000000000000")
            print args["damage"]
            args["already_check_immune"] = True
            return

        cause = args["cause"]
        customTag = args.get("customTag", None)
        print cause
        print customTag

        if cause == MinecraftEnum.ActorDamageCause.Custom and "delay_" in customTag and "delay_instant" not in customTag:
            if args.get("already_delay_damage", False):
                return
            try:
                attack_damage = args["damage"] + 0
                knocked = bool(args["knock"])
                args["already_delay_damage"] = True
                args["damage"] = 0
                args["knock"] = False
                args["ignite"] = False
                _, delay_time_str = customTag.split('_')
                delay_time = float(delay_time_str)
                GameCompLevel.AddTimer(delay_time, GetHurtComp(args["entityId"]).Hurt, attack_damage, MinecraftEnum.ActorDamageCause.Custom,
                                       args.get("srcId", None), args.get("projectileId", None), knocked, "delay_instant")
                return
            except ValueError:
                pass

        entityId = args["entityId"]

        # 如果实体对所有伤害免疫，则直接返回
        if EmptyDamageServerApi.GetEntityIsImmuneAllDamage(entityId, customTag=customTag):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

        if EmptyDamageServerApi.GetEntityIsImmuneDamage(entityId, immune_cause=cause, customTag=customTag):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

        srcId = args.get("srcId", None)

        if srcId and EmptyDamageServerApi.GetEntityIsImmuneToAnotherEntity(entityId, srcId):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

        projectileId = args.get("projectileId", None)

        if projectileId and EmptyDamageServerApi.GetEntityIsImmuneToAnotherEntity(entityId, projectileId):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

        if cause not in [MinecraftEnum.ActorDamageCause.Fire, MinecraftEnum.ActorDamageCause.FireTick] and not EmptyDamageServerApi.GetEntityPastLastHurtTime(
                entityId, cause, customTag):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            print ("----------------------------------")
            print cause
            print args["damage"]
            return
        if not args.get("percent_check_finished", False):
            total_percent = 0
            all_cause_damage_percent = EmptyDamageServerApi.GetEntityPercentageDamageForCustomTag(entityId)
            if all_cause_damage_percent:
                total_percent += all_cause_damage_percent

            cause_damage_percent = EmptyDamageServerApi.GetEntityPercentageDamageForCustomTag(entityId, cause, customTag)
            if cause_damage_percent:
                total_percent += cause_damage_percent

            entity_damage_percent = EmptyDamageServerApi.GetEntityPercentageDamageFromSource(entityId, srcId)
            if entity_damage_percent:
                total_percent += entity_damage_percent

            if total_percent:
                args["damage"] = int(args["damage"] + EmptyHealthServerApi.GetHealthValueByPercentage(entityId, total_percent))
            args["percent_check_finished"] = True

        if not args.get("modifier_check_finished", False):
            total_modifier = 0
            all_cause_damage_modifier = EmptyDamageServerApi.GetEntityDamageModifier(entityId)
            if all_cause_damage_modifier:
                total_modifier += all_cause_damage_modifier

            cause_damage_modifier = EmptyDamageServerApi.GetEntityDamageModifier(entityId, cause, customTag)
            if cause_damage_modifier:
                total_modifier += cause_damage_modifier

            entity_damage_modifier = EmptyDamageServerApi.GetEntityDamageModifierFromSource(entityId, srcId)
            if entity_damage_modifier:
                total_modifier += entity_damage_modifier
            if total_modifier:
                args["damage"] = int(args["damage"] * (1 + total_modifier))
            args["modifier_check_finished"] = True
        if not args.get("real_damage_check_finished", False):
            if EmptyDamageServerApi.GetEntityRealDamageForCustomTag(entityId) or EmptyDamageServerApi.GetEntityRealDamageForCustomTag(entityId, cause,
                                                                                                                                      customTag) or EmptyDamageServerApi.GetEntityRealDamageFromSource(
                entityId, srcId):
                EmptyHealthServerApi.SetEntityHealthByDiff(entityId, args["damage"])
                args["damage"] = 0
            args["real_damage_check_finished"] = True

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
        print ("ActuallyHurtServerEvent Is Active")
        args["test_send"] = "This is Test Send Message"
        print "test_send is send!"

        # 如果伤害值为0，直接返回
        if args["damage"] == 0 or args.get("already_check_immune", False):
            print ("0000000000000000000000000000000")
            print args["damage"]
            args["already_check_immune"] = True
            return

        entityId = args["entityId"]
        cause = args["cause"]
        customTag = args.get("customTag", None)

        # 如果实体对所有伤害免疫，则直接返回
        if EmptyDamageServerApi.GetEntityIsImmuneAllDamage(entityId, customTag=customTag):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

        if EmptyDamageServerApi.GetEntityIsImmuneDamage(entityId, immune_cause=cause, customTag=customTag):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

        srcId = args.get("srcId", None)

        if srcId and EmptyDamageServerApi.GetEntityIsImmuneToAnotherEntity(entityId, srcId):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

        projectileId = args.get("projectileId", None)

        if projectileId and EmptyDamageServerApi.GetEntityIsImmuneToAnotherEntity(entityId, projectileId):
            args["already_check_immune"] = True
            args["damage"] = 0
            args["knock"] = False
            args["ignite"] = False
            return

    def OnFireHurtEvent(self, args):
        # victim	str	受伤实体id
        # src	str	火焰创建者id
        # fireTime	float	着火时间，单位秒, 不支持修改
        # cancel	bool	是否取消此处火焰伤害
        # cancelIgnite	bool	是否取消点燃效果
        print "==============================================="
        print ("OnFireHurtEvent Is Active")

        if args.get("cancel", False) or args.get("already_check_immune", False):
            return

        entityId = args.get("victim", None)

        # 如果实体对所有伤害免疫，则直接返回
        if EmptyDamageServerApi.GetEntityIsImmuneAllDamage(entityId):
            args["already_check_immune"] = True
            args["cancel"] = True
            return

        if EmptyDamageServerApi.GetEntityIsImmuneDamage(entityId, immune_cause=MinecraftEnum.ActorDamageCause.Fire):
            args["already_check_immune"] = True
            args["cancel"] = True
            args["cancelIgnite"] = True
            return
        if EmptyDamageServerApi.GetEntityIsImmuneDamage(entityId, immune_cause=MinecraftEnum.ActorDamageCause.FireTick):
            args["already_check_immune"] = True
            args["cancel"] = True
            args["cancelIgnite"] = True
            return

        srcId = args.get("src", None)

        if srcId and EmptyDamageServerApi.GetEntityIsImmuneToAnotherEntity(entityId, srcId):
            args["already_check_immune"] = True
            args["cancel"] = True
            args["cancelIgnite"] = True
            return

        if not EmptyDamageServerApi.GetEntityPastLastHurtTime(entityId, "fire"):
            args["already_check_immune"] = True
            args["cancel"] = True
            args["cancelIgnite"] = True
            print ("----------------------------------")
            return

        if not EmptyDamageServerApi.GetEntityPastLastHurtTime(entityId, "fire_tick"):
            args["already_check_immune"] = True
            args["cancel"] = True
            args["cancelIgnite"] = True
            print ("----------------------------------")
            return

    # ===============================================
    # DamageEvent Is Active
    # ===============================================
    # ActuallyHurtServerEvent Is Active
    # ===============================================
    # ActorHurtServerEvent Is Active
    # 以上是生物造成伤害的事件触发顺序

    # ===============================================
    # OnFireHurtEvent Is Active
    # ===============================================
    # DamageEvent Is Active
    # ===============================================
    # ActuallyHurtServerEvent Is Active
    # ===============================================
    # ActorHurtServerEvent Is Active
    # ===============================================
    # OnFireHurtEvent Is Active
    # ===============================================
    # DamageEvent Is Active
    # 以上是火焰造成伤害的事件触发顺序

    # ===============================================
    # ActorHurtServerEvent Is Active
    # ===============================================
    # EntityEffectDamageServerEvent Is Active
    # 以上是凋零效果造成伤害的事件触发顺序

    # ===============================================
    # ActorHurtServerEvent Is Active
    # ===============================================
    # EntityEffectDamageServerEvent Is Active
    # 以上是瞬间伤害效果造成伤害的事件触发顺序

    # ===============================================
    # ActorHurtServerEvent Is Active
    # ===============================================
    # EntityEffectDamageServerEvent Is Active
    # 以上是中毒效果造成伤害的事件触发顺序

    # 如果实体攻击是HealthChangeBeforeServerEvent进行了cancel,触发以下事件
    # ===============================================
    # DamageEvent Is Active
    # ===============================================
    # ActuallyHurtServerEvent Is Active
    # ===============================================
    # HealthChangeBeforeServerEvent Is Active

    # 如果着火是HealthChangeBeforeServerEvent进行了cancel,触发以下事件
    # ===============================================
    # OnFireHurtEvent Is Active
    # ===============================================
    # DamageEvent Is Active
    # ===============================================
    # ActuallyHurtServerEvent Is Active
    # ===============================================
    # HealthChangeBeforeServerEvent Is Active

    # 如果Buff效果是HealthChangeBeforeServerEvent进行了cancel,触发以下事件
    # ===============================================
    # HealthChangeBeforeServerEvent Is Active
    # ===============================================
    # EntityEffectDamageServerEvent Is Active
