# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.base_parent_class.ClientListener import *
from fg_more_crabScripts.client.api import EmptyDataClientApi


class ClientSetting(ClientListener):
    def __init__(self):
        super(ClientSetting, self).__init__()
        self.TemplateSetting = False
        self.ClientTemplateSetting = self.get_client_key_value("ClientTemplateSetting", False)
        self.Operation = True
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            # syncOperationEvent
            "SyncOperationEvent": {"func": self.SyncOperationEvent},
            # SyncSettingEvent
            "SyncSettingEvent": {"func": self.SyncSettingEvent},
            # ServerLoadSettingFinishedEvent
            "ServerLoadSettingFinishedEvent": {"func": self.ServerLoadSettingFinishedEvent}
        })
        self.Register()

    def get_client_key_value(self, key, default):
        return EmptyDataClientApi.GetClientKeyValue(key, default)

    def SyncOperationEvent(self, args):
        self.Operation = args["is_op"] in [2, 3]

    def SyncSettingEvent(self, args):
        settings = [
            "TemplateSetting"
        ]
        for setting in settings:
            if setting in args:
                setattr(self, setting, args[setting])

    def ServerLoadSettingFinishedEvent(self, args):
        client_only_settings = {
            "ClientTemplateSetting": self.ClientTemplateSetting
        }
        ClientMain.NotifyToServer("SyncClientOnlySettingEvent", client_only_settings)
