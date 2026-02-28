# -*- coding: utf-8 -*-
import math
import random

class RayFieldManager(object):
    """
    右手系 3D 球形领域内的“射线段”管理（服务端用）
    - 生成 / 增删 / 替换线段
    - 导出 set((start_pos, end_pos, direction, distance), ...)
    - 提供 raycast_and_get_hits(...)：由调用方每 tick/每秒调用；返回命中的 ray_id 列表
    - 提供构造给客户端绘制的 payload（init / update / clear）
    """

    def __init__(self, center, radius, max_segments, dimension_id,
                 min_len=3.0, line_color=(0.0, 1.0, 0.0), field_id=None):
        """
        :param center: (cx, cy, cz)
        :param radius: float > 0
        :param max_segments: int > 0
        :param dimension_id: int（你会传入）
        :param min_len: float，最小线段长度阈值（默认 3.0）
        :param line_color: (r, g, b) in [0,1]，默认绿色
        :param field_id: 可选字符串，标识这个领域（不传则用 id(self)）
        """
        if radius <= 0.0 or max_segments <= 0:
            raise ValueError("radius and max_segments must be positive.")

        self.center = tuple(center)
        self.radius = float(radius)
        self.max_segments = int(max_segments)
        self.dimension_id = int(dimension_id)
        self.min_len = float(min_len)
        self.line_color = tuple(line_color)
        self.field_id = str(field_id) if field_id is not None else str(id(self))

        # ray_id -> {'start':(x,y,z), 'end':(x,y,z), 'dir':(dx,dy,dz), 'dist':float}
        self._rays = {}
        self._next_ray_id = 1
        self._disposed = False

    # ---------- 公共接口 ----------
    def is_pos_in_field(self, pos, margin=0.0):
        """
        判断一个位置是否在领域（球域）内。
        :param pos: (x, y, z)
        :param margin: 允许的外扩边距（>=0），例如 0.5 表示半径临时加 0.5 再判断
        """
        p = tuple(pos)
        r = self.radius + float(margin)
        dx = p[0] - self.center[0]
        dy = p[1] - self.center[1]
        dz = p[2] - self.center[2]
        return (dx * dx + dy * dy + dz * dz) <= (r * r + 1e-6)

    def is_entity_in_field(self, serverApi, entity_id, margin=0.0, use_foot_pos=True):
        """
        判断一个实体是否在领域（球域）内（服务端）。
        :param serverApi: mod.server.extraServerApi
        :param entity_id: 实体 ID
        :param margin: 外扩边距
        :param use_foot_pos: True 用脚底坐标，False 用中心坐标
        """
        comp_factory = serverApi.GetEngineCompFactory()
        pos_comp = comp_factory.CreatePos(entity_id)
        pos = pos_comp.GetFootPos() if use_foot_pos else pos_comp.GetPos()
        return self.is_pos_in_field(pos, margin)

    def generate_initial(self):
        """填充到 max_segments。"""
        self._ensure_not_disposed()
        added = []
        while len(self._rays) < self.max_segments:
            ray_id, line = self._add_random_ray_internal()
            if ray_id is None:
                continue
            added.append(self._line_to_payload(ray_id, line))
        return added  # 便于直接用于 init payload 的 'lines'

    def get_ray(self, ray_id):
        return self._rays.get(ray_id)  # 返回 {'start','end','dir','dist'} 或 None

    def get_rays_set(self):
        """返回题述格式：set((start_pos, end_pos, direction, distance), ...)"""
        result = set()
        for _, line in self._rays.items():
            result.add((line['start'], line['end'], line['dir'], line['dist']))
        return result

    def add_random_ray(self):
        """新增一条随机线段，返回 (ray_id, line_payload)；失败返回 (None, None)。"""
        self._ensure_not_disposed()
        if len(self._rays) >= self.max_segments:
            return (None, None)
        ray_id, line = self._add_random_ray_internal()
        if ray_id is None:
            return (None, None)
        return (ray_id, self._line_to_payload(ray_id, line))

    def add_ray(self, start_pos, end_pos):
        """手动添加；返回 (ray_id, line_payload)。不合法会抛出或返回 (None, None)。"""
        self._ensure_not_disposed()
        if len(self._rays) >= self.max_segments:
            return (None, None)
        sp = tuple(start_pos)
        ep = tuple(end_pos)
        self._validate_point_in_sphere(sp)
        self._validate_point_in_sphere(ep)

        # 保证 start 比 end 高
        if sp[1] < ep[1]:
            sp, ep = ep, sp

        direction, distance = self._dir_and_dist(sp, ep)
        if distance < self.min_len:
            return (None, None)
        ray_id = self._alloc_id()
        self._rays[ray_id] = {'start': sp, 'end': ep, 'dir': direction, 'dist': distance}
        return (ray_id, self._line_to_payload(ray_id, self._rays[ray_id]))

    def remove_ray(self, ray_id):
        """删除一条，返回 True/False。"""
        self._ensure_not_disposed()
        return bool(self._rays.pop(ray_id, None))

    def replace_ray(self, ray_id):
        """
        删除并补一条随机新线；返回 (removed_ids, added_lines_payload_list)。
        若删除失败或补充失败，尽量部分返回。
        """
        self._ensure_not_disposed()
        removed, added = [], []
        old = self._rays.pop(ray_id, None)
        if old:
            removed.append(ray_id)

        rid, payload = self.add_random_ray()
        if rid is not None and payload is not None:
            added.append(payload)
        else:
            # 回滚：保持数量不变
            if old:
                self._rays[ray_id] = old
                removed = []  # 实际未移除
        return (removed, added)

    def random_refresh_rays(self, max_replace_count):
        """
        随机挑选若干条射线，调用 replace_ray 做一次“随机流动”。
        设计目的：
          - 提供一个纯“视觉用”的缓慢随机移动效果；
          - 不依赖任何射线命中事件，在没有怪物时也能让领域看起来是活的。
        :param max_replace_count: 本次最多替换多少条射线
        :return: (removed_ids, added_lines_payload_list)
        """
        self._ensure_not_disposed()
        if max_replace_count <= 0 or not self._rays:
            return ([], [])

        ray_ids = list(self._rays.keys())
        if not ray_ids:
            return ([], [])

        replace_count = min(max_replace_count, len(ray_ids))
        # 使用 random.sample，避免总是只动前几个 id
        chosen_ids = random.sample(ray_ids, replace_count)

        removed_all = []
        added_all = []
        for rid in chosen_ids:
            removed_ids, added_lines = self.replace_ray(rid)
            if removed_ids:
                removed_all.extend(removed_ids)
            if added_lines:
                added_all.extend(added_lines)
        return (removed_all, added_all)

    def clear(self):
        """立即清空全部射线，返回被移除的 ray_id 列表（用于构造 update/clear payload）。"""
        self._ensure_not_disposed()
        removed = self._rays.keys()
        self._rays.clear()
        return list(removed)

    def end(self):
        """结束领域：标记 disposed，并返回 clear 类型的 payload（用于广播给客户端移除可视化）。"""
        if self._disposed:
            # 幂等
            return {'field_id': self.field_id, 'action': 'clear'}
        self._disposed = True
        self._rays.clear()
        return {'field_id': self.field_id, 'action': 'clear'}

    def raycast_and_get_hits(self, serverApi, isThrough=False, filterType=None, max_rays_per_tick=None):
        """
        由调用方每秒/每 tick 调用。返回“命中了生物/实体”的 ray_id 列表。

        性能设计：
        - 旧版行为：每次都对所有射线调用一次 getEntitiesOrBlockFromRay，
          当领域段数很多时，这里是非常大的热点。
        - 新增参数 max_rays_per_tick：
            * None：保持旧行为，全部检测（兼容旧调用点）；
            * 正数 N：本次最多只检测 N 条射线，采用“轮询下标”的方式保证
              多帧下来所有射线都能被检测到，不会永远只检测前几个。
        命中标准：serverApi.getEntitiesOrBlockFromRay(...) 返回的列表里存在 type == "Entity"。
        """
        self._ensure_not_disposed()

        rays_count = len(self._rays)
        if rays_count <= 0:
            return []

        # 无节流需求：保留老逻辑，全部遍历，兼容旧代码
        if max_rays_per_tick is None or max_rays_per_tick <= 0 or max_rays_per_tick >= rays_count:
            iterable_items = list(self._rays.items())
        else:
            # 做一次快照，避免遍历过程中结构变化
            items = list(self._rays.items())
            total = len(items)
            if total == 0:
                return []

            # 轮询起始下标：保证“平均分摊”到多帧里
            if not hasattr(self, "_raycast_cursor"):
                self._raycast_cursor = 0
            start_idx = self._raycast_cursor % total
            count = min(max_rays_per_tick, total)

            indices = [(start_idx + i) % total for i in range(count)]
            self._raycast_cursor = (start_idx + count) % total

            iterable_items = [items[i] for i in indices]

        hits = []
        for ray_id, line in iterable_items:
            res = serverApi.getEntitiesOrBlockFromRay(
                self.dimension_id,
                line['start'],
                line['dir'],
                int(max(1, int(round(line['dist'])))),  # 距离传 int，至少 1
                bool(isThrough),
                filterType
            )
            if not res:
                continue

            # 只要有实体即算命中（“生物”）
            for it in res:
                if it.get('type') == 'Entity':
                    hits.append(ray_id)
                    break
        return hits

    # ---------- 向客户端广播所需的 payload 构造 ----------

    def build_init_payload(self, include_meta=True):
        """
        初始化绘制：默认只包含线。若 include_meta=True，则通过 extras 下发领域元数据（center/radius）。
        """
        payload = {
            'field_id': self.field_id,
            'action': 'init',
            'lines': [self._line_to_payload(rid, line) for rid, line in self._rays.items()]
        }
        if include_meta:
            payload['extras'] = [{
                'kind': 'meta',
                'center': self.center,
                'radius': self.radius
            }]
        return payload
    def build_update_payload(self, added_lines_payload_list, removed_id_list):
        """增删差量 只下发发生变化的射线。"""
        return {
            'field_id': self.field_id,
            'action': 'update',
            'added': list(added_lines_payload_list or []),
            'removed': list(removed_id_list or [])
        }

    # ---------- 内部工具 ----------

    def _ensure_not_disposed(self):
        if self._disposed:
            raise RuntimeError("RayFieldManager already ended/disposed.")

    def _alloc_id(self):
        rid = self._next_ray_id
        self._next_ray_id += 1
        return rid

    def _line_to_payload(self, ray_id, line):
        return {
            'ray_id': int(ray_id),
            'start': line['start'],
            'end': line['end'],
            'color': self.line_color
        }

    def _validate_point_in_sphere(self, p):
        if self._squared_distance(p, self.center) > self.radius * self.radius + 1e-6:
            raise ValueError("Point {} not in sphere(center={}, r={})".format(p, self.center, self.radius))

    def _add_random_ray_internal(self, max_trials=64):
        """在球内随机采样两点，形成合格线段。"""
        trials = 0
        while trials < max_trials:
            trials += 1
            sp = self._random_point_in_ball()
            ep = self._random_point_in_ball()

            # 保证 start 比 end 高
            if sp[1] < ep[1]:
                sp, ep = ep, sp

            direction, distance = self._dir_and_dist(sp, ep)
            if distance >= self.min_len:
                rid = self._alloc_id()
                self._rays[rid] = {'start': sp, 'end': ep, 'dir': direction, 'dist': distance}
                return (rid, self._rays[rid])
        return (None, None)

    def _random_point_in_ball(self):
        """
        体积均匀采样：r = R * U^(1/3)，方向均匀单位向量。
        """
        # 方向
        while True:
            # 高斯法生成方向更稳定
            x = random.gauss(0.0, 1.0)
            y = random.gauss(0.0, 1.0)
            z = random.gauss(0.0, 1.0)
            n = math.sqrt(x*x + y*y + z*z)
            if n > 1e-12:
                ux, uy, uz = x/n, y/n, z/n
                break
        # 半径
        u = random.random()
        r = self.radius * (u ** (1.0/3.0))
        return (self.center[0] + ux * r,
                self.center[1] + uy * r,
                self.center[2] + uz * r)

    def _dir_and_dist(self, sp, ep):
        dx = ep[0] - sp[0]
        dy = ep[1] - sp[1]
        dz = ep[2] - sp[2]
        d = math.sqrt(dx*dx + dy*dy + dz*dz)
        if d < 1e-12:
            return ((0.0, 0.0, 0.0), 0.0)
        return ((dx/d, dy/d, dz/d), d)

    def _squared_distance(self, a, b):
        dx = a[0] - b[0]
        dy = a[1] - b[1]
        dz = a[2] - b[2]
        return dx*dx + dy*dy + dz*dz
