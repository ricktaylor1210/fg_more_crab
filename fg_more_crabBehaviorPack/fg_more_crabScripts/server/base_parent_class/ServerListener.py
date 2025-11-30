# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api.EmptyBaseServerApi import *


class ServerListener(object):
    def __init__(self, need_tick_event=False):
        self.TickCount = 0
        self.engine_events = {
            # engineEventName : {func,priority}
        }
        if need_tick_event:
            self.engine_events = {
                # engineEventName : {func,priority}
                # 服务端tick事件,1秒30次
                "OnScriptTickServer": {"func": self.OnScriptTickServer}
            }
        self.custom_events = {
            # customEventName : {mod_name,listen_system_name,func,priority}
        }
        self.register_finished_events = {}
        self.Register()

    def OnScriptTickServer(self):
        self.Update()

    def Update(self):
        self.TickCount += 1

    def save_listen_event(self, mod_name, listen_system_name, event_name, listen_class, func, priority):
        self.register_finished_events[event_name] = {
            "func": func,
            "priority": priority,
            "listen_class": listen_class,
            "mod_name": mod_name,
            "listen_system_name": listen_system_name,
        }

    def RegisterEvent(self, mod_name, listen_system_name, event_name, listen_class, func, priority=0):
        if mod_name in self.register_finished_events:
            return
        ServerMain.ListenForEvent(mod_name, listen_system_name, event_name, listen_class, func, priority)
        self.save_listen_event(mod_name, listen_system_name, event_name, listen_class, func, priority)
        if DEVELOPMENT:
            print("监听 {}:{}:{}:{}:{}:{}".format(mod_name, listen_system_name, event_name, listen_class, func, priority))

    def Register(self):
        for event_name, event_value in self.engine_events.iteritems():
            func, priority = event_value["func"], event_value.get("priority", 0)
            self.RegisterEvent(ServerEngineNameSpace, ServerEngineSystemName, event_name, self, func, priority)
        for event_name, event_value in self.custom_events.iteritems():
            mod_name, listen_system_name = event_value.get("mod_name", ModName), event_value.get("listen_system_name", ClientSystemName)
            func, priority = event_value["func"], event_value.get("priority", 0)
            self.RegisterEvent(mod_name, listen_system_name, event_name, self, func, priority)
        if DEVELOPMENT:
            print("%s 注册监听器完成" % self.__class__.__name__)

    def UnRegister(self):
        for event_name, event_value in self.register_finished_events.iteritems():
            mod_name, listen_system_name = event_value.get("mod_name", ModName), event_value.get("listen_system_name", ClientSystemName)
            listen_class, func, priority = event_value.get("listen_class", self), event_value["func"], event_value.get("priority", 0)
            ServerMain.UnListenForEvent(mod_name, listen_system_name, event_name, listen_class, func, priority)
            if DEVELOPMENT:
                print("反监听 {}:{}:{}:{}:{}:{}".format(mod_name, listen_system_name, event_name, listen_class, func, priority))
        self.register_finished_events = {}
        if DEVELOPMENT:
            print("%s 反注册监听器完成" % self.__class__.__name__)
