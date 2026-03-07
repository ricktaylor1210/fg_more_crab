# -*- coding: utf-8 -*-
from ServerBaseUtils import *
from utils import AttributeServerUtils, EntitySpatialMotionServerUtils


class ServerMainSystem(ServerSystem):
    BASE_CRAB_IDENTIFIER = "fg:fg_crab"
    CRAB_DISCOVERY_INTERVAL = 20
    CRAB_STATE_UPDATE_INTERVAL = 5
    CRAB_DISCOVERY_RADIUS = 64
    CRAB_RESET_AFTER_NO_TARGET_TICKS = 100
    CRAB_RECORD_STALE_TICKS = 200

    def __init__(self, namespace, system_name):
        super(ServerMainSystem, self).__init__(namespace, system_name)
        SetServerMainSystem(self)
        self._global_tick_count = 0
        self._tracked_base_crab_state = {}
        self._temp_event_index = 0
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerIntendLeaveServerEvent", self, self.PlayerIntendLeaveServerEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 10)
        SetDevelopmentMessage(logging.INFO, "%s ServerMainSystem Load Finished", ModName)

    def PlayerIntendLeaveServerEvent(self, args):
        player_id = args["playerId"]
        if player_id == ServerApi.GetHostPlayerId() and not ServerApi.GetPlayerList():
            self.DestroySystem()

    def DestroySystem(self):
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerIntendLeaveServerEvent", self, self.PlayerIntendLeaveServerEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 10)
        self._tracked_base_crab_state = {}
        SetDevelopmentMessage(logging.INFO, "%s ServerMainSystem Destroyed", ModName)

    @property
    def GlobalTickCount(self):
        return self._global_tick_count

    def OnScriptTickServer(self):
        self._global_tick_count += 1
        if not GetServerMainSystem():
            SetServerMainSystem(self)

        if self._global_tick_count % self.CRAB_DISCOVERY_INTERVAL == 0:
            self._discover_base_crabs_near_players()
            self._purge_stale_base_crab_records()

        if self._global_tick_count % self.CRAB_STATE_UPDATE_INTERVAL == 0:
            self._update_base_crab_combat_state()

    def _discover_base_crabs_near_players(self):
        player_id_list = ServerApi.GetPlayerList() or []
        for player_id in player_id_list:
            player_pos_comp = CompFactory.CreatePos(player_id)
            player_dim_comp = CompFactory.CreateDimension(player_id)
            if player_pos_comp is None or player_dim_comp is None:
                continue

            center_pos = player_pos_comp.GetFootPos()
            dimension_id = player_dim_comp.GetEntityDimensionId()
            nearby_entity_list = EntitySpatialMotionServerUtils.CheckCenterPosAroundEntityList(
                center_pos,
                self.CRAB_DISCOVERY_RADIUS,
                dimension_id
            ) or []

            for entity_id in nearby_entity_list:
                if self._is_base_crab(entity_id):
                    self._remember_base_crab(entity_id)

    def _remember_base_crab(self, entity_id):
        crab_state = self._tracked_base_crab_state.get(entity_id)
        if crab_state is None:
            self._tracked_base_crab_state[entity_id] = {
                "had_target": False,
                "no_target_ticks": 0,
                "last_seen_tick": self._global_tick_count,
            }
            return

        crab_state["last_seen_tick"] = self._global_tick_count

    def _purge_stale_base_crab_records(self):
        stale_entity_id_list = []
        for entity_id, crab_state in self._tracked_base_crab_state.items():
            if self._global_tick_count - crab_state.get("last_seen_tick", 0) > self.CRAB_RECORD_STALE_TICKS:
                stale_entity_id_list.append(entity_id)

        for entity_id in stale_entity_id_list:
            self._tracked_base_crab_state.pop(entity_id, None)

    def _update_base_crab_combat_state(self):
        for entity_id in list(self._tracked_base_crab_state.keys()):
            if not self._is_base_crab(entity_id):
                self._tracked_base_crab_state.pop(entity_id, None)
                continue

            crab_state = self._tracked_base_crab_state[entity_id]
            target_id = AttributeServerUtils.GetAttackTarget(entity_id)

            if target_id:
                crab_state["had_target"] = True
                crab_state["no_target_ticks"] = 0
                continue

            if not crab_state.get("had_target"):
                crab_state["no_target_ticks"] = 0
                continue

            crab_state["no_target_ticks"] += self.CRAB_STATE_UPDATE_INTERVAL
            if crab_state["no_target_ticks"] < self.CRAB_RESET_AFTER_NO_TARGET_TICKS:
                continue

            # 这里在“丢失目标一段时间”后再恢复默认攻击手，避免刚脱战时立刻跳回默认动作。
            # 未来派生蟹只要沿用 fg:reset_attack_mode 事件，就能复用这套脱战复位逻辑。
            self._trigger_entity_event(entity_id, "fg:reset_attack_mode")
            crab_state["had_target"] = False
            crab_state["no_target_ticks"] = 0

    def _is_base_crab(self, entity_id):
        try:
            return AttributeServerUtils.IsEntityTypeStrIn(entity_id, self.BASE_CRAB_IDENTIFIER)
        except Exception:
            return False

    def _trigger_entity_event(self, entity_id, event_name):
        # 用一次性临时 tag 精确锁定当前实体，避免全局命令误触其它同类生物。
        temp_tag = self._make_temp_event_tag()
        tag_comp = CompFactory.CreateTag(entity_id)
        if tag_comp is None:
            return False

        tag_comp.AddEntityTag(temp_tag)
        try:
            command = "/event entity @e[tag=%s] %s" % (temp_tag, event_name)
            GetCompCommandLevel().SetCommand(command)
        finally:
            tag_comp.RemoveEntityTag(temp_tag)
        return True

    def _make_temp_event_tag(self):
        self._temp_event_index += 1
        return "fg_crab_evt_%s" % self._temp_event_index
