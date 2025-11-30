# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyAttributeServerApi
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *


def GetEntityHealth(entity_id):
    """
    获取实体的生命值

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 属性结果
    :rtype: float or None
    """
    return EmptyAttributeServerApi.GetEntityAttr(entity_id, MinecraftEnum.AttrType.HEALTH)


def SetEntityHealth(entity_id, health_value):
    """
    设置实体的生命值

    :param entity_id: 实体ID
    :type entity_id: str

    :param health_value: health_value
    :type health_value: int or float


    :return: 设置结果
    :rtype: bool
    """
    current_health = GetEntityHealth(entity_id)
    if current_health == health_value:
        return True
    return EmptyAttributeServerApi.SetEntityAttr(entity_id, MinecraftEnum.AttrType.HEALTH, max(0, int(health_value)))


def GetEntityMaxHealth(entity_id):
    """
    获取实体的最大生命值

    :param entity_id: 实体ID
    :type entity_id: str


    :return: 属性结果
    :rtype: float or None
    """
    return EmptyAttributeServerApi.GetEntityMaxAttr(entity_id, MinecraftEnum.AttrType.HEALTH)


def SetEntityMaxHealth(entity_id, max_health_value):
    """
    设置实体的最大生命值

    :param entity_id: 实体ID
    :type entity_id: str


    :param max_health_value: max_health_value
    :type max_health_value: int or float


    :return: 设置结果
    :rtype: bool
    """
    return EmptyAttributeServerApi.SetEntityMaxAttr(entity_id, MinecraftEnum.AttrType.HEALTH, max_health_value)


def SetEntityHealthByDiff(entity_id, diff_health):
    """
    根据差值设置实体的生命值

    :param entity_id: 实体ID
    :type entity_id: str

    :param diff_health: diff_health
    :type diff_health: int or float

    :return: 设置结果
    :rtype: bool
    """
    current_health = GetEntityHealth(entity_id)
    new_health = current_health + diff_health
    return SetEntityHealth(entity_id, new_health)


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
    max_health = GetEntityMaxHealth(entity_id)

    if max_health is None or max_health == 0:
        return 0

    health_value = (percentage / 100.0) * max_health
    return health_value


def GetHealthPercentage(entity_id, health_value):
    """
    获取传入生命值占实体最大生命值的百分比。

    :param entity_id: 实体ID
    :type entity_id: str

    :param health_value: 传入的生命值
    :type health_value: float or int

    :return: 生命值占比的百分比
    :rtype: float
    """
    max_health = GetEntityMaxHealth(entity_id)

    if max_health is None or max_health == 0:
        return 0

    percentage = (health_value / float(max_health)) * 100.0
    return percentage


def SetEntityHealthByPercentage(entity_id, percentage):
    """
    根据百分比设置实体的生命值

    :param entity_id: 实体ID
    :type entity_id: str

    :param percentage: 百分比
    :type percentage: float

    :return: 设置结果
    :rtype: bool
    """
    max_health = GetEntityMaxHealth(entity_id)

    if max_health is None:
        return None

    new_health = max_health * (percentage / 100.0)
    return SetEntityHealth(entity_id, int(new_health))


def SetEntityHealthByDiffPercentage(entity_id, diff_percentage):
    """
    根据百分比差值改变实体的生命值。

    :param entity_id: 实体ID
    :type entity_id: str

    :param diff_percentage: 要改变的百分比，正数为增加，负数为减少
    :type diff_percentage: float or int

    :return: 设置结果
    :rtype: bool
    """
    if diff_percentage is None or not isinstance(diff_percentage, (int, float)):
        logging.warn("Invalid diff_percentage provided.")
        return None  # 或者根据业务逻辑返回 False 或其他值

    max_health = GetEntityMaxHealth(entity_id)
    current_health = GetEntityHealth(entity_id)

    if max_health is None or current_health is None:
        return None

    health_change = max_health * (diff_percentage / 100.0)
    new_health = max(0, int(current_health + health_change))
    return SetEntityHealth(entity_id, new_health)


def GetCurrentHealthPercent(entity_id):
    """
    获取生物当前生命值百分比。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 生命值百分比
    :rtype: float
    """
    current_health = GetEntityHealth(entity_id)

    if current_health is None:
        return 0

    health_percent = GetHealthPercentage(entity_id, current_health)
    return health_percent


def SetEntityAHealthToMatchEntityBPercentage(entity_a_id, entity_b_id):
    """
    将生物A的生命百分比设置为生物B的生命百分比。

    :param entity_a_id: 生物A的实体ID
    :type entity_a_id: str

    :param entity_b_id: 生物B的实体ID
    :type entity_b_id: str

    :return: 设置结果
    :rtype: bool
    """
    health_percent_b = GetCurrentHealthPercent(entity_b_id)
    if health_percent_b is None:
        return None
    return SetEntityHealthByPercentage(entity_a_id, health_percent_b)
