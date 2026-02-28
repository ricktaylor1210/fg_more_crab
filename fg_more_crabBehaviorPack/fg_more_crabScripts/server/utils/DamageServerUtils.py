# -*- coding: utf-8 -*-
from ..ServerBaseUtils import *


def calc_real_damage_value(entity_id, origin_damage):
    """
    计算并返回造成真实伤害的伤害数值
    :param entity_id: entity_id
    :type entity_id: str
    :param origin_damage: origin_damage
    :type origin_damage: int | float
    :return: real_damage_value
    :rtype: int | float
    """
    armor = CompFactory.CreateAttr(entity_id).GetAttrValue(MinecraftEnum.AttrType.ARMOR)
    return origin_damage + armor


def set_cause_hurt_cd(cause, cd_value):
    """

    :param cause: cause
    :type cause: str
    :param cd_value: cd_value
    :type cd_value: int | float
    """
    hurt_cd_map = GetCompExtraDataLevel().GetExtraData("FGHurtCD") or {}
    hurt_cd_map[cause] = cd_value
    GetCompExtraDataLevel().SetExtraData("FGHurtCD", hurt_cd_map, True)


@singleton
class IntervalManager(object):
    """
    用于管理生物受击时间间隔的管理器

    管理逻辑：
      1. 根据 victim_id 和 src_id
         若其中只有一个存在则使用存在的，若均不存在则记录为 "default"）以及 cause 记录生物最后受击时间。
      2. 提供获取生物最后受击时间的方法。
      3. 从世界数据中获取两次伤害间的最小间隔：
         通过 CompFactory.CreateExtraData(level_id) 获取数据，使用键 "FGHurtCD" 返回间隔秒数。
      4. 检查生物两次受击是否满足伤害间隔要求：
         同一 source（由 src_id 确定）和 cause 视为一次记录，不同的 source 或 cause 分开记录，
         内部记录字典格式为 {victim_id: {"cause_1": {"default": last_time, "entity_1": last_time}}}。
    """

    def __init__(self):
        """
        初始化 HurtTimeManager 对象，创建受击时间记录字典
        """
        self._lock = threading.RLock()
        self._hurt_records = {}

    def set_last_hit_time(self, victim_id, src_id=None, cause=None, timestamp=None):
        """

        记录生物最后受击时间
        根据 victim_id 和 src_id
        若其中只有一个存在则使用存在的，若均不存在则记录为 "default"）以及 cause 记录受击时间

        :param victim_id: 被击中的生物ID
        :param src_id: 攻击者的ID
        :param cause: 伤害原因
        :param timestamp: 受击时间，若为 None 则使用当前时间
        """
        timestamp = timestamp or time.time()

        key = src_id or "default"
        with self._lock:
            self._hurt_records.setdefault(victim_id, {}).setdefault(cause, {})[key] = timestamp
            SetDevelopmentMessage(logging.INFO, "Set last hit time for victim_id=%s, cause=%s, key=%s, time=%s",
                                  victim_id, cause, key, timestamp)

    def get_last_hit_time(self, victim_id, src_id=None, cause=None):
        """
        获取生物最后受击时间
        根据 victim_id 和 src_id （同 set_last_hit_time 的逻辑）以及 cause 获取记录的受击时间

        :param victim_id: 被击中的生物ID
        :param src_id: 攻击者的ID
        :param cause: 伤害原因
        :return: 记录的受击时间，若无记录则返回 None
        """
        key = src_id or "default"

        with self._lock:
            if victim_id in self._hurt_records and cause in self._hurt_records[victim_id]:
                return self._hurt_records[victim_id][cause].get(key)
            return None

    def get_hurt_interval_map(self):
        """
        获取世界数据中两次伤害的间隔时间
        根据 level_id，通过 CompFactory.CreateExtraData 获取数据，使用键 "FGHurtCD" 返回间隔秒数

        :return: 两次伤害间的时间间隔（秒）
        """
        hurt_cd_map = GetCompExtraDataLevel().GetExtraData("FGHurtCD") or {"global": 0.3}
        if "global" not in hurt_cd_map:
            hurt_cd_map["global"] = 0.3
        return hurt_cd_map

    def check_hurt_interval(self, victim_id, cause, src_id=None, current_time=None):
        """
        检查生物两次受击是否符合伤害间隔
        根据 victim_id 和 src_id 以及 cause，
        若不存在记录则视为第一次受击；若存在，则判断当前受击时间与上次记录时间之差是否大于等于伤害间隔。
        如果符合间隔，则更新记录并返回 True，否则返回 False。

        :param victim_id: 被击中的生物ID
        :param cause: 伤害原因
        :param src_id: 攻击者的ID
        :param current_time: 当前受击时间，若为 None 则使用当前时间
        :return: 布尔值，True 表示符合伤害间隔，可以记录此次伤害；False 表示未达到间隔要求
        """
        current_time = current_time or time.time()
        interval_map = self.get_hurt_interval_map()

        interval = None

        # 1. 直接匹配完整 cause
        if cause in interval_map:
            interval = interval_map[cause]
        else:
            # 2. 拆分层级 cause
            parts = cause.split("::")
            candidates = []

            for i in range(1, len(parts) + 1):
                sub_cause = "::".join(parts[:i])
                if sub_cause in interval_map:
                    candidates.append(interval_map[sub_cause])

            if candidates:
                interval = min(candidates)
        # 3. 如果还没找到，取 global（默认 0.3）
        if interval is None:
            interval = interval_map.get("global", 0.3)

        # 获取上次受击时间
        last_time = self.get_last_hit_time(victim_id, src_id, cause)
        # 没有受击记录 -> 第一次受击
        if last_time is None:
            return True

        # 判断时间差
        return current_time - last_time >= interval


class DamageBaseDataManager(object):
    # 所有子类共享的作用域
    VALID_SCOPES = ("all", "entity", "cause")

    def __init__(self, data_key):
        self.data_key = data_key
        self._lock = threading.RLock()
        self._initialized = True

    def _load_data(self, entity_id):
        with self._lock:
            comp = CompFactory.CreateExtraData(entity_id)
            # 如果返回值为 None，则初始化默认数据
            stored_data = comp.GetExtraData(self.data_key)
            if stored_data is None:
                stored_data = self._default_data()
                comp.SetExtraData(self.data_key, stored_data, autoSave=True)
            else:
                stored_data = self._validate_data_structure(stored_data)
            return stored_data

    def _save_data(self, entity_id, data):
        with self._lock:
            comp = CompFactory.CreateExtraData(entity_id)
            comp.SetExtraData(self.data_key, data, autoSave=True)

    def auto_check_expiration(self, entity_id, save_after=True):
        with self._lock:
            data = self._load_data(entity_id)
            now = time.time()  # 保存当前时间，减少重复调用
            # 清理 "all" 范围下的数据
            for sub in self.VALID_SUBTYPES:
                data["all"][sub] = [item for item in data["all"].get(sub, [])
                                    if item.get("end_time") is None or item.get("end_time") > now]
            # 清理 "entity" 与 "cause" 范围下的数据
            for scope in ("entity", "cause"):
                for key in list(data[scope].keys()):
                    sub_dict = data[scope][key]
                    self._clean_sub_dict(sub_dict, now)
                    if all(len(sub_dict.get(sub, [])) == 0 for sub in self.VALID_SUBTYPES):
                        del data[scope][key]
            if save_after:
                self._save_data(entity_id, data)
            return data

    def extend_all_durations(self, entity_id, additional_seconds):
        """
        为所有存在有效期的数据记录延长持续时间（永久记录除外）

        :param entity_id: 实体ID
        :type entity_id: int | str
        :param additional_seconds: 需要延长的秒数
        :type additional_seconds: int | float
        """
        if additional_seconds <= 0:
            raise ValueError("additional_seconds must be greater than 0")
        now = time.time()
        with self._lock:
            data = self._load_data(entity_id)
            for scope in self.VALID_SCOPES:
                if scope == "all":
                    scope_data = data[scope]
                    for subtype in self.VALID_SUBTYPES:
                        for item in scope_data.get(subtype, []):
                            if item["end_time"] is not None and item["end_time"] > now:
                                item["end_time"] += additional_seconds
                                item["duration"] += additional_seconds
                else:
                    for target_id, sub_dict in data[scope].iteritems():
                        for subtype in self.VALID_SUBTYPES:
                            for item in sub_dict.get(subtype, []):
                                if item["end_time"] is not None and item["end_time"] > now:
                                    item["end_time"] += additional_seconds
                                    item["duration"] += additional_seconds
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO,
                                  "Extended all durations by %s seconds for entity_id=%s", additional_seconds,
                                  entity_id)

    def _clean_sub_dict(self, sub_dict, now):
        for sub in self.VALID_SUBTYPES:
            if sub in sub_dict and isinstance(sub_dict[sub], list):
                sub_dict[sub] = [item for item in sub_dict[sub]
                                 if item.get("end_time") is None or item.get("end_time") > now]
        return sub_dict

    def _smooth_combine(self, values, decay=0.95):
        """
        将一组数值按绝对值降序排列后，使用权重递减平滑叠加。
        """
        if not values:
            return 0.0
        # 按绝对值降序排列
        values_sorted = sorted(values, key=lambda x: abs(x), reverse=True)
        combined = 0.0
        weight = 1.0
        for v in values_sorted:
            combined += v * weight
            weight *= decay
        return combined

    def _aggregate_percentage(self, items, now):
        """
        辅助函数：将多个百分比数值按照公式合并
        :param items: 记录列表
        :type items: list
        :param now: 当前时间戳
        :type now: float
        """
        combined = 0.0
        for item in items:
            if item.get("end_time") is None or item.get("end_time") > now:
                value = max(-100.0, min(300.0, item.get("value", 0)))  # 限制范围 [-100, 300]
                combined += value
        return round(combined, 5)

    def _aggregate_items(self, items, subtype, now):
        valid_items = [item for item in items if item.get("end_time") is None or item.get("end_time") > now]
        if subtype == self.SUBTYPE_FULL:
            return any(item.get("value") is True for item in valid_items)
        elif subtype == self.SUBTYPE_NUMERIC:
            return sum(item.get("value", 0) for item in valid_items)
        elif subtype == self.SUBTYPE_MULTIPLE:
            # 将 multiple 值平滑叠加，单位仍为数值（在最终计算时将除以 100）
            values = [item.get("value", 0) for item in valid_items]
            combined = self._smooth_combine(values)
            return round(combined, 5)
        elif subtype == self.SUBTYPE_PARTIAL:
            # 每条百分比记录先限制在 [-100,300] 内，再平滑叠加
            values = [max(-100.0, min(300.0, item.get("value", 0))) for item in valid_items]
            combined = self._smooth_combine(values)
            # 最终结果也限制在 [-100,300] 范围内
            combined = max(-100.0, min(300.0, combined))
            return round(combined, 5)

    # 子类必须实现 _default_data 和 _validate_data_structure
    def _default_data(self):
        raise NotImplementedError

    def _validate_data_structure(self, data):
        raise NotImplementedError


@singleton
class DamageModifierManager(DamageBaseDataManager):
    """
    用于管理伤害修正数据的API
    """

    # 定义常量
    SCOPE_ALL = "all"
    SCOPE_ENTITY = "entity"
    SCOPE_CAUSE = "cause"
    VALID_SCOPES = (SCOPE_ALL, SCOPE_ENTITY, SCOPE_CAUSE)

    SUBTYPE_FULL = "full"
    SUBTYPE_NUMERIC = "numeric"
    SUBTYPE_PARTIAL = "partial"
    SUBTYPE_MULTIPLE = "multiple"
    VALID_SUBTYPES = (SUBTYPE_FULL, SUBTYPE_NUMERIC, SUBTYPE_PARTIAL, SUBTYPE_MULTIPLE)

    OP_TYPE_ADD = "add"
    OP_TYPE_MUL = "mul"
    OP_TYPE_MAX = "max"
    VALID_OP_TYPES = (OP_TYPE_ADD, OP_TYPE_MUL, OP_TYPE_MAX)

    def __init__(self, data_key="damage_modifier_data"):
        """
        初始化 DamageModifierManager 对象

        :param data_key: 存储伤害修正数据的键名，可自定义
        :type data_key: str
        """
        super(DamageModifierManager, self).__init__(data_key)

    @staticmethod
    def build_condition_by_tag(tag):
        """
        构建一个按 tag 精确匹配的 condition 函数：
        item["tag"] == tag 时返回 True
        """
        def _condition(item):
            return item.get("tag") == tag
        return _condition

    @staticmethod
    def build_condition_by_fields(**fields):
        """
        通用版构造器：按多个字段完全匹配来删除
        例如：build_condition_by_fields(tag="skill:fire", value=-50)
        """
        def _condition(item):
            # 注意：这里使用 get，兼容旧数据缺字段的情况
            for key, expected in fields.iteritems():   # 若是 py3 环境改成 items()
                if item.get(key) != expected:
                    return False
            return True
        return _condition

    def _default_data(self):
        """
        返回默认的伤害修正数据结构

        :return: 默认伤害修正数据结构，包含 "all"、"entity"、"cause" 三部分
        :rtype: dict
        """
        return {
            "all": {
                self.SUBTYPE_FULL: [],
                self.SUBTYPE_NUMERIC: [],
                self.SUBTYPE_PARTIAL: [],
                self.SUBTYPE_MULTIPLE: []
            },
            "entity": {},
            "cause": {}
        }

    def _validate_data_structure(self, data):
        """
        验证并补全数据结构中必须存在的字段

        :param data: 输入数据结构
        :type data: dict
        :return: 补全后的数据结构
        :rtype: dict
        """
        if not isinstance(data, dict):
            return self._default_data()
        if "all" not in data or not isinstance(data["all"], dict):
            data["all"] = {}
        for key in self.VALID_SUBTYPES:
            if key not in data["all"] or not isinstance(data["all"][key], list):
                data["all"][key] = []
        if "entity" not in data or not isinstance(data["entity"], dict):
            data["entity"] = {}
        if "cause" not in data or not isinstance(data["cause"], dict):
            data["cause"] = {}
        return data

    def _validate_scope_and_subtype(self, scope, sub_type, target_required=False, target_id=None):
        """
        校验 scope 与 sub_type 的合法性，并判断是否需要 target_id

        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "numeric", "partial", "multiple")
        :type sub_type: str
        :param target_required: 当 scope 不为 "all" 时是否必须提供 target_id
        :type target_required: bool
        :param target_id: 目标ID
        :type target_id: int, str | None
        """
        if scope not in self.VALID_SCOPES:
            raise ValueError("Invalid scope: {}".format(scope))
        if sub_type not in self.VALID_SUBTYPES:
            raise ValueError("Invalid sub_type: {}. Must be one of {}".format(sub_type, self.VALID_SUBTYPES))
        if scope in (self.SCOPE_ENTITY, self.SCOPE_CAUSE) and target_required and target_id is None:
            raise AttributeError("For scope {} target_id must be provided.".format(scope))

    def _init_target_data(self, data, scope, target_id):
        """
        为 entity 或 cause 类型初始化数据结构

        :param data: 伤害修正数据结构
        :type data: dict
        :param scope: 数据作用域 ("entity", "cause")
        :type scope: str
        :param target_id: 目标ID
        :type target_id: int | str
        """
        if scope not in (self.SCOPE_ENTITY, self.SCOPE_CAUSE):
            return
        if target_id not in data[scope]:
            data[scope][target_id] = {
                self.SUBTYPE_FULL: [],
                self.SUBTYPE_NUMERIC: [],
                self.SUBTYPE_PARTIAL: [],
                self.SUBTYPE_MULTIPLE: []
            }


    def set(self, entity_id, scope, sub_type, value, duration, target_id=None, tag=None):
        """
        添加一条伤害修正数据记录

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "numeric", "partial", "multiple")
        :type sub_type: str
        :param value: 伤害修正数据值（对于 full 类型为 bool，其它类型为数值）
        :param duration: 记录的有效时长（秒），如果为 None 则表示永久状态
        :type duration: int, float | None
        :param target_id: 当 scope 不为 "all" 时必须提供，表示目标实体或原因ID
        :type target_id: int, str | None
        :param tag: 用于标记这条修正记录来源的标记（技能名、buff id 等），便于后续按条件删除
        :type tag: str | int | dict | None
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        if duration is not None and duration <= 0:
            raise ValueError("duration must be greater than 0 if provided")
        with self._lock:
            data = self._load_data(entity_id)
            now = time.time()
            if duration is None:
                end_time = None
            else:
                end_time = now + duration

            # 这里多存一个 tag 字段
            new_item = {
                "value": value,
                "duration": duration,
                "end_time": end_time,
                "tag": tag
            }

            if scope == self.SCOPE_ALL:
                data["all"][sub_type].append(new_item)
            else:
                self._init_target_data(data, scope, target_id)
                data[scope][target_id][sub_type].append(new_item)
            self._save_data(entity_id, data)
            SetDevelopmentMessage(
                logging.INFO,
                "Set new damage_modifier record: entity_id=%s, scope=%s, sub_type=%s, target_id=%s, tag=%s",
                entity_id, scope, sub_type, target_id, tag
            )

    def get(self, entity_id, scope, sub_type, target_id=None):
        """
        获取指定 scope 与 sub_type 对应的伤害修正数据列表

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "numeric", "partial", "multiple")
        :type sub_type: str
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int, str | None
        :return: 满足条件的伤害修正数据记录列表
        :rtype: list
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        self.auto_check_expiration(entity_id, save_after=True)
        data = self._load_data(entity_id)
        if scope == self.SCOPE_ALL:
            return data["all"].get(sub_type, [])
        else:
            return data[scope].get(target_id, {}).get(sub_type, [])

    def get_all(self, entity_id):
        """
        获取当前存储的所有伤害修正数据（包含 "all"、"entity"、"cause"）

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :return: 全部伤害修正数据结构
        :rtype: dict
        """
        self.auto_check_expiration(entity_id, save_after=True)
        return self._load_data(entity_id)

    def pop(self, entity_id, scope, sub_type, index=-1, target_id=None):
        """
        从指定 scope 与 sub_type 的数据列表中移除并返回一条记录

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "numeric", "partial", "multiple")
        :type sub_type: str
        :param index: 要移除记录在列表中的索引，默认为 -1（最后一条记录）
        :type index: int
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int, str | None
        :return: 移除的记录，如果没有则返回 None
        :rtype: dict | None
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        self.auto_check_expiration(entity_id, save_after=False)
        with self._lock:
            data = self._load_data(entity_id)
            if scope == self.SCOPE_ALL:
                target_list = data["all"][sub_type]
            else:
                target_list = data[scope].get(target_id, {}).get(sub_type, [])
            if not target_list or not (-len(target_list) <= index < len(target_list)):
                return None
            popped_item = target_list.pop(index)
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO,
                                  "Popped damage_modifier record: entity_id=%s, scope=%s, sub_type=%s, target_id=%s, index=%s",
                                  entity_id, scope, sub_type, target_id, index)
            return popped_item

    def remove_by_condition(self, entity_id, scope, sub_type, target_id=None, condition=None, count=1):
        """
        从指定 scope 与 sub_type 的数据列表中，按自定义条件移除若干条记录

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "numeric", "partial", "multiple")
        :type sub_type: str
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int, str | None
        :param condition: 用于判断记录是否满足移除条件的函数 类似 lambda x:x["value"]==-50
        :type condition: function | None
        :param count: 最大移除记录数，默认为 1
        :type count: int
        :return: 移除的记录列表
        :rtype: list
        """
        if condition is None or count <= 0:
            return []
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        self.auto_check_expiration(entity_id, save_after=False)
        removed_items = []
        with self._lock:
            data = self._load_data(entity_id)
            if scope == self.SCOPE_ALL:
                target_list = data["all"].get(sub_type, [])
            else:
                target_list = data[scope].get(target_id, {}).get(sub_type, [])
            for i in reversed(range(len(target_list))):
                item = target_list[i]
                if condition(item):
                    removed_items.append(target_list.pop(i))
                    if len(removed_items) >= count:
                        break
            self._save_data(entity_id, data)
        removed_items.reverse()
        SetDevelopmentMessage(logging.INFO,
                              "Removed %d records by condition: entity_id=%s, scope=%s, sub_type=%s, target_id=%s",
                              len(removed_items), entity_id, scope, sub_type, target_id)
        return removed_items
    def remove_all_by_tag(self, entity_id, tag, max_per_list=999999999):
        """
        删除当前 entity_id 下所有 tag == 指定值 的伤害修正记录
        （包含 all / entity / cause 三个 scope 的所有子类型）。

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param tag: 要匹配的 tag 值
        :type tag: any
        :param max_per_list: 对每个列表最多尝试删除多少条，默认一个很大的数，相当于“删光”
        :type max_per_list: int
        :return: 被删除的所有记录列表
        :rtype: list
        """
        # 如果你已经实现了 build_condition_by_tag，就用它
        try:
            condition = self.build_condition_by_tag(tag)
        except AttributeError:
            # 兼容你没加 build_condition_by_tag 的情况
            def condition(item):
                return item.get("tag") == tag

        removed = []

        # 先拿一份 snapshot，避免遍历过程中结构变化导致 key 迭代出问题
        all_data = self.get_all(entity_id)

        # 1. all scope
        for sub_type in self.VALID_SUBTYPES:
            removed.extend(
                self.remove_by_condition(
                    entity_id=entity_id,
                    scope=self.SCOPE_ALL,
                    sub_type=sub_type,
                    condition=condition,
                    count=max_per_list
                )
            )

        # 2. entity scope
        for target_id in list(all_data["entity"].keys()):
            for sub_type in self.VALID_SUBTYPES:
                removed.extend(
                    self.remove_by_condition(
                        entity_id=entity_id,
                        scope=self.SCOPE_ENTITY,
                        sub_type=sub_type,
                        target_id=target_id,
                        condition=condition,
                        count=max_per_list
                    )
                )

        # 3. cause scope
        for cause_id in list(all_data["cause"].keys()):
            for sub_type in self.VALID_SUBTYPES:
                removed.extend(
                    self.remove_by_condition(
                        entity_id=entity_id,
                        scope=self.SCOPE_CAUSE,
                        sub_type=sub_type,
                        target_id=cause_id,
                        condition=condition,
                        count=max_per_list
                    )
                )

        return removed
    def clear(self, entity_id, scope, sub_type, target_id=None):
        """
        清空指定 scope 与 sub_type 下的伤害修正数据（全部清空，无论是否过期）

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "numeric", "partial", "multiple")
        :type sub_type: str
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int, str | None
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        with self._lock:
            data = self._load_data(entity_id)
            if scope == self.SCOPE_ALL:
                data["all"][sub_type] = []
            else:
                if target_id in data[scope]:
                    data[scope][target_id][sub_type] = []
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO, "Cleared records: entity_id=%s, scope=%s, sub_type=%s, target_id=%s",
                                  entity_id, scope, sub_type, target_id)

    def clear_all(self, entity_id):
        """
        彻底清空整个伤害修正数据结构

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        """
        with self._lock:
            data = self._default_data()
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO, "Cleared all records for entity_id=%s", entity_id)

    def compute(self, entity_id):
        """
        按需求对现有伤害修正数据进行综合计算：
          - full: 若存在任一未过期且值为 True 的记录，则结果为 True；否则 False
          - numeric: 累加所有未过期的 numeric 值
          - partial: 按百分比叠加公式聚合所有未过期的 partial 值
          - multiple: 累加所有未过期的 multiple 值

            {
                "all": {
                    "full": True,
                    "numeric": 50.0,
                    "partial": 34.56,
                    "multiple": 5.0
                },
                "entity": {
                    "entity_2002": {
                        "full": False,
                        "numeric": 10.0,
                        "partial": 12.5,
                        "multiple": 3.0
                    }
                },
                "cause": {
                    "fire_damage": {
                        "full": False,
                        "numeric": 5.0,
                        "partial": 20.0,
                        "multiple": 2.0
                    }
                }
            }

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :return: 综合计算后的结果结构
        :rtype: dict
        """

        self.auto_check_expiration(entity_id, save_after=False)
        data = self._load_data(entity_id)
        now = time.time()
        result = {"all": {}, "entity": {}, "cause": {}}
        for subtype in self.VALID_SUBTYPES:
            result["all"][subtype] = self._aggregate_items(data["all"].get(subtype, []), subtype, now)
        for ent_id, sub_dict in data["entity"].iteritems():
            tmp = {}
            for subtype in self.VALID_SUBTYPES:
                tmp[subtype] = self._aggregate_items(sub_dict.get(subtype, []), subtype, now)
            result["entity"][ent_id] = tmp
        for cause_id, sub_dict in data["cause"].iteritems():
            tmp = {}
            for subtype in self.VALID_SUBTYPES:
                tmp[subtype] = self._aggregate_items(sub_dict.get(subtype, []), subtype, now)
            result["cause"][cause_id] = tmp
        return result


@singleton
class ReflectionDamageManager(DamageBaseDataManager):
    """
    用于管理反弹伤害数据的API
    """

    SCOPE_ALL = "all"
    SCOPE_ENTITY = "entity"
    SCOPE_CAUSE = "cause"
    VALID_SCOPES = (SCOPE_ALL, SCOPE_ENTITY, SCOPE_CAUSE)

    # 定义反弹伤害的子类型：
    # full         - 完全反弹（布尔类型，若存在任一 True，则触发全反弹）
    # flat         - 固定值反弹（直接加算固定伤害）
    # percentage   - 百分比反弹（按百分比计算反弹伤害）
    # multiple     - 反弹倍率（多个倍率叠乘）
    VALID_FULL = "full"
    VALID_FLAT = "flat"
    VALID_PERCENTAGE = "percentage"
    VALID_MULTIPLE = "multiple"
    VALID_SUBTYPES = (VALID_FULL, VALID_FLAT, VALID_PERCENTAGE, VALID_MULTIPLE)

    # 定义操作类型，用于批量叠加未过期的数值数据
    OP_TYPE_ADD = "add"  # 累加
    OP_TYPE_MUL = "mul"  # 百分比叠加：采用类似公式
    OP_TYPE_MAX = "max"  # 取最大值
    VALID_OP_TYPES = (OP_TYPE_ADD, OP_TYPE_MUL, OP_TYPE_MAX)

    def __init__(self, data_key="reflection_damage_data"):
        """
        初始化 ReflectionDamageManager 对象

        :param data_key: 存储反弹伤害数据的键名，可自定义
        :type data_key: str
        """
        super(ReflectionDamageManager, self).__init__(data_key)

    def _default_data(self):
        """
        返回默认的反弹伤害数据结构

        :return: 默认反弹伤害数据结构，包含 "all"、"entity"、"cause" 三部分
        :rtype: dict
        """
        return {
            "all": {
                self.VALID_FULL: [],
                self.VALID_FLAT: [],
                self.VALID_PERCENTAGE: [],
                self.VALID_MULTIPLE: []
            },
            "entity": {},
            "cause": {}
        }

    def _validate_data_structure(self, data):
        """
        验证并补全数据结构中必须存在的字段

        :param data: 输入数据结构
        :type data: dict
        :return: 补全后的数据结构
        :rtype: dict
        """
        if not isinstance(data, dict):
            return self._default_data()
        if "all" not in data or not isinstance(data["all"], dict):
            data["all"] = {}
        for key in self.VALID_SUBTYPES:
            if key not in data["all"] or not isinstance(data["all"][key], list):
                data["all"][key] = []
        if "entity" not in data or not isinstance(data["entity"], dict):
            data["entity"] = {}
        if "cause" not in data or not isinstance(data["cause"], dict):
            data["cause"] = {}
        return data

    def _validate_scope_and_subtype(self, scope, sub_type, target_required=False, target_id=None):
        """
        校验 scope 与 sub_type 的合法性，并判断是否需要 target_id

        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "flat", "percentage", "multiple")
        :type sub_type: str
        :param target_required: 当 scope 不为 "all" 时是否必须提供 target_id
        :type target_required: bool
        :param target_id: 目标ID
        :type target_id: int, str | None
        """
        if scope not in self.VALID_SCOPES:
            raise ValueError("Invalid scope: {}".format(scope))
        if sub_type not in self.VALID_SUBTYPES:
            raise ValueError("Invalid sub_type: {}. Must be one of {}".format(sub_type, self.VALID_SUBTYPES))
        if scope in (self.SCOPE_ENTITY, self.SCOPE_CAUSE) and target_required and target_id is None:
            raise AttributeError("For scope {} target_id must be provided.".format(scope))

    def _init_target_data(self, data, scope, target_id):
        """
        为 entity 或 cause 类型初始化数据结构

        :param data: 反弹伤害数据结构
        :type data: dict
        :param scope: 数据作用域 ("entity", "cause")
        :type scope: str
        :param target_id: 目标ID
        :type target_id: int | str
        """
        if scope not in (self.SCOPE_ENTITY, self.SCOPE_CAUSE):
            return
        if target_id not in data[scope]:
            data[scope][target_id] = {
                self.VALID_FULL: [],
                self.VALID_FLAT: [],
                self.VALID_PERCENTAGE: [],
                self.VALID_MULTIPLE: []
            }

    def set(self, entity_id, scope, sub_type, value, duration, target_id=None):
        """
        添加一条反弹伤害数据记录

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "flat", "percentage", "multiple")
        :type sub_type: str
        :param value: 反弹伤害数据值（对于 full 类型为 bool，其它类型为数值）
        :param duration: 记录的有效时长（秒），如果为 None 则表示永久状态
        :type duration: int, float | None
        :param target_id: 当 scope 不为 "all" 时必须提供，表示目标实体或原因ID
        :type target_id: int, str | None
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        if duration is not None and duration <= 0:
            raise ValueError("duration must be greater than 0 if provided")
        with self._lock:
            data = self._load_data(entity_id)
            now = time.time()
            if duration is None:
                end_time = None
            else:
                end_time = now + duration
            new_item = {"value": value, "duration": duration, "end_time": end_time}
            if scope == self.SCOPE_ALL:
                data["all"][sub_type].append(new_item)
            else:
                self._init_target_data(data, scope, target_id)
                data[scope][target_id][sub_type].append(new_item)
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO,
                                  "Set new reflection record: entity_id=%s, scope=%s, sub_type=%s, target_id=%s",
                                  entity_id, scope, sub_type, target_id)

    def get(self, entity_id, scope, sub_type, target_id=None):
        """
        获取指定 scope 与 sub_type 对应的反弹伤害数据列表

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "flat", "percentage", "multiple")
        :type sub_type: str
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int, str | None
        :return: 满足条件的反弹伤害数据记录列表
        :rtype: list
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        self.auto_check_expiration(entity_id, save_after=True)
        data = self._load_data(entity_id)
        if scope == self.SCOPE_ALL:
            return data["all"].get(sub_type, [])
        else:
            return data[scope].get(target_id, {}).get(sub_type, [])

    def get_all(self, entity_id):
        """
        获取当前存储的所有反弹伤害数据（包含 "all"、"entity"、"cause"）

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :return: 全部反弹伤害数据结构
        :rtype: dict
        """
        self.auto_check_expiration(entity_id, save_after=True)
        return self._load_data(entity_id)

    def pop(self, entity_id, scope, sub_type, index=-1, target_id=None):
        """
        从指定 scope 与 sub_type 的数据列表中移除并返回一条记录

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "flat", "percentage", "multiple")
        :type sub_type: str
        :param index: 要移除记录在列表中的索引，默认为 -1（最后一条记录）
        :type index: int
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int, str | None
        :return: 移除的记录，如果没有则返回 None
        :rtype: dict | None
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        self.auto_check_expiration(entity_id, save_after=False)
        with self._lock:
            data = self._load_data(entity_id)
            if scope == self.SCOPE_ALL:
                target_list = data["all"][sub_type]
            else:
                target_list = data[scope].get(target_id, {}).get(sub_type, [])
            if not target_list or not (-len(target_list) <= index < len(target_list)):
                return None
            popped_item = target_list.pop(index)
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO,
                                  "Popped reflection record: entity_id=%s, scope=%s, sub_type=%s, target_id=%s, index=%s",
                                  entity_id, scope, sub_type, target_id, index)
            return popped_item

    def remove_by_condition(self, entity_id, scope, sub_type, target_id=None, condition=None, count=1):
        """
        从指定 scope 与 sub_type 的数据列表中，按自定义条件移除若干条记录

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "flat", "percentage", "multiple")
        :type sub_type: str
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int, str | None
        :param condition: 用于判断记录是否满足移除条件的函数
        :type condition: function | None
        :param count: 最大移除记录数，默认为 1
        :type count: int
        :return: 移除的记录列表
        :rtype: list
        """
        if condition is None or count <= 0:
            return []
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        self.auto_check_expiration(entity_id, save_after=False)
        removed_items = []
        with self._lock:
            data = self._load_data(entity_id)
            if scope == self.SCOPE_ALL:
                target_list = data["all"].get(sub_type, [])
            else:
                target_list = data[scope].get(target_id, {}).get(sub_type, [])
            for i in reversed(range(len(target_list))):
                item = target_list[i]
                if condition(item):
                    removed_items.append(target_list.pop(i))
                    if len(removed_items) >= count:
                        break
            self._save_data(entity_id, data)
        removed_items.reverse()
        SetDevelopmentMessage(logging.INFO,
                              "Removed %d records by condition: entity_id=%s, scope=%s, sub_type=%s, target_id=%s",
                              len(removed_items), entity_id, scope, sub_type, target_id)
        return removed_items

    def clear(self, entity_id, scope, sub_type, target_id=None):
        """
        清空指定 scope 与 sub_type 下的反弹伤害数据（全部清空，无论是否过期）

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :param scope: 数据作用域 ("all", "entity", "cause")
        :type scope: str
        :param sub_type: 数据子类型 ("full", "flat", "percentage", "multiple")
        :type sub_type: str
        :param target_id: 当 scope 不为 "all" 时的目标ID
        :type target_id: int | str | None
        """
        self._validate_scope_and_subtype(scope, sub_type, target_required=(scope != self.SCOPE_ALL),
                                         target_id=target_id)
        with self._lock:
            data = self._load_data(entity_id)
            if scope == self.SCOPE_ALL:
                data["all"][sub_type] = []
            else:
                if target_id in data[scope]:
                    data[scope][target_id][sub_type] = []
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO,
                                  "Cleared reflection records: entity_id=%s, scope=%s, sub_type=%s, target_id=%s",
                                  entity_id, scope, sub_type, target_id)

    def clear_all(self, entity_id):
        """
        彻底清空整个反弹伤害数据结构

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        """
        with self._lock:
            data = self._default_data()
            self._save_data(entity_id, data)
            SetDevelopmentMessage(logging.INFO, "Cleared all reflection records for entity_id=%s", entity_id)

    def _aggregate_percentage(self, items, now):
        """
        辅助函数：将多个百分比数值按照公式合并
        :param items: 记录列表
        :type items: list
        :param now: 当前时间戳
        :type now: float
        """
        # 取出所有未过期记录的数值
        values = [item.get("value", 0) for item in items if item.get("end_time") is None or item.get("end_time") > now]
        # 使用平滑叠加（权重递减）
        combined = self._smooth_combine(values)
        # 最终结果限制最大为 100%
        return min(round(combined, 5), 100.0)

    def _aggregate_items(self, items, subtype, now):
        """
        辅助函数：对单个子类型的记录列表进行聚合计算，统一处理未过期的记录。

        聚合规则说明：
          - full: 若存在任一未过期且值为 True 的记录，则返回 True；否则 False。
          - flat、multiple: 累加所有未过期的数值。
          - percentage: 对所有未过期的数值使用公式进行百分比叠加计算。

        :param items: 记录列表
        :type items: list
        :param subtype: 子类型 (使用常量：VALID_FULL, VALID_FLAT, VALID_PERCENTAGE, VALID_MULTIPLE)
        :type subtype: str
        :param now: 当前时间戳
        :type now: float
        :return: 聚合后的结果
        """
        valid_items = [item for item in items if item.get("end_time") is None or item.get("end_time") > now]
        if subtype == self.VALID_FULL:
            return any(item.get("value") is True for item in valid_items)
        elif subtype == self.VALID_FLAT:
            # flat 类型依然使用简单累加
            return sum(item.get("value", 0) for item in valid_items)
        elif subtype == self.VALID_MULTIPLE:
            # multiple 类型采用平滑叠加
            values = [item.get("value", 0) for item in valid_items]
            combined = self._smooth_combine(values)
            return round(combined, 5)
        elif subtype == self.VALID_PERCENTAGE:
            return self._aggregate_percentage(items, now)

    def compute(self, entity_id):
        """
                对现有反弹伤害数据进行综合计算：
          - full: 若存在任一未过期且值为 True 的记录，则结果为 True；否则 False
          - flat: 累加所有未过期的 flat 值
          - percentage: 对所有未过期的 percentage 值使用百分比叠加公式计算
          - multiple: 累加所有未过期的 multiple 值

            {
                "all": {
                    "full": bool,
                    "flat": float,
                    "percentage": float,  # 按百分比公式聚合后的结果
                    "multiple": float
                },
                "entity": {
                    "entity_id": {
                        "full": bool,
                        "flat": float,
                        "percentage": float,
                        "multiple": float
                    },
                    # 更多实体...
                },
                "cause": {
                    "cause_id": {
                        "full": bool,
                        "flat": float,
                        "percentage": float,
                        "multiple": float
                    },
                    # 更多原因...
                }
            }

        :param entity_id: 当前操作的实体ID
        :type entity_id: int | str
        :return: 综合计算后的结果结构
        :rtype: dict
        """
        self.auto_check_expiration(entity_id, save_after=False)
        data = self._load_data(entity_id)
        now = time.time()
        result = {"all": {}, "entity": {}, "cause": {}}
        for subtype in self.VALID_SUBTYPES:
            result["all"][subtype] = self._aggregate_items(data["all"].get(subtype, []),
                                                           subtype, now)
        for ent_id, sub_dict in data["entity"].iteritems():
            tmp = {}
            for subtype in self.VALID_SUBTYPES:
                tmp[subtype] = self._aggregate_items(sub_dict.get(subtype, []),
                                                     subtype, now)
            result["entity"][ent_id] = tmp
        for cause_id, sub_dict in data["cause"].iteritems():
            tmp = {}
            for subtype in self.VALID_SUBTYPES:
                tmp[subtype] = self._aggregate_items(sub_dict.get(subtype, []),
                                                     subtype, now)
            result["cause"][cause_id] = tmp
        return result

# @singleton
# class LifeSyncManager(object):
#     """
#     用于管理生物间生命值同步状态的管理器
#
#     同步规则：
#       1. 同步生物（syncer）只能同时同步一个目标生物（target）。
#       2. 同步模式支持：
#          - "absolute"：同步生物直接复制目标生物的当前生命值和生命上限。
#          - "percentage"：同步生物保持自身生命上限不变，根据目标的生命比例计算当前生命值。
#       3. 当目标生物生命值发生变化时，更新所有同步该目标的同步生物（支持绝对或百分比方式的增减）。
#       4. 被同步生物可以被多个生物同步；在建立同步状态时，为目标添加同步生物的标记，
#          在取消同步状态时，从目标上移除相应标记。
#       5. 任一生物死亡后，双方的同步状态都应被取消。
#     """
#
#     # 定义同步模式常量
#     MODE_ABSOLUTE = "absolute"
#     MODE_PERCENTAGE = "percentage"
#     VALID_MODES = (MODE_ABSOLUTE, MODE_PERCENTAGE)
#
#     def __init__(self):
#         # 防止重复初始化
#         if hasattr(self, "_initialized") and self._initialized:
#             return
#         # 锁保护同步关系的数据结构
#         self._lock = threading.RLock()
#         # 同步关系字典：key 为同步生物的 syncer_id，
#         # value 为 {"target_id": str, "mode": mode, "original_max_hp": value, "original_hp": value, "duration": value, "end_time": value}
#         self._sync_map = {}
#         # 目标生物到同步生物 id 集合的映射，方便更新目标变化时查找所有同步生物
#         self._target_syncers = {}
#         self._initialized = True
#
#     def set_sync(self, syncer_id, target_id, mode, duration=None, end_time=None):
#         """
#         建立同步关系，将同步生物 syncer_id 与目标生物 target_id 按 mode 同步
#
#         :param syncer_id: 同步生物的 id
#         :param target_id: 被同步生物的 id
#         :param mode: 同步模式，支持 MODE_ABSOLUTE 或 MODE_PERCENTAGE
#         :param duration: 同步持续时间（单位秒），如果为 None 则表示永久同步
#         :param end_time: 同步结束的时间戳，如果为 None 且 duration 不为 None，则自动计算；若两者均为 None，则表示永久同步
#         :raises ValueError: 当 mode 不在支持范围内时
#         """
#         if mode not in self.VALID_MODES:
#             raise ValueError("mode must be either "{}" or "{}"".format(self.MODE_ABSOLUTE, self.MODE_PERCENTAGE))
#         with self._lock:
#             # 如果同步生物已有同步状态，则先取消之前的同步
#             if syncer_id in self._sync_map:
#                 self.cancel_sync_by_syncer(syncer_id)
#             # 记录同步生物原始的最大生命值（绝对同步下后续用于恢复）
#             comp_health_syncer = CompFactory.CreateAttr(syncer_id)
#             original_hp = comp_health_syncer.GetAttrValue(MinecraftEnum.AttrType.HEALTH)
#             original_max_hp = comp_health_syncer.GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)
#             if end_time is None and duration is not None:
#                 end_time = time.time() + duration
#             self._sync_map[syncer_id] = {
#                 "target_id": target_id,
#                 "mode": mode,
#                 "original_hp": original_hp,
#                 "original_max_hp": original_max_hp,
#                 "duration": duration,
#                 "end_time": end_time
#             }
#             # 更新目标对应的同步生物集合
#             if target_id not in self._target_syncers:
#                 self._target_syncers[target_id] = []
#             self._target_syncers[target_id].append(syncer_id)
#             # 初始同步，直接更新同步生物的生命值
#             self._update_sync_for_syncer(syncer_id)
#             SetDevelopmentMessage(logging.INFO, "Established sync: syncer_id=%s, target_id=%s, mode=%s, duration=%s, end_time=%s",
#                                   syncer_id, target_id, mode, duration, end_time)
#
#     def _update_sync_for_syncer(self, syncer_id):
#         """
#         根据当前目标生物的状态更新单个同步生物的生命值
#
#         :param syncer_id: 同步生物的 id
#         """
#         mapping = self._sync_map.get(syncer_id)
#         if not mapping:
#             return
#         # 检查同步状态是否已过期（非永久同步）
#         if mapping.get("end_time") is not None and time.time() >= mapping.get("end_time"):
#             self.cancel_sync_by_syncer(syncer_id)
#             SetDevelopmentMessage(logging.INFO, "Sync expired and canceled for syncer_id=%s", syncer_id)
#             return
#
#         target_id = mapping["target_id"]
#         mode = mapping["mode"]
#
#         comp_health_target = CompFactory.CreateAttr(target_id)
#         comp_health_syncer = CompFactory.CreateAttr(syncer_id)
#
#         target_current_hp = comp_health_target.GetAttrValue(MinecraftEnum.AttrType.HEALTH)
#         target_max_hp = comp_health_target.GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)
#         # 检查目标生命值的合法性
#         if not isinstance(target_current_hp, (int, float)) or not isinstance(target_max_hp, (int, float)) or target_max_hp <= 0:
#             raise ValueError("Invalid target HP values: target_current_hp={}, target_max_hp={}".format(target_current_hp, target_max_hp))
#
#         if mode == self.MODE_ABSOLUTE:
#             # 绝对同步：复制目标的生命值和上限
#             comp_health_syncer.SetAttrMaxValue(MinecraftEnum.AttrType.HEALTH, target_max_hp)
#             comp_health_syncer.SetAttrValue(MinecraftEnum.AttrType.HEALTH, target_current_hp, 0)
#         elif mode == self.MODE_PERCENTAGE:
#             # 百分比同步：保持自身最大生命值不变，按照目标生命比例计算当前生命值
#             syncer_max_hp = comp_health_syncer.GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)
#             if not isinstance(syncer_max_hp, (int, float)) or syncer_max_hp <= 0:
#                 raise ValueError("Invalid syncer_max_hp: {}".format(syncer_max_hp))
#             ratio = max(0.0, min(1.0, float(target_current_hp) / target_max_hp))
#             new_current = max(0, min(syncer_max_hp, int(ratio * syncer_max_hp)))
#             comp_health_syncer.SetAttrValue(MinecraftEnum.AttrType.HEALTH, new_current, 0)
#             new_current = comp_health_syncer.GetAttrValue(MinecraftEnum.AttrType.HEALTH)
#             new_max = comp_health_syncer.GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)
#             SetDevelopmentMessage(logging.INFO, "Updated syncer_id=%s: mode=%s, new current_hp=%s, max_hp=%s",
#                                   syncer_id, mode, new_current, new_max)
#
#     def update_sync_on_target_change(self, target_id):
#         """
#         当目标生物的生命值或生命上限变化时，更新所有同步该目标的同步生物
#
#         :param target_id: 被同步生物的 id
#         """
#         with self._lock:
#             syncer_ids = list(self._target_syncers.get(target_id, []))
#             for syncer_id in syncer_ids:
#                 self._update_sync_for_syncer(syncer_id)
#             SetDevelopmentMessage(logging.INFO, "Updated all syncers for target_id=%s", target_id)
#
#     def cancel_sync_by_syncer(self, syncer_id):
#         """
#         取消指定同步生物的同步状态
#
#         :param syncer_id: 同步生物的 id
#         """
#         with self._lock:
#             mapping = self._sync_map.pop(syncer_id, None)
#             if not mapping:
#                 return
#             target_id = mapping["target_id"]
#             mode = mapping["mode"]
#             original_max = mapping.get("original_max_hp")
#
#             comp_health_target = CompFactory.CreateAttr(target_id)
#             comp_health_syncer = CompFactory.CreateAttr(syncer_id)
#
#             comp_health_syncer.SetAttrMaxValue(MinecraftEnum.AttrType.HEALTH, original_max)
#             if mode == self.MODE_PERCENTAGE:
#                 # 手动取消时，根据目标当前状态更新同步生物的当前生命值
#                 syncer_current_hp = comp_health_syncer.GetAttrValue(MinecraftEnum.AttrType.HEALTH)
#                 target_max_hp = comp_health_target.GetAttrMaxValue(MinecraftEnum.AttrType.HEALTH)
#                 ratio = (float(syncer_current_hp) / float(target_max_hp)) if target_max_hp > 0 else 0.0
#                 new_current = int(ratio * original_max)
#                 comp_health_syncer.SetAttrValue(MinecraftEnum.AttrType.HEALTH, new_current, 0)
#             # 移除目标中对应的同步记录
#             if target_id in self._target_syncers:
#                 self._target_syncers[target_id].remove(syncer_id)
#                 if not self._target_syncers[target_id]:
#                     del self._target_syncers[target_id]
#             SetDevelopmentMessage(logging.INFO, "Canceled sync for syncer_id=%s", syncer_id)
#
#     def cancel_sync_by_target(self, target_id):
#         """
#         取消与目标生物相关的所有同步状态，
#         即取消所有同步该目标的同步生物的同步状态
#
#         :param target_id: 被同步生物的 id
#         """
#         with self._lock:
#             syncer_ids = list(self._target_syncers.get(target_id, []))
#             for syncer_id in syncer_ids:
#                 if syncer_id in self._sync_map:
#                     self.cancel_sync_by_syncer(syncer_id)
#             if target_id in self._target_syncers:
#                 del self._target_syncers[target_id]
#             SetDevelopmentMessage(logging.INFO, "Canceled all syncs for target_id=%s", target_id)
#
#     def on_death(self, creature_id):
#         """
#         当生物死亡时，取消与其相关的所有同步状态。
#         如果该生物为同步生物，则取消其同步关系；
#         如果为被同步生物，则取消所有同步其的状态。
#
#         :param creature_id: 死亡生物的 id
#         """
#         with self._lock:
#             if creature_id in self._sync_map:
#                 self.cancel_sync_by_syncer(creature_id)
#             if creature_id in self._target_syncers:
#                 self.cancel_sync_by_target(creature_id)
#             SetDevelopmentMessage(logging.INFO, "Processed death for creature_id=%s, canceled all related syncs", creature_id)
#
#     def update_all_syncs(self):
#         """
#         遍历所有同步生物，并根据各自目标生物的当前状态更新其生命值
#         """
#         with self._lock:
#             for syncer_id in list(self._sync_map.keys()):
#                 self._update_sync_for_syncer(syncer_id)
#             SetDevelopmentMessage(logging.INFO, "Updated sync for all syncers")
#
#     def auto_check_expiration(self):
#         """
#         自动检测并取消所有已过期的生命同步状态
#         """
#         with self._lock:
#             for syncer_id in list(self._sync_map.keys()):
#                 mapping = self._sync_map[syncer_id]
#                 if mapping.get("end_time") is not None and time.time() >= mapping.get("end_time"):
#                     self.cancel_sync_by_syncer(syncer_id)
#
#     def extend_all_durations(self, entity_id, additional_seconds):
#         """
#         为所有存在有效期的数据记录延长持续时间（永久记录除外）
#
#         :param entity_id: 实体ID
#         :type entity_id: int | str
#         :param additional_seconds: 需要延长的秒数
#         :type additional_seconds: int | float
#         """
#         if additional_seconds <= 0:
#             raise ValueError("additional_seconds must be greater than 0")
#         now = time.time()
#         with self._lock:
#             data = self._load_data(entity_id)
#             for scope in self.VALID_SCOPES:
#                 if scope == "all":
#                     scope_data = data[scope]
#                     for subtype in self.VALID_SUBTYPES:
#                         for item in scope_data.get(subtype, []):
#                             if item["end_time"] is not None and item["end_time"] > now:
#                                 item["end_time"] += additional_seconds
#                                 item["duration"] += additional_seconds
#                 else:
#                     for target_id, sub_dict in data[scope].iteritems():
#                         for subtype in self.VALID_SUBTYPES:
#                             for item in sub_dict.get(subtype, []):
#                                 if item["end_time"] is not None and item["end_time"] > now:
#                                     item["end_time"] += additional_seconds
#                                     item["duration"] += additional_seconds
#             self._save_data(entity_id, data)
#             SetDevelopmentMessage(logging.INFO,
#                                   "Extended all durations by %s seconds for entity_id=%s", additional_seconds, entity_id)
