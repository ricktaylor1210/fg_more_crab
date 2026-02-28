# -*- coding: utf-8 -*-
import math
import random


class SphereField(object):
    """
    简洁的球形领域（服务端用）
    - 仅做几何与维度判定；不负责渲染/射线/广播
    - Python2 兼容
    """

    def __init__(self, center, radius, dimension_id, field_id=None, enabled=True, use_foot_pos=True,
                 follow_entity_id=None, follow_offset=(0.0, 0.0, 0.0),
                 follow_dimension=True, follow_use_foot_pos=None,
                 auto_sync_follow=True):
        """
        :param center: (x, y, z) 初始中心；若 follow_entity_id 存在则作为“同步前兜底”
        :param radius: float > 0
        :param dimension_id: int 初始维度；若 follow_dimension=True 则会被跟随实体维度覆盖
        :param follow_entity_id: 可选，领域跟随的实体 id
        :param follow_offset: 可选，领域中心相对跟随实体位置的偏移 (ox, oy, oz)
        :param follow_dimension: True 时领域维度随实体维度变化
        :param follow_use_foot_pos: None 则沿用 use_foot_pos；否则覆盖跟随时使用脚底/中心点
        :param auto_sync_follow: True 则在判定/过滤入口自动同步一次（避免调用方忘记同步）
        """
        if radius <= 0.0:
            raise ValueError("radius must be positive")

        self._center = tuple(center)
        self._radius = float(radius)
        self._dimension_id = int(dimension_id)
        self._field_id = str(field_id) if field_id is not None else str(id(self))
        self._enabled = bool(enabled)
        self._use_foot_pos_default = bool(use_foot_pos)

        self._follow_entity_id = follow_entity_id
        self._follow_offset = tuple(follow_offset) if follow_offset is not None else (0.0, 0.0, 0.0)
        self._follow_dimension = bool(follow_dimension)
        self._follow_use_foot_pos = None if follow_use_foot_pos is None else bool(follow_use_foot_pos)
        self._auto_sync_follow = bool(auto_sync_follow)

    # ------------------ 基础信息 ------------------

    def get_id(self):
        return self._field_id

    def get_center(self):
        return self._center

    def get_radius(self):
        return self._radius

    def get_dimension_id(self):
        return self._dimension_id

    def set_center(self, center):
        self._center = tuple(center)

    def set_radius(self, radius):
        r = float(radius)
        if r <= 0.0:
            raise ValueError("radius must be positive")
        self._radius = r

    def set_dimension_id(self, dim_id):
        self._dimension_id = int(dim_id)

    # <editor-fold desc="follw entity">
    def is_movable(self):
        """是否处于“跟随移动”模式"""
        return self._follow_entity_id is not None

    def set_follow_entity(self, entity_id, offset=(0.0, 0.0, 0.0),
                          follow_dimension=True, use_foot_pos=None, auto_sync=True):
        """
        开启/更新跟随目标。
        :param entity_id: 跟随实体 id
        :param offset: 领域中心相对实体位置偏移
        :param follow_dimension: 是否跟随实体维度
        :param use_foot_pos: 跟随时使用脚底/中心点；None 则沿用构造 use_foot_pos
        :param auto_sync: 是否在接口入口自动同步
        """
        self._follow_entity_id = entity_id
        self._follow_offset = tuple(offset) if offset is not None else (0.0, 0.0, 0.0)
        self._follow_dimension = bool(follow_dimension)
        self._follow_use_foot_pos = None if use_foot_pos is None else bool(use_foot_pos)
        self._auto_sync_follow = bool(auto_sync)

    def clear_follow_entity(self):
        """关闭跟随，领域回到静止模式（中心保持为最后一次同步后的值）"""
        self._follow_entity_id = None

    def sync_with_follow_entity(self, serverApi):
        """
        手动同步一次中心/维度（当 auto_sync_follow=False 时推荐每 tick 调一次）
        :return: bool 同步是否成功
        """
        comp_factory = serverApi.GetEngineCompFactory()
        return self._sync_follow_target(serverApi, comp_factory=comp_factory)

    def _sync_follow_target(self, serverApi, comp_factory=None):
        """
        内部：把中心（以及可选维度）同步到跟随实体。
        - 同步失败时不抛异常，保留原中心，避免技能逻辑被打断
        """
        if not self._follow_entity_id:
            return False

        if comp_factory is None:
            comp_factory = serverApi.GetEngineCompFactory()

        use_foot = self._use_foot_pos_default if self._follow_use_foot_pos is None else self._follow_use_foot_pos

        try:
            pos_comp = comp_factory.CreatePos(self._follow_entity_id)
            pos = pos_comp.GetFootPos() if use_foot else pos_comp.GetPos()
        except Exception:
            return False

        if not pos:
            return False

        try:
            px, py, pz = float(pos[0]), float(pos[1]), float(pos[2])
        except Exception:
            return False

        ox, oy, oz = self._follow_offset
        self._center = (px + ox, py + oy, pz + oz)

        if self._follow_dimension:
            try:
                dim_comp = comp_factory.CreateDimension(self._follow_entity_id)
                dim_id = dim_comp.GetEntityDimensionId()
                self._dimension_id = int(dim_id)
            except Exception:
                # 维度同步失败不影响中心同步
                pass

        return True

    # </editor-fold>

    # ------------------ 开关控制 ------------------

    def open(self):
        """开启领域判定"""
        self._enabled = True

    def close(self):
        """关闭领域判定"""
        self._enabled = False

    def is_open(self):
        return self._enabled

    # ------------------ 判定接口 ------------------

    def is_entity_in_field(self, serverApi, entity_id, entity_dimension_id=None,
                           margin=0.0, use_foot_pos=None, respect_dimension=True):
        """
        判定单个生物是否在领域内。
        :param serverApi: mod.server.extraServerApi
        :param entity_id: 实体 id
        :param entity_dimension_id: 可选，若已知则传入可省一次查询
        :param margin: 外扩半径（>=0），如 0.5
        :param use_foot_pos: 覆盖默认坐标口径；None 则沿用构造时的默认
        :param respect_dimension: True 则要求实体维度与领域维度一致
        :return: bool
        """
        if not self._enabled:
            return False

        comp_factory = serverApi.GetEngineCompFactory()

        if self._follow_entity_id and self._auto_sync_follow:
            self._sync_follow_target(serverApi, comp_factory=comp_factory)

        # 维度判定（可选）
        if respect_dimension:
            dim_id = entity_dimension_id
            if dim_id is None:
                dim_comp = comp_factory.CreateDimension(entity_id)
                # 个别版本 API 名可能不同，如 GetEntityDimensionId / GetEntityDimensionId()
                dim_id = dim_comp.GetEntityDimensionId()
            if int(dim_id) != self._dimension_id:
                return False

        # 位置获取
        pos_comp = comp_factory.CreatePos(entity_id)
        use_foot = self._use_foot_pos_default if use_foot_pos is None else bool(use_foot_pos)
        pos = pos_comp.GetFootPos() if use_foot else pos_comp.GetPos()

        return self._is_pos_in_sphere(pos, margin)

    def filter_entities_in_field(self, serverApi, entity_map,
                                 margin=0.0, use_foot_pos=None,
                                 respect_dimension=True, return_dict=False,
                                 exclude_entity_list=None, exclude_tag_list=None,
                                 exclude_family_list=None,
                                 has_tag_list=None, has_family_list=None,
                                 include_entity_list=None):
        """
        过滤并返回在领域内的实体（输入为 {entity_id: {'dimensionId': int, 'identifier': str}, ...}）。

        注意 include_entity_list 的语义（已调整）：
        :param include_entity_list: 可选，额外追加要判定的实体 id 列表。
            - 它不是“筛选器”，不会限制 entity_map 的遍历范围；
            - 会优先对 include_entity_list 中的实体做“维度 + 位置(是否在领域内)”判定；
            - include_entity_list 中的实体不会参与 tag/family 的 exclude/has 判定；
            - exclude_entity_list 仍然优先（即便在 include 中，也会被排除）。
        """
        if (not self._enabled) or (not entity_map and not include_entity_list):
            return {} if return_dict else []

        comp_factory = serverApi.GetEngineCompFactory()

        if self._follow_entity_id and self._auto_sync_follow:
            self._sync_follow_target(serverApi, comp_factory=comp_factory)

        result_ids, result_dict = [], {}

        exclude_ids = set(exclude_entity_list) if exclude_entity_list else None

        # include：不是筛选器，是“额外追加一批仅做(维度+位置)判定”的实体
        include_list = list(include_entity_list) if include_entity_list else []
        include_ids = set(include_list) if include_list else None

        exclude_tags = set(exclude_tag_list) if exclude_tag_list else None
        exclude_families = set(exclude_family_list) if exclude_family_list else None

        has_tags = set(has_tag_list) if has_tag_list else None
        has_families = set(has_family_list) if has_family_list else None
        need_has_filter = bool(has_tags) or bool(has_families)

        use_foot = self._use_foot_pos_default if use_foot_pos is None else bool(use_foot_pos)

        # 只有确实需要时才创建组件，避免每个实体都无脑创建
        need_tag_comp = bool(exclude_tags) or bool(has_tags)
        need_attr_comp = bool(exclude_families) or bool(has_families)

        # ---- A) 先处理 include_entity_list：只做 exclude_id + (可选)维度 + 位置 ----
        # 设计约束：include 中的实体不走 tag/family（包括 exclude_* 与 has_*），避免被“属性判定”影响。
        if include_list:
            # 用于去重，避免 include_list 里重复 id 或者后续重复写入
            already_added = set()

            for eid in include_list:
                if not eid or eid in already_added:
                    continue
                already_added.add(eid)

                if exclude_ids and eid in exclude_ids:
                    continue

                info = entity_map.get(eid) if entity_map else None
                if info is None:
                    info = {}

                # 维度过滤（可选）
                dim_ok = True
                dim_id = None
                if respect_dimension:
                    dim_from_map = info.get('dimensionId') if isinstance(info, dict) else None
                    if dim_from_map is None:
                        try:
                            dim_comp = comp_factory.CreateDimension(eid)
                            dim_from_map = dim_comp.GetEntityDimensionId()
                        except Exception:
                            dim_ok = False
                    if dim_ok:
                        dim_id = dim_from_map
                        if int(dim_from_map) != self._dimension_id:
                            dim_ok = False

                if not dim_ok:
                    continue

                # 位置过滤
                try:
                    pos_comp = comp_factory.CreatePos(eid)
                    pos = pos_comp.GetFootPos() if use_foot else pos_comp.GetPos()
                except Exception:
                    continue

                if self._is_pos_in_sphere(pos, margin):
                    if return_dict:
                        # 尽量补充 dimensionId，避免调用方拿到空 dict 不好用
                        if isinstance(info,
                                      dict) and respect_dimension and dim_id is not None and 'dimensionId' not in info:
                            info = dict(info)
                            info['dimensionId'] = dim_id
                        result_dict[eid] = info
                    else:
                        result_ids.append(eid)

        # ---- B) 再处理 entity_map：走“原先逻辑” ----
        if not entity_map:
            return result_dict if return_dict else result_ids

        for entity_id, info in entity_map.items():
            # include 中的实体已经在 A 段决定收不收了，这里跳过，避免被 tag/family 逻辑影响
            if include_ids and entity_id in include_ids:
                continue

            # ---- 1) 最便宜的排除：id ----
            if exclude_ids and entity_id in exclude_ids:
                continue

            # ---- 2) 维度过滤（可选）----
            if respect_dimension:
                dim_from_map = info.get('dimensionId') if isinstance(info, dict) else None
                if dim_from_map is None:
                    dim_comp = comp_factory.CreateDimension(entity_id)
                    dim_from_map = dim_comp.GetEntityDimensionId()
                if int(dim_from_map) != self._dimension_id:
                    continue

            # ---- 3) tag / family 的排除（exclude 优先）----
            tag_comp = None
            if need_tag_comp:
                tag_comp = comp_factory.CreateTag(entity_id)

                if exclude_tags:
                    excluded = False
                    for tag_str in exclude_tags:
                        if tag_comp.EntityHasTag(tag_str):
                            excluded = True
                            break
                    if excluded:
                        continue

            attr_comp = None
            fam_set = None
            if need_attr_comp:
                attr_comp = comp_factory.CreateAttr(entity_id)
                fam_list = attr_comp.GetTypeFamily() or []
                if not isinstance(fam_list, (list, tuple, set)):
                    fam_list = [fam_list]
                fam_set = set(fam_list)

                if exclude_families and (fam_set & exclude_families):
                    continue

            # ---- 4) has_* 的包含过滤（OR：tag 命中 OR family 命中）----
            if need_has_filter:
                tag_match = False
                family_match = False

                if has_tags:
                    if tag_comp is None:
                        tag_comp = comp_factory.CreateTag(entity_id)
                    for tag_str in has_tags:
                        if tag_comp.EntityHasTag(tag_str):
                            tag_match = True
                            break

                if has_families:
                    if fam_set is None:
                        if attr_comp is None:
                            attr_comp = comp_factory.CreateAttr(entity_id)
                        fam_list = attr_comp.GetTypeFamily() or []
                        if not isinstance(fam_list, (list, tuple, set)):
                            fam_list = [fam_list]
                        fam_set = set(fam_list)
                    if fam_set & has_families:
                        family_match = True

                if not (tag_match or family_match):
                    continue

            # ---- 5) 位置过滤（最后再做，减少 CreatePos 调用）----
            pos_comp = comp_factory.CreatePos(entity_id)
            pos = pos_comp.GetFootPos() if use_foot else pos_comp.GetPos()

            if self._is_pos_in_sphere(pos, margin):
                if return_dict:
                    result_dict[entity_id] = info
                else:
                    result_ids.append(entity_id)

        return result_dict if return_dict else result_ids

    def filter_all_living_in_field(self, serverApi,
                                   margin=0.0, use_foot_pos=None,
                                   respect_dimension=True, return_dict=False,
                                   exclude_entity_list=None, exclude_tag_list=None,
                                   exclude_family_list=None,
                                   has_tag_list=None, has_family_list=None,
                                   include_entity_list=None):
        """
        封装一个“自动把 EngineActor + PlayerList 合并后再过滤”的便捷接口。
        支持 exclude_* 与 has_*（has_* 为 OR；exclude_* 优先）。

        include_entity_list 语义（已调整）：
        - 额外追加要判定的实体 id，只做(维度+位置)判定，不参与 tag/family 的 exclude/has 判定；
        - 不再把 include_entity_list 强行塞入 entity_map，避免被后续 tag/family 逻辑影响。
        """
        comp_factory = serverApi.GetEngineCompFactory()

        if self._follow_entity_id and self._auto_sync_follow:
            self._sync_follow_target(serverApi, comp_factory=comp_factory)

        # 1. 引擎实体（怪物等）
        entity_map = dict(serverApi.GetEngineActor() or {})

        # 2. 玩家
        player_list = serverApi.GetPlayerList() or []
        for player_id in player_list:
            if player_id in entity_map:
                continue
            dim_comp = comp_factory.CreateDimension(player_id)
            dim_id = dim_comp.GetEntityDimensionId()
            entity_map[player_id] = {
                "dimensionId": dim_id,
                "identifier": "minecraft:player",
            }

        # 3. 复用过滤逻辑（include_entity_list 由 filter_entities_in_field 内部单独处理）
        return self.filter_entities_in_field(
            serverApi,
            entity_map,
            margin=margin,
            use_foot_pos=use_foot_pos,
            respect_dimension=respect_dimension,
            return_dict=return_dict,
            exclude_entity_list=exclude_entity_list,
            exclude_tag_list=exclude_tag_list,
            exclude_family_list=exclude_family_list,
            has_tag_list=has_tag_list,
            has_family_list=has_family_list,
            include_entity_list=include_entity_list,
        )

    def generate_edge_points_to_center(self,serverApi, count, y=None, randomize_phase=True, jitter_strength=0.4):
        """
        在 XZ 平面上，从领域边缘生成 count 个点位，面向领域中心。
        注意：起点位置的 y 一律采用领域中心的 y（忽略入参 y）。
        :param count: 需要的点位数量（<=0 返回空）
        :param y: 兼容旧签名，已忽略；起点 y 总为中心 y
        :param randomize_phase: True 时为等间距方案增加随机相位
        :param jitter_strength: 分层随机抖动强度（0~0.5 建议），仅用于 count>=4
        :return: list of (pos, rot_unit, end_pos)
                 pos=(x,y,z) 为边缘起点；rot_unit=(dx,dy,dz) 为单位向量，水平朝向中心（dy=0）；
                 end_pos 为从 pos 沿 rot_unit 前进、在球体内的最终位置（即射线与对侧球面的交点）
        """
        if count is None or count <= 0:
            return []
        count = int(count)

        if serverApi is not None and self._follow_entity_id and self._auto_sync_follow:
            comp_factory = serverApi.GetEngineCompFactory()
            self._sync_follow_target(serverApi, comp_factory=comp_factory)

        cx, cy, cz = self._center[0], self._center[1], self._center[2]
        R = self._radius

        twopi = 6.283185307179586
        res = []

        # ---- 角度分配 ----
        angles = []
        if count == 1:
            base = random.random() * twopi
            angles = [base]
        elif count == 2:
            base = random.random() * twopi
            angles = [base, (base + math.pi) % twopi]
        elif count == 3:
            base = (random.random() * twopi) if randomize_phase else 0.0
            step = twopi / 3.0
            angles = [(base + i * step) % twopi for i in range(3)]
        else:
            base = (random.random() * twopi) if randomize_phase else 0.0
            step = twopi / float(count)
            jitter_half = step * max(0.0, min(0.5, jitter_strength)) * 0.5
            for i in range(count):
                a = base + i * step
                if jitter_half > 0.0:
                    a += random.uniform(-jitter_half, jitter_half)
                angles.append(a % twopi)

        # ---- 角度 -> 点位与朝向 + 终点 ----
        for a in angles:
            # 圆周起点（半径 R，y 固定为 cy）
            px = cx + R * math.cos(a)
            pz = cz + R * math.sin(a)
            pos = (px, cy, pz)

            # 朝向中心（水平分量，dy=0）
            vx = cx - px
            vz = cz - pz
            mag = math.sqrt(vx * vx + vz * vz)
            if mag < 1e-8:
                # 退化保护（半径过小或数值异常）
                dx, dz = 0.0, 1.0
            else:
                dx, dz = vx / mag, vz / mag
            rot_unit = (dx, 0.0, dz)

            # 计算“在领域内最终会移动到的位置” end_pos：
            # 通用做法：射线 P + t * d 与球 (X - C)^2 = R^2 的交点。
            # 设 m = P - C，则 (m + t d)^2 = R^2。因 P 在球面上，m·m = R^2，
            # 化简得：2 t (m·d) + t^2 = 0 -> t=0 或 t_exit = -2 (m·d)。
            mx, mz = px - cx, pz - cz  # m 的水平分量（y 相同为 0）
            mdotd = mx * dx + mz * dz
            t_exit = -2.0 * mdotd  # 期望为正（d 指向内侧时 mdotd<0）

            # 数值稳健性：若出现意外负值，退回到几何直觉 2R
            if t_exit <= 1e-8:
                t_exit = 2.0 * R

            end_pos = (px + dx * t_exit, cy, pz + dz * t_exit)

            res.append((pos, rot_unit, end_pos))

        return res

    # ------------------ 内部工具 ------------------

    def _is_pos_in_sphere(self, pos, margin):
        cx, cy, cz = self._center
        px, py, pz = tuple(pos)
        dx = px - cx
        dy = py - cy
        dz = pz - cz
        r = self._radius + float(margin)
        return (dx*dx + dy*dy + dz*dz) <= (r * r + 1e-6)
