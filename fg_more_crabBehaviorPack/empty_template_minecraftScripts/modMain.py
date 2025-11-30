# -*- coding: utf-8 -*-

from ModBaseApi import *

ClientMainInstance = None
ServerMainInstance = None


@Mod.Binding(name=ModName, version=ModVersion)
class ModMain(object):

    def __init__(self):
        print("modMain初始化")

    @Mod.InitServer()
    def ServerInit(self):
        print("modMain服务端初始化")
        ServerApi.RegisterSystem(ModName, ServerSystemName, ServerSystemClsPath)

    @Mod.DestroyServer()
    def ServerDestroy(self):
        print("modMain服务端摧毁")

    @Mod.InitClient()
    def ClientInit(self):
        print("modMain客户端初始化")
        # 注册一个自定义的客户端Component
        ClientApi.RegisterSystem(ModName, ClientSystemName, ClientSystemClsPath)

    @Mod.DestroyClient()
    def ClientDestroy(self):
        print("modMain客户端摧毁")


class ServerMain(ServerSystem):
    def __init__(self, namespace, systemName):
        super(ServerMain, self).__init__(namespace, systemName)
        # 提前为ServerMainInstance赋值
        SetServerMain(self)
        self._global_tick_count = 0
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 10)
        # import
        from server.src.ServerMobInstancesController import ServerMobInstancesController
        from server.src.ServerCameraController import ServerCameraController
        from server.src.ServerBeforeDamageController import ServerBeforeDamageController
        from server.src.ServerAfterDamageController import ServerAfterDamageController
        from server.src.ServerMusic import ServerMusic
        from server.src.ServerSetting import ServerSetting
        from server.src.ServerEmptyUnLock import ServerEmptyUnLock
        self.ServerMobInstancesController = ServerMobInstancesController()
        self.ServerCameraController = ServerCameraController()
        self.ServerBeforeDamageController = ServerBeforeDamageController()
        self.ServerAfterDamageController = ServerAfterDamageController()
        self.ServerMusic = ServerMusic()
        self.ServerSetting = ServerSetting()
        self.ServerEmptyUnLock = ServerEmptyUnLock()

    def GlobalTickCount(self):
        return self._global_tick_count

    def OnScriptTickServer(self):
        self._global_tick_count += 1

    def Destroy(self):
        # UnRegister
        self.ServerMobInstancesController.UnRegister()
        self.ServerCameraController.UnRegister()
        self.ServerBeforeDamageController.UnRegister()
        self.ServerAfterDamageController.UnRegister()
        self.ServerMusic.UnRegister()
        self.ServerSetting.UnRegister()
        self.ServerEmptyUnLock.UnRegister()


class ClientMain(ClientSystem):
    def __init__(self, namespace, systemName):
        super(ClientMain, self).__init__(namespace, systemName)
        # ClientMainInstance
        SetClientMain(self)
        self._global_tick_count = 0
        self.ListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "OnScriptTickClient", self, self.OnScriptTickClient, 10)
        # import
        from client.src.ClientMobInstancesController import ClientMobInstancesController
        from client.src.ClientCameraController import ClientCameraController
        from client.src.ClientParticleController import ClientParticleController
        from client.src.ClientEmptyUnLock import ClientEmptyUnLock
        from client.src.ClientMusic import ClientMusic
        from client.src.ClientSetting import ClientSetting
        from client.ui.base_class.UIManager import UIManager
        self.ClientCameraController = ClientCameraController()
        self.ClientMobInstancesController = ClientMobInstancesController()
        self.ClientParticleController = ClientParticleController()
        self.ClientEmptyUnLock = ClientEmptyUnLock()
        self.ClientMusic = ClientMusic()
        self.ClientSetting = ClientSetting()
        self.UIManager = UIManager()

    def GlobalTickCount(self):
        return self._global_tick_count

    def OnScriptTickClient(self):
        self._global_tick_count += 1

    def Destroy(self):
        # UnRegister
        self.ClientCameraController.UnRegister()
        self.ClientMobInstancesController.UnRegister()
        self.ClientParticleController.UnRegister()
        self.ClientEmptyUnLock.UnRegister()
        self.ClientMusic.UnRegister()
        self.ClientSetting.UnRegister()


def SetClientMain(class_instance):
    global ClientMainInstance
    ClientMainInstance = class_instance


def GetClientMain():
    """
    GetClientMain
    :rtype: ClientMain
    """
    return ClientMainInstance


def SetServerMain(class_instance):
    global ServerMainInstance
    ServerMainInstance = class_instance


def GetServerMain():
    """
    GetServerMain
    :rtype: ServerMain
    """
    return ServerMainInstance
