# -*- coding: utf-8 -*-

from fg_more_crabScripts.server.api import EmptyGameServerApi, EmptyDataServerApi, EmptyHealthServerApi
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *


def GetCauseIsForceDamage(cause):
    can_force_damage_tag_list = EmptyDataServerApi.GetExtraDataLevel("can_force_damage_tag_list")

    if not can_force_damage_tag_list:
        can_force_damage_tag_list = ["force_damage"]

    # 确保默认标签在列表中
    if "force_damage" not in can_force_damage_tag_list:
        can_force_damage_tag_list.append("force_damage")

    return cause in can_force_damage_tag_list


def AddCauseToForceDamage(cause):
    can_force_damage_tag_list = EmptyDataServerApi.GetExtraDataLevel("can_force_damage_tag_list")

    if not can_force_damage_tag_list:
        can_force_damage_tag_list = ["force_damage"]

    # 确保默认标签在列表中
    if "force_damage" not in can_force_damage_tag_list:
        can_force_damage_tag_list.append("force_damage")

    can_force_damage_tag_list.append(cause)

    EmptyDataServerApi.SetExtraDataLevel("can_force_damage_tag_list", can_force_damage_tag_list)


def AddCauseListToForceDamage(cause_list):
    can_force_damage_tag_list = EmptyDataServerApi.GetExtraDataLevel("can_force_damage_tag_list")

    if not can_force_damage_tag_list:
        can_force_damage_tag_list = ["force_damage"]

    # 确保默认标签在列表中
    if "force_damage" not in can_force_damage_tag_list:
        can_force_damage_tag_list.append("force_damage")

    for cause in cause_list:
        if cause not in can_force_damage_tag_list:
            can_force_damage_tag_list.append(cause)

    EmptyDataServerApi.SetExtraDataLevel("can_force_damage_tag_list", can_force_damage_tag_list)


def GetCauseIsImmuneHurtTime(cause):
    can_immune_hurt_time_tag_list = EmptyDataServerApi.GetExtraDataLevel("can_immune_hurt_time_tag_list")

    if not can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list = ["immune_hurt_time", "sync_damage"]

    # 确保默认标签在列表中
    if "immune_hurt_time" not in can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list.append("immune_hurt_time")
    if "sync_damage" not in can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list.append("sync_damage")

    return cause in can_immune_hurt_time_tag_list


def AddCauseToImmuneHurtTime(cause):
    can_immune_hurt_time_tag_list = EmptyDataServerApi.GetExtraDataLevel("can_immune_hurt_time_tag_list")

    if not can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list = ["immune_hurt_time", "sync_damage"]

    # 确保默认标签在列表中
    if "immune_hurt_time" not in can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list.append("immune_hurt_time")
    if "sync_damage" not in can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list.append("sync_damage")

    can_immune_hurt_time_tag_list.append(cause)
    EmptyDataServerApi.SetExtraDataLevel("can_immune_hurt_time_tag_list", can_immune_hurt_time_tag_list)


def AddCauseListToImmuneHurtTime(cause_list):
    can_immune_hurt_time_tag_list = EmptyDataServerApi.GetExtraDataLevel("can_immune_hurt_time_tag_list")

    if not can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list = ["immune_hurt_time", "sync_damage"]

    # 确保默认标签在列表中
    if "immune_hurt_time" not in can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list.append("immune_hurt_time")
    if "sync_damage" not in can_immune_hurt_time_tag_list:
        can_immune_hurt_time_tag_list.append("sync_damage")
    for cause in cause_list:
        if cause not in can_immune_hurt_time_tag_list:
            can_immune_hurt_time_tag_list.append(cause)

    EmptyDataServerApi.SetExtraDataLevel("can_immune_hurt_time_tag_list", can_immune_hurt_time_tag_list)


def GetEntityIsImmuneDamage(entity_id, immune_cause="all", customTag=None):
    if customTag:
        tags = customTag.split("::")
        for tag in tags:
            current_immune_cause = "custom_%s" % tag if immune_cause == "custom" else immune_cause
            immune_finished_time = GetExtraDataComp(entity_id).GetExtraData("immune_%s" % current_immune_cause)
            if immune_finished_time is not None:
                if immune_finished_time == float('inf'):
                    return True
                if time.time() < immune_finished_time:
                    return True
        return False

    immune_finished_time = GetExtraDataComp(entity_id).GetExtraData("immune_%s" % immune_cause)
    if immune_finished_time is not None:
        if immune_finished_time == float('inf'):
            return True
        return time.time() < immune_finished_time

    return False


def GetEntityIsImmuneAllDamage(entity_id, customTag=None, check_immune_force_damage=True):
    if customTag:
        tags = customTag.split("::")
        for tag in tags:
            if check_immune_force_damage and GetCauseIsForceDamage(tag):
                if GetEntityIsImmuneDamage(entity_id, immune_cause="custom", customTag=tag):
                    return True
        return False

    immune_finished_time = GetExtraDataComp(entity_id).GetExtraData("immune_all")
    if immune_finished_time is not None:
        if immune_finished_time == float('inf'):
            return True
        return time.time() < immune_finished_time

    return False


def SetEntityIsImmuneDamage(entity_id, immune_state=True, immune_cause="all", customTag=None, duration_time=0):
    if immune_cause == "custom" and customTag:
        immune_cause = "custom_%s" % customTag

    if immune_state:
        if duration_time == 0:
            # 设置为永久免疫
            GetExtraDataComp(entity_id).SetExtraData("immune_%s" % immune_cause, float('inf'))
        else:
            # 设置为临时免疫
            immune_finished_time = time.time() + duration_time
            GetExtraDataComp(entity_id).SetExtraData("immune_%s" % immune_cause, immune_finished_time)
    else:
        if immune_cause == "all" and customTag is None:
            # 取消所有免疫状态
            extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
            for key in extra_data:
                if key.startswith("immune_"):
                    GetExtraDataComp(entity_id).CleanExtraData(key)
                    if DEVELOPMENT:
                        print("取消了实体 {} 的所有免疫状态。".format(entity_id))
        else:
            # 取消特定的免疫状态
            GetExtraDataComp(entity_id).CleanExtraData("immune_%s" % immune_cause)
            if DEVELOPMENT:
                print("取消了实体 {} 的免疫状态：{}。".format(entity_id, immune_cause))


def CleanUpExpiredImmunities():
    """
    清理所有实体中过期的免疫状态。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("immune_") and isinstance(value, (int, float)):
                if value != float('inf') and current_time >= value:
                    keys_to_delete.append(key)

        # 删除过期的免疫状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期免疫状态: {}".format(entity_id, keys_to_delete))


def GetEntityIsImmuneToAnotherEntity(entity_id, source_entity_id):
    """
    检查实体是否对来自特定实体的伤害免疫。

    :param entity_id: 被检查的实体ID
    :param source_entity_id: 伤害源实体ID
    :return: 如果免疫，返回 True，否则返回 False
    """
    immune_key = "immune_from_%s" % source_entity_id

    immune_finished_time = GetExtraDataComp(entity_id).GetExtraData(immune_key)

    if immune_finished_time is not None:
        if immune_finished_time == float('inf'):
            return True
        return time.time() < immune_finished_time

    return False


def SetEntityIsImmuneToAnotherEntity(entity_id, source_entity_id=None, immune_state=True, duration_time=0):
    """
    设置实体对来自特定实体的免疫状态。
    如果 `immune_state` 为 False 且未传入 `source_entity_id`，则清除目标实体上的所有免疫状态。

    :param entity_id: 被免疫的实体ID
    :param source_entity_id: 伤害源实体ID
    :param immune_state: 是否免疫，True 为免疫，False 为不免疫
    :param duration_time: 免疫持续时间，0 表示永久免疫
    """
    if immune_state:
        if source_entity_id is not None:
            immune_key = "immune_from_%s" % source_entity_id

            if duration_time == 0:
                # 设置为永久免疫
                GetExtraDataComp(entity_id).SetExtraData(immune_key, float('inf'))
            else:
                # 设置为临时免疫
                immune_finished_time = time.time() + duration_time
                GetExtraDataComp(entity_id).SetExtraData(immune_key, immune_finished_time)
    else:
        if source_entity_id is None:
            # 清除所有免疫状态
            extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
            for key in extra_data:
                if key.startswith("immune_from_"):
                    GetExtraDataComp(entity_id).CleanExtraData(key)
                    if DEVELOPMENT:
                        print("取消了实体 {} 的所有免疫状态。".format(entity_id))
        else:
            # 取消来自特定实体的免疫状态
            immune_key = "immune_from_%s" % source_entity_id
            GetExtraDataComp(entity_id).CleanExtraData(immune_key)
            if DEVELOPMENT:
                print("取消了实体 {} 对实体 {} 的免疫状态。".format(entity_id, source_entity_id))


def CleanUpExpiredEntitySpecificImmunities():
    """
    清理所有实体中过期的对来自特定实体的伤害免疫状态。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("immune_from_") and isinstance(value, (int, float)):
                if value != float('inf') and current_time >= value:
                    keys_to_delete.append(key)

        # 删除过期的免疫状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期对特定实体的免疫状态: {}".format(entity_id, keys_to_delete))


def GetEntitySyncDamageToAnotherEntity(entity_id):
    """
    检查实体是否需要同步特定实现方法的伤害给其他实体，并检测同步时间是否合理。

    :param entity_id: 被检查的实体ID
    :return: 返回一个字典，键为同步伤害的目标实体ID，值为实现方法类型

        default 直接造成伤害,cause是被伤害的实体受到的cause,会参与免疫伤害计算和其他抵消伤害计算
        default_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是被伤害的实体受到的cause,会参与免疫伤害计算和其他抵消伤害计算

        cause_sync 直接造成伤害,cause是sync_damage,会参与免疫伤害计算和其他抵消伤害计算
        cause_sync_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是sync_damage,会参与免疫伤害计算和其他抵消伤害计算

        force_cause_sync 直接造成伤害,cause是force_damage,会参与免疫伤害计算和其他抵消伤害计算,会跳过免疫伤害检测
        force_cause_sync_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是force_damage,会参与免疫伤害计算和其他抵消伤害计算,会跳过免疫伤害检测

        true_damage 直接扣除生命
        true_damage_percent 直接扣除生命,伤害数值是百分比生命
    """
    sync_entity_dict = {}
    extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
    current_time = time.time()

    for key, value in extra_data.items():
        if key.startswith("sync_damage_") and isinstance(value, (int, float)):
            # 检查时间是否合理
            if value == float('inf') or current_time < value:
                # 从键中解析出method_type和sync_entity_id
                key_parts = key.replace("sync_damage_", "").split("_to_")
                if len(key_parts) == 2:
                    method_type, sync_entity_id = key_parts
                    sync_entity_dict[sync_entity_id] = method_type

    return sync_entity_dict


def GetEntitiesByDamageTypeForEntity(entity_id, damage_method_type="default"):
    """
    获取某个实体同步伤害类型为特定方法的所有目标实体列表。

    :param entity_id: 被检查的实体ID
    :param damage_method_type: 需要查询的伤害类型
        default 直接造成伤害,cause是被伤害的实体受到的cause,会参与免疫伤害计算和其他抵消伤害计算
        default_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是被伤害的实体受到的cause,会参与免疫伤害计算和其他抵消伤害计算

        cause_sync 直接造成伤害,cause是sync_damage,会参与免疫伤害计算和其他抵消伤害计算
        cause_sync_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是sync_damage,会参与免疫伤害计算和其他抵消伤害计算

        force_cause_sync 直接造成伤害,cause是force_damage,会参与免疫伤害计算和其他抵消伤害计算,会跳过免疫伤害检测
        force_cause_sync_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是force_damage,会参与免疫伤害计算和其他抵消伤害计算,会跳过免疫伤害检测

        true_damage 直接扣除生命
        true_damage_percent 直接扣除生命,伤害数值是百分比生命
    :return: 返回一个列表，包含所有需要同步特定伤害类型的目标实体ID
    """
    sync_entity_list = []
    extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
    current_time = time.time()

    for key, value in extra_data.items():
        if key.startswith("sync_damage_%s_to_" % damage_method_type) and isinstance(value, (int, float)):
            # 检查时间是否合理
            if value == float('inf') or current_time < value:
                sync_entity_id = key.replace("sync_damage_%s_to_" % damage_method_type, "")
                sync_entity_list.append(sync_entity_id)

    return sync_entity_list


def SetEntitySyncDamageToAnotherEntity(entity_id, sync_entity_id=None, method_type="default", sync_state=True, duration_time=0):
    """
    设置实体是否需要同步特定实现方法的伤害给其他实体。
    如果 `sync_state` 为 False 且未传入 `sync_entity_id`，则清除目标实体上的所有同步关系。

    :param entity_id: 被伤害的实体ID
    :param sync_entity_id: 同步实体ID
    :param method_type: 实现方法类型
        default 直接造成伤害,cause是被伤害的实体受到的cause,会参与免疫伤害计算和其他抵消伤害计算
        default_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是被伤害的实体受到的cause,会参与免疫伤害计算和其他抵消伤害计算

        cause_sync 直接造成伤害,cause是sync_damage,会参与免疫伤害计算和其他抵消伤害计算
        cause_sync_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是sync_damage,会参与免疫伤害计算和其他抵消伤害计算

        force_cause_sync 直接造成伤害,cause是force_damage,会参与免疫伤害计算和其他抵消伤害计算,会跳过免疫伤害检测
        force_cause_sync_percent 直接造成伤害,伤害数值是百分比生命,例如该伤害是原实体的10%,则造成sync实体的10%生命伤害,cause是force_damage,会参与免疫伤害计算和其他抵消伤害计算,会跳过免疫伤害检测

        true_damage 直接扣除生命
        true_damage_percent 直接扣除生命,伤害数值是百分比生命
    :param sync_state: 是否同步，True 为同步，False 为不同步
    :param duration_time: 同步持续时间，0 表示永久同步
    """
    if sync_state:
        if sync_entity_id is not None:
            sync_key = "sync_damage_%s_to_%s" % (method_type, sync_entity_id)

            if duration_time == 0:
                # 设置为永久同步
                GetExtraDataComp(entity_id).SetExtraData(sync_key, float('inf'))
            else:
                # 设置为临时同步
                sync_end_time = time.time() + duration_time
                GetExtraDataComp(entity_id).SetExtraData(sync_key, sync_end_time)
    else:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)

        if sync_entity_id is None:
            # 清除所有同步关系
            for key in extra_data:
                if key.startswith("sync_damage_"):
                    GetExtraDataComp(entity_id).CleanExtraData(key)
                    if DEVELOPMENT:
                        print("取消了实体 {} 的所有同步伤害关系。".format(entity_id))
        else:
            # 取消与特定实体的同步关系
            sync_key = "sync_damage_%s_to_%s" % (method_type, sync_entity_id)
            GetExtraDataComp(entity_id).CleanExtraData(sync_key)
            if DEVELOPMENT:
                print("取消了实体 {} 对实体 {} 的同步伤害关系。".format(entity_id, sync_entity_id))


def CleanUpExpiredSyncs():
    """
    清理所有实体中过期的同步伤害数据，包含不同实现方法类型的同步伤害。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("sync_damage_") and isinstance(value, (int, float)):
                if value != float('inf') and current_time >= value:
                    keys_to_delete.append(key)

        # 删除过期的同步伤害状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期同步伤害数据: {}".format(entity_id, keys_to_delete))


def GetEntitySyncDeathStatusToAnotherEntity(entity_id):
    """
    检查实体是否需要同步死亡状态给其他实体。

    :param entity_id: 被检查的实体ID
    :return: 需要同步死亡状态的entity_id列表，若无则返回空列表
    """
    sync_death_list = []
    extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
    current_time = time.time()

    for key, value in extra_data.items():
        if key.startswith("sync_death_to_") and isinstance(value, (int, float)):
            # 检查时间是否合理
            if value == float('inf') or current_time < value:
                sync_entity_id = key.replace("sync_death_to_", "")
                sync_death_list.append(sync_entity_id)

    return sync_death_list


def SetEntitySyncDeathStatusToAnotherEntity(entity_id, sync_entity_id=None, sync_state=True, duration_time=0):
    """
    设置实体是否需要同步死亡状态给其他实体。
    如果 `sync_state` 为 False 且未传入 `sync_entity_id`，则清除目标实体上的所有同步死亡状态。

    :param entity_id: 被死亡的实体ID
    :param sync_entity_id: 需要同步死亡状态的目标实体ID
    :param sync_state: 是否同步，True 为同步，False 为不同步
    :param duration_time: 同步持续时间，0 表示永久同步
    """
    if sync_state:
        if sync_entity_id is not None:
            sync_key = "sync_death_to_%s" % sync_entity_id

            if duration_time == 0:
                # 设置为永久同步
                GetExtraDataComp(entity_id).SetExtraData(sync_key, float('inf'))
            else:
                # 设置为临时同步
                sync_end_time = time.time() + duration_time
                GetExtraDataComp(entity_id).SetExtraData(sync_key, sync_end_time)
    else:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)

        if sync_entity_id is None:
            # 清除所有同步死亡状态
            for key in extra_data:
                if key.startswith("sync_death_to_"):
                    GetExtraDataComp(entity_id).CleanExtraData(key)
                    if DEVELOPMENT:
                        print("取消了实体 {} 的所有同步死亡状态。".format(entity_id))
        else:
            # 取消与特定实体的同步死亡状态
            sync_key = "sync_death_to_%s" % sync_entity_id
            GetExtraDataComp(entity_id).CleanExtraData(sync_key)
            if DEVELOPMENT:
                print("取消了实体 {} 对实体 {} 的同步死亡状态。".format(entity_id, sync_entity_id))


def CleanUpExpiredSyncDeathStatuses():
    """
    清理所有实体中过期的同步死亡状态数据。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("sync_death_to_") and isinstance(value, (int, float)):
                if value != float('inf') and current_time >= value:
                    keys_to_delete.append(key)

        # 删除过期的同步死亡状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期同步死亡状态数据: {}".format(entity_id, keys_to_delete))


def GetEntityDamageLastHurtTime(entity_id, damage_cause="all", customTag=None):
    if customTag:
        tags = customTag.split("::")
        for tag in tags:
            current_damage_cause = "custom_%s" % tag if damage_cause == "custom" else damage_cause
            damage_last_hurt_time = GetExtraDataComp(entity_id).GetExtraData("damage_last_hurt_time_%s" % current_damage_cause)
            if damage_last_hurt_time:
                return damage_last_hurt_time
        return 0

    damage_last_hurt_time = GetExtraDataComp(entity_id).GetExtraData("damage_last_hurt_time_%s" % damage_cause)
    return damage_last_hurt_time if damage_last_hurt_time else 0


def SetEntityDamageLastHurtTime(entity_id, damage_cause="all", customTag=None):
    if damage_cause == "custom" and customTag:
        damage_cause = "custom_%s" % customTag
    GetExtraDataComp(entity_id).SetExtraData("damage_last_hurt_time_%s" % damage_cause, time.time())


def GetDamageIntervalTime():
    damage_interval_time = EmptyDataServerApi.GetExtraDataLevel("damage_interval_time")
    return damage_interval_time if damage_interval_time else 0.5


def GetEntityPastLastHurtTime(entity_id, damage_cause="all", customTag=None):
    if customTag:
        tags = customTag.split("::")
        for tag in tags:
            if GetCauseIsForceDamage(tag):
                return True
            if GetCauseIsImmuneHurtTime(tag) or GetEntityDamageLastHurtTime(entity_id, damage_cause, customTag=tag) == 0:
                return True
            if (time.time() - GetEntityDamageLastHurtTime(entity_id, damage_cause, customTag=tag)) >= GetDamageIntervalTime():
                return True
        return False

    if customTag and GetCauseIsForceDamage(customTag):
        return True
    if GetCauseIsImmuneHurtTime(customTag) or GetEntityDamageLastHurtTime(entity_id, damage_cause, customTag) == 0:
        return True
    return (time.time() - GetEntityDamageLastHurtTime(entity_id, damage_cause, customTag)) >= GetDamageIntervalTime()


def GetEntitiesSyncedHealthFromSource(source_entity_id):
    """
    获取与指定实体同步生命且未过期的所有目标实体ID列表。

    :param source_entity_id: 源实体ID
    :type source_entity_id: str
    :return: 与该源实体同步且未过期的所有目标实体ID列表
    :rtype: list
    """
    sync_targets = []
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()

    for entity_id in all_entities:
        if GetEntityHealthSource(entity_id) == source_entity_id:
            sync_targets.append(entity_id)

    return sync_targets


def GetEntityHealthSource(entity_id):
    """
    获取指定实体的生命值来源实体ID。

    :param entity_id: 目标实体ID
    :type entity_id: str
    :return: 如果存在未过期的生命值来源实体ID，则返回该ID，否则返回 None
    :rtype: str or None
    """
    extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
    current_time = time.time()
    for key, value in extra_data.items():
        if key.startswith("sync_health_from_") and isinstance(value, (int, float)):
            # 检查同步是否过期
            if value == float('inf') or current_time < value:
                return key.replace("sync_health_from_", "")

    return None


def SetEntityHealthSync(target_entity_id, source_entity_id=None, sync_state=True, duration_time=0):
    """
    设置其他实体是否需要同步生命值给目标实体。如果目标实体已经被同步，则取消旧的同步，应用新的同步。

    :param target_entity_id: 目标实体ID（例如A）
    :param source_entity_id: 发起同步的实体ID（例如B）
    :param sync_state: 是否同步，True 为同步，False 为不同步
    :param duration_time: 同步持续时间，0 表示永久同步
    """
    sync_key = "sync_health_from_%s" % source_entity_id

    if sync_state:
        # 检查目标实体是否已经有来自其他实体的同步关系
        extra_data = copy.deepcopy(GetExtraDataComp(target_entity_id).GetWholeExtraData())

        for key in extra_data:
            if key.startswith("sync_health_from_"):
                existing_sync = key
                # 如果目标实体已经有同步关系，先取消旧的同步关系
                GetExtraDataComp(target_entity_id).CleanExtraData(existing_sync)
                if DEVELOPMENT:
                    print("取消了实体 {} 与实体 {} 的旧同步关系。".format(target_entity_id, existing_sync.replace("sync_health_from_", "")))

        GetExtraDataComp(target_entity_id).SetExtraData(sync_key, float('inf') if duration_time == 0 else time.time() + duration_time)
        if DEVELOPMENT:
            print("实体 {} 现在被实体 {} 同步。".format(target_entity_id, source_entity_id))
        return True
    else:
        extra_data = copy.deepcopy(GetExtraDataComp(target_entity_id).GetWholeExtraData())

        if source_entity_id is None:
            # 如果没有传入 source_entity_id 且 sync_state 为 False，清除所有同步关系
            for key in extra_data:
                if key.startswith("sync_health_from_"):
                    GetExtraDataComp(target_entity_id).CleanExtraData(key)
                    if DEVELOPMENT:
                        print("取消了实体 {} 的所有同步关系。".format(target_entity_id))
        else:
            # 如果传入了 source_entity_id，清除指定的同步关系
            sync_key = "sync_health_from_%s" % source_entity_id
            if sync_key in extra_data:
                GetExtraDataComp(target_entity_id).CleanExtraData(sync_key)
                if DEVELOPMENT:
                    print("取消了实体 {} 与实体 {} 的同步关系。".format(target_entity_id, source_entity_id))
        return True


def CleanUpExpiredHealthSyncs():
    """
    清理所有实体中过期的同步生命值数据。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("sync_health_from_") and isinstance(value, (int, float)):
                if value != float('inf') and current_time >= value:
                    keys_to_delete.append(key)

        # 删除过期的同步生命值状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期同步生命值数据: {}".format(entity_id, keys_to_delete))


def SyncHealthForEntity(entity_id):
    """
    同步所有与传入实体ID有关联的生命值。包括与该实体同步的目标实体和该实体的生命值来源。

    :param entity_id: 需要同步的实体ID
    :type entity_id: str
    """
    source_entity_id = GetEntityHealthSource(entity_id)
    if source_entity_id:
        EmptyHealthServerApi.SetEntityAHealthToMatchEntityBPercentage(entity_id, source_entity_id)


def SyncAllEntitiesHealth():
    """
    定时同步所有需要同步生命值的实体。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()

    for entity_id in all_entities:
        SyncHealthForEntity(entity_id)


def GetEntityDamageModifier(entity_id, damage_cause="all", customTag=None):
    if customTag:
        tags = customTag.split("::")
        for tag in tags:
            current_damage_cause = "custom_%s" % tag if damage_cause == "custom" else damage_cause
            data = GetExtraDataComp(entity_id).GetExtraData("damage_modifier_%s" % current_damage_cause)
            if data:
                modifier = data.get("modifier", 0.0)
                expiration_time = data.get("expiration_time", 0.0)
                if time.time() < expiration_time or expiration_time == float('inf'):
                    return modifier
        return 0.0  # 如果所有tag都没有找到对应的修正值，则返回0.0

    data = GetExtraDataComp(entity_id).GetExtraData("damage_modifier_%s" % damage_cause)
    if data:
        modifier = data.get("modifier", 0.0)
        expiration_time = data.get("expiration_time", 0.0)
        if time.time() < expiration_time or expiration_time == float('inf'):
            return modifier

    return 0.0  # 默认返回0.0表示无增减幅


def SetEntityDamageModifier(entity_id, modifier=None, damage_cause="all", customTag=None, duration_time=0):
    if damage_cause == "custom" and customTag:
        damage_cause = "custom_%s" % customTag

    if modifier is None or modifier == 0.0:
        # 如果modifier为None或0.0，清除对应的伤害修正值
        GetExtraDataComp(entity_id).CleanExtraData("damage_modifier_%s" % damage_cause)
        if DEVELOPMENT:
            print("清除了实体 {} 的伤害修正：{}".format(entity_id, damage_cause))
    else:
        expiration_time = float('inf') if duration_time == 0 else time.time() + duration_time

        data = {
            "modifier": modifier,
            "expiration_time": expiration_time
        }

        GetExtraDataComp(entity_id).SetExtraData("damage_modifier_%s" % damage_cause, data)

        if DEVELOPMENT:
            print("设置了实体 {} 的伤害修正：{}，修正值：{}，过期时间：{}".format(entity_id, damage_cause, modifier, expiration_time))


def CleanUpExpiredDamageModifiers():
    """
    清理所有实体中过期的伤害修正值。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("damage_modifier_"):
                if isinstance(value, dict):
                    expiration_time = value.get("expiration_time", 0.0)
                    if expiration_time != float('inf') and current_time >= expiration_time:
                        keys_to_delete.append(key)

        # 删除过期的伤害修正值
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期伤害修正值: {}".format(entity_id, keys_to_delete))


def GetEntityDamageModifierFromSource(entity_id, source_entity_id):
    if source_entity_id is None:
        return 0.0

    data = GetExtraDataComp(entity_id).GetExtraData("damage_modifier_from_%s" % source_entity_id)

    if data:
        modifier = data.get("modifier", 0.0)
        expiration_time = data.get("expiration_time", 0.0)

        if time.time() < expiration_time or expiration_time == float('inf'):
            return modifier

    return 0.0  # 默认返回0.0表示无增减幅


def SetEntityDamageModifierFromSource(entity_id, source_entity_id, modifier, duration_time=0):
    if source_entity_id is None:
        return

    if modifier is None or modifier == 0.0:
        # 如果modifier为None或0.0，清除对应的伤害修正值
        GetExtraDataComp(entity_id).CleanExtraData("damage_modifier_from_%s" % source_entity_id)
        if DEVELOPMENT:
            print("清除了实体 {} 对来自实体 {} 的伤害修正".format(entity_id, source_entity_id))
    else:
        expiration_time = float('inf') if duration_time == 0 else time.time() + duration_time

        data = {
            "modifier": modifier,
            "expiration_time": expiration_time
        }

        GetExtraDataComp(entity_id).SetExtraData("damage_modifier_from_%s" % source_entity_id, data)

        if DEVELOPMENT:
            print("设置了实体 {} 对来自实体 {} 的伤害修正值：{}，过期时间：{}".format(entity_id, source_entity_id, modifier, expiration_time))


def CleanUpExpiredDamageModifiersFromSources():
    """
    清理所有实体中过期的、来源于特定实体的伤害修正值。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("damage_modifier_from_"):
                if isinstance(value, dict):
                    expiration_time = value.get("expiration_time", 0.0)
                    if expiration_time != float('inf') and current_time >= expiration_time:
                        keys_to_delete.append(key)

        # 删除过期的伤害修正值
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期来源伤害修正值: {}".format(entity_id, keys_to_delete))


def GetEntityRealDamageForCustomTag(entity_id, damage_cause="all", customTag=None):
    if customTag:
        tags = customTag.split("::")
        for tag in tags:
            current_damage_cause = "custom_%s" % tag if damage_cause == "custom" else damage_cause
            data = GetExtraDataComp(entity_id).GetExtraData("real_damage_%s" % current_damage_cause)
            if data:
                state = data.get("state", False)
                expiration_time = data.get("expiration_time", 0.0)
                if time.time() < expiration_time or expiration_time == float('inf'):
                    return state
        return False

    data = GetExtraDataComp(entity_id).GetExtraData("real_damage_%s" % damage_cause)
    if data:
        state = data.get("state", False)
        expiration_time = data.get("expiration_time", 0.0)
        if time.time() < expiration_time or expiration_time == float('inf'):
            return state

    return False


def SetEntityRealDamageForCustomTag(entity_id, damage_cause="all", customTag=None, state=True, duration_time=0):
    if damage_cause == "custom" and customTag:
        damage_cause = "custom_%s" % customTag

    if state is None or state is False:
        # 如果state为False或None，清除对应的真实伤害状态
        GetExtraDataComp(entity_id).CleanExtraData("real_damage_%s" % damage_cause)
        if DEVELOPMENT:
            print("清除了实体 {} 在 cause: {} 和标签: {} 下的真实伤害状态".format(entity_id, damage_cause, customTag))
    else:
        expiration_time = float('inf') if duration_time == 0 else time.time() + duration_time

        data = {
            "state": True,
            "expiration_time": expiration_time
        }

        GetExtraDataComp(entity_id).SetExtraData("real_damage_%s" % damage_cause, data)

        if DEVELOPMENT:
            print("设置了实体 {} 在 cause: {} 和标签: {} 下的真实伤害状态，过期时间：{}".format(entity_id, damage_cause, customTag, expiration_time))


def CleanUpExpiredRealDamageForCustomTags():
    """
    清理所有实体中过期的真实伤害状态，基于 damage_cause 和 customTag。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("real_damage_"):
                if isinstance(value, dict):
                    expiration_time = value.get("expiration_time", 0.0)
                    if expiration_time != float('inf') and current_time >= expiration_time:
                        keys_to_delete.append(key)

        # 删除过期的真实伤害状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期真实伤害状态: {}".format(entity_id, keys_to_delete))


def SetEntityRealDamageFromSource(entity_id, source_entity_id, state=True, duration_time=0):
    if source_entity_id is None:
        return

    if state is None or state is False:
        # 如果state为False或None，清除对应的真实伤害状态
        GetExtraDataComp(entity_id).CleanExtraData("real_damage_from_%s" % source_entity_id)
        if DEVELOPMENT:
            print("清除了实体 {} 对来自实体 {} 的真实伤害状态".format(entity_id, source_entity_id))
    else:
        expiration_time = float('inf') if duration_time == 0 else time.time() + duration_time

        data = {
            "state": True,
            "expiration_time": expiration_time
        }

        GetExtraDataComp(entity_id).SetExtraData("real_damage_from_%s" % source_entity_id, data)

        if DEVELOPMENT:
            print("设置了实体 {} 对来自实体 {} 的真实伤害状态，过期时间：{}".format(entity_id, source_entity_id, expiration_time))


def GetEntityRealDamageFromSource(entity_id, source_entity_id):
    if source_entity_id is None:
        return False

    data = GetExtraDataComp(entity_id).GetExtraData("real_damage_from_%s" % source_entity_id)

    if data:
        state = data.get("state", False)
        expiration_time = data.get("expiration_time", 0.0)

        if time.time() < expiration_time or expiration_time == float('inf'):
            return state

    return False  # 默认返回False表示不是真实伤害


def CleanUpExpiredRealDamageFromSources():
    """
    清理所有实体中过期的、来自特定实体的真实伤害状态。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("real_damage_from_"):
                if isinstance(value, dict):
                    expiration_time = value.get("expiration_time", 0.0)
                    if expiration_time != float('inf') and current_time >= expiration_time:
                        keys_to_delete.append(key)

        # 删除过期的真实伤害状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期来自来源实体的真实伤害状态: {}".format(entity_id, keys_to_delete))


def GetEntityPercentageDamageForCustomTag(entity_id, damage_cause="all", customTag=None):
    if customTag:
        tags = customTag.split("::")
        for tag in tags:
            current_damage_cause = "custom_%s" % tag if damage_cause == "custom" else damage_cause
            key = "percentage_damage_%s" % current_damage_cause
            data = GetExtraDataComp(entity_id).GetExtraData(key)
            if data:
                percentage = data.get("percentage", 0.0)
                expiration_time = data.get("expiration_time", 0.0)
                if time.time() < expiration_time or expiration_time == float('inf'):
                    return percentage
        return 0.0

    key = "percentage_damage_%s" % damage_cause
    data = GetExtraDataComp(entity_id).GetExtraData(key)
    if data:
        percentage = data.get("percentage", 0.0)
        expiration_time = data.get("expiration_time", 0.0)
        if time.time() < expiration_time or expiration_time == float('inf'):
            return percentage

    return 0.0


def SetEntityPercentageDamageForCustomTag(entity_id, percentage, damage_cause="all", customTag=None, duration_time=0):
    if damage_cause == "custom" and customTag:
        damage_cause = "custom_%s" % customTag

    key = "percentage_damage_%s" % damage_cause

    if percentage is None or percentage == 0.0:
        # 如果percentage为None或0.0，清除对应的百分比伤害状态
        GetExtraDataComp(entity_id).CleanExtraData(key)
        if DEVELOPMENT:
            print("清除了实体 {} 的百分比伤害状态：{}".format(entity_id, key))
    else:
        expiration_time = float('inf') if duration_time == 0 else time.time() + duration_time

        data = {
            "percentage": percentage,
            "expiration_time": expiration_time
        }

        GetExtraDataComp(entity_id).SetExtraData(key, data)

        if DEVELOPMENT:
            print("设置了实体 {} 的百分比伤害状态：{}，百分比：{}，过期时间：{}".format(entity_id, key, percentage, expiration_time))


def CleanUpExpiredPercentageDamageForCustomTags():
    """
    清理所有实体中过期的、基于 damage_cause 和 customTag 的百分比伤害状态。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("percentage_damage_"):
                if isinstance(value, dict):
                    expiration_time = value.get("expiration_time", 0.0)
                    if expiration_time != float('inf') and current_time >= expiration_time:
                        keys_to_delete.append(key)

        # 删除过期的百分比伤害状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期百分比伤害状态: {}".format(entity_id, keys_to_delete))


def GetEntityPercentageDamageFromSource(entity_id, source_entity_id):
    if source_entity_id is None:
        return 0.0

    key = "percentage_damage_from_%s" % source_entity_id

    data = GetExtraDataComp(entity_id).GetExtraData(key)

    if data:
        percentage = data.get("percentage", 0.0)
        expiration_time = data.get("expiration_time", 0.0)

        if time.time() < expiration_time or expiration_time == float('inf'):
            return percentage

    return 0.0  # 默认返回0.0表示无百分比伤害


def SetEntityPercentageDamageFromSource(entity_id, percentage, source_entity_id, duration_time=0):
    if source_entity_id is None:
        return

    key = "percentage_damage_from_%s" % source_entity_id

    if percentage is None or percentage == 0.0:
        # 如果percentage为None或0.0，清除对应的百分比伤害状态
        GetExtraDataComp(entity_id).CleanExtraData(key)
        if DEVELOPMENT:
            print("清除了实体 {} 的百分比伤害状态：{}".format(entity_id, key))
    else:
        expiration_time = float('inf') if duration_time == 0 else time.time() + duration_time

        data = {
            "percentage": percentage,
            "expiration_time": expiration_time
        }

        GetExtraDataComp(entity_id).SetExtraData(key, data)

        if DEVELOPMENT:
            print("设置了实体 {} 的百分比伤害状态：{}，百分比：{}，过期时间：{}".format(entity_id, key, percentage, expiration_time))


def CleanUpExpiredPercentageDamageFromSources():
    """
    清理所有实体中过期的、基于 source_entity_id 的百分比伤害状态。
    """
    all_entities = EmptyGameServerApi.GetEngineActorList() + EmptyGameServerApi.GetAllPlayerList()
    current_time = time.time()

    for entity_id in all_entities:
        extra_data = EmptyDataServerApi.GetEntityAllExtraData(entity_id)
        keys_to_delete = []

        for key, value in extra_data.items():
            if key.startswith("percentage_damage_from_"):
                if isinstance(value, dict):
                    expiration_time = value.get("expiration_time", 0.0)
                    if expiration_time != float('inf') and current_time >= expiration_time:
                        keys_to_delete.append(key)

        # 删除过期的百分比伤害状态
        for key in keys_to_delete:
            GetExtraDataComp(entity_id).CleanExtraData(key)

        if keys_to_delete and DEVELOPMENT:
            print("清理了实体 {} 的过期百分比伤害状态: {}".format(entity_id, keys_to_delete))


def CleanUpAllExpiredData():
    """
    统一调用所有的清理方法，清理实体中过期的免疫状态、同步伤害数据、
    对来自特定实体的免疫状态，以及同步死亡状态数据。
    """
    CleanUpExpiredImmunities()
    CleanUpExpiredSyncs()
    CleanUpExpiredEntitySpecificImmunities()
    CleanUpExpiredSyncDeathStatuses()
    CleanUpExpiredHealthSyncs()
    CleanUpExpiredDamageModifiers()
    CleanUpExpiredDamageModifiersFromSources()
    CleanUpExpiredRealDamageForCustomTags()
    CleanUpExpiredRealDamageFromSources()
    CleanUpExpiredPercentageDamageForCustomTags()
    CleanUpExpiredPercentageDamageFromSources()

    if DEVELOPMENT:
        print("已执行所有清理方法。")
