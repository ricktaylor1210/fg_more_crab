# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.base_parent_class.ServerListener import *
from fg_more_crabScripts.server.api import EmptyDataServerApi as DataApi


class ServerEmptyUnLock(ServerListener):
    def __init__(self):
        super(ServerEmptyUnLock, self).__init__(True)
        self.check_unlock_time = time.time() + 1800
        self.check_finished = False
        self.engine_events.update({
            # engineEventName : {func,priority}
            # 玩家发送聊天信息时触发
            "ServerChatEvent": {"func": self.ServerChatEvent}
        })
        self.Register()

    def GetEmptyStudioUnLockState(self):
        return DataApi.GetExtraDataLevel("empty_unlock")

    def ServerChatEvent(self, args):
        # username	str	玩家名称
        # playerId	str	玩家id
        # message	str	玩家发送的聊天消息内容
        # cancel	bool	是否取消这个聊天事件，若取消可以设置为True
        # bChatById	bool	是否把聊天消息发送给指定在线玩家，而不是广播给所有在线玩家，若只发送某些玩家可以设置为True
        # bForbid	bool	是否禁言，仅apollo可用。true：被禁言，玩家聊天会提示“你已被管理员禁言”。
        # toPlayerIds	list(str)	接收聊天消息的玩家id列表，bChatById为True时生效
        message = args["message"]
        if str.lower(message) == "emptystudio" and time.time() >= CanUnlockTime:
            self.unlock_empty_studio_query()

    def OnScriptTickServer(self):
        if GlobalTickCount() % 30 == 0:
            if not self.check_finished and time.time() >= self.check_unlock_time:
                self.check_finished = True
                self.time_down_unlock()
                ServerMain.UnListenForEvent(ModName, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 0)

    def unlock_empty_studio_query(self):
        ServerMain.BroadcastToAllClient("SetEmptyStudioUnLockStateToUnLockEvent", {})

    def time_down_unlock(self):
        ServerMain.BroadcastToAllClient("SetTimeDownUnLockStateToUnLockEvent", {})
