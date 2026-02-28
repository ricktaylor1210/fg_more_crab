# -*- coding: utf-8 -*-
import time
import copy
import random
import uuid
import math
import json
import traceback
import logging
import threading

from mod.common.utils.mcmath import Vector3, Quaternion

CanUnlockTime = time.mktime((2025, 2, 1, 20, 0, 0, 0, 0, 0))
IN_DEVELOPMENT = False
DEVELOPMENT_LEVEL = logging.ERROR

FGModName = "FGGeneralModName"
# Mod Version
ModName = "fg_more_crab"
MOD_VERSION = "1.0.0"
ConfigVersion = MOD_VERSION.replace(".", "_")

ModScriptFilePath = "%sScripts" % ModName

# Client System
ClientSystemName = "%sClientSystem" % ModName
ClientSystemClsPath = ModScriptFilePath + ".client.ClientMainSystem.ClientMainSystem"

# Server System
ServerSystemName = "%sServerSystem" % ModName
ServerSystemClsPath = ModScriptFilePath + ".server.ServerMainSystem.ServerMainSystem"


def SetDevelopmentMessage(level, message, *args):
    """
    根据 DEVELOPMENT_LEVEL 级别输出日志信息（兼容不可序列化对象）
    :param level: 日志级别
    :param message: 日志消息，支持 format 或 %
    :param args: 可变参数
    """
    global DEVELOPMENT_LEVEL

    # 开关太低或者配置不正确时直接跳过，避免额外开销
    if not isinstance(DEVELOPMENT_LEVEL, int) or level < DEVELOPMENT_LEVEL:
        return

    def safe_serialize(obj):
        """
        将任意对象转换为可读字符串：
        1. 优先使用 json 序列化，方便在日志里看结构化数据
        2. json 不支持则退回到 str()
        3. str() 还失败就给一个兜底占位符
        """
        try:
            return json.dumps(obj, indent=2, ensure_ascii=False)
        except Exception:
            try:
                return str(obj)
            except Exception:
                return "<Unserializable: {}>".format(type(obj).__name__)

    def build_fallback_message(msg, processed):
        """
        兜底拼接：无论上面的格式化逻辑出什么问题，
        都至少把原始 message 和参数列表打出来，保证调试信息不丢。
        """
        if processed:
            return "{} | 参数: {}".format(msg, ", ".join(processed))
        return msg

    def format_with_best_effort(msg, processed):
        """
        尝试按约定的两种格式语法进行格式化：
        1. 如果包含 '{}'，优先尝试 str.format
        2. 否则如果包含 '%'，尝试旧式 % 格式化
        3. 任何格式化异常都在这里吞掉并用兜底形式输出
        这样“占位符和参数不匹配”这类问题不会影响游戏逻辑。
        """
        # 没有参数就直接用原始 message
        if not processed:
            return msg

        # 尝试 str.format 风格
        if "{}" in msg:
            try:
                return msg.format(*processed)
            except Exception:
                # 格式化失败（占位符太多、类型不匹配等） -> 兜底
                return build_fallback_message(msg, processed)

        # 尝试 % 风格
        if "%" in msg:
            try:
                return msg % tuple(processed)
            except Exception:
                # 同样兜底
                return build_fallback_message(msg, processed)

        # 没有任何占位符，直接把参数挂在后面
        return build_fallback_message(msg, processed)

    try:
        # 先把所有参数安全地转成字符串，避免后续格式化再抛异常
        processed_args = [safe_serialize(arg) for arg in args]

        # 用“尽最大努力”的方式格式化
        core_message = format_with_best_effort(message, processed_args)

        # 统一加上前缀，便于在日志里筛选
        formatted_message = "[Development] " + core_message

        logging.log(level, formatted_message)

    except Exception as e:
        # 能到这里说明是“更底层”的异常（比如 logging 本身问题），
        # 而不是简单的字符串格式写错，这种仍然保留你原来的策略。
        if IN_DEVELOPMENT:
            # 开发环境：抛出完整异常，保留 traceback，方便追根溯源
            raise
        else:
            # 线上环境：只输出兜底日志，避免游戏逻辑中断
            print("[Development] 日志处理失败：{} | 参数: {} | 错误: {}".format(
                message, args, e
            ))

def get_setting_major_version(mod_version):
    """
    提取用于【配置存档隔离】的“设置大版本号”。

    当前策略：只看 X.Y.Z 里的第一个数字 X。
    比如：
      - 4.0.5 -> "4"
      - 4.1.0 -> "4"
      - 5.0.0 -> "5"

    以后如果你想改成“前两位一起算大版本”（比如 4.0 / 4.1 分开），
    只需要改这里的实现，不用动 Client / ServerSetting 的代码。
    """
    if not mod_version:
        # 兜底，避免 None 或空串时直接炸
        return "1"

    parts = str(mod_version).split(".")
    # 至少返回第一段；为空时也给个兜底
    return parts[0] or "1"


# 用于配置存档的“大版本号”
SettingMajorVersion = get_setting_major_version(MOD_VERSION)
