# -*- coding: utf-8 -*-
import copy

from . import AttributeServerUtils
from ..ServerBaseUtils import *


def GetEntityForwardPos(entity_id, distant, is_foot_pos=False, is_center_pos=False):
    """
    根据传入的entity_id和distant，计算出实体视角前方distant距离处的坐标
        该方法依赖于AttributeServerUtils.GetEntityDir和AttributeServerUtils.GetEntityPos（或AttributeServerUtils.GetEntityFootPos）来获取实体当前的方向和位置。
        参数is_foot_pos用于决定是否获取实体脚下的坐标。当is_foot_pos为True时，使用AttributeServerUtils.GetEntityFootPos；否则使用AttributeServerUtils.GetEntityPos。

    :param entity_id: 实体的ID
    :type entity_id: str
    :param distant: 前方的距离
    :type distant: float
    :param is_foot_pos: 是否获取实体脚下的坐标，True为获取脚下坐标，False为获取实体中心坐标
    :type is_foot_pos: bool
    :param is_center_pos: 是否获取实体中间的坐标
    :type is_center_pos: bool

    :return: 计算得出的前方坐标
    :rtype: tuple[int or float,int or float,int or float] or None
    """
    if is_foot_pos:
        current_pos = CompFactory.CreatePos(entity_id).GetFootPos()
    elif is_center_pos:
        current_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
    else:
        current_pos = CompFactory.CreatePos(entity_id).GetPos()
    if current_pos is None:
        return None
    motion_dir = GetEntityForwardMotionDir(entity_id, distant)
    if motion_dir is None:
        return None
    distant_pos = (current_pos[0] + motion_dir[0], current_pos[1] + motion_dir[1], current_pos[2] + motion_dir[2])
    return distant_pos


def GetEntityForwardMotionDir(entity_id, distant):
    """
    根据传入的entity_id和distant，计算出实体视角前方distant距离处的方向（Dir）
        该方法依赖于AttributeServerUtils.GetEntityDir来获取实体当前的方向。
        通过将当前方向与distant相乘，计算得出实体视角前方distant距离处的方向。

    :param entity_id: 实体的ID
    :type entity_id: str
    :param distant: 前方的距离
    :type distant: float

    :return: 计算得出的前方方向（Dir）
    :rtype: tuple[int or float,int or float,int or float] or None
    """
    current_dir = AttributeServerUtils.GetEntityDir(entity_id)
    if current_dir is None:
        return None
    motion_dir = (current_dir[0] * distant, current_dir[1] * distant, current_dir[2] * distant)
    return motion_dir


def CheckCenterPosAroundEntityList(center_pos, around_square, dimension_id, exclude_entity_list=None, has_tag="",
                                   has_not_tag="", exclude_family_list=None,
                                   has_family_list=None, filters=None):
    # filters = filters if filters else {
    #     "all_of": [
    #         {
    #             "test": "is_family",
    #             "subject": "other",
    #             "operator": "!=",
    #             "value": "test"
    #         }
    #     ]
    # }
    # if exclude_family_list:
    #     for family in exclude_family_list:
    #         filters["all_of"].append({"test": "is_family", "subject": "other", "operator": "!=", "value": "%s" % family})
    # if has_family_list:
    #     for family in has_family_list:
    #         filters["all_of"].append({"test": "is_family", "subject": "other", "value": "%s" % family})
    #
    # if has_tag:
    #     for tag_name in has_tag:
    #         filters["all_of"].append({"test": "has_tag", "subject": "other", "value": "%s" % tag_name})
    # if has_not_tag:
    #     for tag_name in has_not_tag:
    #         filters["all_of"].append({"test": "has_tag", "operator": "!=", "subject": "other", "value": "%s" % tag_name})
    c_x, c_y, c_z = center_pos

    start_pos = ServerApi.GetIntPos((c_x - around_square, c_y - around_square, c_z - around_square))
    end_pos = ServerApi.GetIntPos((c_x + around_square, c_y + around_square, c_z + around_square))
    around_entity_list = GetCompGameLevel().GetEntitiesInSquareArea(None, start_pos, end_pos, dimension_id)
    if around_entity_list is None:
        return None

    entity_distance_list = []
    for entity_id in around_entity_list:
        if exclude_entity_list and entity_id in exclude_entity_list:
            continue

        comp_type = CompFactory.CreateEngineType(entity_id)

        entity_type = comp_type.GetEngineType()
        if entity_type in [MinecraftEnum.EntityType.ItemEntity, MinecraftEnum.EntityType.Experience,
                           MinecraftEnum.EntityType.ExperiencePotion]:
            continue

        entity_type_str = comp_type.GetEngineTypeStr()
        if entity_type_str in ["minecraft:xp_orb", "minecraft:xp_bottle"]:
            continue

        entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
        delta = Vector3(entity_center_pos) - Vector3(center_pos)
        if delta.Length() <= around_square:
            entity_distance_list.append((entity_id, delta.Length()))

    # 根据距离对实体进行排序
    entity_distance_list.sort(key=lambda x: x[1])
    # 从排序后的列表中提取实体ID
    dear_list = [entity_id for entity_id, _ in entity_distance_list]
    return dear_list


def has_disable_search_filter(filters):
    """
    检查 filters['all_of'] 里是否已经有针对 disable_search 的筛选条件，
    通过 value == "disable_search" 粗粒度判断，兼容 has_tag / is_family 等不同 test。
    """
    # 这里做一个轻量防御：如果 filters 不是 dict，直接认为没有筛 disable_search
    if not isinstance(filters, dict):
        return False

    all_of_filters = filters.get("all_of") or []
    for filter_item in all_of_filters:
        if filter_item.get("value") == "disable_search":
            return True
    return False


def CheckEntityAroundEntityList(main_entity_id, around_square, exclude_entity_list=None, has_tag="", has_not_tag="",
                                exclude_family_list=None,
                                has_family_list=None, filters=None):
    """
    检测指定实体ID周围的其他实体
        该方法利用GameServerApi.GetCompGameLocalPlayer和GameServerApi.GetEntitiesAround接口，检测给定实体（main_entity_id）周围一定范围（around_square）内的其他实体。
        可以通过exclude_entity_list参数来排除某些特定的实体。
        该方法还会自动排除项目实体和经验实体。

    :param main_entity_id: 需要进行检测的主实体ID
    :type main_entity_id: str
    :param around_square: 检测的范围
    :type around_square: int or float
    :param exclude_entity_list: 需要排除的实体ID列表，默认为None
    :type exclude_entity_list: list[str] or None
    :param has_tag: 需要拥有的tag
    :type has_tag: str or list[str]
    :param has_not_tag: 需要排除的tag
    :type has_not_tag: str or list[str]
    :param exclude_family_list: 需要排除的实体family，默认为None
    :type exclude_family_list: list[str] or None
    :param has_family_list: 需要拥有的实体family，默认为None
    :type has_family_list: list[str] or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 检测到的周围实体的ID列表
    :rtype: list[str] or None
    """
    if not GetCompGameLevel().IsEntityAlive(main_entity_id):
        return None

    main_entity_center_pos = AttributeServerUtils.GetEntityCenterPos(main_entity_id)
    if main_entity_center_pos is None:
        return None

    # 1. 统一初始化 filters，保证有 "all_of" 这个 key 可以继续追加条件
    if filters is None:
        filters = {
            "all_of": [
                {
                    "test": "is_family",
                    "subject": "other",
                    "operator": "!=",
                    "value": "test",
                }
            ]
        }
    else:
        # 如果调用方自己传了 filters，但没给 all_of，就帮他补一个空列表
        filters.setdefault("all_of", [])

    # 2. 正常处理调用方显式要排除的 family
    if exclude_family_list:
        for family in exclude_family_list:
            filters["all_of"].append(
                {
                    "test": "is_family",
                    "subject": "other",
                    "operator": "!=",
                    "value": "%s" % family,
                }
            )

    # 3. 归一化 exclude_family_list，避免后面对 None 做成员判断
    exclude_family_list = exclude_family_list or []

    # 4. 如果：调用方没有显式排除 disable_search 且 filters 中也没有任何针对
    #    disable_search 的筛选条件，则自动追加一个排除 disable_search 的 family 条件
    if "disable_search" not in exclude_family_list and not has_disable_search_filter(filters):
        filters["all_of"].append(
            {
                "test": "is_family",
                "subject": "other",
                "operator": "!=",
                "value": "disable_search",
            }
        )
    if "disable_search" not in exclude_family_list and not has_disable_search_filter(filters):
        filters["all_of"].append({
            "test": "is_family",
            "subject": "other",
            "operator": "!=",
            "value": "disable_search",
        })
    if has_family_list:
        for family in has_family_list:
            filters["all_of"].append({"test": "is_family", "subject": "other", "value": "%s" % family})

    if has_tag:
        for tag_name in has_tag:
            filters["all_of"].append({"test": "has_tag", "subject": "other", "value": "%s" % tag_name})
    if has_not_tag:
        for tag_name in has_not_tag:
            filters["all_of"].append(
                {"test": "has_tag", "operator": "!=", "subject": "other", "value": "%s" % tag_name})

    around_entity_list = CompFactory.CreateGame(main_entity_id).GetEntitiesAround(main_entity_id,
                                                                                  int(math.ceil(around_square)),
                                                                                  filters)
    if around_entity_list is None:
        return None
    entity_distance_list = []
    for entity_id in around_entity_list:
        if exclude_entity_list and entity_id in exclude_entity_list:
            continue
        if entity_id == main_entity_id:
            continue
        entity_type = CompFactory.CreateEngineType(entity_id).GetEngineType()
        if entity_type in [MinecraftEnum.EntityType.ItemEntity, MinecraftEnum.EntityType.Experience]:
            continue
        entity_type_str = CompFactory.CreateEngineType(entity_id).GetEngineTypeStr()
        if entity_type_str in ["fg:break_block", "minecraft:falling_block"]:
            continue

        entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
        delta = Vector3(entity_center_pos) - Vector3(main_entity_center_pos)
        if delta.Length() <= around_square:
            entity_distance_list.append((entity_id, delta.Length()))

    # 根据距离对实体进行排序
    entity_distance_list.sort(key=lambda x: x[1])
    # 从排序后的列表中提取实体ID
    dear_list = [entity_id for entity_id, _ in entity_distance_list]
    return dear_list


def GetTrackMotionRot(main_entity_id, target_entity_id):
    dir_t_to_s = CalcVectorByDoubleEntityId(target_entity_id, main_entity_id)
    if dir_t_to_s:
        rot = ServerApi.GetRotFromDir(tuple(dir_t_to_s))
        return rot
    return None


def GetTrackMotionRotByPos(main_pos, target_pos):
    dir_t_to_s = CalcVectorByDoublePoint(main_pos, target_pos)
    if dir_t_to_s:
        rot = ServerApi.GetRotFromDir(tuple(dir_t_to_s))
        return rot
    return None


def CheckEntitySectorAroundEntityListApi(main_entity_id, around_radius=6, radius_angle=60, exclude_entity_list=None,
                                         is_front=False, has_tag="", has_not_tag="",
                                         exclude_family_list=None, has_family_list=None, filters=None):
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
    :param has_tag: 需要拥有的tag
    :type has_tag: str or list[str]
    :param has_not_tag: 需要排除的tag
    :type has_not_tag: str or list[str]
    :param exclude_family_list: 需要排除的实体family，默认为None
    :type exclude_family_list: list[str] or None
    :param has_family_list: 需要拥有的实体family，默认为None
    :type has_family_list: list[str] or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 根据传入参数所获得的扇形范围内的生物ID列表
    :rtype: list[str] or None
    """
    if not GetCompGameLevel().IsEntityAlive(main_entity_id):
        return None

    main_entity_center_pos = AttributeServerUtils.GetEntityCenterPos(main_entity_id)
    if main_entity_center_pos is None:
        return None

    main_entity_dir = ServerApi.GetDirFromRot(
        (0, CompFactory.CreateRot(main_entity_id).GetRot()[1])) if is_front else AttributeServerUtils.GetEntityDir(
        main_entity_id)
    if main_entity_dir is None:
        return None

    main_entity_size = CompFactory.CreateCollisionBox(main_entity_id).GetSize()
    if main_entity_size is None:
        return None

    cx, cy, cz = main_entity_center_pos
    dx, dy, dz = main_entity_dir
    s0, s1 = main_entity_size

    main_entity_center_pos = (
        cx - dx * s0 * 0.5,
        cy - dy * s0 * 0.5,
        cz - dz * s0 * 0.5,
    )

    around_entity_list = CheckEntityAroundEntityList(main_entity_id, around_radius, exclude_entity_list, has_tag,
                                                     has_not_tag, exclude_family_list,
                                                     has_family_list, filters=filters)
    # print "around_entity_list is ->", around_entity_list
    # print "args is ->", main_entity_id, around_radius, exclude_entity_list, has_tag, has_not_tag, exclude_family_list,has_family_list, filters
    if around_entity_list is None:
        return None
    dear_list = []
    for entity_id in around_entity_list:
        entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
        delta = Vector3(entity_center_pos) - Vector3(main_entity_center_pos)

        # ========= 水平角（XZ 平面，与前向的夹角，非负） =========
        horizontal_delta = Vector3(delta[0], 0.0, delta[2])  # 仅 XZ
        horizontal_dir = Vector3(dx, 0.0, dz).Normalized()  # 仅 XZ

        if horizontal_delta.Length() == 0 or horizontal_dir.Length() == 0:
            horizontal_angle = 0.0
        else:
            h_dot = Vector3.Dot(horizontal_delta.Normalized(), horizontal_dir)
            h_dot = max(-1.0, min(1.0, h_dot))
            horizontal_angle = math.degrees(math.acos(h_dot))  # [0°, 180°]

        # ========= 垂直角（相对水平的仰/俯角，带符号）=========
        # 基岩版：Y 为上，水平距离在 XZ
        hlen = math.sqrt(delta[0] ** 2 + delta[2] ** 2)  # 水平（XZ）距离
        vertical_angle_signed = math.degrees(math.atan2(delta[1], hlen))  # [-90°, +90°]
        vertical_angle = abs(vertical_angle_signed)  # 与水平夹角的绝对值

        # print "entity_id", entity_id
        # print "vertical_angle", vertical_angle
        # print "horizontal_angle", horizontal_angle
        # print "radius_angle", radius_angle
        # 角度判定：只要水平或垂直方向有任一超出允许角度，就认为不在扇形内
        # 之前用 AND，会变成“水平和垂直都偏得很厉害才剔除”，扇形范围比预期大一截
        if vertical_angle > radius_angle or horizontal_angle > radius_angle:
            continue
        # if vertical_angle > radius_angle and  horizontal_angle > radius_angle:
        #     continue

        dear_list.append(entity_id)
    return dear_list


def CheckEntitySectorAroundNearEntityListApi(main_entity_id, around_radius=6, radius_angle=60, exclude_entity_list=None,
                                             is_front=False, priority_weight=0.5,
                                             has_tag="", has_not_tag="", exclude_family_list=None, has_family_list=None,
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
    :param priority_weight: 控制筛选优先级的权重，0表示完全按距离，1表示完全按角度，0.5表示距离和角度同等重要
    :type priority_weight: float
    :param is_front: 是否只考虑水平方向，不考虑低头或抬头的角度，默认为False
    :type is_front: bool
    :param has_tag: 需要拥有的tag
    :type has_tag: str or list[str]
    :param has_not_tag: 需要排除的tag
    :type has_not_tag: str or list[str]
    :param exclude_family_list: 需要排除的实体family，默认为None
    :type exclude_family_list: list[str] or None
    :param has_family_list: 需要拥有的实体family，默认为None
    :type has_family_list: list[str] or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 距离最近的生物的ID，如果没有找到则返回None
    :rtype: str or None
    """
    if not GetCompGameLevel().IsEntityAlive(main_entity_id):
        return None
    sector_around_entity_list = CheckEntitySectorAroundEntityListApi(main_entity_id, around_radius, radius_angle,
                                                                     exclude_entity_list, is_front, has_tag,
                                                                     has_not_tag, exclude_family_list, has_family_list,
                                                                     filters=filters)
    if sector_around_entity_list is None:
        return None

    main_entity_dir = ServerApi.GetDirFromRot(
        (0, CompFactory.CreateRot(main_entity_id).GetRot()[1])) if is_front else AttributeServerUtils.GetEntityDir(
        main_entity_id)
    if main_entity_dir is None:
        return None

    main_entity_size = CompFactory.CreateCollisionBox(main_entity_id).GetSize()
    if main_entity_size is None:
        return None

    main_entity_center_pos = AttributeServerUtils.GetEntityCenterPos(main_entity_id)
    if main_entity_center_pos is None:
        return None

    # main_entity_center_pos = (
    #     main_entity_center_pos[0] - main_entity_dir[0] * main_entity_size[0] * 0.5, main_entity_center_pos[1] - main_entity_dir[0] * main_entity_size[0] * 0.5,
    #     main_entity_center_pos[2] - main_entity_dir[2] * main_entity_size[0] * 0.5)

    # 将中心点沿着朝向方向平移半个碰撞箱，用来近似生物“前脸”的位置
    # 原代码第二行用了 main_entity_dir[0]（X 分量）去改 Y，高度方向会乱偏
    main_entity_center_pos = (
        main_entity_center_pos[0] - main_entity_dir[0] * main_entity_size[0] * 0.5,
        main_entity_center_pos[1] - main_entity_dir[1] * main_entity_size[0] * 0.5,
        main_entity_center_pos[2] - main_entity_dir[2] * main_entity_size[0] * 0.5,
    )

    near_mob_id = None
    best_score = None  # 新增一个用于记录最佳得分的变量

    for entity_id in sector_around_entity_list:
        entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
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


def CheckEntityAroundNearEntityListApi(main_entity_id, around_radius=6, exclude_entity_list=None, has_tag="",
                                       has_not_tag="", exclude_family_list=None,
                                       has_family_list=None, filters=None):
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
    :param has_tag: 需要拥有的tag
    :type has_tag: str or list
    :param has_not_tag: 需要排除的tag
    :type has_not_tag: str or list
    :param exclude_family_list: 需要排除的实体family，默认为None
    :type exclude_family_list: list[str] or None
    :param has_family_list: 需要拥有的实体family，默认为None
    :type has_family_list: list[str] or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 距离最近的生物的ID，如果没有找到则返回None
    :rtype: str or None
    """
    around_entity_list = CheckEntityAroundEntityList(main_entity_id, around_radius, exclude_entity_list, has_tag,
                                                     has_not_tag, exclude_family_list,
                                                     has_family_list, filters=filters)
    return around_entity_list[0] if around_entity_list else None


def CheckEntityCubeAroundEntityListApi(main_entity_id, width, length, height=4, rot=None, exclude_entity_list=None,
                                       has_tag="", has_not_tag="",
                                       exclude_family_list=None, has_family_list=None, filters=None):
    """
    根据传入的中心生物ID获取矩形范围内的其他生物
        该方法根据传入的中心生物ID（main_entity_id）、矩形的宽度（width）、长度（length）、高度（height）等参数，
        检测并返回在矩形范围内的其他生物的ID列表。
        可以通过exclude_entity_list参数来排除某些特定的生物。

    :param main_entity_id: 需要检测的中心生物的ID
    :type main_entity_id: str
    :param width: 矩形的宽度
    :type width: float or int
    :param length: 矩形的长度
    :type length: float or int
    :param height: 矩形的高度，默认为4
    :type height: float or int
    :param rot: rot
    :param exclude_entity_list: 需要排除的生物ID列表，默认为None
    :type exclude_entity_list: list[str] or None
    :param has_tag: 需要拥有的tag
    :type has_tag: str or list[str]
    :param has_not_tag: 需要排除的tag
    :type has_not_tag: str or list[str]
    :param exclude_family_list: 需要排除的实体family，默认为None
    :type exclude_family_list: list[str] or None
    :param has_family_list: 需要拥有的实体family，默认为None
    :type has_family_list: list[str] or None
    :param filters: filters
    :type filters: dict or list or None

    :return: 根据传入参数所获得的矩形范围内的生物ID列表
    :rtype: list[str] or None
    """
    if not GetCompGameLevel().IsEntityAlive(main_entity_id):
        return None
    cube_vertices = CalculateRectVertices(main_entity_id, width, length, height, rot)
    if cube_vertices is None:
        return None
    around_entity_list = CheckEntityAroundEntityList(main_entity_id, max(width, length, height) * 2,
                                                     exclude_entity_list, has_tag, has_not_tag,
                                                     exclude_family_list, has_family_list, filters=filters)
    cube_entity_list = []
    for entity_id in around_entity_list:
        entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
        if entity_center_pos is None:
            continue
        if IsPointInCube(entity_center_pos, cube_vertices):
            cube_entity_list.append(entity_id)
    return cube_entity_list


def CheckEntitiesInAabbAroundEntity(main_entity_id, width, length, height=4, rot=None,
                                    exclude_entity_list=None, has_tag="", has_not_tag="",
                                    exclude_family_list=None, has_family_list=None, filters=None):
    """
    根据传入的中心生物ID获取【轴对齐】矩形范围内的其他生物
        这里按需求 A 实现：
        - 用实体中心作为 AABB 中心；
        - 在世界坐标下按 X/Y/Z 轴对齐；
        - 各轴范围为 [center - size/2, center + size/2]。
        rot 参数在这个实现中不再影响范围，仅保留给兼容用。
    """
    if not GetCompGameLevel().IsEntityAlive(main_entity_id):
        return None

    # 1. 获取立方体中心：直接用实体中心，而不是像之前那样沿朝向偏移 half_length
    main_entity_center_pos = AttributeServerUtils.GetEntityCenterPos(main_entity_id)
    if main_entity_center_pos is None:
        return None

    # 2. 计算各轴半尺寸（你要长宽高都为 5 的话，width=length=height=5 就行）
    half_width = width / 2.0
    half_length = length / 2.0
    half_height = height / 2.0

    # 3. 构建一个轴对齐的 AABB（X=宽，Y=高，Z=长）
    min_bounds, max_bounds = calculate_new_bounds_3d(
        main_entity_center_pos,
        half_width=half_width,
        half_height=half_height,
        half_length=half_length
    )

    # 4. 仍然用一个比较大的半径先粗筛一圈附近实体，避免全图遍历
    search_radius = max(width, length, height) * 2
    around_entity_list = CheckEntityAroundEntityList(
        main_entity_id,
        search_radius,
        exclude_entity_list,
        has_tag,
        has_not_tag,
        exclude_family_list,
        has_family_list,
        filters=filters
    )

    # 5. 用 AABB 做精准过滤
    cube_entity_list = []
    for entity_id in around_entity_list:
        entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
        if entity_center_pos is None:
            continue

        # 只要在 X/Y/Z 三个轴上的坐标都落在 [min_bounds, max_bounds] 就算在立方体内
        if IsPosInBounds(entity_center_pos, min_bounds, max_bounds):
            cube_entity_list.append(entity_id)

    return cube_entity_list


def CalculateRectVertices(entity_id, width, length, height=4, rot=None):
    """
    计算矩形的八个顶点坐标
        该方法根据传入的实体ID（entity_id）、矩形的宽度（width）、长度（length）、高度（height）参数，
        计算并返回矩形的八个顶点坐标列表。

    :param entity_id: 实体的ID
    :type entity_id: str
    :param width: 矩形的宽度
    :type width: float or int
    :param length: 矩形的长度
    :type length: float or int
    :param height: 矩形的高度，默认为4
    :type height: float or int

    :param rot:rot

    :return: 矩形的八个顶点坐标 [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4), (x5, y5, z5), (x6, y6, z6), (x7, y7, z7), (x8, y8, z8)]
    :rtype: list[tuple[int or float,int or float,int or float]] or None
    """
    if not GetCompGameLevel().IsEntityAlive(entity_id):
        return None
    entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
    if entity_center_pos is None:
        return None
    entity_x, entity_y, entity_z = entity_center_pos

    entity_rot = rot if rot else CompFactory.CreateRot(entity_id).GetRot()
    if entity_rot is None:
        return None
    dir_x, dir_y, dir_z = ServerApi.GetDirFromRot((0, entity_rot[1]))

    half_width = width / 2.0
    half_length = length / 2.0
    half_height = height / 2.0

    # 计算立方体中心点坐标
    cube_center = (entity_x + dir_x * half_length, entity_y, entity_z + dir_z * half_length)

    perpendicular_dir_x = -dir_z
    perpendicular_dir_z = dir_x

    # 计算立方体的8个顶点
    vertices = []
    for dx in [-half_width, half_width]:
        for dy in [-half_height, half_height]:
            for dz in [-half_length, half_length]:
                # 首先计算在中心点的基础上，进行平移后的坐标
                temp_x = cube_center[0] + dx * perpendicular_dir_x + dz * dir_x
                temp_y = cube_center[1] + dy
                temp_z = cube_center[2] + dx * perpendicular_dir_z + dz * dir_z

                vertices.append((temp_x, temp_y, temp_z))

    return vertices


def CalculateCubeCenter(entity_id, length):
    """
    计算矩形的中心坐标
        该方法根据传入的实体ID（entity_id）和矩形的长度（length）参数，
        计算并返回矩形的中心坐标。

    :param entity_id: 实体的ID
    :type entity_id: str
    :param length: 矩形的长度
    :type length: float or int

    :return: 矩形的中心坐标 (cube_center_x, cube_center_y, cube_center_z)
    :rtype: tuple[int or float,int or float,int or float] or None
    """
    if not GetCompGameLevel().IsEntityAlive(entity_id):
        return None
    entity_center_pos = AttributeServerUtils.GetEntityCenterPos(entity_id)
    if entity_center_pos is None:
        return None
    entity_x, entity_y, entity_z = entity_center_pos

    entity_rot = CompFactory.CreateRot(entity_id).GetRot()
    if entity_rot is None:
        return None
    dir_x, dir_y, dir_z = ServerApi.GetDirFromRot((0, entity_rot[1]))

    half_length = length / 2.0

    cube_center_x = entity_x + dir_x * half_length
    cube_center_y = entity_y
    cube_center_z = entity_z + dir_z * half_length

    return cube_center_x, cube_center_y, cube_center_z


def calculate_new_bounds(pos, diff_value, change_x=True, change_y=True, change_z=True):
    """
    计算给定位置在指定差值下的最小和最大坐标范围。

    参数:
    pos (tuple): 三维坐标位置，以(x, y, z)形式给出。
    diff_value (float): 用于计算范围的差值。
    change_x (bool): 是否计算x轴上的新范围，默认为True。
    change_y (bool): 是否计算y轴上的新范围，默认为True。
    change_z (bool): 是否计算z轴上的新范围，默认为True。

    返回:
    tuple: 包含两个元组，第一个元组为(min_x, min_y, min_z)，第二个元组为(max_x, max_y, max_z)。
    """
    x, y, z = pos

    # 计算x的范围
    if change_x:
        min_x = x - diff_value
        max_x = x + diff_value
    else:
        min_x = max_x = x

    # 计算y的范围
    if change_y:
        min_y = y - diff_value
        max_y = y + diff_value
    else:
        min_y = max_y = y

    # 计算z的范围
    if change_z:
        min_z = z - diff_value
        max_z = z + diff_value
    else:
        min_z = max_z = z

    return (min_x, min_y, min_z), (max_x, max_y, max_z)


def calculate_new_bounds_3d(center_pos, half_width, half_height, half_length):
    """
    根据中心点和各轴半尺寸，计算轴对齐的 AABB 边界。

    :param center_pos: 中心点 (cx, cy, cz)
    :param half_width: X 轴方向半宽
    :param half_height: Y 轴方向半高
    :param half_length: Z 轴方向半长
    :return: (min_bounds, max_bounds)
    """
    cx, cy, cz = center_pos

    min_bounds = (cx - half_width,
                  cy - half_height,
                  cz - half_length)
    max_bounds = (cx + half_width,
                  cy + half_height,
                  cz + half_length)

    return min_bounds, max_bounds


def IsPosInBounds(pos, min_bounds, max_bounds):
    """
    检查给定位置是否在最小和最大坐标范围内。

    参数:
    pos (tuple): 三维坐标位置，以 (x, y, z) 形式给出。
    min_bounds (tuple): 最小坐标范围，以 (min_x, min_y, min_z) 形式给出。
    max_bounds (tuple): 最大坐标范围，以 (max_x, max_y, max_z) 形式给出。

    返回:
    bool: 如果位置在范围内则返回 True，否则返回 False。
    """
    x, y, z = pos
    min_x, min_y, min_z = min_bounds
    max_x, max_y, max_z = max_bounds

    return min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z


def IsPointInCube(point, vertices):
    """
    检查点是否位于立方体内部
        该方法用于检查给定的点是否位于由顶点坐标列表vertices定义的立方体内部。

    :param point: 待检查的点坐标 (x, y, z)
    :type point: tuple
    :param vertices: 立方体的八个顶点坐标列表 [(x1, y1, z1), (x2, y2, z2), (x3, y3, z3), (x4, y4, z4), (x5, y5, z5), (x6, y6, z6), (x7, y7, z7), (x8, y8, z8)]
    :type vertices: list of tuples

    :return: 如果点位于立方体内部，则返回True；否则返回False。
    :rtype: bool
    """
    min_x = min(vertices, key=lambda t: t[0])[0]
    max_x = max(vertices, key=lambda t: t[0])[0]
    min_y = min(vertices, key=lambda t: t[1])[1]
    max_y = max(vertices, key=lambda t: t[1])[1]
    min_z = min(vertices, key=lambda t: t[2])[2]
    max_z = max(vertices, key=lambda t: t[2])[2]

    x, y, z = point

    return min_x <= x <= max_x and min_y <= y <= max_y and min_z <= z <= max_z


_delay_set_motion_timer_dict = {}


def SetPlayerMotion(player_list, motion):
    """
    对传入的玩家ID或玩家ID列表设置运动参数
        该方法用于设置玩家ID或玩家ID列表的运动参数。可以同时设置多个实体的运动参数。

    :param player_list: 实体ID或实体ID列表
    :type player_list: str or list[str]
    :param motion: 运动参数 (dx, dy, dz)
    :type motion: tuple[int or float,int or float,int or float] or list[int or float,int or float,int or float]
    """

    def set_entity_motion(entity_id, set_motion):
        CompFactory.CreateActorMotion(entity_id).SetPlayerMotion(set_motion)

    entity_list = tuple(player_list) if isinstance(player_list, list) else player_list
    if entity_list in _delay_set_motion_timer_dict:
        GetCompGameLevel().CancelTimer(_delay_set_motion_timer_dict[entity_list])
        _delay_set_motion_timer_dict.pop(_delay_set_motion_timer_dict)
    if isinstance(entity_list, str):
        set_entity_motion(entity_list, motion)
    else:
        for entity in entity_list:
            set_entity_motion(entity, motion)


def SetEntityMotion(entity_id, motion):
    """
    对传入的实体ID设置运动参数

    :param entity_id: 实体ID
    :type entity_id: str or list[str] or tuple[str]
    :param motion: 运动参数 (dx, dy, dz)
    :type motion: tuple[int or float,int or float,int or float] or list[int or float,int or float,int or float]
    """

    if isinstance(entity_id, list) or isinstance(entity_id, tuple):
        SetEntityMotionList(entity_id, motion)
        return
    if entity_id in _delay_set_motion_timer_dict:
        GetCompGameLevel().CancelTimer(_delay_set_motion_timer_dict[entity_id])
        _delay_set_motion_timer_dict.pop(_delay_set_motion_timer_dict)
    if entity_id in ServerApi.GetPlayerList():
        CompFactory.CreateActorMotion(entity_id).SetPlayerMotion(motion)
    else:
        CompFactory.CreateActorMotion(entity_id).SetMotion(motion)


def SetEntityMotionList(entity_list, motion):
    """
    对传入的实体ID或实体ID列表设置运动参数
        该方法用于设置实体ID或实体ID列表的运动参数。可以同时设置多个实体的运动参数。

    :param entity_list: 实体ID或实体ID列表
    :type entity_list: list[str] or tuple[str]
    :param motion: 运动参数 (dx, dy, dz)
    :type motion: tuple[int or float,int or float,int or float] or list[int or float,int or float,int or float]
    """

    def set_entity_motion(entity_id, set_motion):
        if entity_id in ServerApi.GetPlayerList():
            CompFactory.CreateActorMotion(entity_id).SetPlayerMotion(set_motion)
        else:
            CompFactory.CreateActorMotion(entity_id).SetMotion(set_motion)

    entity_list = tuple(entity_list)
    if entity_list in _delay_set_motion_timer_dict:
        GetCompGameLevel().CancelTimer(_delay_set_motion_timer_dict[entity_list])
        _delay_set_motion_timer_dict.pop(_delay_set_motion_timer_dict)
    for entity in entity_list:
        set_entity_motion(entity, motion)


def DelaySetEntityMotion(delay_time, entity_list, motion):
    """
    延迟对传入的实体ID或实体ID列表设置运动参数
        该方法用于延迟一定时间后，对实体ID或实体ID列表设置运动参数。

    :param delay_time: 延迟时间（秒）
    :type delay_time: float
    :param entity_list: 实体ID或实体ID列表
    :type entity_list: str or list[str]
    :param motion: 运动参数 (dx, dy, dz)
    :type motion: tuple[int or float,int or float,int or float] or list[int or float,int or float,int or float]

    """
    if entity_list in _delay_set_motion_timer_dict:
        GetCompGameLevel().CancelTimer(_delay_set_motion_timer_dict[entity_list])
        _delay_set_motion_timer_dict.pop(_delay_set_motion_timer_dict)
    _delay_set_motion_timer_dict[entity_list] = GetCompGameLevel().AddTimer(delay_time, SetEntityMotion, entity_list,
                                                                            motion)


def CalcDistantByDoublePoint(point_1, point_2):
    """
    计算两个坐标点之间的直线距离
        该方法根据传入的两个坐标点，计算它们之间的直线距离。

    :param point_1: 第一个坐标点 (x1, y1, z1)
    :type point_1: tuple
    :param point_2: 第二个坐标点 (x2, y2, z2)
    :type point_2: tuple

    :return: 两个坐标点之间的直线距离
    :rtype: float
    """
    (x1, y1, z1), (x2, y2, z2) = point_1, point_2
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2 + (z2 - z1) ** 2)


def CalcDistantByDoubleEntityId(entity_id_1, entity_id_2, is_head=False):
    """
    计算两个实体的直线距离
        该方法根据传入的两个实体的entity_id，计算它们之间的直线距离。

    :param entity_id_1: 第一个实体的entity_id
    :type entity_id_1: str
    :param entity_id_2: 第二个实体的entity_id
    :type entity_id_2: str
    :param is_head: is_head
    :type is_head: bool

    :return: 两个实体之间的直线距离
    :rtype: float or None
    """
    if not GetCompGameLevel().IsEntityAlive(entity_id_1) or not GetCompGameLevel().IsEntityAlive(entity_id_2):
        return None
    if is_head:
        pos_1 = CompFactory.CreatePos(entity_id_1).GetPos()
        pos_2 = CompFactory.CreatePos(entity_id_2).GetPos()
    else:
        pos_1 = CompFactory.CreatePos(entity_id_1).GetFootPos()
        pos_2 = CompFactory.CreatePos(entity_id_2).GetFootPos()
    if pos_1 is None or pos_2 is None:
        return None
    return CalcDistantByDoublePoint(pos_1, pos_2)


def CalcVectorByDoublePoint(point_1, point_2):
    """
    计算两个坐标点之间的向量
        该方法根据传入的两个坐标点，计算从point_2指向point_1的向量，并将其归一化。

    :param point_1: 第一个坐标点 (x1, y1, z1)
    :type point_1: tuple[int or float,int or float,int or float]
    :param point_2: 第二个坐标点 (x2, y2, z2)
    :type point_2: tuple[int or float,int or float,int or float]

    :return: 从point_2指向point_1的归一化向量 (dx, dy, dz)
    :rtype: tuple[int or float,int or float,int or float]
    """
    delta = Vector3(point_1) - Vector3(point_2)
    return delta.Normalized()


def CalcVectorByDoubleEntityId(entity_id_1, entity_id_2):
    """
    根据传入的两个实体的entity_id计算向量
        该方法根据传入的两个实体的entity_id，计算从entity_id_2指向entity_id_1的向量，并将其归一化。

    :param entity_id_1: 第一个实体的entity_id
    :type entity_id_1: str
    :param entity_id_2: 第二个实体的entity_id
    :type entity_id_2: str

    :return: 从entity_id_2指向entity_id_1的归一化向量 (dx, dy, dz)
    :rtype: tuple[int or float,int or float,int or float] or None
    """
    if not GetCompGameLevel().IsEntityAlive(entity_id_1) or not GetCompGameLevel().IsEntityAlive(entity_id_2):
        return None
    entity_id_1_pos = CompFactory.CreatePos(entity_id_1).GetFootPos()
    entity_id_2_pos = CompFactory.CreatePos(entity_id_2).GetFootPos()
    if entity_id_1_pos and entity_id_2_pos:
        return CalcVectorByDoublePoint(entity_id_1_pos, entity_id_2_pos)
    return None


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


def NormalizeVector(vector_tuple):
    """
    归一化向量
    :param vector_tuple: 待归一化的向量 (dx, dy, dz)
    :type vector_tuple: tuple[int or float,int or float,int or float]
    :return: 归一化向量
    :rtype: tuple[int or float,int or float,int or float]
    """
    x, y, z = vector_tuple
    length = math.sqrt(x ** 2 + y ** 2 + z ** 2)
    if length == 0:
        return 0, 0, 0  # 避免除以零
    return x / length, y / length, z / length


def RemoveEntityAllOldMotion(entity_id):
    """
    RemoveEntityAllOldMotion
    :param entity_id: entity_id
    :type entity_id: str
    """
    comp_action_motion = CompFactory.CreateActorMotion(entity_id)

    if AttributeServerUtils.CheckEntityIsPlayer(entity_id):
        for MID in copy.deepcopy(comp_action_motion.GetPlayerMotions()):
            comp_action_motion.RemovePlayerMotion(MID)
    else:
        for MID in copy.deepcopy(comp_action_motion.GetEntityMotions()):
            comp_action_motion.RemoveEntityMotion(MID)


def RemoveEntityMotionById(entity_id, motion_id):
    """
    RemoveEntityMotionById
    :param entity_id: entity_id
    :type entity_id: str
    :param motion_id: motion_id
    :type motion_id: int
    """

    if AttributeServerUtils.CheckEntityIsPlayer(entity_id):
        CompFactory.CreateActorMotion(entity_id).RemovePlayerMotion(motion_id)
    else:
        CompFactory.CreateActorMotion(entity_id).RemoveEntityMotion(motion_id)


def AddEntityTrackMotion(entity_id, target_pos, dura_time, start_pos=None, relative_coord=False, is_loop=False,
                         target_rot=None, start_rot=None,
                         use_velocity_dir=False, need_remove_old_motion=True):
    """
    给实体添加轨迹运动器
        该方法用于向指定实体添加轨迹运动器，实现指定终点、时间、起点等参数来控制实体的运动轨迹。

    该接口不屏蔽生物本身的AI运动，并且生物在空中时会受到跌落伤害，当有AI运动发生时，最终的表现结果可能与预期有差异，建议将生物设置为NPC。
    轨迹运动器不可叠加，仅能添加一个。
    由于引擎中在加载的区块以外的实体时会停止一切活动，建议将运动范围控制在玩家位置±100内。
    设置朝向后会根据相应的参数计算出最终朝向，若此时的targetRot > startRot，则会顺时针旋转，反之逆时针旋转。

    :param entity_id: 目标实体的entity_id
    :type entity_id: str
    :param target_pos: 轨迹的终点坐标 (x, y, z)
    :type target_pos: tuple[int or float,int or float,int or float]
    :param dura_time: 到达终点所需的时间（秒）
    :type dura_time: float
    :param start_pos: 轨迹的起点坐标，默认为None，表示使用实体当前位置作为起点
    :type start_pos: tuple[int or float,int or float,int or float] or None
    :param relative_coord: 是否使用相对坐标设置起点和终点的位置以及朝向，默认为False
    :type relative_coord: bool
    :param is_loop: 是否循环运动，若为True，则实体会在起点和终点之间往复运动，默认为False
    :type is_loop: bool
    :param target_rot: 实体到达target_pos时的朝向，受参数relative_coord影响，默认为None，表示使用实体当前朝向
    :type target_rot: tuple[int or float,int or float,int or float] or None
    :param start_rot: 实体到达start_pos时的朝向，受参数relative_coord影响，默认为None，表示使用实体当前朝向
    :type start_rot: tuple[int or float,int or float,int or float] or None
    :param use_velocity_dir: 是否使用运动中的速度方向作为朝向，默认为False，若为True，则参数target_rot和start_rot无效
    :type use_velocity_dir: bool
    :param need_remove_old_motion: 是否移除旧运动执行器
    :type need_remove_old_motion: bool



    :return: 运动器ID，添加失败时返回-1
    :rtype: int or None
    """
    if not GetCompGameLevel().IsEntityAlive(entity_id):
        return
    if need_remove_old_motion:
        RemoveEntityAllOldMotion(entity_id)
    comp_action_motion = CompFactory.CreateActorMotion(entity_id)
    if AttributeServerUtils.CheckEntityIsPlayer(entity_id):
        motion_id = comp_action_motion.AddPlayerTrackMotion(target_pos, dura_time, start_pos, relative_coord, is_loop,
                                                            target_rot, start_rot,
                                                            use_velocity_dir)
        comp_action_motion.StartPlayerMotion(motion_id)
        return motion_id if motion_id and motion_id != -1 else None
    motion_id = comp_action_motion.AddEntityTrackMotion(target_pos, dura_time, start_pos, relative_coord, is_loop,
                                                        target_rot, start_rot,
                                                        use_velocity_dir)
    comp_action_motion.StartEntityMotion(motion_id)
    # print comp_action_motion.GetEntityMotions()
    return motion_id if motion_id and motion_id != -1 else None


def AddEntityVelocityMotion(entity_id, velocity, accelerate=None, useVelocityDir=True):
    """
    给实体添加速度运动器
        该方法用于向指定实体添加轨迹运动器，实现指定终点、时间、起点等参数来控制实体的运动轨迹。
        该接口不屏蔽生物本身的AI运动以及重力作用，当有AI运动发生时，最终的表现结果可能与预期有差异。
        速度运动器可叠加多个，且可与环绕运动器互相叠加。
        由于引擎中在加载的区块以外的实体时会停止一切活动，建议将实体的运动范围控制在玩家位置±100内。
        该接口不屏蔽玩家控制的移动以及重力作用，当有玩家控制发生时，最终的表现结果可能与预期有差异。由于玩家的头部与相机控制相关，若需要使运动器控制玩家的头部，请使用DepartCamera分离玩家与摄像机。
        由于引擎中有加载的区块限制，建议将玩家的运动范围控制在当前位置±100内。

    :param entity_id: 目标实体的entity_id
    :type entity_id: str
    :param velocity: 速度，包含大小、方向
    :type velocity: tuple[int or float,int or float,int or float]
    :param accelerate: 加速度，包含大小、方向，默认为None，表示没有加速度
    :type accelerate: tuple[int or float,int or float,int or float] or None
    :param useVelocityDir: 是否使用当前速度的方向作为此刻实体的朝向，默认为True
    :type useVelocityDir: bool

    :return: 运动器ID，添加失败时返回-1
    :rtype: int or None
    """
    comp_action_motion = CompFactory.CreateActorMotion(entity_id)
    if AttributeServerUtils.CheckEntityIsPlayer(entity_id):
        motion_id = comp_action_motion.AddPlayerVelocityMotion(velocity, accelerate, useVelocityDir)
        comp_action_motion.StartPlayerMotion(motion_id)
        return motion_id if motion_id and motion_id != -1 else None
    motion_id = comp_action_motion.AddEntityVelocityMotion(velocity, accelerate, useVelocityDir)
    comp_action_motion.StartEntityMotion(motion_id)
    return motion_id if motion_id and motion_id != -1 else None


def ChangeValueInPos(pos, absolute, change_pos):
    """
    根据传入的坐标以及坐标差值返回一个新坐标
        该方法根据传入的坐标（pos）、绝对值标志（absolute）、和坐标差值（change_pos）来计算新的坐标。

    :param pos: 原始坐标 (x, y, z)
    :type pos: tuple[int or float,int or float,int or float]
    :param absolute: 是否绝对值，若为True，则将坐标变化应用为绝对值，否则应用为增量
    :type absolute: bool
    :param change_pos: 需要改变的坐标差值，根据absolute参数的不同，可以是增量或绝对值
    :type change_pos: tuple[int or float,int or float,int or float]

    :return: 新的坐标 (x, y, z)
    :rtype: tuple[int or float,int or float,int or float]
    """
    try:
        if absolute:
            return tuple(new if change != 0 else old for old, new, change in zip(pos, change_pos, change_pos))
        return tuple(pos[i] + change_pos[i] for i in range(3))
    except Exception as e:
        return pos


def CeilPosValue(pos):
    """
    将传入坐标中的值都Ceil

    :param pos: 原始坐标 (x, y, z)
    :type pos: tuple[int or float,int or float,int or float]

    :return: 新的坐标 (x, y, z)
    :rtype: tuple[int or float,int or float,int or float]
    """
    return tuple(math.ceil(i) for i in pos)


def IntPosValue(pos):
    """
    将传入坐标中的值都int

    :param pos: 原始坐标 (x, y, z)
    :type pos: tuple[int or float,int or float,int or float]

    :return: 新的坐标 (x, y, z)
    :rtype: tuple[int,int,int]
    """
    return tuple(int(i) for i in pos)


def SetPosToBlockPos(pos):
    """
    将传入坐标中的值设置成block的pos

    :param pos: 原始坐标 (x, y, z)
    :type pos: tuple[int or float,int or float,int or float]

    :return: block的pos (x, y, z)
    :rtype: tuple[int,int,int]
    """
    # return tuple(int(math.ceil(i) if i > 0 else math.floor(i)) for i in pos)
    return tuple(round(i) for i in pos)
    # return tuple(int(i) for i in pos)


def GetEntitiesInSquareArea(start_pos, end_pos, dimension_id):
    """
    获取传入坐标范围内的生物
        该方法用于获取指定坐标范围内的生物实体。

    :param start_pos: 范围的起始坐标 (x1, y1, z1)
    :type start_pos: tuple[int or float,int or float,int or float]
    :param end_pos: 范围的结束坐标 (x2, y2, z2)
    :type end_pos: tuple[int or float,int or float,int or float]
    :param dimension_id: 维度ID
    :type dimension_id: int

    :return: 在指定范围内的生物实体列表
    :rtype: list[str]
    """
    x1, y1, z1 = start_pos
    x1, y1, z1 = int(x1), int(y1), int(z1)
    x2, y2, z2 = end_pos
    x2, y2, z2 = int(x2), int(y2), int(z2)
    min_pos = (min(x1, x2) - 2, min(y1, y2) - 2, min(z1, z2) - 2)
    max_pos = (max(x1, x2) + 2, max(y1, y2) + 2, max(z1, z2) + 2)
    return GetCompGameLevel().GetEntitiesInSquareArea(None, min_pos, max_pos, dimension_id)
