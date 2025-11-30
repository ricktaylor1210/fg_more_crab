# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyGameServerApi
from fg_more_crabScripts.server.api import EmptyAttributeServerApi
from fg_more_crabScripts.server.api import EmptyLocationDealServerApi
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *


def GetBlockDictByPos(pos, dimension_id=-1):
    """
    获取指定位置和维度的方块信息

    已经加载的地形才能获取方块信息，支持获取对应维度的常加载区块内方块信息
    对于有多种状态的方块，aux计算比较复杂，推荐使用GetBlockStates获取方块状态字典
    用于获取给定位置和维度（如果提供）的方块的信息。如果没有提供维度ID，将默认为-1。


    :param pos: 方块的位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    :return: 返回该位置的方块信息字典
        name	str	必须设置，方块identifier，包含命名空间及名称，如minecraft:air
        aux	int	方块附加值，可缺省，默认为0
    :rtype: dict or None
    """
    block_dict = CompBlockInfo.GetBlockNew(EmptyLocationDealServerApi.SetPosToBlockPos(pos), dimension_id)
    return block_dict if block_dict else None


def GetBlockName(pos, dimension_id=-1):
    """
    获取指定位置和维度的方块的名称

    :param pos: 需要设获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    :return: 方块名称
    :rtype: str or None
    """
    block_dict = GetBlockDictByPos(EmptyLocationDealServerApi.SetPosToBlockPos(pos), dimension_id)
    return block_dict.get("name", None) if block_dict else None


def GetBlockIsAir(pos, dimension_id=-1):
    """
    获取指定位置和维度的方块是否为空气

    :param pos: 需要获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    :return: 是否是空气
    :rtype: bool
    """
    block_name = GetBlockName(pos, dimension_id)
    return block_name == "minecraft:air" if block_name else False


def GetBlockCanPass(pos, dimension_id=-1):
    """
    获取指定位置和维度的方块能否通过

    :param pos: 需要获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    :return: 能否通过
    :rtype: bool
    """
    block_name = GetBlockName(pos, dimension_id)
    return block_name in ["minecraft:air", "minecraft:flowing_water", "minecraft:water", "minecraft:tallgrass", "minecraft:fire", "minecraft:vine",
                          "minecraft:leaves", "minecraft:azalea_leaves", "minecraft:azalea_leaves_flowered", "minecraft:leaves2", "minecraft:web",
                          "minecraft:ladder", "minecraft:rail", "minecraft:activator_rail", "minecraft:detector_rail",
                          "minecraft:golden_rail"] if block_name else False


def GetBlockIsWater(pos, dimension_id=-1):
    """
    获取指定位置和维度的方块是否为水

    :param pos: 需要获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    :return: 是否是水
    :rtype: bool
    """
    block_name = GetBlockName(pos, dimension_id)
    return block_name in ["minecraft:flowing_water", "minecraft:water"] if block_name else False


def GetBlockIsLava(pos, dimension_id=-1):
    """
    获取指定位置和维度的方块是否为岩浆

    :param pos: 需要获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    :return: 是否是岩浆
    :rtype: bool
    """
    block_name = GetBlockName(pos, dimension_id)
    return block_name in ["minecraft:flowing_lava", "minecraft:lava"] if block_name else False


def GetBlockIsHurt(pos, dimension_id=-1):
    """
    获取指定位置和维度的方块是否为伤害性方块

    :param pos: 需要获取的方块位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    :return: 是否是伤害性方块
    :rtype: bool
    """
    block_name = GetBlockName(pos, dimension_id)
    return block_name in ["minecraft:magma", "minecraft:cactus", "minecraft:campfire", "minecraft:soul_campfire", "minecraft:fire", "minecraft:sweet_berries",
                          "minecraft:wither_rose", "minecraft:flowing_lava", "minecraft:lava"] if block_name else False


def CheckSpaceCanEntityEnter(entity_id, target_pos):
    """
    判断实体的大小能否进入目标位置

    :param entity_id:entity_id
    :type entity_id:str
    :param target_pos:target_pos
    :type target_pos:tuple[int or float,int or float,int or float]
    :return:能否进入目标位置
    :rtype:bool
    """
    if not EmptyGameServerApi.GetEntityIsAlive(entity_id):
        return False

    dimension_id = EmptyAttributeServerApi.GetEntityDimension(entity_id)
    if dimension_id is None:
        return False

    entity_size = EmptyAttributeServerApi.GetEntitySize(entity_id)

    if entity_size is None:
        return False

    width, height = entity_size
    width, height = int(math.ceil(width)), int(math.ceil(height))
    half_width = int(math.ceil(width / 2.0))

    for diff_x in range(-half_width, half_width + 1):
        for diff_z in range(-half_width, half_width + 1):
            for diff_y in range(height):
                block_pos = EmptyLocationDealServerApi.ChangeValueInPos(target_pos, False, (diff_x, diff_y, diff_z))
                if not GetBlockCanPass(block_pos, dimension_id):
                    return False
    return True


def CheckEntityCanMoveToPos(entity_id, target_pos):
    """
    判断实体能否进入目标位置

    :param entity_id:entity_id
    :type entity_id:str
    :param target_pos:target_pos
    :type target_pos:pos[int or float,int or float,int or float]
    :return:能否进入目标位置
    :rtype:bool
    """

    def has_vertical_surface_to_climb(check_climb_pos):
        """
        检查攀爬类型的实体在目标位置是否至少有一面垂直表面可以攀爬。

        :return: 如果至少有一面可以攀爬的垂直表面，则返回True
        :rtype:bool
        """
        for dx, dz in [(-1, 0), (1, 0), (0, -1), (0, 1)]:  # 检查四个水平方向
            adjacent_pos = EmptyLocationDealServerApi.ChangeValueInPos(check_climb_pos, False, (dx, 0, dz))
            if not GetBlockIsAir(adjacent_pos):
                return True  # 找到一个非空气的垂直表面
        return False

    if not EmptyGameServerApi.GetEntityIsAlive(entity_id):
        return False

    navigation_type = EmptyAttributeServerApi.GetEntityNavigationType(entity_id)
    if navigation_type is None:
        return False
    dimension_id = EmptyAttributeServerApi.GetEntityDimension(entity_id)
    if dimension_id is None:
        return False
    ground_pos = EmptyLocationDealServerApi.ChangeValueInPos(target_pos, False, (0, -1, 0))
    if CheckSpaceCanEntityEnter(entity_id, target_pos):

        # 对于飞行、漂浮和悬停类型，直接返回True
        if navigation_type in ["navigation_fly", "navigation_float", "navigation_hover"]:
            return True

        # 对于水陆两栖类型，确保目标位置是空气或水
        elif navigation_type == "navigation_generic":
            return not GetBlockIsAir(ground_pos, dimension_id)

            # 对于攀爬类型，确保目标位置的下方不是空气（即有地面支持）
        elif navigation_type == "navigation_climb":
            return not GetBlockIsAir(ground_pos, dimension_id) and not GetBlockIsWater(ground_pos, dimension_id)

        # 对于陆地寻路类型，确保目标位置的下方不是空气（即有地面支持）
        elif navigation_type == "navigation_walk":
            return not GetBlockIsAir(ground_pos, dimension_id) and not GetBlockIsWater(ground_pos, dimension_id)
    elif navigation_type == "navigation_climb":
        # 对于攀爬类型，可以考虑是否有垂直表面可以攀爬
        return has_vertical_surface_to_climb(target_pos)

    return False


def SetBlock(pos, blockDict, **kwargs):
    """
    设置某一位置的方块。
    已经加载的地形才能设置方块，支持在对应维度的常加载区块内设置方块。

    注意：
    - 如果使用SetBlockNew接口替换含有方块实体的方块，在某些情况下可能需要特殊处理。
    - 对于多状态方块的`aux`值设置，推荐使用GetBlockAuxValueFromStates方法。

    :param pos: 需要设置的方块的坐标。
    :type pos: tuple[int or float,int or float,int or float]
    :param blockDict: 要设置的方块的属性字典。
    :type blockDict: dict
    :param kwargs: 可选参数，包括：
        - oldBlockHandling (int): 0表示替换，1表示销毁，2表示保留。默认为0。
        - dimension_id (int): 方块所在的维度ID。默认为-1。
        - isLegacy (bool): 是否设置为传统的`aux`。True。
        - updateNeighbors (bool): 是否给相邻的方块触发方块更新 (opens new window)以及BlockNeighborChangedServerEvent事件。默认为True触发。若选择不触发可节省约30%的性能消耗。

    :type kwargs: any

    :return: 是否成功设置方块。
    :rtype: bool
    """
    pos = EmptyLocationDealServerApi.SetPosToBlockPos(pos)
    return CompBlockInfo.SetBlockNew(pos, blockDict, kwargs.get("oldBlockHandling", 0), kwargs.get("dimension_id", -1), kwargs.get("isLegacy", True),
                                     kwargs.get("updateNeighbors", True))


def SetBlockToAir(pos, dimension_id=-1, updateNeighbors=True):
    """
    将指定位置和维度的方块设置为空气

    这个方法用于将指定位置和维度（如果提供）的方块设置为空气。如果没有提供维度ID，将默认为-1。

    :param pos: 需要设置为空气的方块位置
    :type pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int
    :param updateNeighbors: 是否给相邻的方块触发方块更新 (opens new window)以及BlockNeighborChangedServerEvent事件。默认为True触发。若选择不触发可节省约30%的性能消耗。
    :type updateNeighbors: bool

    :return: 是否成功设置方块。
    :rtype: bool

    """
    return SetBlock(pos, {"name": "minecraft:air", "aux": 0}, dimension_id=dimension_id, updateNeighbors=updateNeighbors)


def SetBlockToAirByList(pos_list, dimension_id=-1):
    """
    将指定位置list和维度的方块设置为空气

    这个方法用于将指定位置和维度（如果提供）的方块设置为空气。如果没有提供维度ID，将默认为-1。

    :param pos_list: 需要设置为空气的方块位置list
    :type pos_list: list[tuple[int or float,int or float,int or float]]
    :param dimension_id: 方块所在的维度ID，如果不提供，默认为-1
    :type dimension_id: int

    """

    for block_pos in pos_list:
        SetBlockToAir(block_pos, dimension_id)


def GetBlankBlockPalette():
    """
    获取一个空白的方块调色板

    该方法用于生成并获取一个空白的方块调色板实例。如果获取失败，将返回None。

    :return: 返回生成的方块调色板实例，如获取失败则返回None
    :rtype: BlockPaletteComponent or None
    """
    return CompBlock.GetBlankBlockPalette()


def DeserializeBlockPalette(data_dict):
    """
    反序列化方块调色板数据

    该方法用于将给定的方块调色板数据字典反序列化并填充到一个新生成的方块调色板实例中。这主要用于方块调色板在客户端和服务端之间的数据传输。

    :param data_dict: 包含方块调色板数据的字典
    :type data_dict: dict

    :return: 返回填充完成的方块调色板实例，如果反序列化或实例化失败则返回None
    :rtype: BlockPaletteComponent or None
    """
    block_palette_instance = GetBlankBlockPalette()
    if block_palette_instance:
        deserialize_res = block_palette_instance.DeserializeBlockPalette(data_dict)
        if deserialize_res:
            return block_palette_instance
    return None


def CreateSingleBlockPaletteData(block_identifier, block_aux, exclude_block_list=None):
    """
    根据指定的方块参数生成块调色板数据字典

    该方法用于根据给定的方块标识符和aux值生成一个包含方块调色板数据的字典。

    :param block_identifier: 方块的标识符，用于唯一确定一个方块类型
    :type block_identifier: str
    :param block_aux: 方块的aux值，用于指定方块的状态或变种
    :type block_aux: int
    :param exclude_block_list: 需要排除的方块列表
    :type exclude_block_list: list[str]

    :return: 返回生成的块调色板数据字典
    :rtype: dict
    """
    if exclude_block_list is None:
        exclude_block_list = ["minecraft:air", "minecraft:flowing_water", "minecraft:water", "minecraft:flowing_lava", "minecraft:lava"]
    if block_identifier in exclude_block_list:
        return None
    block_palette_data = {'extra': {}, 'void': False, 'actor': {}, 'volume': (1, 1, 1), 'common': {('%s' % block_identifier, block_aux): [0]},
                          'eliminateAir': True}
    return block_palette_data


def CreateSingleBlockPaletteDataByBlockDict(block_dict):
    """
    根据指定的方块字典生成块调色板数据字典

    该方法用于根据给定的方块字典生成一个包含方块调色板数据的字典。方块字典应包括方块的标识符（"name"）和aux值（"aux"）。

    :param block_dict: 包含方块标识符和aux值的字典
    :type block_dict: dict

    :return: 返回生成的块调色板数据字典
    :rtype: dict or None
    """
    return CreateSingleBlockPaletteData(block_dict["name"], block_dict["aux"])


def CreateSingleBlockPaletteDataByBlockPos(block_pos, block_dimension_id):
    """
    根据指定的方块坐标和维度ID生成块调色板数据字典

    该方法用于根据给定的方块坐标和维度ID生成一个包含方块调色板数据的字典。

    :param block_pos: 指定方块的坐标
    :type block_pos: tuple[int or float,int or float,int or float]
    :param block_dimension_id: 指定方块所在的维度ID
    :type block_dimension_id: int

    :return: 返回生成的块调色板数据字典
    :rtype: dict or None
    """
    block_dict = GetBlockDictByPos(block_pos, block_dimension_id)
    return CreateSingleBlockPaletteDataByBlockDict(block_dict) if block_dict else None


def CreateSingleBlockPaletteDataDictByBlockPosList(block_pos_list, block_dimension_id):
    """
    根据指定的方块坐标列表和维度ID生成块调色板数据字典映射

    该方法用于根据给定的方块坐标列表和维度ID生成一个映射，每个坐标对应一个包含方块调色板数据的字典。

    :param block_pos_list: 指定方块坐标的列表
    :type block_pos_list: list[tuple[int or float,int or float,int or float]]
    :param block_dimension_id: 指定方块所在的维度ID
    :type block_dimension_id: int

    :return: 返回生成的块调色板数据字典映射
    :rtype: dict
    """
    BlockPaletteComponentDataDict = {}
    for block_pos in block_pos_list:
        BlockPaletteComponentData = CreateSingleBlockPaletteDataByBlockPos(block_pos, block_dimension_id)
        if BlockPaletteComponentData:
            BlockPaletteComponentDataDict[block_pos] = BlockPaletteComponentData
    return BlockPaletteComponentDataDict


def CreateBreakBlockEntity(center_pos, dimension_id, block_pos_list, **kwargs):
    """
    在指定中心坐标、维度ID和方块坐标列表基础上生成破坏的方块实体

    该方法用于在给定的中心坐标、维度ID和方块坐标列表下，创建一个或多个破坏的方块实体。

    :param center_pos: 需要生成破坏方块的中心坐标
    :type center_pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 方块所在的维度ID
    :type dimension_id: int
    :param block_pos_list: 需要生成破坏方块的坐标列表
    :type block_pos_list: list[tuple[int or float,int or float,int or float]]
    :param kwargs: 可选参数，包括：
        - need_remove_origin_block (bool): 是否需要移除原有方块。默认为True。
        - use_self_palette_dict (bool): 是否使用自定义调色板。默认为False。
        - self_palette_dict (dict): 自定义调色板字典。默认为{}。
        - out_motion (float): 外部动力。默认为-7。
        - up_motion (float): 上升动力。默认为1.3。
    :type kwargs: any

    """
    if not block_pos_list:
        return
    spawn_block_entity_map = {}
    block_pos_with_entity_id_dict = {}
    for block_pos in block_pos_list:
        block_entity_id = ServerMain.CreateEngineEntityByTypeStr("fg:break_blocks", block_pos, (0, 0), dimension_id, False)
        block_dict = GetBlockDictByPos(block_pos, dimension_id)
        if block_dict:
            spawn_block_entity_map[block_entity_id] = block_dict
        if not block_entity_id:
            continue
        block_pos_with_entity_id_dict[block_pos] = block_entity_id
        EmptyLocationDealServerApi.SetEntityMotion(block_entity_id, EmptyLocationDealServerApi.ChangeValueInPos(
            EmptyLocationDealServerApi.ZoomVector(EmptyLocationDealServerApi.CalcVectorByDoublePoint(center_pos, block_pos), kwargs.get("out_motion", -7)),
            True,
            (0, kwargs.get("up_motion", 1.3), 0)))
    ServerMain.BroadcastToAllClient("CreateBreakBlockEntityEvent",
                                    {"block_pos_palette_dict": CreateSingleBlockPaletteDataDictByBlockPosList(block_pos_list, dimension_id) if not kwargs.get(
                                        "use_self_palette_dict", False) else kwargs.get("self_palette_dict", {}),
                                     "block_pos_with_entity_id_dict": block_pos_with_entity_id_dict})
    if kwargs.get("need_remove_origin_block", True):
        EmptyGameServerApi.AddTimer(0.03, SetBlockToAirByList, block_pos_list, dimension_id)
    return spawn_block_entity_map



def GetRandomDestroyedBlocksPosListAPi(center_pos, dimension_id, radius, num_blocks, exclude_block_list=None, can_destroy_time=99):
    """
    根据传入的中心坐标、维度ID、半径和要生成的随机破坏的方块数量，计算出一个随机的破坏的方块坐标列表。

    :param center_pos: 中心坐标 (x, y, z)
    :type center_pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 维度ID
    :type dimension_id: int
    :param radius: 范围半径
    :type radius: int
    :param num_blocks: 要生成的随机破坏的方块数量
    :type num_blocks: int
    :param exclude_block_list: 排除的方块名称列表，默认为None
    :type exclude_block_list: list[str] or None
    :param can_destroy_time: 可以破坏方块的时间
    :type can_destroy_time: int or float

    :return: 随机破坏的方块坐标列表 [(x1, y1, z1), (x2, y2, z2), ...]
    :rtype: list
    """
    if exclude_block_list is None:
        exclude_block_list = ["minecraft:air", "minecraft:bedrock", "minecraft:command_block", "minecraft:command_block_minecart", "minecraft:barrier",
                              "minecraft:chain_command_block", "minecraft:repeating_command_block", "minecraft:light_block"]
    center_x, center_y, center_z = center_pos
    center_x, center_y, center_z, radius = int(center_x), int(center_y), int(center_z), int(radius)
    destroyed_blocks = []
    retry_count = 0
    while len(destroyed_blocks) < num_blocks and retry_count < (radius ** 3):
        retry_count += 1
        x = random.randint(center_x - radius, center_x + radius)
        y = random.randint(center_y - radius, center_y + radius)
        z = random.randint(center_z - radius, center_z + radius)
        block_pos = (x, y, z)
        if GetBlockName(block_pos, dimension_id) in exclude_block_list:
            continue
        block_name = GetBlockName(block_pos, dimension_id)
        if block_name not in exclude_block_list:
            block_basic_info = CompBlockInfo.GetBlockBasicInfo(block_name)
            print block_name, block_basic_info["destroyTime"],can_destroy_time
            if block_basic_info["destroyTime"] > can_destroy_time or block_basic_info["destroyTime"] <= -1:
                continue
            destroyed_blocks.append(block_pos)
    return destroyed_blocks


def GetRandomDestroyedBlocksPosListByEntityDirectionAPi(entity_id, width, height, front, num_blocks, exclude_block_list=None, can_destroy_time=99):
    """
    根据生物朝向以及传入的中心坐标、维度ID、半径和要生成的随机破坏的方块数量，计算出一个随机的破坏的方块坐标列表。

    :param entity_id: entity_id
    :type entity_id: str
    :param width: width
    :type width: int or float
    :param height: height
    :type height: int or float
    :param front: front
    :type front: int or float
    :param num_blocks: 要生成的随机破坏的方块数量
    :type num_blocks: int
    :param exclude_block_list: 排除的方块名称列表，默认为None
    :type exclude_block_list: list[str] or None
    :param can_destroy_time: 可以破坏的方块破坏时间
    :type can_destroy_time: int or float

    :return: 随机破坏的方块坐标列表 [(x1, y1, z1), (x2, y2, z2), ...]
    :rtype: list[tuple[int or float,int or float,int or float]] or None
    """
    if not EmptyGameServerApi.GetEntityIsAlive(entity_id):
        return None
    dimension_id = EmptyAttributeServerApi.GetEntityDimension(entity_id)
    if dimension_id is None:
        return []
    start_pos = EmptyLocationDealServerApi.GetEntityForwardPos(entity_id, 0, is_center_pos=True)
    if start_pos is None:
        return []
    entity_dir = EmptyAttributeServerApi.GetEntityDir(entity_id)
    if entity_dir is None:
        return []
    diff_center = tuple(round(i) for i in entity_dir)
    destroyed_blocks = []
    current_z = start_pos[2]
    max_z = start_pos[2] + front
    wave_radius = 0
    potential_blocks = []

    if exclude_block_list is None:
        exclude_block_list = ["minecraft:air", "minecraft:bedrock", "minecraft:command_block", "minecraft:command_block_minecart", "minecraft:barrier",
                              "minecraft:chain_command_block", "minecraft:repeating_command_block", "minecraft:light_block"]

    while len(destroyed_blocks) < num_blocks:
        # 生成当前波纹半径的所有可能坐标
        for x_offset in range(-wave_radius, wave_radius + 1):
            for y_offset in range(-1, wave_radius + 1):
                for z_offset in range(-wave_radius, wave_radius + 1):
                    if abs(x_offset) == wave_radius or abs(y_offset) == wave_radius:
                        x = start_pos[0] + x_offset + diff_center[0]
                        y = start_pos[1] + y_offset
                        z = start_pos[2] + z_offset + diff_center[2]
                        block_pos = (x, y, z)
                        block_name = GetBlockName(block_pos, dimension_id)
                        if block_name not in exclude_block_list:
                            block_basic_info = CompBlockInfo.GetBlockBasicInfo(block_name)
                            if block_basic_info["destroyTime"] > can_destroy_time:
                                continue
                            potential_blocks.append(block_pos)

        # 随机选择坐标进行破坏
        random.shuffle(potential_blocks)
        while potential_blocks and len(destroyed_blocks) < num_blocks:
            destroyed_blocks.append(potential_blocks.pop())

        # 检查是否需要增加波纹半径或 Z 坐标
        wave_radius += 1
        if wave_radius > max(width, height):
            wave_radius = 0
            current_z += 1
            if current_z > max_z:
                break

    return destroyed_blocks


def GetInvertedConeBlocksPosListAPi(center_pos, dimension_id, layers, initial_radius, radius_decrement=1, exclude_block_list=None, random_remove=False,
                                    random_remove_count=5):
    """
    根据传入的中心坐标、维度ID、层数、初始半径以及半径衰减，计算出一个倒锥形的方块坐标列表。

    :param center_pos: 中心坐标 (x, y, z)
    :type center_pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 维度ID
    :type dimension_id: int
    :param layers: 层数
    :type layers: int
    :param initial_radius: 初始半径
    :type initial_radius: int
    :param radius_decrement: 半径衰减，默认为1
    :type radius_decrement: int
    :param exclude_block_list: 排除的方块名称列表，默认为None
    :type exclude_block_list: list[str] or None
    :param random_remove: 是否随机移除部分方块，默认为False
    :type random_remove: bool
    :param random_remove_count: 随机移除的方块数量，默认为5
    :type random_remove_count: int

    :return: 方块坐标列表 [(x1, y1, z1), (x2, y2, z2), ...]
    :rtype:  list[tuple[int or float,int or float,int or float]] or None
    """
    if exclude_block_list is None:
        exclude_block_list = ["minecraft:air"]
    center_x, center_y, center_z = center_pos
    center_x, center_y, center_z = int(center_x), int(center_y), int(center_z)
    inverted_cone_blocks = []
    current_radius = initial_radius

    # 从脚底开始往上计算每一层的方块坐标
    for layer in range(1, layers + 1):
        for x in range(center_x - current_radius, center_x + current_radius + 1):
            for z in range(center_z - current_radius, center_z + current_radius + 1):
                y = center_y - layer  # y坐标从脚底往下递减
                block_pos = (x, y, z)
                if GetBlockName(block_pos, dimension_id) in exclude_block_list:
                    continue
                inverted_cone_blocks.append((x, y, z))

        current_radius -= radius_decrement  # 每一层半径递减
        if current_radius < 0:
            break  # 当半径小于0时，停止生成

    if random_remove:
        for _ in range(random_remove_count):
            if len(inverted_cone_blocks) <= 0:
                break
            element_to_remove = random.choice(inverted_cone_blocks)
            inverted_cone_blocks.remove(element_to_remove)

    return inverted_cone_blocks
