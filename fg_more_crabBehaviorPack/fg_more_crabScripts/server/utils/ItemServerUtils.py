# -*- coding: utf-8 -*-
from . import AttributeServerUtils
from ..ServerBaseUtils import *


def GetPlayerItem(player_id, pos_type, slot_pos, get_user_data=False):
    """
    获取玩家物品的信息

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param pos_type: 指定的玩家ID。
    :type pos_type: int
    :param slot_pos: 指定的玩家ID。
    :type slot_pos: int
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品信息字典，没有物品则返回None
    :rtype:dict or None
    """
    return CompFactory.CreateItem(player_id).GetPlayerItem(pos_type, slot_pos, get_user_data)


def GetCarriedItem(player_id, get_user_data=False):
    """
    获取右手物品的信息

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品信息字典，没有物品则返回None
    :rtype:dict or None
    """
    return GetPlayerItem(player_id, MinecraftEnum.ItemPosType.CARRIED, 0, get_user_data)


def GetCarriedItemName(player_id, get_user_data=False):
    """
    获取右手物品的名称

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品名称
    :rtype:str or None
    """
    item_dict = GetCarriedItem(player_id, get_user_data)
    return item_dict["newItemName"] if item_dict else None


def GetOffhandItem(player_id, get_user_data=False):
    """
    获取左手物品的信息

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品信息字典，没有物品则返回None
    :rtype:dict or None
    """
    return GetPlayerItem(player_id, MinecraftEnum.ItemPosType.OFFHAND, 0, get_user_data)


def GetOffhandItemName(player_id, get_user_data=False):
    """
    获取左手物品的名称

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param get_user_data:是否获取物品的userData，默认为False
    :type get_user_data:bool
    :return:物品名称
    :rtype:str or None
    """
    item_dict = GetOffhandItem(player_id, get_user_data)
    return item_dict["newItemName"] if item_dict else None

def CheckPlayerHasItem(player_id, item_name, item_aux=0, count=1):
    """
    检查指定玩家是否拥有特定属性的物品。

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param item_name: 物品名称。
    :type item_name: str
    :param item_aux: 物品的附加属性值。
    :type item_aux: int
    :param count: 需要检查的物品数量。
    :type count: int

    :return: 返回物品所在的位置类型和索引，如果没有找到则返回None。
    :rtype: tuple[int, int] or tuple[None, None]
    """
    for pos_type in range(4):
        item_dict_list = CompFactory.CreateItem(player_id).GetPlayerAllItems(pos_type)
        for index, item_dict in enumerate(item_dict_list):
            if item_dict and item_dict["newItemName"] == item_name and item_dict["newAuxValue"] == item_aux and item_dict["count"] >= count:
                return pos_type, index
    return None, None

def SpawnEntityItemToLevel(item_dict, entity_id):
    """
    根据传入的物品字典和实体ID，生成物品到游戏世界中。

    :param item_dict: 描述物品属性的字典。
    :type item_dict: dict
    :param entity_id: 指定的实体ID。
    :type entity_id: str

    """

    class spawn_item_class(object):
        def __init__(self, spawn_entity_id, spawn_item_dict):
            self.spawn_retry_count = 0
            self.spawn_entity_id = spawn_entity_id
            self.spawn_item_dict = spawn_item_dict
            self.SpawnEntityItemToLevel()

        def SpawnEntityItemToLevel(self):
            self.spawn_retry_count += 1
            if self.spawn_retry_count > 10:
                return
            spawn_dimension_id = CompFactory.CreateDimension(self.spawn_entity_id).GetEntityDimensionId()
            if spawn_dimension_id is None:
                GetCompGameLevel().AddTimer(0.5, self.SpawnEntityItemToLevel)
                return
            spawn_pos = AttributeServerUtils.GetEntityCenterPos(self.spawn_entity_id)
            if spawn_pos is None:
                GetCompGameLevel().AddTimer(0.5, self.SpawnEntityItemToLevel)
                return
            res = GetServerMainSystem().CreateEngineItemEntity(self.spawn_item_dict, spawn_dimension_id, spawn_pos)
            if not res:
                GetCompGameLevel().AddTimer(0.5, self.SpawnEntityItemToLevel)

    spawn_item_class(entity_id, item_dict)


def SpawnItemByBlock(block_identifier, spawn_pos, block_aux=0, probability=1, bonus_loot_level=0, dimension_id=-1, allow_randomness=True):
    """
    产生方块随机掉落（该方法不适用于实体方块）
    时运等级[bonusLootLevel]只对部分方块生效 掉落概率[probability]对部分农作物树叶不生效
    可在对应维度的常加载区块产生掉落

    :param block_identifier:方块的identifier，如minecraft:wool
    :type block_identifier:str
    :param spawn_pos:掉落位置
    :type spawn_pos:tuple[int or float,int or float,int or float]
    :param block_aux:方块的附加值
    :type block_aux:int
    :param probability:掉落概率，范围为[0, 1]，0为不掉落，1为100%掉落
    :type probability:float
    :param bonus_loot_level:时运等级，默认为0
    :type bonus_loot_level:int
    :param dimension_id:掉落方块的维度，默认值为-1，传入非负值时用于获取产生方块掉落的维度；否则将随机挑选一个存在玩家的维度产生掉落
    :type dimension_id:int
    :param allow_randomness:是否允许随机采集，默认为True，如果为False，掉落概率probability无效
    :type allow_randomness:bool
    :return:是否成功
    :rtype:bool
    """
    return GetCompBlockInfoLevel().SpawnResources(block_identifier, spawn_pos, block_aux, probability, bonus_loot_level, dimension_id, allow_randomness)

def SpawnItemToPlayerInv(player_id, item_dict, slot_pos=None, fail_need_spawn_to_level=False):
    """
    生成物品到玩家背包
    当slotPos不设置时，当设置的数量超过单个槽位堆叠的上限时，会将多余的物品设置到另外的空闲槽位.如果生成的物品与背包中有的槽位的物品种类一致，该接口也会将物品增加到这些槽位中。注意：如果背包中剩余的物品数目和增加的物品数目之和大于64，则会生成物品数目到64，但是接口返回失败。


    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param item_dict: 物品信息字典，没有物品则返回None
    :type item_dict: dict or None
    :param slot_pos: 物品所在的位置索引。
    :type slot_pos: int or None
    :param fail_need_spawn_to_level: 失败了是否要生成到世界。
    :type fail_need_spawn_to_level: bool

    :return:设置成功返回True
    :rtype:bool
    """
    if slot_pos is None:
        spawn_res = CompFactory.CreateItem(player_id).SpawnItemToPlayerInv(item_dict, player_id)
    else:
        spawn_res = CompFactory.CreateItem(player_id).SpawnItemToPlayerInv(item_dict, player_id, slot_pos)
    if fail_need_spawn_to_level and not spawn_res:
        SpawnEntityItemToLevel(item_dict, player_id)
    return spawn_res


def GetPlayerItemCount(player_id, pos_type, pos_index):
    """
    根据传入的信息设置玩家指定物品槽位的物品数量。

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param pos_type: 物品所在的位置类型。
    :type pos_type: int
    :param pos_index: 物品所在的位置索引。
    :type pos_index: int

    """
    comp_item_player = CompFactory.CreateItem(player_id)
    item_dict = comp_item_player.GetPlayerItem(pos_type, pos_index, True)
    return item_dict["count"]

def SetPlayerItemCount(player_id, pos_type, pos_index, count=1, diff=False):
    """
    根据传入的信息设置玩家指定物品槽位的物品数量。

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param pos_type: 物品所在的位置类型。
    :type pos_type: int
    :param pos_index: 物品所在的位置索引。
    :type pos_index: int
    :param count: 需要设置的物品数量。
    :type count: int
    :param diff: 如果为True，则数量设置为相对变化；否则设置为绝对值。
    :type diff: bool

    """
    itemsDictMap = dict()
    comp_item_player = CompFactory.CreateItem(player_id)
    item_dict = comp_item_player.GetPlayerItem(pos_type, pos_index, True)
    if diff:
        item_dict["count"] += count  # 相对变化
    else:
        item_dict["count"] = count  # 绝对值设置
    itemsDictMap[(pos_type, pos_index)] = item_dict
    comp_item_player.SetPlayerAllItems(itemsDictMap)


def SetDurabilityByPercentage(entity_id, pos_type, slot_pos, percentage, is_diff=True):
    """
    根据传入的百分比修改物品的耐久度。

    :param entity_id: 实体ID
    :type entity_id: str

    :param pos_type: 位置类型
    :type pos_type: int

    :param slot_pos: 槽位位置
    :type slot_pos: int or None

    :param percentage: 要设置或增加的耐久度百分比（0-100）
    :type percentage: float

    :param is_diff: 如果为True，将百分比作为增量添加到当前耐久度上；如果为False，直接设置为百分比对应的耐久度值。
    :type is_diff: bool

    :return: 设置操作的结果，成功返回True，失败返回False
    :rtype bool
    """
    comp_item = CompFactory.CreateItem(entity_id)
    max_durability = comp_item.GetItemMaxDurability(pos_type, slot_pos, False)
    if max_durability is None or max_durability == 0:
        return False

    if percentage == 0:
        new_durability = 0  # 直接设置耐久度为0
    elif is_diff:
        # 获取当前耐久度
        current_durability = comp_item.GetItemDurability(pos_type, slot_pos)
        if current_durability is None:
            return False

        # 计算增量的耐久度值
        diff_durability = int((percentage / 100.0) * max_durability)
        new_durability = current_durability + diff_durability
        # 确保不会超过最大耐久度
        new_durability = min(new_durability, max_durability)
    else:
        # 直接计算并设置新的耐久度值
        new_durability = int((percentage / 100.0) * max_durability)

    # 设置新的耐久度
    return comp_item.SetItemDurability(pos_type, slot_pos, new_durability)
