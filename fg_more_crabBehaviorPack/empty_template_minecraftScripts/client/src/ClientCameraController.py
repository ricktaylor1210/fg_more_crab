# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.api import (
    EmptyQueryClientApi, EmptyAttributeClientApi, EmptyGameClientApi,
    EmptyBlockClientApi, EmptyDataClientApi
)
from fg_more_crabScripts.client.base_parent_class.ClientListener import *
from fg_more_crabScripts.client.base_parent_class.ClientTaskFunction import ClientTaskFunction
from fg_more_crabScripts.client.src.ClientEntity import ClientEntity
from fg_more_crabScripts.client.src.ClientPlayer import ClientPlayer


class ClientCameraController(ClientListener):
    def __init__(self):
        super(ClientCameraController, self).__init__(True)
        self.controller_uuid = uuid.uuid4()
        self.local_input_vector = (0.0, 0.0)
        self.task_class = None
        EmptyDataClientApi.SetClientKeyValue("camera_task_queue", [], "empty_studio", True)
        self.engine_events = {
            "OnKeyPressInGame": {"func": self.OnKeyPressInGame},
            "ClientJumpButtonPressDownEvent": {"func": self.ClientJumpButtonPressDownEvent},
            "ClientJumpButtonReleaseEvent": {"func": self.ClientJumpButtonReleaseEvent}
        }
        self.custom_events = {
            "CameraBindEntityDeathEvent": {"func": self.CameraBindEntityDeathEvent}
        }
        self.Register()

    def OnScriptTickClient(self):
        current_input = GetActionMotionComp(LocalPlayerId).GetInputVector()
        if current_input != self.local_input_vector:
            self.local_input_vector = current_input
            ClientMain.NotifyToServer("PlayerInputChangeEvent", {"input_vector": current_input})

    def OnKeyPressInGame(self, args):
        is_down = args["isDown"]
        key = args["key"]
        if is_down == "0":
            self.handle_key_press(key)

    def handle_key_press(self, key):
        pass
        # if key == str(MinecraftEnum.KeyBoardType.KEY_NUMPAD2):
        #     self.notify_server_with_entity("KeyDownButton2TestEvent")
        # elif key == str(MinecraftEnum.KeyBoardType.KEY_NUMPAD3):
        #     self.notify_server_with_entity("KeyDownButton3TestEvent")
        # elif key == str(MinecraftEnum.KeyBoardType.KEY_NUMPAD4):
        #     ClientMain.NotifyToServer("KeyDownButton4TestEvent", {})
        # elif key == str(MinecraftEnum.KeyBoardType.KEY_NUMPAD1):
        #     self.SetCameraBindToPickEntity(
        #         render_local_player=True, lock_player_controller=True,
        #         control_entity=True, sync_position=False,
        #         reset_back_origin_position=True, immune_damage=True,
        #         sync_damage=True
        #     )
        # elif key == str(MinecraftEnum.KeyBoardType.KEY_NUMPAD0):
        #     self.ResetCameraBind()

    def notify_server_with_entity(self, event_name):
        pick_entity_id = EmptyAttributeClientApi.GetPickFacingEntity()
        if pick_entity_id:
            ClientMain.NotifyToServer(event_name, {"pick_entity_id": pick_entity_id})

    def SetCameraBindToPickEntity(self, **kwargs):
        pick_entity_id = EmptyAttributeClientApi.GetPickFacingEntity()
        if pick_entity_id:
            self.task_class = ClientTaskFunction(
                "camera_task_queue",
                lambda: self.SetCameraBindToEntity(pick_entity_id, **kwargs),
                self.controller_uuid,
                True
            )

    def SetCameraBindToEntity(self, entity_id, **kwargs):
        kwargs["bind_to_entity_id"] = entity_id
        control_entity = kwargs.setdefault("control_entity", False)
        sync_position = kwargs.setdefault("sync_position", False)

        # 调整设置根据 control_entity 和 sync_position
        if control_entity:
            self._setup_for_control_entity()
        elif sync_position:
            self._setup_for_sync_position()

        CompCamera.SetCameraBindActorId(entity_id)
        GameCompLevel.SetRenderLocalPlayer(kwargs["render_local_player"])
        CompOperation.SetCanAttack(not kwargs["lock_player_controller"])
        ClientMain.NotifyToServer("PlayerBindCameraToEntityEvent", kwargs)

    def _setup_for_control_entity(self):
        CompOperation.SetCanAll(True)
        CompOperation.SetCanAttack(False)

    def _setup_for_sync_position(self):
        CompOperation.SetCanAll(False)
        CompOperation.SetCanDrag(True)
        CompOperation.SetCanChat(True)
        CompOperation.SetCanScreenShot(True)
        CompOperation.SetCanOpenInv(True)
        CompOperation.SetCanPause(True)
        CompOperation.SetCanPerspective(True)
        self._hide_gui_elements(True)

    def ResetCameraBind(self):
        if self.task_class:
            self.task_class.ClearCurrentTaskQueue()
            self.task_class = None

        CompCamera.ResetCameraBindActorId()
        GameCompLevel.SetRenderLocalPlayer(True)
        CompOperation.SetCanAll(True)
        self._hide_gui_elements(False)
        ClientMain.NotifyToServer("PlayerUnBindCameraToEntityEvent", {})

    def _hide_gui_elements(self, hide):
        ClientApi.HideSneakGui(hide)
        ClientApi.HideHorseHealthGui(hide)
        ClientApi.HideAirSupplyGUI(hide)
        ClientApi.HideInteractGui(hide)
        ClientApi.HideHungerGui(hide)
        ClientApi.HideSwimGui(hide)
        ClientApi.HideMoveGui(hide)
        ClientApi.HideJumpGui(hide)

    def CameraBindEntityDeathEvent(self, args):
        self.ResetCameraBind()

    def ClientJumpButtonPressDownEvent(self, args):
        ClientMain.NotifyToServer("PlayerJumpStateChangeEvent", {"is_down": True})

    def ClientJumpButtonReleaseEvent(self, args):
        ClientMain.NotifyToServer("PlayerJumpStateChangeEvent", {"is_down": False})
