# -*- coding: utf-8 -*-
from ServerBaseUtils import *


class ServerMainSystem(ServerSystem):
    def __init__(self, namespace, system_name):
        super(ServerMainSystem, self).__init__(namespace, system_name)
        SetServerMainSystem(self)
        self._global_tick_count = 0
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerIntendLeaveServerEvent", self, self.PlayerIntendLeaveServerEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 10)
        SetDevelopmentMessage(logging.INFO, "%s ServerMainSystem Load Finished", ModName)

    def PlayerIntendLeaveServerEvent(self,args):
        player_id=args["playerId"]
        if player_id==ServerApi.GetHostPlayerId() and not ServerApi.GetPlayerList():
            self.DestroySystem()

    def DestroySystem(self):
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerIntendLeaveServerEvent", self, self.PlayerIntendLeaveServerEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 10)
        SetDevelopmentMessage(logging.INFO, "%s ServerMainSystem Destroyed", ModName)

    @property
    def GlobalTickCount(self):
        return self._global_tick_count

    def OnScriptTickServer(self):
        self._global_tick_count += 1
        if not GetServerMainSystem():
            SetServerMainSystem(self)