# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyDataServerApi as DataApi
from fg_more_crabScripts.server.api import EmptyGameServerApi as GameApi
from fg_more_crabScripts.server.api import EmptyAttributeServerApi as AttributeApi
from fg_more_crabScripts.server.base_parent_class.ServerListener import *


class ServerSetting(ServerListener):
    def __init__(self):
        super(ServerSetting, self).__init__(True)
        # setting展示
        self.TemplateSetting = True
        # 客户端单独的setting
        self.ClientTemplateSettingMap = {}

        self.engine_events.update({
            # engineEventName : {func,priority}
            "ClientLoadAddonsFinishServerEvent": {"func": self.ClientLoadAddonsFinishServerEvent}
        })
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            "PlayerSaveSettingEvent": {"func": self.PlayerSaveSettingEvent},
            "SyncClientOnlySettingEvent": {"func": self.SyncClientOnlySettingEvent}
        })
        self.Register()

    def SyncClientOnlySettingEvent(self, args):
        player_id = args["__id__"]
        self.ClientTemplateSettingMap[player_id] = args["ClientTemplateSetting"]

    def PlayerSaveSettingEvent(self, args):
        player_id = args["__id__"]
        settings = [
            "TemplateSetting"
        ]
        for setting in settings:
            if setting in args:
                setattr(self, setting, args[setting])
        self.TriggerBurstByClickMap[player_id] = args.get("TriggerBurstByClick", False)
        self.SaveCurrentSetting()

    def ClientLoadAddonsFinishServerEvent(self, args):
        playerId = args["playerId"]
        ModSetting = DataApi.GetExtraDataLevel("%sSetting" % ModName)
        if ModSetting:
            self.load_mob_setting(ModSetting)
        else:
            self.SaveCurrentSetting()
        ServerMain.NotifyToClient(playerId, "ServerLoadSettingFinishedEvent", {})
        ServerMain.NotifyToClient(playerId, "SyncOperationEvent", {"is_op": CompFactory.CreatePlayer(playerId).GetPlayerOperation()})

    def load_mob_setting(self, ModSetting):
        self.TemplateSetting = ModSetting.setdefault("TemplateSetting", True)
        ServerMain.BroadcastToAllClient("SyncSettingEvent", ModSetting)

    def OnScriptTickServer(self):
        if GlobalTickCount() % 30 == 0:
            for player_id in GameApi.GetAllPlayerList():
                ServerMain.NotifyToClient(player_id, "SyncOperationEvent", {"is_op": AttributeApi.GetPlayerOperation(player_id)})

    def SaveCurrentSetting(self):
        ModSetting = {
            "TemplateSetting": self.TemplateSetting
        }
        DataApi.SetExtraDataLevel("%sSetting" % ModName, ModSetting)
        ServerMain.BroadcastToAllClient("SyncSettingEvent", ModSetting)
