# -*- coding: utf-8 -*-
from ModMainConfig import *
from mod.common.mod import Mod

import mod.server.extraServerApi as ServerApi


@Mod.Binding(name=ModName, version=MOD_VERSION)
class ModMain(object):
    def __init__(self):
        self.ServerMainSystem = None
        SetDevelopmentMessage(logging.INFO, "%s init", ModName)

    @Mod.InitServer()
    def ServerInit(self):
        self.ServerMainSystem = ServerApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

    @Mod.DestroyServer()
    def ServerDestroy(self):
        server_main_system = self.ServerMainSystem
        if not server_main_system:
            return
        self.ServerMainSystem = None
        server_main_system.DestroySystem()
