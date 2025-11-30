# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyGameServerApi, EmptyAttributeServerApi
from fg_more_crabScripts.server.base_parent_class.ServerListener import *


class ServerEntity(ServerListener):
    def __init__(self, entity_id, itemName=None, auxValue=None):
        self.EntityId = entity_id

        self.itemName = itemName
        self.auxValue = auxValue
        self.IsItem = bool(self.itemName)

        self.EntityTypeStr = EmptyAttributeServerApi.GetEngineTypeStr(self.EntityId)
        self.LoadPosition = EmptyAttributeServerApi.GetEntityFootPos(self.EntityId)
        print ("------------------------------------")
        print self.EntityId, self.EntityTypeStr
        super(ServerEntity, self).__init__(False)

    def UnRegister(self):
        print ("==================================================")
        print self.EntityId, self.EntityTypeStr
        super(ServerEntity, self).UnRegister()

    def Update(self):
        pass
