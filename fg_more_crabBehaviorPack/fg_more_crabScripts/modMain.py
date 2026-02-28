# -*- coding: utf-8 -*-

from ModMainConfig import *
from mod.common.mod import Mod

import mod.client.extraClientApi as ClientApi
import mod.server.extraServerApi as ServerApi


@Mod.Binding(name=ModName, version=MOD_VERSION)
class ModMain(object):

    def __init__(self):
        SetDevelopmentMessage(logging.INFO, "%s初始化", ModName)
        self.ServerMainSystem = None
        self.ClientMainSystem = None

    @Mod.InitServer()
    def ServerInit(self):
        print "%s 服务端初始化" % ModName

        self.ServerMainSystem = ServerApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

        print "%s 服务端初始化完成" % ModName

    @Mod.DestroyServer()
    def ServerDestroy(self):
        print "%s 服务端开始摧毁" % ModName

        self.ServerMainSystem.DestroySystem()

        print "%s 服务端摧毁完成" % ModName


    @Mod.InitClient()
    def ClientInit(self):
        print "%s 客户端开始初始化" % ModName

        self.ClientMainSystem = ClientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

        print "%s 客户端初始化完成" % ModName

    @Mod.DestroyClient()
    def ClientDestroy(self):
        print "%s 客户端开始摧毁" % ModName

        self.ClientMainSystem.DestroySystem()

        print "%s 客户端摧毁完成" % ModName
