# -*- coding: utf-8 -*-
from ServerBaseUtils import *
from utils import AttributeServerUtils, EntitySpatialMotionServerUtils


class ServerMainSystem(ServerSystem):
    TIMID_CRAB_IDENTIFIER = "fg:fg_crab"
    HELP_CRAB_IDENTIFIER = "fg:fg_crab_help"
    TRACKED_CRAB_IDENTIFIERS = {
        TIMID_CRAB_IDENTIFIER: "flee",
        HELP_CRAB_IDENTIFIER: "help",
    }
    CRAB_DISCOVERY_INTERVAL = 20
    CRAB_STATE_UPDATE_INTERVAL = 5
    CRAB_DISCOVERY_RADIUS = 64
    CRAB_RESET_AFTER_NO_TARGET_TICKS = 100
    CRAB_RECORD_STALE_TICKS = 200
    CRAB_ALLY_REACTION_RADIUS = 10
    CRAB_HELP_TARGET_SEARCH_RADIUS = 12

    def __init__(self, namespace, system_name):
        super(ServerMainSystem, self).__init__(namespace, system_name)
        SetServerMainSystem(self)
        self._global_tick_count = 0
        self._tracked_crab_state = {}
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
        self._tracked_crab_state = {}
        SetDevelopmentMessage(logging.INFO, "%s ServerMainSystem Destroyed", ModName)

    @property
    def GlobalTickCount(self):
        return self._global_tick_count

    def OnScriptTickServer(self):
        self._global_tick_count += 1
        if not GetServerMainSystem():
            SetServerMainSystem(self)

        if self._global_tick_count % self.CRAB_DISCOVERY_INTERVAL == 0:
            self._discover_crabs_near_players()
            self._purge_stale_crab_records()

        if self._global_tick_count % self.CRAB_STATE_UPDATE_INTERVAL == 0:
            self._update_crab_state()

    def _discover_crabs_near_players(self):
        for player_id in ServerApi.GetPlayerList() or []:
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
                crab_mode = self._get_crab_mode(entity_id)
                if crab_mode:
                    self._remember_crab(entity_id, crab_mode)

    def _remember_crab(self, entity_id, crab_mode):
        crab_state = self._tracked_crab_state.get(entity_id)
        current_health = self._safe_get_health(entity_id)
        if crab_state is None:
            self._tracked_crab_state[entity_id] = {
                'mode': crab_mode,
                'had_target': False,
                'no_target_ticks': 0,
                'last_health': current_health,
                'last_seen_tick': self._global_tick_count,
            }
            return

        crab_state['mode'] = crab_mode
        crab_state['last_seen_tick'] = self._global_tick_count
        if crab_state.get('last_health') is None and current_health is not None:
            crab_state['last_health'] = current_health

    def _purge_stale_crab_records(self):
        stale_entity_id_list = []
        for entity_id, crab_state in self._tracked_crab_state.items():
            if self._global_tick_count - crab_state.get('last_seen_tick', 0) > self.CRAB_RECORD_STALE_TICKS:
                stale_entity_id_list.append(entity_id)

        for entity_id in stale_entity_id_list:
            self._tracked_crab_state.pop(entity_id, None)

    def _update_crab_state(self):
        for entity_id in list(self._tracked_crab_state.keys()):
            crab_mode = self._get_crab_mode(entity_id)
            if not crab_mode:
                self._tracked_crab_state.pop(entity_id, None)
                continue

            crab_state = self._tracked_crab_state[entity_id]
            crab_state['mode'] = crab_mode
            self._handle_health_change(entity_id, crab_state)
            self._handle_target_reset(entity_id, crab_state)

    def _handle_health_change(self, entity_id, crab_state):
        current_health = self._safe_get_health(entity_id)
        if current_health is None or current_health <= 0:
            self._tracked_crab_state.pop(entity_id, None)
            return

        last_health = crab_state.get('last_health')
        crab_state['last_health'] = current_health
        if last_health is None or current_health >= last_health:
            return

        attacker_id = self._resolve_likely_attacker(entity_id)
        if crab_state.get('mode') == 'flee':
            self._notify_nearby_flee_crabs(entity_id)
            return

        self._notify_nearby_help_crabs(entity_id, attacker_id)

    def _handle_target_reset(self, entity_id, crab_state):
        target_id = AttributeServerUtils.GetAttackTarget(entity_id)
        if target_id:
            crab_state['had_target'] = True
            crab_state['no_target_ticks'] = 0
            return

        if not crab_state.get('had_target'):
            crab_state['no_target_ticks'] = 0
            return

        crab_state['no_target_ticks'] += self.CRAB_STATE_UPDATE_INTERVAL
        if crab_state['no_target_ticks'] < self.CRAB_RESET_AFTER_NO_TARGET_TICKS:
            return

        # 丢失目标一段时间后才恢复默认攻击手，避免战斗末尾动作来回跳。
        self._trigger_entity_event(entity_id, 'fg:reset_attack_mode')
        crab_state['had_target'] = False
        crab_state['no_target_ticks'] = 0

    def _notify_nearby_flee_crabs(self, hurt_entity_id):
        hurt_pos, dimension_id = self._get_entity_pos_and_dimension(hurt_entity_id)
        if hurt_pos is None:
            return

        nearby_entity_list = EntitySpatialMotionServerUtils.CheckCenterPosAroundEntityList(
            hurt_pos,
            self.CRAB_ALLY_REACTION_RADIUS,
            dimension_id,
            exclude_entity_list=[hurt_entity_id]
        ) or []

        for entity_id in nearby_entity_list:
            if self._get_crab_mode(entity_id) != 'flee':
                continue
            if AttributeServerUtils.GetAttackTarget(entity_id):
                # 已经锁定仇恨目标的个体保持报仇，不再被群体逃跑覆盖。
                continue
            self._trigger_entity_event(entity_id, 'fg:alert_escape')

    def _notify_nearby_help_crabs(self, hurt_entity_id, attacker_id):
        hurt_pos, dimension_id = self._get_entity_pos_and_dimension(hurt_entity_id)
        if hurt_pos is None:
            return

        nearby_entity_list = EntitySpatialMotionServerUtils.CheckCenterPosAroundEntityList(
            hurt_pos,
            self.CRAB_ALLY_REACTION_RADIUS,
            dimension_id
        ) or []

        for entity_id in nearby_entity_list:
            if self._get_crab_mode(entity_id) != 'help':
                continue

            if attacker_id:
                AttributeServerUtils.SetAttackTarget(entity_id, attacker_id)

            self._trigger_entity_event(entity_id, 'fg:on_assist_hit')
            tracked_state = self._tracked_crab_state.get(entity_id)
            if tracked_state is not None:
                tracked_state['had_target'] = True if attacker_id else tracked_state.get('had_target', False)
                tracked_state['no_target_ticks'] = 0

    def _resolve_likely_attacker(self, hurt_entity_id):
        attack_target = AttributeServerUtils.GetAttackTarget(hurt_entity_id)
        if attack_target:
            return attack_target

        hurt_pos, dimension_id = self._get_entity_pos_and_dimension(hurt_entity_id)
        if hurt_pos is None:
            return None

        nearby_entity_list = EntitySpatialMotionServerUtils.CheckCenterPosAroundEntityList(
            hurt_pos,
            self.CRAB_HELP_TARGET_SEARCH_RADIUS,
            dimension_id,
            exclude_entity_list=[hurt_entity_id]
        ) or []

        nearest_entity_id = None
        nearest_distance_sq = None
        for entity_id in nearby_entity_list:
            if self._get_crab_mode(entity_id):
                continue
            if not self._is_revenge_target(entity_id):
                continue

            entity_pos = self._safe_get_entity_pos(entity_id)
            if entity_pos is None:
                continue

            distance_sq = self._distance_sq(hurt_pos, entity_pos)
            if nearest_distance_sq is None or distance_sq < nearest_distance_sq:
                nearest_distance_sq = distance_sq
                nearest_entity_id = entity_id

        return nearest_entity_id

    def _is_revenge_target(self, entity_id):
        return (
            AttributeServerUtils.IsEntityFamilyMatch(entity_id, 'player')
            or AttributeServerUtils.IsEntityFamilyMatch(entity_id, 'monster')
        )

    def _get_crab_mode(self, entity_id):
        for identifier, crab_mode in self.TRACKED_CRAB_IDENTIFIERS.items():
            try:
                if AttributeServerUtils.IsEntityTypeStrIn(entity_id, identifier):
                    return crab_mode
            except Exception:
                continue
        return None

    def _safe_get_health(self, entity_id):
        try:
            return AttributeServerUtils.GetHealthValue(entity_id)
        except Exception:
            return None

    def _safe_get_entity_pos(self, entity_id):
        pos_comp = CompFactory.CreatePos(entity_id)
        if pos_comp is None:
            return None
        try:
            return pos_comp.GetFootPos()
        except Exception:
            return None

    def _get_entity_pos_and_dimension(self, entity_id):
        pos_comp = CompFactory.CreatePos(entity_id)
        dimension_comp = CompFactory.CreateDimension(entity_id)
        if pos_comp is None or dimension_comp is None:
            return None, None
        try:
            return pos_comp.GetFootPos(), dimension_comp.GetEntityDimensionId()
        except Exception:
            return None, None

    def _distance_sq(self, pos_a, pos_b):
        diff_x = pos_a[0] - pos_b[0]
        diff_y = pos_a[1] - pos_b[1]
        diff_z = pos_a[2] - pos_b[2]
        return diff_x * diff_x + diff_y * diff_y + diff_z * diff_z

    def _trigger_entity_event(self, entity_id, event_name):
        temp_tag = self._make_temp_event_tag()
        tag_comp = CompFactory.CreateTag(entity_id)
        if tag_comp is None:
            return False

        tag_comp.AddEntityTag(temp_tag)
        try:
            command = '/event entity @e[tag=%s] %s' % (temp_tag, event_name)
            GetCompCommandLevel().SetCommand(command)
        finally:
            tag_comp.RemoveEntityTag(temp_tag)
        return True

    def _make_temp_event_tag(self):
        self._temp_event_index += 1
        return 'fg_crab_evt_%s' % self._temp_event_index
