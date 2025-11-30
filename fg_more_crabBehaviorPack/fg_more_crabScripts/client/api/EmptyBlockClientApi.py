# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


def GetBlankBlockPalette():
    """
    获取一个空白的方块调色板。

    :return: 返回生成的方块调色板实例，如获取失败则返回None
    :rtype: BlockPaletteComponent or None
    """
    return CompBlock.GetBlankBlockPalette()


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
