# -*- coding: utf-8 -*-

from ..ServerBaseUtils import *


def LockSkillButton(player_id, skill_path,priority=10):
    """
    锁定特定技能按钮，使指定的玩家不能使用该技能。

    参数：
    player_id (int): 要锁定技能的玩家的ID。
    skill_path (str/list): 要锁定的技能函数名称。

    动作：
    向客户端发送“ServerLockSkillButtonEvent”事件，通知客户端锁定该技能按钮。
    """
    GetServerMainSystem().NotifyToClient(player_id, "ServerLockSkillButtonEvent", {"skill_path": skill_path,"priority":priority})


def UnLockSkillButton(player_id, skill_path,priority=10):
    """
    解锁特定技能按钮，使指定的玩家能够再次使用该技能。

    参数：
    player_id (int): 要解锁技能的玩家的ID。
    skill_path (str/list): 要解锁的技能函数名称。

    动作：
    向客户端发送“ServerUnLockSkillButtonEvent”事件，通知客户端解锁该技能按钮。
    """
    GetServerMainSystem().NotifyToClient(player_id, "ServerUnLockSkillButtonEvent", {"skill_path": skill_path,"priority":priority})


def LockAllSkillButton(player_id,priority=10):
    """
    锁定所有技能按钮，使指定的玩家不能使用任何技能。

    参数：
    player_id (int): 要锁定技能的玩家的ID。

    动作：
    向客户端发送“ServerLockAllSkillButtonEvent”事件，通知客户端锁定所有技能按钮。
    """
    GetServerMainSystem().NotifyToClient(player_id, "ServerLockAllSkillButtonEvent", {"priority":priority})


def UnLockAllSkillButton(player_id,priority=10):
    """
    解锁所有技能按钮，使指定的玩家能够再次使用所有技能。

    参数：
    player_id (int): 要解锁技能的玩家的ID。

    动作：
    向客户端发送“ServerUnLockAllSkillButtonEvent”事件，通知客户端解锁所有技能按钮。
    """
    GetServerMainSystem().NotifyToClient(player_id, "ServerUnLockAllSkillButtonEvent", {"priority":priority})
