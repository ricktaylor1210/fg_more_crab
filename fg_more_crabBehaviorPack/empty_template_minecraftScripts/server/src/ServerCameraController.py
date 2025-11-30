# -*- coding: utf-8 -*-
import math

from fg_more_crabScripts.server.api import EmptyAttributeServerApi, EmptyLocationDealServerApi, EmptyFightServerApi, EmptyDamageServerApi
from fg_more_crabScripts.server.base_parent_class.ServerListener import *
from fg_more_crabScripts.server.src.ServerPlayer import ServerPlayer
from fg_more_crabScripts.server.src.ServerEntity import ServerEntity


class ServerCameraController(ServerListener):
    def __init__(self):
        super(ServerCameraController, self).__init__(True)
        self.PlayerCameraBindEntityDataMap = {}
        self.PlayerInputVectorData = {}
        self.PlayerJumpStateData = {}
        self.ControlEntityJumpArriveMaxPowerMap = {}
        self.engine_events = {
            "MobDieEvent": {"func": self.MobDieEvent, "priority": 0},
            "OnMobHitBlockServerEvent": {"func": self.OnMobHitBlockServerEvent, "priority": 0}
        }
        self.custom_events = {
            "PlayerInputChangeEvent": {"func": self.PlayerInputChangeEvent},
            "PlayerJumpStateChangeEvent": {"func": self.PlayerJumpStateChangeEvent},
            "PlayerBindCameraToEntityEvent": {"func": self.PlayerBindCameraToEntityEvent},
            "PlayerUnBindCameraToEntityEvent": {"func": self.PlayerUnBindCameraToEntityEvent}
        }
        self.Register()

    def PlayerJumpStateChangeEvent(self, args):
        player_id = args["__id__"]
        is_down = args["is_down"]
        self.PlayerJumpStateData[player_id] = is_down

    def OnMobHitBlockServerEvent(self, args):
        # entityId	str	碰撞到方块的生物Id
        # posX	int	碰撞方块x坐标
        # posY	int	碰撞方块y坐标
        # posZ	int	碰撞方块z坐标
        # blockId	str	碰撞方块的identifier
        # auxValue	int	碰撞方块的附加值
        # dimensionId	int	维度id
        pass

    def PlayerInputChangeEvent(self, args):
        player_id = args["__id__"]
        input_vector = args["input_vector"]
        self.PlayerInputVectorData[player_id] = input_vector

    def MobDieEvent(self, args):
        entity_id = args["id"]
        if entity_id in self.PlayerCameraBindEntityDataMap:
            self._unbind_camera(entity_id)
            ServerMain.NotifyToClient(entity_id, "CameraBindEntityDeathEvent", {})
        else:
            for player_id, bind_data in self.PlayerCameraBindEntityDataMap.items():
                if entity_id == bind_data["bind_to_entity_id"]:
                    self._unbind_camera(player_id)
                    ServerMain.NotifyToClient(player_id, "CameraBindEntityDeathEvent", {})
                    break

    def PlayerBindCameraToEntityEvent(self, kwargs):
        player_id = kwargs["__id__"]
        bind_to_entity_id = kwargs.get("bind_to_entity_id")
        if not bind_to_entity_id:
            return

        bind_data = {
            "bind_to_entity_id": bind_to_entity_id,
            "origin_foot_pos": EmptyAttributeServerApi.GetEntityFootPos(player_id),
            "origin_size": EmptyAttributeServerApi.GetEntitySize(player_id),
            "render_local_player": kwargs.get("render_local_player", False),
            "lock_player_controller": kwargs.get("lock_player_controller", True),
            "reset_back_origin_position": kwargs.get("reset_back_origin_position", True),
            "sync_position": kwargs.get("sync_position", False),
            "immune_damage": kwargs.get("immune_damage", False),
            "sync_damage": kwargs.get("sync_damage", False),
            "sync_damage_method_type": kwargs.get("sync_damage_method_type", "force_cause_sync_percent"),
            "sync_survive": kwargs.get("sync_survive", False),
            "control_entity": kwargs.get("control_entity", False)
        }

        self.PlayerCameraBindEntityDataMap[player_id] = bind_data
        EmptyAttributeServerApi.SetEntityFootPos(player_id, EmptyLocationDealServerApi.ChangeValueInPos(bind_data["origin_foot_pos"], False, (0, 16, 0)))
        EmptyAttributeServerApi.SetEntitySize(player_id, (0, 0))

        if bind_data["control_entity"]:
            EmptyFightServerApi.BlockEntityAI(bind_to_entity_id, freeze_anim=False, can_auto_unlock=False)
            GameCompLevel.OpenMobHitBlockDetection(bind_to_entity_id, 0.0001)
            EmptyAttributeServerApi.SetEntityFootPos(player_id, EmptyAttributeServerApi.GetEntityFootPos(bind_to_entity_id))
        else:
            EmptyFightServerApi.BlockEntityAI(bind_to_entity_id, freeze_anim=False, can_auto_unlock=False)
            GetGravityComp(player_id).SetGravity(0.0001)

        if bind_data["sync_damage"]:
            EmptyDamageServerApi.SetEntitySyncDamageToAnotherEntity(bind_to_entity_id, player_id, bind_data["sync_damage_method_type"], True)
        if bind_data["sync_survive"]:
            EmptyDamageServerApi.SetEntitySyncDeathStatusToAnotherEntity(bind_to_entity_id, player_id)
        if bind_data["immune_damage"]:
            EmptyDamageServerApi.SetEntityIsImmuneDamage(player_id)

    def OnScriptTickServer(self):
        tick_count = GlobalTickCount()
        if tick_count % 15 == 0:
            self._reset_attack_targets()
        if tick_count % 30 == 0:
            self._recover_entity_air_supply()
            self._sync_entity_positions()
        elif tick_count % 3 == 0:
            self._track_controlled_entities()

    def PlayerUnBindCameraToEntityEvent(self, kwargs):
        player_id = kwargs["__id__"]
        if player_id not in self.PlayerCameraBindEntityDataMap:
            return

        self._unbind_camera(player_id)

    def _unbind_camera(self, player_id):
        bind_data = self.PlayerCameraBindEntityDataMap.pop(player_id, None)
        if not bind_data:
            return

        bind_to_entity_id = bind_data["bind_to_entity_id"]
        EmptyFightServerApi.UnBlockEntityAI(bind_to_entity_id)
        EmptyLocationDealServerApi.RemoveEntityAllOldMotion(player_id)
        GameCompLevel.CloseMobHitBlockDetection(bind_to_entity_id)

        if bind_data["reset_back_origin_position"]:
            EmptyAttributeServerApi.SetEntityFootPos(player_id, bind_data["origin_foot_pos"])
            EmptyAttributeServerApi.SetEntitySize(player_id, bind_data["origin_size"])

        GetGravityComp(player_id).SetGravity(GameCompLevel.GetLevelGravity())
        EmptyDamageServerApi.SetEntitySyncDamageToAnotherEntity(bind_to_entity_id, player_id, sync_state=False)
        EmptyDamageServerApi.SetEntitySyncDeathStatusToAnotherEntity(bind_to_entity_id, player_id, sync_state=False)
        EmptyDamageServerApi.SetEntityIsImmuneDamage(player_id, False)

    def _reset_attack_targets(self):
        for player_id, bind_data in self.PlayerCameraBindEntityDataMap.items():
            bind_to_entity_id = bind_data["bind_to_entity_id"]
            around_entities = EmptyLocationDealServerApi.CheckEntityAroundEntityList(player_id, 8)
            EmptyAttributeServerApi.ClearAttackTargetIfMatched(bind_to_entity_id, player_id)

            for entity_id in around_entities:
                if entity_id != bind_to_entity_id:
                    EmptyAttributeServerApi.ClearAttackTargetIfMatched(entity_id, player_id)

    def _sync_entity_positions(self):
        for player_id, bind_data in self.PlayerCameraBindEntityDataMap.items():
            if bind_data["control_entity"]:
                self.AddControlMotion(player_id, bind_data["bind_to_entity_id"])
                # EmptyLocationDealServerApi.AddEntityTrackMotion(bind_data["bind_to_entity_id"], EmptyAttributeServerApi.GetEntityFootPos(player_id), 0.09,
                #                                                 start_rot=EmptyAttributeServerApi.GetEntityRot(player_id),
                #                                                 target_rot=EmptyAttributeServerApi.GetEntityRot(player_id))
            elif bind_data["sync_position"]:
                self._sync_position(player_id, bind_data)

    def dot_product_perpendicular(self, v):
        # 原始向量
        x, y = v

        # 旋转90度后的向量
        perpendicular_v = (-y, x)

        # 计算点积
        dot_product = x * perpendicular_v[0] + y * perpendicular_v[1]

        return dot_product

    def AddControlMotion(self, player_id, control_entity_id):
        dimension_id = EmptyAttributeServerApi.GetEntityDimension(player_id)
        player_rot = EmptyAttributeServerApi.GetEntityRot(player_id)
        player_dir = EmptyAttributeServerApi.GetEntityDir(player_id)

        control_entity_rot = EmptyAttributeServerApi.GetEntityRot(control_entity_id)
        control_entity_pos = EmptyAttributeServerApi.GetEntityFootPos(control_entity_id)

        input_vector = self.PlayerInputVectorData.setdefault(player_id, (0.0, 0.0))
        is_jump = self.PlayerJumpStateData.setdefault(player_id, False)
        jump_power = GetGravityComp(control_entity_id).GetJumpPower()
        max_check_ground_diff_y = int(math.ceil(jump_power * 3.0))

        if all(x is not None for x in [dimension_id, player_rot, player_dir, control_entity_rot, control_entity_pos, jump_power]):

            x_vector = 0.0
            z_vector = 0.0
            if input_vector != (0.0, 0.0):
                # 将player_dir转换为Vector3类型并忽略y轴
                original_vector = Vector3(player_dir[0], 0, player_dir[2])

                # 创建绕y轴旋转90度的四元数
                rotation = Quaternion.Euler(0, 90, 0)

                # 旋转original_vector
                rotated_vector = rotation * original_vector

                # 缩放旋转后的向量
                scaled_rotated_vector = rotated_vector * input_vector[0] * 1.0

                # 缩放原始向量
                scaled_original_vector = original_vector * input_vector[1] * 1.0

                # 计算最终向量
                final_vector = scaled_rotated_vector + scaled_original_vector

                x_vector = final_vector.x
                z_vector = final_vector.z

            if not self.ControlEntityJumpArriveMaxPowerMap.setdefault(control_entity_id, False):
                ray_message = ServerApi.getEntitiesOrBlockFromRay(dimension_id, control_entity_pos, (0.0, -1.0, 0.0), max_check_ground_diff_y + 2, False,
                                                                  MinecraftEnum.RayFilterType.OnlyBlocks)

                print control_entity_pos[1] - ray_message[0]["hitPos"][1]
                print jump_power * 3.0
                if ray_message and ray_message[0]["hitPos"] and control_entity_pos[1] - ray_message[0]["hitPos"][1] >= jump_power * 3.0:
                    self.ControlEntityJumpArriveMaxPowerMap[control_entity_id] = True

            if self.ControlEntityJumpArriveMaxPowerMap[control_entity_id]:
                ray_message = ServerApi.getEntitiesOrBlockFromRay(dimension_id, control_entity_pos, (0.0, -1.0, 0.0), 1, False,
                                                                  MinecraftEnum.RayFilterType.OnlyBlocks)

                if ray_message and ray_message[0]["hitPos"] and control_entity_pos[1] - ray_message[0]["hitPos"][1] <= 0.01:
                    self.ControlEntityJumpArriveMaxPowerMap[control_entity_id] = False
            y_motion = -jump_power * 3.0
            if is_jump and not self.ControlEntityJumpArriveMaxPowerMap[control_entity_id]:
                y_motion = jump_power * 3.0
            ray_rot = (x_vector, y_motion, z_vector)
            ray_check_pos=control_entity_pos
            if y_motion>0:
                ray_check_pos=EmptyLocationDealServerApi.ChangeValueInPos(control_entity_pos,False,(0,1,0))
            ray_message = ServerApi.getEntitiesOrBlockFromRay(dimension_id, ray_check_pos, ray_rot, max_check_ground_diff_y, False,
                                                              MinecraftEnum.RayFilterType.OnlyBlocks)
            print "y_motion",y_motion
            if not ray_message:
                print ("4444444444444444444444444444444")
                target_pos = EmptyLocationDealServerApi.ChangeValueInPos(control_entity_pos, False, ray_rot)
            elif ray_message and ray_message[0]["hitPos"]:
                if control_entity_pos[1] > ray_message[0]["hitPos"][1]:
                    target_pos = ray_message[0]["hitPos"]
                    print ("1111111111111111111111111111111")
                    print target_pos
                else:
                    print ("2222222222222222222222222222222222")
                    ray_rot = (x_vector, 0.0, z_vector)
                    ray_message = ServerApi.getEntitiesOrBlockFromRay(dimension_id, control_entity_pos, ray_rot, max_check_ground_diff_y, False,
                                                                      MinecraftEnum.RayFilterType.OnlyBlocks)
                    if ray_message and ray_message[0]["hitPos"]:
                        target_pos = ray_message[0]["hitPos"]
                    else:
                        target_pos = EmptyLocationDealServerApi.ChangeValueInPos(control_entity_pos, False, ray_rot)
            else:
                print ("3333333333333333333333333333333333")
                target_pos = EmptyLocationDealServerApi.ChangeValueInPos(control_entity_pos, False, ray_rot)
            EmptyLocationDealServerApi.AddEntityTrackMotion(control_entity_id, target_pos, 0.03, target_rot=player_rot, start_rot=player_rot)

    def _sync_position(self, player_id, bind_data):
        EmptyLocationDealServerApi.SetEntityMotion(bind_data["bind_to_entity_id"], (0.5, 0, 0.5))
        player_foot_pos = EmptyAttributeServerApi.GetEntityFootPos(bind_data["bind_to_entity_id"])
        if player_foot_pos:
            EmptyLocationDealServerApi.AddEntityTrackMotion(player_id, EmptyLocationDealServerApi.ChangeValueInPos(player_foot_pos, False, (0, 16, 0)), 0.09)

    def _track_controlled_entities(self):
        for player_id, bind_data in self.PlayerCameraBindEntityDataMap.items():
            if bind_data["control_entity"]:
                self.AddControlMotion(player_id, bind_data["bind_to_entity_id"])
                # EmptyLocationDealServerApi.AddEntityTrackMotion(bind_data["bind_to_entity_id"], EmptyAttributeServerApi.GetEntityFootPos(player_id), 0.09,
                #                                                 start_rot=EmptyAttributeServerApi.GetEntityRot(player_id),
                #                                                 target_rot=EmptyAttributeServerApi.GetEntityRot(player_id))

    def _recover_entity_air_supply(self):
        for player_id in self.PlayerCameraBindEntityDataMap.keys():
            EmptyAttributeServerApi.SetCurrentAirSupplyToMaxAirSupply(player_id)
