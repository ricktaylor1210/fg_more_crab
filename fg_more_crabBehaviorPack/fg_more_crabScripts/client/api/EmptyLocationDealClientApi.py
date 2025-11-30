# coding=utf-8
from mod.common.utils.mcmath import Vector3

from fg_more_crabScripts.client.api import EmptyAttributeClientApi as AttributeApi
from fg_more_crabScripts.client.api import EmptyGameClientApi as GameApi
from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


def GetEntityForwardMotionDir(entity_id, distant, change_x=True, change_y=True, change_z=True):
    """
    根据传入的entity_id、distant计算得出生物视角前方distant的Dir

    :param entity_id: 实体的entity_id。
    :type entity_id: str
    :param distant: 距离实体前方的距离。
    :type distant: float
    :param change_x: 是否改变X坐标。
    :type change_x: bool
    :param change_y: 是否改变Y坐标。
    :type change_y: bool
    :param change_z: 是否改变Z坐标。
    :type change_z: bool

    :return: 距离实体前方指定距离的位置坐标。
    :rtype: tuple[float,float,float] or None
    """
    current_dir = AttributeApi.GetEntityDir(entity_id)
    if current_dir is None:
        return None
    distant_pos = (
        current_dir[0] * distant if change_x else current_dir[0],
        current_dir[1] * distant if change_y else current_dir[1],
        current_dir[2] * distant if change_z else current_dir[2]
    )
    return distant_pos


def ChangeValueInPos(pos, absolute=False, change_pos=(0, 0, 0)):
    """
    根据传入的坐标以及坐标差值返回一个新坐标
        该方法根据传入的坐标（pos）、绝对值标志（absolute）、和坐标差值（change_pos）来计算新的坐标。

    :param pos: 原始坐标 (x, y, z)
    :type pos: tuple[float,float,float]
    :param absolute: 是否绝对值，若为True，则将坐标变化应用为绝对值，否则应用为增量
    :type absolute: bool
    :param change_pos: 需要改变的坐标差值，根据absolute参数的不同，可以是增量或绝对值
    :type change_pos: tuple[float,float,float]

    :return: 新的坐标 (x, y, z)
    :rtype: tuple[float,float,float]
    """
    if absolute:
        return tuple(new if change != 0 else old for old, new, change in zip(pos, change_pos, change_pos))
    return pos[0] + change_pos[0], pos[1] + change_pos[1], pos[2] + change_pos[2]


def CalcDistantByDoublePoint(point_1, point_2):
    """
    根据传入的两个坐标计算直线距离。

    :param point_1: 第一个点的坐标 (x1, y1, z1)。
    :type point_1: tuple[float,float,float]
    :param point_2: 第二个点的坐标 (x2, y2, z2)。
    :type point_2: tuple[float,float,float]

    :return: 两点之间的直线距离。
    :rtype: float
    """
    (x1, y1, z1), (x2, y2, z2) = point_1, point_2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def CalcDistantByDoubleEntityId(entity_id_1, entity_id_2):
    """
    根据传入的两个实体entity_id计算直线距离。

    :param entity_id_1: 第一个实体的entity_id。
    :type entity_id_1: str
    :param entity_id_2: 第二个实体的entity_id。
    :type entity_id_2: str

    :return: 两个实体之间的直线距离。
    :rtype: float or None
    """
    point_1 = AttributeApi.GetEntityCenterPos(entity_id_1)
    point_2 = AttributeApi.GetEntityCenterPos(entity_id_2)
    if point_1 is None or point_2 is None:
        return None
    return CalcDistantByDoublePoint(point_1, point_2)


def CheckEntityAroundEntityList(main_entity_id, around_square, exclude_entity_list=None, filters=None):
    """
    检测指定实体ID周围的其他实体
        该方法利用GameApi.GetCompGameLocalPlayer和GameApi.GetEntitiesAround接口，检测给定实体（main_entity_id）周围一定范围（aroundSquare）内的其他实体。
        可以通过exclude_entity_list参数来排除某些特定的实体。
        该方法还会自动排除项目实体和经验实体。

    :param main_entity_id: 需要进行检测的主实体ID
    :type main_entity_id: str
    :param around_square: 检测的范围
    :type around_square: int or float
    :param exclude_entity_list: 需要排除的实体ID列表，默认为None
    :type exclude_entity_list: list[str] or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 检测到的周围实体的ID列表
    :rtype: list[str] or None
    """
    if not GameApi.GetEntityIsAlive(main_entity_id):
        return None

    main_entity_center_pos = AttributeApi.GetEntityCenterPos(main_entity_id)
    if main_entity_center_pos is None:
        return None

    filters = filters if filters else {}

    around_entity_list = GetGameComp(main_entity_id).GetEntitiesAround(main_entity_id, int(math.ceil(around_square)), filters)
    if around_entity_list is None:
        return None

    # 存储实体ID和它们到主实体的距离
    entity_distance_pairs = []
    for entity_id in around_entity_list:
        if exclude_entity_list and entity_id in exclude_entity_list:
            continue

        if entity_id == main_entity_id:
            continue

        entity_type = AttributeApi.GetEngineType(entity_id)
        if entity_type in [MinecraftEnum.EntityType.ItemEntity, MinecraftEnum.EntityType.Experience]:
            continue

        entity_center_pos = AttributeApi.GetEntityCenterPos(entity_id)
        delta = Vector3(entity_center_pos) - Vector3(main_entity_center_pos)
        if delta.Length() > around_square:
            continue

        # 将实体ID和距离作为元组添加到列表中
        entity_distance_pairs.append((entity_id, delta.Length()))

    # 根据距离从小到大排序
    entity_distance_pairs.sort(key=lambda pair: pair[1])

    # 从排序后的列表中提取实体ID
    dear_list = [pair[0] for pair in entity_distance_pairs]

    return dear_list if dear_list else None


def CheckEntityAroundNearEntityListApi(main_entity_id, around_radius=6, exclude_entity_list=None, filters=None):
    """
    根据传入的中心生物ID获取范围内距离最近的生物ID
        该方法根据传入的中心生物ID（main_entity_id）、范围的长度（around_radius）等参数，
        检测范围内距离最近的其他生物的ID。
        可以通过exclude_entity_list参数来排除某些特定的生物。

    :param main_entity_id: 需要检测的中心生物的ID
    :type main_entity_id: str
    :param around_radius: 半径长度，默认为6
    :type around_radius: float
    :param exclude_entity_list: 需要排除的生物ID列表，默认为None
    :type exclude_entity_list: list or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 距离最近的生物的ID，如果没有找到则返回None
    :rtype: str or None
    """
    around_entity_list = CheckEntityAroundEntityList(main_entity_id, around_radius, exclude_entity_list, filters=filters)
    return around_entity_list[0] if around_entity_list else None


def CheckEntitySectorAroundEntityListApi(main_entity_id, around_radius=6, radius_angle=60, exclude_entity_list=None, is_front=False, filters=None):
    """
    根据传入的中心生物ID获取扇形范围内的其他生物
        该方法根据传入的中心生物ID（main_entity_id）、扇形范围的长度（around_radius）、扇形范围的角度（radius_angle）等参数，
        检测并返回在扇形范围内的其他生物的ID列表。
        可以通过exclude_entity_list参数来排除某些特定的生物。
        is_front参数用于控制是否只考虑水平方向，不考虑低头或抬头的角度。

    :param main_entity_id: 需要检测的中心生物的ID
    :type main_entity_id: str
    :param around_radius: 扇形的半径长度，默认为6
    :type around_radius: float
    :param radius_angle: 扇形的角度，默认为60
    :type radius_angle: float
    :param exclude_entity_list: 需要排除的生物ID列表，默认为None
    :type exclude_entity_list: list[str] or None
    :param is_front: 是否只考虑水平方向，不考虑低头或抬头的角度，默认为False
    :type is_front: bool
    :param exclude_entity_list: 需要排除的实体ID列表，默认为None
    :type exclude_entity_list: list[str] or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 根据传入参数所获得的扇形范围内的生物ID列表
    :rtype: list[str] or None
    """
    if not GameApi.GetEntityIsAlive(main_entity_id):
        return None
    main_entity_center_pos = AttributeApi.GetEntityCenterPos(main_entity_id)
    if main_entity_center_pos is None:
        return None

    main_entity_dir = ClientApi.GetDirFromRot((0, AttributeApi.GetEntityRot(main_entity_id)[1])) if is_front else AttributeApi.GetEntityDir(main_entity_id)
    if main_entity_dir is None:
        return None

    main_entity_size = AttributeApi.GetEntitySize(main_entity_id)
    if main_entity_size is None:
        return None

    main_entity_center_pos = (
        main_entity_center_pos[0] - main_entity_dir[0] * main_entity_size[0] * 0.5, main_entity_center_pos[1] - main_entity_dir[0] * main_entity_size[0] * 0.5,
        main_entity_center_pos[2] - main_entity_dir[2] * main_entity_size[0] * 0.5)

    around_entity_list = CheckEntityAroundEntityList(main_entity_id, around_radius, exclude_entity_list, filters=filters)
    if around_entity_list is None:
        return None

    dear_list = []
    for entity_id in around_entity_list:
        entity_center_pos = AttributeApi.GetEntityCenterPos(entity_id)
        delta = Vector3(entity_center_pos) - Vector3(main_entity_center_pos)
        dot_product = Vector3.Dot(delta.Normalized(), Vector3(main_entity_dir).Normalized())
        dot_product = max(-1, min(dot_product, 1))
        # 计算角度
        angle = math.degrees(math.acos(dot_product))
        if angle > radius_angle:
            continue

        dear_list.append(entity_id)
    return dear_list if dear_list else None


def CheckEntitySectorAroundNearEntityListApi(main_entity_id, around_radius=6, radius_angle=60, exclude_entity_list=None, is_front=False, priority_weight=0.5,
                                             filters=None):
    """
    根据传入的中心生物ID获取扇形范围内距离最近的生物ID
        该方法根据传入的中心生物ID（main_entity_id）、扇形范围的长度（around_radius）、扇形范围的角度（radius_angle）等参数，
        检测扇形范围内距离最近的其他生物的ID。
        可以通过exclude_entity_list参数来排除某些特定的生物。

    :param main_entity_id: 需要检测的中心生物的ID
    :type main_entity_id: str
    :param around_radius: 扇形的半径长度，默认为6
    :type around_radius: float
    :param radius_angle: 扇形的角度，默认为60
    :type radius_angle: float
    :param exclude_entity_list: 需要排除的生物ID列表，默认为None
    :type exclude_entity_list: list[str] or None
    :param is_front: 是否只考虑水平方向，不考虑低头或抬头的角度，默认为False
    :type is_front: bool
    :param priority_weight: 控制筛选优先级的权重，0表示完全按距离，1表示完全按角度，0.5表示距离和角度同等重要
    :type priority_weight: float

    :param filters: filters
    :type filters: dict or list or None

    :return: 距离最近的生物的ID，如果没有找到则返回None
    :rtype: str or None
    """
    if not GameApi.GetEntityIsAlive(main_entity_id):
        return None

    sector_around_entity_list = CheckEntitySectorAroundEntityListApi(main_entity_id, around_radius, radius_angle, exclude_entity_list, is_front,
                                                                     filters=filters)
    if sector_around_entity_list is None:
        return None

    main_entity_dir = ClientApi.GetDirFromRot((0, AttributeApi.GetEntityRot(main_entity_id)[1])) if is_front else AttributeApi.GetEntityDir(main_entity_id)
    if main_entity_dir is None:
        return None

    main_entity_size = AttributeApi.GetEntitySize(main_entity_id)
    if main_entity_size is None:
        return None

    main_entity_center_pos = AttributeApi.GetEntityCenterPos(main_entity_id)
    if main_entity_center_pos is None:
        return None

    main_entity_center_pos = (
        main_entity_center_pos[0] - main_entity_dir[0] * main_entity_size[0] * 0.5, main_entity_center_pos[1] - main_entity_dir[0] * main_entity_size[0] * 0.5,
        main_entity_center_pos[2] - main_entity_dir[2] * main_entity_size[0] * 0.5)

    near_mob_id = None
    best_score = None  # 新增一个用于记录最佳得分的变量

    for entity_id in sector_around_entity_list:
        entity_center_pos = AttributeApi.GetEntityCenterPos(entity_id)
        delta = Vector3(entity_center_pos) - Vector3(main_entity_center_pos)
        distance = delta.Length()
        dot_product = Vector3.Dot(delta.Normalized(), Vector3(main_entity_dir).Normalized())
        dot_product = max(-1, min(dot_product, 1))
        # 计算角度
        angle = math.degrees(math.acos(dot_product))

        # 根据权重计算得分
        score = priority_weight * angle + (1 - priority_weight) * distance

        # 检查是否是最佳得分
        if near_mob_id is None or score < best_score:
            near_mob_id = entity_id
            best_score = score

    return near_mob_id


def ZoomVector(vector_tuple, multiple, separation=False, multiple_x=1.0, multiple_y=1.0, multiple_z=1.0):
    """
    缩放传入的向量
        该方法用于对传入的向量进行缩放操作。可以选择是否分离缩放各个分量，也可以单独指定各个分量的缩放倍数。

    :param vector_tuple: 待缩放的向量 (dx, dy, dz)
    :type vector_tuple: tuple[int or float,int or float,int or float]
    :param multiple: 缩放倍数，如果不分离缩放，则该倍数应用于所有分量
    :type multiple: float
    :param separation: 是否分离缩放，默认为False
    :type separation: bool
    :param multiple_x: X轴分量的缩放倍数，默认为1.0
    :type multiple_x: float
    :param multiple_y: Y轴分量的缩放倍数，默认为1.0
    :type multiple_y: float
    :param multiple_z: Z轴分量的缩放倍数，默认为1.0
    :type multiple_z: float

    :return: 缩放后的向量
    :rtype: tuple[int or float,int or float,int or float]
    """
    dx, dy, dz = vector_tuple

    if separation:
        # 如果分离缩放，对每个分量应用不同的倍数
        return dx * multiple_x, dy * multiple_y, dz * multiple_z
    else:
        # 如果不分离缩放，对所有分量应用相同的倍数
        return dx * multiple, dy * multiple, dz * multiple
