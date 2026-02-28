# -*- coding: utf-8 -*-

from ..ClientBaseUtils import *



def GetBlockName(pos):
    """
    获取指定位置和维度的方块的名称

    :param pos: 需要设获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]

    :return: 方块名称
    :rtype: str or None
    """
    block_info = GetCompBlockInfoLevel().GetBlock(pos)
    return block_info[0]

def GetBlockIsAir(pos):
    """
    获取指定位置和维度的方块是否为空气

    :param pos: 需要获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]

    :return: 是否是空气
    :rtype: bool
    """
    block_name = GetBlockName(pos)
    return block_name == "minecraft:air" if block_name else False

def GetBlockIsWater(pos):
    """
    获取指定位置和维度的方块是否为水

    :param pos: 需要获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]

    :return: 是否是水
    :rtype: bool
    """
    block_name = GetBlockName(pos)
    return block_name in {"minecraft:flowing_water", "minecraft:water"} if block_name else False

def GetBlankBlockPalette():
    """
    获取一个空白的方块调色板。

    :return: 返回生成的方块调色板实例，如获取失败则返回None
    :rtype: BlockPaletteComponent or None
    """
    return GetCompBlockLevel().GetBlankBlockPalette()


def DeserializeBlockPalette(data_dict):
    """
    反序列化方块调色板数据字典中的数据，将块调色板数据字典中的数据输入到已经实例化的方块调色板实例中，用于方块调色板在客户端及服务端的事件数据之间传输。

    :param data_dict: 调色板数据字典
    :type data_dict: dict

    :return: 返回生成的方块调色板实例，如获取失败则返回None
    :rtype: BlockPaletteComponent or None
    """
    block_palette_instance = GetBlankBlockPalette()
    if block_palette_instance:
        deserialize_result = block_palette_instance.DeserializeBlockPalette(data_dict)
        if deserialize_result:
            return block_palette_instance
    return None


CanPassBlockSet = {'minecraft:red_mushroom', 'minecraft:dead_brain_coral', 'minecraft:azalea_leaves_flowered',
                   'minecraft:fire', 'minecraft:leaves2', 'minecraft:white_tulip', 'minecraft:bubble_coral',
                   'minecraft:deadbush', 'minecraft:azalea_leaves', 'minecraft:dead_bubble_coral',
                   'minecraft:pink_petals', 'minecraft:cyan_carpet', 'minecraft:flowing_water',
                   'minecraft:warped_roots', 'minecraft:poppy', 'minecraft:allium', 'minecraft:short_grass',
                   'minecraft:brain_coral', 'minecraft:light_blue_carpet', 'minecraft:horn_coral',
                   'minecraft:lily_of_the_valley', 'minecraft:oak_sapling', 'minecraft:green_carpet',
                   'minecraft:birch_sapling', 'minecraft:white_carpet', 'minecraft:pitcher_plant',
                   'minecraft:peony', 'minecraft:air', 'minecraft:dead_tube_coral',
                   'minecraft:mangrove_propagule', 'minecraft:crimson_roots', 'minecraft:brown_mushroom',
                   'minecraft:ladder', 'minecraft:seagrass', 'minecraft:golden_rail', 'minecraft:rail',
                   'minecraft:oxeye_daisy', 'minecraft:rose_bush', 'minecraft:cornflower',
                   'minecraft:gray_carpet', 'minecraft:azure_bluet', 'minecraft:detector_rail',
                   'minecraft:yellow_carpet', 'minecraft:tall_grass', 'minecraft:red_tulip',
                   'minecraft:dead_horn_coral', 'minecraft:torchflower', 'minecraft:acacia_sapling',
                   'minecraft:lilac', 'minecraft:pink_carpet', 'minecraft:activator_rail',
                   'minecraft:spruce_sapling', 'minecraft:crimson_fungus', 'minecraft:blue_orchid',
                   'minecraft:brown_carpet', 'minecraft:orange_carpet', 'minecraft:sunflower',
                   'minecraft:orange_tulip', 'minecraft:jungle_sapling', 'minecraft:magenta_carpet',
                   'minecraft:water', 'minecraft:yellow_flower', 'minecraft:web', 'minecraft:leaves',
                   'minecraft:wither_rose', 'minecraft:red_carpet', 'minecraft:tube_coral',
                   'minecraft:lime_carpet', 'minecraft:fire_coral', 'minecraft:blue_carpet', 'minecraft:vine',
                   'minecraft:light_gray_carpet', 'minecraft:black_carpet', 'minecraft:dead_fire_coral',
                   'minecraft:pink_tulip', 'minecraft:dark_oak_sapling', 'minecraft:cherry_sapling',
                   'minecraft:purple_carpet', 'minecraft:magenta_carpet', 'minecraft:pink_carpet',
                   'minecraft:gray_carpet', 'minecraft:blue_carpet', 'minecraft:purple_carpet',
                   'minecraft:yellow_carpet', 'minecraft:light_blue_carpet', 'minecraft:red_carpet',
                   'minecraft:green_carpet', 'minecraft:cyan_carpet', 'minecraft:white_carpet',
                   'minecraft:snow_layer', 'minecraft:light_gray_carpet', 'minecraft:brown_carpet',
                   'minecraft:orange_carpet', 'minecraft:lime_carpet',
                   'minecraft:black_carpet'}
