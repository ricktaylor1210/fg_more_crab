# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.base_parent_class.ServerListener import *
from fg_more_crabScripts.server.api import EmptyGameServerApi as GameApi


class ServerMusic(ServerListener):
    def __init__(self):
        super(ServerMusic, self).__init__()
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            "SyncPlaySoundEvent": {"func": self.SyncPlaySoundEvent}
        })
        self.Register()

    def SyncPlaySoundEvent(self, args):
        ServerMain.NotifyToMultiClients(GameApi.GetRelevantPlayer(args["__id__"]), "SyncPlaySoundEvent", args)

    def PlaySoundToAllClient(self, entity_id, music_name, only=False, pos=(0, 1, 0), volume=1, pitch=1, loop=False):
        ServerMain.BroadcastToAllClient("SyncPlaySoundEvent",
                                        {"music_name": music_name, "only": only, "pos": pos, "volume": volume, "pitch": pitch, "loop": loop,
                                         "entityId": entity_id})

    def StopSoundToAllClient(self, music_name):
        ServerMain.BroadcastToAllClient("SyncStopSoundEvent", {"music_name": music_name})
