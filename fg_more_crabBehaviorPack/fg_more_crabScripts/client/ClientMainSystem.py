# -*- coding: utf-8 -*-
from ClientBaseUtils import *


# ClientMainSystem.py
class ClientMainSystem(ClientSystem):
    def __init__(self, namespace, system_name):
        super(ClientMainSystem, self).__init__(namespace, system_name)
        SetClientMainSystem(self)
        self._global_tick_count = 0
        self._ui_init_finished = False

        self.ListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "UnLoadClientAddonScriptsBefore", self, self.UnLoadClientAddonScriptsBefore, 10)
        self.ListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "UiInitFinished", self, self.UiInitFinishedEvent, 10)
        self.ListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "OnScriptTickClient", self, self.OnScriptTickClient, 10)

        SetDevelopmentMessage(logging.INFO, "%s ClientMainSystem Load Finished", ModName)

    def UnLoadClientAddonScriptsBefore(self,args):
        self.DestroySystem()

    def Destroy(self):
        self.DestroySystem()

    def DestroySystem(self):
        self.UnListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "OnScriptTickClient", self, self.OnScriptTickClient, 10)
        self.UnListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "UiInitFinished", self, self.UiInitFinishedEvent, 10)
        self.UnListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "UnLoadClientAddonScriptsBefore", self, self.UnLoadClientAddonScriptsBefore, 10)
        SetDevelopmentMessage(logging.INFO, "%s ClientMainSystem Destroyed", ModName)

    @property
    def GlobalTickCount(self):
        return self._global_tick_count

    @property
    def UIInitFinished(self):
        return self._ui_init_finished

    def UiInitFinishedEvent(self, *args, **kwargs):
        self._ui_init_finished = True
        GetClientMainSystem().NotifyToServer("ClientUILoadFinishedEvent", {})

    def OnScriptTickClient(self):
        self._global_tick_count += 1
        if not GetClientMainSystem():
            SetClientMainSystem(self)
