# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api import EmptyGameClientApi as GameApi
from fg_more_crabScripts.client.api.EmptyBaseClientApi import *

AutoUnlockJumpTimer = None
AutoUnlockAllControlTimer = None


def GetPickFacingData():
    """
    获取准星选中的实体或者方块。

    :return: pickData
    :rtype: dict[]
        选中目标为实体时，返回值为：
        {
            "type": "Entity",
            "entityId":  entityId
        }
        选中目标为方块时，返回值为：
        {
            "type": "Block",
            "x":  x,
            "y":  y,
            "z":  z,
            "face": face
        }
        没有选中目标时，返回值为：
        {
            "type": "None"
        }
    """
    return CompCamera.PickFacing()


def GetPickFacingEntity():
    """
    获取准星选中的实体。

    :return: entityId
    :rtype: str or None
    """
    pick_data = GetPickFacingData()
    if pick_data["type"] == "Entity":
        return pick_data["entityId"]
    return None


def GetEntityPos(entity_id):
    """
    根据传入的entity_id获取实体的位置坐标。
    对于非玩家，获取到的是脚底部位的位置
    对于玩家，如果处于行走，站立，游泳，潜行，滑翔状态，获得的位置比脚底位置高1.62；如果处于睡觉状态，获得的位置比最低位置高0.2
    类似接口有GetFootPos，对任何实体都是获取脚底部位的位置

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 位置坐标 (x, y, z)
    :rtype: tuple[float,float,float] or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_pos = GetPosComp(entity_id).GetPos()
    return entity_pos if entity_pos else None


def GetEntityFootPos(entity_id):
    """
    根据传入的entity_id获取实体的脚下位置坐标。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 脚下位置坐标 (x, y, z)
    :rtype: tuple[float,float,float] or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_foot_pos = GetPosComp(entity_id).GetFootPos()
    return entity_foot_pos if entity_foot_pos else None


def GetEntityModAttr(entity_id, attr_name, default_value=None, attr_mod_name=ModName):
    """
    获取entity自定义的mod属性
    :param entity_id: entity_id
    :type entity_id: str
    :param attr_name: attr_name
    :type attr_name: str
    :param default_value: default_value
    :type default_value: any
    :param attr_mod_name: get_mod_name
    :type attr_mod_name: str
    :return: 自定义的mod属性
    :rtype: any
    """
    return GetModAttrComp(entity_id).GetAttr(attr_mod_name + attr_name, default_value)


def GetOwnerId(entity_id):
    """
    获取驯服生物的主人id

    :param entity_id: entity_id
    :type entity_id: str
    :return: Owner
    :rtype: str or None
    """
    return GetTameComp(entity_id).GetOwnerId()


def GetEntityCenterPos(entity_id):
    """
    获取entity_id的中间位置

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 中间位置
    :rtype: tuple[float,float,float] or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_pos = GetEntityPos(entity_id)
    entity_foot_pos = GetEntityFootPos(entity_id)
    if entity_pos is None or entity_foot_pos is None:
        return None
    x1, y1, z1 = entity_pos
    x2, y2, z2 = entity_foot_pos
    return (x1 + x2) / 2.0, (y1 + y2) / 2.0, (z1 + z2) / 2.0


def GetEntityMotion(entity_id):
    """
    根据传入的entity_id获取实体的Motion。
    获取生物的瞬时移动方向向量。与服务端不同，客户端不会计算摩擦等因素，获取到的是上一帧的向量，与服务器获取到的值会不相等

    :param entity_id: 实体ID
    :type entity_id: str

    :return: Motion (x, y, z)
    :rtype: tuple[float,float,float] or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_motion = GetActionMotionComp(entity_id).GetMotion()
    return entity_motion if entity_motion else None


def GetEntityRot(entity_id):
    """
    获取实体头与水平方向的俯仰角度和竖直方向的旋转角度

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 旋转角度 俯仰角度及绕竖直方向旋转的角度，单位为度而不是弧度
    :rtype: tuple[float,float] or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_rot = GetEntityRotComp(entity_id).GetRot()
    return entity_rot if entity_rot else None


def GetEntityDir(entity_id):
    """
    根据传入的entity_id获取实体的方向向量。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 方向向量 (x, y, z)
    :rtype: tuple[float,float,float] or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_rot = GetEntityRot(entity_id)
    if entity_rot:
        entity_dir = ClientApi.GetDirFromRot(entity_rot)
        if entity_dir:
            return entity_dir
    return None


def SetEntityMotion(entity_id, motion=(0, 0, 0)):
    """
    设置entity_id的motion
    如果频繁快速修改本地玩家的瞬时移动向量，可能会触发引擎服务端的反作弊机制（例如掉落伤害），需要频繁快速修改时最好搭配服务端SetMotion同步修改

    :param entity_id: 实体ID
    :type entity_id: str

    :param motion: motion
    :type motion: tuple[float,float,float]

    :return: 设置结果
    :rtype: bool
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return False
    set_result = GetActionMotionComp(entity_id).SetMotion(motion)
    if set_result and entity_id == LocalPlayerId:
        ClientMain.NotifyToServer("SyncPlayerMotionEvent", {"motion": motion})
    return set_result


def GetEngineTypeStr(entity_id):
    """
    根据传入的entity_id获取实体的类型字符串。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 类型字符串
    :rtype: str or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_type_str = GetEntityTypeComp(entity_id).GetEngineTypeStr()
    return entity_type_str if entity_type_str else None


def GetEngineType(entity_id):
    """
    根据传入的entity_id获取实体的类型。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 类型
    :rtype: int or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_type = GetEntityTypeComp(entity_id).GetEngineType()
    return entity_type if entity_type else None


def CheckEngineTypeIsSelectType(entity_id, select_type):
    """
    检测entity是否是select_type,注意,此接口不一定能返回正确的结果,例如一个mob可能会属于item,可以用其他方式来判定,例如tag和family

    :param entity_id: 实体ID
    :type entity_id: str

    :param select_type: select_type
    :type select_type: MinecraftEnum.EntityType

    :return: 是否是select_type
    :rtype: bool
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return False
    return GetEngineType(entity_id) & select_type == select_type


def GetEntitySize(entity_id):
    """
    根据传入的entity_id获取实体的大小。

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 包围盒大小
    :rtype: tuple[float,float] or None
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return None
    entity_size = GetCollisionBoxComp(entity_id).GetSize()
    return entity_size if entity_size else None


def LockMoveAndJump(is_lock):
    """
    锁定或解锁实体的移动和跳跃能力。

    :param is_lock: True表示锁定，False表示解锁
    :type is_lock: bool
    """
    global AutoUnlockJumpTimer
    if AutoUnlockJumpTimer:
        GameApi.CancelTimer(AutoUnlockJumpTimer)
    CompOperation.SetCanMove(not is_lock)
    CompOperation.SetCanJump(not is_lock)


def LockMoveAndJumpAndAutoUnlock(un_lock_time=2.0):
    """
    锁定实体的移动和跳跃能力，在un_lock_time之后自动解锁。

    :param un_lock_time: 自动解锁的时间
    :type un_lock_time: float
    """
    LockMoveAndJump(True)
    global AutoUnlockJumpTimer
    if AutoUnlockJumpTimer:
        GameApi.CancelTimer(AutoUnlockJumpTimer)
    AutoUnlockJumpTimer = GameApi.AddTimer(un_lock_time, LockMoveAndJump, False)


def LockPlayerAllControl(is_lock):
    """
    锁定玩家的所有控制能力

    :param is_lock: True表示锁定，False表示解锁
    :type is_lock: bool
    """
    global AutoUnlockAllControlTimer
    if AutoUnlockAllControlTimer:
        GameApi.CancelTimer(AutoUnlockAllControlTimer)
        AutoUnlockAllControlTimer = None
    LockMoveAndJump(is_lock)
    CompOperation.SetCanDrag(not is_lock)
    CompOperation.SetCanAttack(not is_lock)
    CompOperation.SetCanInair(not is_lock)
    CompOperation.SetCanPause(not is_lock)
    CompOperation.SetCanOpenInv(not is_lock)
    CompOperation.SetCanPerspective(not is_lock)
    CompOperation.SetCanScreenShot(not is_lock)
    CompOperation.SetCanWalkMode(not is_lock)
    CompOperation.SetMoveLock(not is_lock)
    if is_lock:
        GetActionMotionComp(LocalPlayerId).LockInputVector((0, 0))
        GetActionMotionComp(LocalPlayerId).LockVerticalMove(True)
    else:
        GetActionMotionComp(LocalPlayerId).UnlockInputVector()
        GetActionMotionComp(LocalPlayerId).UnLockVerticalMove()


def LockPlayerAllControlAndAutoUnlock(un_lock_time=2.0):
    """
    锁定玩家的所有控制能力，在un_lock_time之后自动解锁。

    :param un_lock_time: 自动解锁的时间
    :type un_lock_time: float or int
    """
    LockPlayerAllControl(True)
    global AutoUnlockAllControlTimer
    if AutoUnlockAllControlTimer:
        GameApi.CancelTimer(AutoUnlockAllControlTimer)
        AutoUnlockAllControlTimer = None
    AutoUnlockAllControlTimer = GameApi.AddTimer(un_lock_time, LockPlayerAllControl, False)


def CheckEntityIsPlayer(entity_id):
    """
    检测传入的entity_id是否是玩家

    :param entity_id: 实体ID
    :type entity_id: str

    :return: 是否是玩家
    :rtype: bool
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return False
    return entity_id in GameApi.GetAllPlayerList()


def CheckEntityIsItemEntity(entity_id):
    if not GameApi.GetEntityIsAlive(entity_id):
        return False
    return GetEngineType(entity_id) == MinecraftEnum.EntityType.ItemEntity


def CheckEntityIsProject(entity_id):
    if not GameApi.GetEntityIsAlive(entity_id):
        return False
    return CheckEngineTypeIsSelectType(entity_id, MinecraftEnum.EntityType.Projectile)


def CheckEntityIsMoveBlock(entity_id):
    if not GameApi.GetEntityIsAlive(entity_id):
        return False
    return GetEngineType(entity_id) in [MinecraftEnum.EntityType.FallingBlock, MinecraftEnum.EntityType.MovingBlock]


def CheckEntityIsMob(entity_id):
    """
    获取实体是否是生物
    :param entity_id: entity_id
    :type entity_id: str
    :return: 是否是生物
    :rtype: bool
    """
    if not GameApi.GetEntityIsAlive(entity_id):
        return False
    return CheckEngineTypeIsSelectType(entity_id, MinecraftEnum.EntityType.Mob)
