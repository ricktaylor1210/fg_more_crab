# -*- coding: utf-8 -*-

from fg_more_crabScripts.server.api import EmptyAttributeServerApi as AttributeApi
from fg_more_crabScripts.server.api import EmptyGameServerApi as GameApi
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *

_spawn_item_retry_count_dict = {}


def UnwrapUserData(data):
    if isinstance(data, dict) and '__type__' in data and '__value__' in data:
        return data['__value__']
    return data


def WrapUserData(data, data_type=None):
    if isinstance(data, bool):  # Byte (True/False)
        return {'__type__': 1, '__value__': data}
    elif isinstance(data, int):
        if -(2 ** 15) <= data < (2 ** 15):  # Short
            return {'__type__': 2, '__value__': data}
        elif -(2 ** 31) <= data < (2 ** 31):  # Int
            return {'__type__': 3, '__value__': data}
        elif -(2 ** 63) <= data < (2 ** 63):  # Int64
            return {'__type__': 4, '__value__': data}
    elif isinstance(data, float):
        if data_type == 5:  # Float
            return {'__type__': 5, '__value__': data}
        else:  # Double
            return {'__type__': 6, '__value__': data}
    elif isinstance(data, list):
        if all(isinstance(i, int) for i in data):  # IntArray or ByteArray
            if data_type == 7:  # ByteArray
                return {'__type__': 7, '__value__': data}
            else:  # IntArray
                return {'__type__': 11, '__value__': data}
        else:  # List (recursive conversion)
            return {'__type__': 9, '__value__': [WrapUserData(i) for i in data]}
    elif isinstance(data, dict):  # Compound (recursive conversion)
        return {'__type__': 10, '__value__': {k: WrapUserData(v) for k, v in data.items()}}
    elif isinstance(data, str):  # String
        return {'__type__': 8, '__value__': data}
    else:
        raise ValueError("Unsupported data type")


def ChangeItemDurability(entity_id, pos_type, slot_pos, durability, is_diff=True):
    """
    更改物品的耐久度。

    :param entity_id: 实体ID
    :type entity_id: str

    :param pos_type: 位置类型
    :type pos_type: int

    :param slot_pos: 槽位位置
    :type slot_pos: int or None

    :param durability: 要更改的耐久度值
    :type durability: int

    :param is_diff: 如果为True，将durability视为增量或减量并添加到当前耐久度上。如果为False，直接将durability值设置为新的耐久度。
    :type is_diff: bool

    :return: set_result
    :rtype bool
    """
    if is_diff:
        if GetItemMaxDurability(entity_id, pos_type, slot_pos, False):
            return False
        current_durability = GetItemDurability(entity_id, pos_type, slot_pos)
        if current_durability is None or current_durability == 0:
            return False

        new_durability = current_durability + durability
        new_durability = max(new_durability, 0)
        return SetItemDurability(entity_id, pos_type, slot_pos, new_durability)
    else:
        return SetItemDurability(entity_id, pos_type, slot_pos, durability)


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
    max_durability = GetItemMaxDurability(entity_id, pos_type, slot_pos, False)
    if max_durability is None or max_durability == 0:
        return False

    if percentage == 0:
        new_durability = 0  # 直接设置耐久度为0
    elif is_diff:
        # 获取当前耐久度
        current_durability = GetItemDurability(entity_id, pos_type, slot_pos)
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
    return SetItemDurability(entity_id, pos_type, slot_pos, new_durability)


def GetDurabilityPercentage(entity_id, pos_type, slot_pos):
    """
    获取当前耐久度占最大耐久度的百分比。

    :param entity_id: 实体ID
    :type entity_id: str

    :param pos_type: 位置类型
    :type pos_type: int

    :param slot_pos: 槽位位置
    :type slot_pos: int or None

    :return: 当前耐久度占最大耐久度的百分比（0-100），如果无法获取耐久度信息，则返回None
    :rtype float or None
    """
    current_durability = GetItemDurability(entity_id, pos_type, slot_pos)
    max_durability = GetItemMaxDurability(entity_id, pos_type, slot_pos, False)

    if current_durability is None or max_durability is None or max_durability == 0:
        return None

    return (current_durability / max_durability) * 100


def GetDurabilityFromPercentage(entity_id, pos_type, slot_pos, percentage):
    """
    根据传入的百分比计算对应的耐久度数值。

    :param entity_id: 实体ID
    :type entity_id: str

    :param pos_type: 位置类型
    :type pos_type: int

    :param slot_pos: 槽位位置
    :type slot_pos: int or None

    :param percentage: 百分比值（0-100）
    :type percentage: float

    :return: 对应的耐久度数值，如果无法获取最大耐久度信息，则返回None
    :rtype int or None
    """
    max_durability = GetItemMaxDurability(entity_id, pos_type, slot_pos, False)

    if max_durability is None or max_durability == 0:
        return None

    return int((percentage / 100.0) * max_durability)


def GetItemDurability(entity_id, pos_type, slot_pos):
    """
    获取指定槽位的物品耐久

    :param entity_id: entity_id
    :type entity_id: str

    :param pos_type: pos_type
    :type pos_type: int

    :param slot_pos: slot_pos
    :type slot_pos:int or None

    :return: int
    :rtype durability
    """
    return GetItemComp(entity_id).GetItemDurability(pos_type, slot_pos)


def GetItemMaxDurability(entity_id, pos_type, slot_pos, is_user_data=False):
    """
    获取指定槽位的最大物品耐久

    :param entity_id: entity_id
    :type entity_id: str

    :param pos_type: pos_type
    :type pos_type: int

    :param slot_pos: slot_pos
    :type slot_pos:int or None

    :param is_user_data: 如果为True，则只尝试获取该物品userData特殊设置的值，没有特殊设置过则返回0。如果为False，则会先尝试获取userData中的值，没有的话获取该类物品通用值。
    :type is_user_data:bool

    :return: int
    :rtype max_durability
    """
    return GetItemComp(entity_id).GetItemMaxDurability(pos_type, slot_pos, is_user_data)


def SetItemDurability(entity_id, pos_type, slot_pos, durability):
    """
    设置物品的耐久值

    :param entity_id: entity_id
    :type entity_id: str

    :param pos_type: pos_type
    :type pos_type: int

    :param slot_pos: slot_pos
    :type slot_pos:int or None

    :param durability: durability
    :type durability:  int

    :return: set_result
    :rtype bool
    """
    return GetItemComp(entity_id).SetItemDurability(pos_type, slot_pos, durability)


def SetItemMaxDurability(entity_id, pos_type, slot_pos, max_durability, is_user_data=False):
    """
    设置物品的最大耐久值
        若物品堆叠数量大于1时，耐久度的变更对整一叠的物品生效。并且耐久度为0后，每次消耗耐久度的行为会使数量减一
        为物品设置的userData最大耐久度在计算时优先级最高，userData数据存盘。
        在砂轮或背包合并时，若两个物品都有userData，只会保留其中一个。在铁砧中修复时，最大耐久取被修复物品的耐久。
        当最大耐久值被更改时，当前耐久度也会按比例修复。
        对同一类所有物品设置的最大耐久度不存盘，每次重启世界都会重新初始化，可以通过对应item json的minecraft:max_damage组件设置初始化最大耐久度
        如果设置的是背包物品，当slot值为-1时，设置左手物品的最大耐久值

    :param entity_id: entity_id
    :type entity_id: str

    :param pos_type: pos_type
    :type pos_type: int

    :param slot_pos: slot_pos
    :type slot_pos:int or None

    :param max_durability: max_durability(0-32767)
    :type max_durability:  int

    :param is_user_data: 如果为True，则该设置只对指定物品生效，如果为False，则对同一类所有物品生效
    :type is_user_data:bool

    :return: set_result
    :rtype bool
    """
    return GetItemComp(entity_id).SetItemMaxDurability(pos_type, slot_pos, max_durability, is_user_data)


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
    return CompBlockInfo.SpawnResources(block_identifier, spawn_pos, block_aux, probability, bonus_loot_level, dimension_id, allow_randomness)


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
            spawn_dimension_id = AttributeApi.GetEntityDimension(self.spawn_entity_id)
            if spawn_dimension_id is None:
                GameApi.AddTimer(0.5, self.SpawnEntityItemToLevel)
                return
            spawn_pos = AttributeApi.GetEntityCenterPos(self.spawn_entity_id)
            if spawn_pos is None:
                GameApi.AddTimer(0.5, self.SpawnEntityItemToLevel)
                return
            res = CompItem.SpawnItemToLevel(self.spawn_item_dict, spawn_dimension_id, spawn_pos)
            if not res:
                GameApi.AddTimer(0.5, self.SpawnEntityItemToLevel)

    spawn_item_class(entity_id, item_dict)


def CheckPlayerItemApi(player_id, item_name, item_aux=0, count=1):
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
        item_dict_list = GetItemComp(player_id).GetPlayerAllItems(pos_type)
        for index, item_dict in enumerate(item_dict_list):
            if item_dict and item_dict["newItemName"] == item_name and item_dict["newAuxValue"] == item_aux and item_dict["count"] >= count:
                return pos_type, index
    return None, None


def SetPlayerItem(player_id, pos_type, slot_pos=0, item_dict=None):
    """
    根据传入的信息设置玩家指定物品槽位的物品数量。

    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param pos_type: 物品所在的位置类型。
    :type pos_type: int
    :param item_dict: 物品信息字典，没有物品则返回None
    :type item_dict: dict or None
    :param slot_pos: 物品所在的位置索引。
    :type slot_pos: int

    :return:设置成功返回True
    :rtype:bool
    """
    if item_dict is None:
        item_dict = {'itemName': 'minecraft:air', 'count': 1, 'auxValue': 0}
    return GetItemComp(player_id).SetEntityItem(pos_type, item_dict, slot_pos)


def SpawnItemToPlayerCarried(player_id, item_dict):
    """
    生成物品到玩家背包
    当slotPos不设置时，当设置的数量超过单个槽位堆叠的上限时，会将多余的物品设置到另外的空闲槽位.如果生成的物品与背包中有的槽位的物品种类一致，该接口也会将物品增加到这些槽位中。注意：如果背包中剩余的物品数目和增加的物品数目之和大于64，则会生成物品数目到64，但是接口返回失败。


    :param player_id: 指定的玩家ID。
    :type player_id: str
    :param item_dict: 物品信息字典，没有物品则返回None
    :type item_dict: dict or None

    :return:设置成功返回True
    :rtype:bool
    """
    return GetItemComp(player_id).SpawnItemToPlayerCarried(item_dict, player_id)


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
        spawn_res = GetItemComp(player_id).SpawnItemToPlayerInv(item_dict, player_id)
    else:
        spawn_res = GetItemComp(player_id).SpawnItemToPlayerInv(item_dict, player_id, slot_pos)
    if fail_need_spawn_to_level and not spawn_res:
        SpawnEntityItemToLevel(item_dict, player_id)
    return spawn_res


def SetPlayerItemCountApi(player_id, pos_type, pos_index, count=1, diff=False):
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
    item_dict = GetPlayerItem(player_id, pos_type, pos_index, True)
    if diff:
        item_dict["count"] += count  # 相对变化
    else:
        item_dict["count"] = count  # 绝对值设置
    itemsDictMap[(pos_type, pos_index)] = item_dict
    GetItemComp(player_id).SetPlayerAllItems(itemsDictMap)


def GetPlayerItem(player_id, pos_type, slot_pos, get_user_data=False):
    """
    获取右手物品的信息

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
    return GetItemComp(player_id).GetPlayerItem(pos_type, slot_pos, get_user_data)


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


def AddEnchantToInvItem(player_id, slot_pos, enchant_type, level):
    """
    给物品栏的物品添加附魔信息。

    :param player_id: 玩家ID
    :type player_id: str

    :param slot_pos: 物品栏槽位
    :type slot_pos: int

    :param enchant_type: 附魔类型
    :type enchant_type: int

    :param level: 附魔等级
    :type level: int

    :return: 设置结果，成功返回True，失败返回False
    :rtype bool
    """
    comp = GetItemComp(player_id)
    return comp.AddEnchantToInvItem(slot_pos, enchant_type, level)


def AddModEnchantToInvItem(player_id, slot_pos, mod_enchant_id, level):
    """
    给物品栏中物品添加自定义附魔信息。

    :param player_id: 玩家ID
    :type player_id: str

    :param slot_pos: 物品栏槽位
    :type slot_pos: int

    :param mod_enchant_id: 自定义附魔identifier
    :type mod_enchant_id: str

    :param level: 自定义附魔等级
    :type level: int

    :return: 设置结果，成功返回True，失败返回False
    :rtype bool
    """
    comp = GetItemComp(player_id)
    return comp.AddModEnchantToInvItem(slot_pos, mod_enchant_id, level)


def GetInvItemEnchantData(player_id, slot_pos):
    """
    获取物品栏的物品附魔信息。

    :param player_id: 玩家ID
    :type player_id: str

    :param slot_pos: 物品栏槽位
    :type slot_pos: int

    :return: 附魔信息列表，每个tuple由附魔类型和附魔等级组成
    :rtype list[tuple(int, int)]
    """
    comp = GetItemComp(player_id)
    return comp.GetInvItemEnchantData(slot_pos)


def GetInvItemModEnchantData(player_id, slot_pos):
    """
    获取物品栏的物品自定义附魔信息。

    :param player_id: 玩家ID
    :type player_id: str

    :param slot_pos: 物品栏槽位
    :type slot_pos: int

    :return: 自定义附魔信息列表，每个tuple由自定义附魔ID和附魔等级组成
    :rtype list[tuple(str, int)]
    """
    comp = GetItemComp(player_id)
    return comp.GetInvItemModEnchantData(slot_pos)


def RemoveEnchantToInvItem(player_id, slot_pos, enchant_type):
    """
    给物品栏的物品移除附魔信息。

    :param player_id: 玩家ID
    :type player_id: str

    :param slot_pos: 物品栏槽位
    :type slot_pos: int

    :param enchant_type: 附魔类型
    :type enchant_type: int

    :return: 移除结果，成功返回True，失败返回False
    :rtype bool
    """
    comp = GetItemComp(player_id)
    return comp.RemoveEnchantToInvItem(slot_pos, enchant_type)


def RemoveModEnchantToInvItem(player_id, slot_pos, mod_enchant_id):
    """
    给物品栏中物品移除自定义附魔信息。

    :param player_id: 玩家ID
    :type player_id: str

    :param slot_pos: 物品栏槽位
    :type slot_pos: int

    :param mod_enchant_id: 自定义附魔identifier
    :type mod_enchant_id: str

    :return: 移除结果，成功返回True，失败返回False
    :rtype bool
    """
    comp = GetItemComp(player_id)
    return comp.RemoveModEnchantToInvItem(slot_pos, mod_enchant_id)


def GetPlayerStandardEnchant(player_id, pos_type, slot_pos, get_user_data=False):
    """
    获取物品的标准附魔信息。

    :param player_id: 玩家ID。
    :type player_id: str

    :param pos_type: 物品所在位置的类型（例如：背包、装备栏等）。
    :type pos_type: int

    :param slot_pos: 物品在物品栏中的槽位位置。
    :type slot_pos: int

    :param get_user_data: 是否获取物品的userData，默认为False。
    :type get_user_data: bool

    :return: 标准附魔信息列表，格式为[(EnchantType, 等级)]，没有附魔则返回空列表。
    :rtype: list
    """
    # 获取物品信息字典
    item_dict = GetPlayerItem(player_id, pos_type, slot_pos, get_user_data)

    if item_dict is None:
        return []

    # 提取标准附魔信息
    enchant_data = item_dict.get('enchantData', [])

    return enchant_data


def GetPlayerModEnchant(player_id, pos_type, slot_pos, get_user_data=False):
    """
    获取物品的自定义附魔信息。

    :param player_id: 玩家ID。
    :type player_id: str

    :param pos_type: 物品所在位置的类型（例如：背包、装备栏等）。
    :type pos_type: int

    :param slot_pos: 物品在物品栏中的槽位位置。
    :type slot_pos: int

    :param get_user_data: 是否获取物品的userData，默认为False。
    :type get_user_data: bool

    :return: 自定义附魔信息列表，格式为[(自定义附魔ID, 等级)]，没有附魔则返回空列表。
    :rtype: list
    """
    # 获取物品信息字典
    item_dict = GetPlayerItem(player_id, pos_type, slot_pos, get_user_data)

    if item_dict is None:
        return []

    # 提取自定义附魔信息
    mod_enchant_data = item_dict.get('modEnchantData', [])

    return mod_enchant_data


def HasStandardEnchant(player_id, pos_type, slot_pos, enchant_type, get_user_data=False):
    """
    检测物品是否含有指定的标准附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param pos_type: 物品所在位置的类型（例如：背包、装备栏等）。
    :type pos_type: int

    :param slot_pos: 物品在物品栏中的槽位位置。
    :type slot_pos: int

    :param enchant_type: 要检测的标准附魔类型（枚举类型）。
    :type enchant_type: int

    :param get_user_data: 是否获取物品的userData，默认为False。
    :type get_user_data: bool

    :return: 如果物品含有指定的标准附魔，返回True；否则返回False。
    :rtype: bool
    """
    # 获取物品的标准附魔信息
    enchant_data = GetPlayerStandardEnchant(player_id, pos_type, slot_pos, get_user_data)

    # 遍历标准附魔数据，检测是否含有指定的附魔类型
    for e_type, level in enchant_data:
        if e_type == enchant_type:
            return True

    return False


def HasModEnchant(player_id, pos_type, slot_pos, mod_enchant_id, get_user_data=False):
    """
    检测物品是否含有指定的自定义附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param pos_type: 物品所在位置的类型（例如：背包、装备栏等）。
    :type pos_type: int

    :param slot_pos: 物品在物品栏中的槽位位置。
    :type slot_pos: int

    :param mod_enchant_id: 要检测的自定义附魔的ID。
    :type mod_enchant_id: str

    :param get_user_data: 是否获取物品的userData，默认为False。
    :type get_user_data: bool

    :return: 如果物品含有指定的自定义附魔，返回True；否则返回False。
    :rtype: bool
    """
    # 获取物品的自定义附魔信息
    mod_enchant_data = GetPlayerModEnchant(player_id, pos_type, slot_pos, get_user_data)

    # 遍历自定义附魔数据，检测是否含有指定的自定义附魔ID
    for enchant_id, level in mod_enchant_data:
        if enchant_id == mod_enchant_id:
            return True

    return False


def GetStandardEnchantLevel(player_id, pos_type, slot_pos, enchant_type, get_user_data=False):
    """
    获取物品的指定标准附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param pos_type: 物品所在位置的类型（例如：背包、装备栏等）。
    :type pos_type: int

    :param slot_pos: 物品在物品栏中的槽位位置。
    :type slot_pos: int

    :param enchant_type: 要检测的标准附魔类型（枚举类型）。
    :type enchant_type: int

    :param get_user_data: 是否获取物品的userData，默认为False。
    :type get_user_data: bool

    :return: 如果找到该标准附魔，返回其等级；如果未找到，返回None。
    :rtype: int or None
    """
    # 获取物品的标准附魔信息
    enchant_data = GetPlayerStandardEnchant(player_id, pos_type, slot_pos, get_user_data)

    # 遍历标准附魔数据，查找指定附魔类型的等级
    for e_type, level in enchant_data:
        if e_type == enchant_type:
            return level

    return None


def GetModEnchantLevel(player_id, pos_type, slot_pos, mod_enchant_id, get_user_data=False):
    """
    获取物品的指定自定义附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param pos_type: 物品所在位置的类型（例如：背包、装备栏等）。
    :type pos_type: int

    :param slot_pos: 物品在物品栏中的槽位位置。
    :type slot_pos: int

    :param mod_enchant_id: 要检测的自定义附魔ID。
    :type mod_enchant_id: str

    :param get_user_data: 是否获取物品的userData，默认为False。
    :type get_user_data: bool

    :return: 如果找到该自定义附魔，返回其等级；如果未找到，返回None。
    :rtype: int or None
    """
    # 获取物品的自定义附魔信息
    mod_enchant_data = GetPlayerModEnchant(player_id, pos_type, slot_pos, get_user_data)

    # 遍历自定义附魔数据，查找指定自定义附魔ID的等级
    for enchant_id, level in mod_enchant_data:
        if enchant_id == mod_enchant_id:
            return level

    return None


def HasRightHandStandardEnchant(player_id, enchant_type):
    """
    检测右手物品是否含有指定标准附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param enchant_type: 标准附魔类型（枚举类型）。
    :type enchant_type: int

    :return: 如果物品含有指定的标准附魔，返回True，否则返回False。
    :rtype: bool
    """
    return HasStandardEnchant(player_id, MinecraftEnum.ItemPosType.CARRIED, 0, enchant_type)


def HasRightHandModEnchant(player_id, mod_enchant_id):
    """
    检测右手物品是否含有指定自定义附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param mod_enchant_id: 自定义附魔ID。
    :type mod_enchant_id: str

    :return: 如果物品含有指定的自定义附魔，返回True，否则返回False。
    :rtype: bool
    """
    return HasModEnchant(player_id, MinecraftEnum.ItemPosType.CARRIED, 0, mod_enchant_id)


def GetRightHandStandardEnchantLevel(player_id, enchant_type):
    """
    获取右手物品的指定标准附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param enchant_type: 标准附魔类型（枚举类型）。
    :type enchant_type: int

    :return: 附魔等级，若物品不含有指定附魔，则返回None。
    :rtype: int or None
    """
    return GetStandardEnchantLevel(player_id, MinecraftEnum.ItemPosType.CARRIED, 0, enchant_type)


def GetRightHandModEnchantLevel(player_id, mod_enchant_id):
    """
    获取右手物品的指定自定义附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param mod_enchant_id: 自定义附魔ID。
    :type mod_enchant_id: str

    :return: 附魔等级，若物品不含有指定附魔，则返回None。
    :rtype: int or None
    """
    return GetModEnchantLevel(player_id, MinecraftEnum.ItemPosType.CARRIED, 0, mod_enchant_id)


def HasLeftHandStandardEnchant(player_id, enchant_type):
    """
    检测左手物品是否含有指定标准附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param enchant_type: 标准附魔类型（枚举类型）。
    :type enchant_type: int

    :return: 如果物品含有指定的标准附魔，返回True，否则返回False。
    :rtype: bool
    """
    return HasStandardEnchant(player_id, MinecraftEnum.ItemPosType.OFFHAND, 0, enchant_type)


def HasLeftHandModEnchant(player_id, mod_enchant_id):
    """
    检测左手物品是否含有指定自定义附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param mod_enchant_id: 自定义附魔ID。
    :type mod_enchant_id: str

    :return: 如果物品含有指定的自定义附魔，返回True，否则返回False。
    :rtype: bool
    """
    return HasModEnchant(player_id, MinecraftEnum.ItemPosType.OFFHAND, 0, mod_enchant_id)


def GetLeftHandStandardEnchantLevel(player_id, enchant_type):
    """
    获取左手物品的指定标准附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param enchant_type: 标准附魔类型（枚举类型）。
    :type enchant_type: int

    :return: 附魔等级，若物品不含有指定附魔，则返回None。
    :rtype: int or None
    """
    return GetStandardEnchantLevel(player_id, MinecraftEnum.ItemPosType.OFFHAND, 0, enchant_type)


def GetLeftHandModEnchantLevel(player_id, mod_enchant_id):
    """
    获取左手物品的指定自定义附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param mod_enchant_id: 自定义附魔ID。
    :type mod_enchant_id: str

    :return: 附魔等级，若物品不含有指定附魔，则返回None。
    :rtype: int or None
    """
    return GetModEnchantLevel(player_id, MinecraftEnum.ItemPosType.OFFHAND, 0, mod_enchant_id)


def HasArmorStandardEnchant(player_id, slot_pos, enchant_type):
    """
    检测盔甲物品是否含有指定标准附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param slot_pos: 盔甲物品所在的槽位（0为头盔，1为胸甲，2为护腿，3为靴子）。
    :type slot_pos: int

    :param enchant_type: 标准附魔类型（枚举类型）。
    :type enchant_type: int

    :return: 如果物品含有指定的标准附魔，返回True，否则返回False。
    :rtype: bool
    """
    return HasStandardEnchant(player_id, MinecraftEnum.ItemPosType.ARMOR, slot_pos, enchant_type)


def HasArmorModEnchant(player_id, slot_pos, mod_enchant_id):
    """
    检测盔甲物品是否含有指定自定义附魔。

    :param player_id: 玩家ID。
    :type player_id: str

    :param slot_pos: 盔甲物品所在的槽位（0为头盔，1为胸甲，2为护腿，3为靴子）。
    :type slot_pos: int

    :param mod_enchant_id: 自定义附魔ID。
    :type mod_enchant_id: str

    :return: 如果物品含有指定的自定义附魔，返回True，否则返回False。
    :rtype: bool
    """
    return HasModEnchant(player_id, MinecraftEnum.ItemPosType.ARMOR, slot_pos, mod_enchant_id)


def GetArmorStandardEnchantLevel(player_id, slot_pos, enchant_type):
    """
    获取盔甲物品的指定标准附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param slot_pos: 盔甲物品所在的槽位（0为头盔，1为胸甲，2为护腿，3为靴子）。
    :type slot_pos: int

    :param enchant_type: 标准附魔类型（枚举类型）。
    :type enchant_type: int

    :return: 附魔等级，若物品不含有指定附魔，则返回None。
    :rtype: int or None
    """
    return GetStandardEnchantLevel(player_id, MinecraftEnum.ItemPosType.ARMOR, slot_pos, enchant_type)


def GetArmorModEnchantLevel(player_id, slot_pos, mod_enchant_id):
    """
    获取盔甲物品的指定自定义附魔等级。

    :param player_id: 玩家ID。
    :type player_id: str

    :param slot_pos: 盔甲物品所在的槽位（0为头盔，1为胸甲，2为护腿，3为靴子）。
    :type slot_pos: int

    :param mod_enchant_id: 自定义附魔ID。
    :type mod_enchant_id: str

    :return: 附魔等级，若物品不含有指定附魔，则返回None。
    :rtype: int or None
    """
    return GetModEnchantLevel(player_id, MinecraftEnum.ItemPosType.ARMOR, slot_pos, mod_enchant_id)
