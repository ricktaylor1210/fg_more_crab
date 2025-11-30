# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.base_parent_class.ClientListener import *

from fg_more_crabScripts.client.api import EmptyDataClientApi as DataApi

from fg_more_crabScripts.client.api import EmptyQueryClientApi as QueryApi


class ClientEmptyUnLock(ClientListener):
    def __init__(self):
        super(ClientEmptyUnLock, self).__init__()
        self.engine_events.update({
            # engineEventName : {func,priority}
            # 玩家进入当前玩家所在的区块AOI后，玩家皮肤数据异步加载完成后触发的事件
            # 由于玩家皮肤是异步加载的原因，该事件触发时机比AddPlayerAOIClientEvent晚，触发该事件后可以对该玩家调用相关玩家渲染接口。
            # 当前客户端每加载好一个玩家的皮肤，就会触发一次该事件，比如刚进入世界时，localPlayer加载好会触发一次，周围的所有玩家加载好后也会分别触发一次。
            "AddPlayerCreatedClientEvent": {"func": self.AddPlayerCreatedClientEvent},
        })
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            "SetEmptyStudioUnLockStateToUnLockEvent": {"func": self.SetEmptyStudioUnLockStateToUnLock}
        })
        self.Register()

    def AddPlayerCreatedClientEvent(self, args):
        # playerId	str	玩家id
        playerId = args["playerId"]
        if self.GetEmptyStudioUnLockState():
            QueryApi.SetEntityQueryAndNotifyToServer(playerId, "empty_unlock", 1)

    def CheckCurrentTimeCanUnlock(self):
        return time.time() >= CanUnlockTime

    def GetEmptyStudioUnLockState(self):
        if self.CheckCurrentTimeCanUnlock():
            return DataApi.GetClientKeyValue("empty_studio", {}, "empty_studio").get("empty_unlock", False)
        return False

    def SetEmptyStudioUnLockStateToUnLock(self, *args):
        current_empty_studio_data = DataApi.GetClientKeyValue("empty_studio", {}, "empty_studio")
        current_empty_studio_data["empty_unlock"] = True
        DataApi.SetClientKeyValue("empty_studio", current_empty_studio_data, "empty_studio")
        QueryApi.SetLocalPlayerQueryAndNotifyToServer("empty_unlock", 1)

    def SetTimeDownUnLockStateToUnLockEvent(self, *args):
        if self.CheckCurrentTimeCanUnlock():
            current_empty_studio_data = DataApi.GetClientKeyValue("empty_studio", {}, "empty_studio")
            current_empty_studio_data["empty_unlock"] = True
            DataApi.SetClientKeyValue("empty_studio", current_empty_studio_data, "empty_studio")
            QueryApi.SetLocalPlayerQueryAndNotifyToServer("empty_unlock", 1)
