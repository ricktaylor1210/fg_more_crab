# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


def ReverseClientKeyValue(key, config_name=ModName, is_global=True):
    """
    反转传入的client—config-key的值，仅适用于bool类型

    :param key: key
    :type key: str
    :param config_name: config_name
    :type config_name: str
    :param is_global: 是否全局数据
    :type is_global: bool
    :return: 反转后的key-value
    :rtype: bool
    """
    clientConfig = ConfigClient.GetConfigData(config_name, is_global)
    current_value = clientConfig.get(key, False)
    clientConfig[key] = not current_value
    ConfigClient.SetConfigData(config_name, clientConfig, is_global)
    return clientConfig[key]


def SetClientKeyValue(key, value, config_name=ModName, is_global=True):
    """
    设置client的key的value
    :param key: key
    :type key: str
    :param value: value
    :type value: any
    :param config_name: config_name
    :type config_name: str
    :param is_global: 是否全局数据
    :type is_global: bool
    :return: value
    :rtype: any
    """
    clientConfig = ConfigClient.GetConfigData(config_name, is_global)
    clientConfig[key] = value
    ConfigClient.SetConfigData(config_name, clientConfig, is_global)
    return value


def GetClientKeyValue(key, default=None, config_name=ModName, is_global=True):
    """
    获取 client的key值
    :param key: key
    :type key: str
    :param default: default value
    :type default: any
    :param config_name: config_name
    :type config_name: str
    :param is_global: 是否全局数据
    :type is_global: bool
    :return: value
    :rtype: any
    """
    clientConfig = ConfigClient.GetConfigData(config_name, is_global)
    return clientConfig.get(key, default)
