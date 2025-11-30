# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.base_parent_class.ClientListener import *
from fg_more_crabScripts.client.api import EmptyGameClientApi as GameApi


class ClientMusic(ClientListener):
    def __init__(self):
        super(ClientMusic, self).__init__()
        self.delay_timer = None
        self.sound_id_dict = {}
        self.engine_events.update({
            # engineEventName : {func,priority}
            "OnMusicStopClientEvent": {"func": self.OnMusicStopClientEvent}
        })
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            "SyncPlaySoundEvent": {"func": self.SyncPlaySoundEvent},
            "SyncStopSoundEvent": {"func": self.SyncStopSoundEvent}
        })
        self.Register()

    def OnMusicStopClientEvent(self, args):
        # 音乐停止时，当玩家调用StopCustomMusic来停止自定义背景音乐时，会触发该事件
        # musicName	str	音乐名称
        musicName = args["musicName"]
        self.sound_id_dict.pop(musicName, None)

    def PlaySound(self, music_name, only=False, delay=False, delay_time=0.1, pos=(0, 1, 0), volume=1, pitch=1, loop=False, entityId=LocalPlayerId,
                  is_sync=False):
        if loop and music_name in self.sound_id_dict:
            return

        if self.delay_timer:
            GameApi.CancelTimer(self.delay_timer)
            self.delay_timer = None

        if delay:
            self.delay_timer = GameApi.AddTimer(delay_time, self.PlaySound, music_name, only, False, 0.1, pos, volume, pitch, loop, entityId)
            return

        if only:
            for music_id in self.sound_id_dict.values():
                CompSound.StopCustomMusicById(music_id)
            self.sound_id_dict.clear()

        if not is_sync:
            ClientMain.NotifyToServer("SyncPlaySoundEvent", {
                "music_name": music_name, "only": only, "pos": pos, "volume": volume, "pitch": pitch, "loop": loop, "entityId": entityId
            })

        sound_id = CompSound.PlayCustomMusic(music_name, pos, volume, pitch, loop, entityId)
        if sound_id not in ["-1", "-2", "-3", "-4", "-5", "-6"]:
            self.sound_id_dict[music_name] = sound_id

    def StopSound(self, music_name):
        sound_id = self.sound_id_dict.pop(music_name, None)
        if sound_id:
            CompSound.StopCustomMusicById(sound_id)

    def SyncPlaySoundEvent(self, args):
        self.PlaySound(
            music_name=args["music_name"],
            only=args["only"],
            pos=args["pos"],
            volume=args["volume"],
            pitch=args["pitch"],
            loop=args["loop"],
            entityId=args["entityId"],
            is_sync=True
        )

    def SyncStopSoundEvent(self, args):
        self.StopSound(args["music_name"])
