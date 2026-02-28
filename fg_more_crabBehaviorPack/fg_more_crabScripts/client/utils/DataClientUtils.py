# -*- coding: utf-8 -*-
from ..ClientBaseUtils import *

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
    clientConfig = GetCompConfigClientLevel().GetConfigData(config_name, is_global)
    clientConfig[key] = value
    GetCompConfigClientLevel().SetConfigData(config_name, clientConfig, is_global)
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
    clientConfig = GetCompConfigClientLevel().GetConfigData(config_name, is_global)
    return clientConfig.get(key, default)
