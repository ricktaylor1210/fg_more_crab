# -*- coding: utf-8 -*-
from ..ClientBaseUtils import *


class ClientListener(object):
    def __init__(self,  need_tick_event=False):
        """
        :param need_tick_event: need_auto_listen_tick_event
        :type need_tick_event: bool
        """
        self.TickCount = 0
        self.engine_events = {
            # engineEventName : {func,priority}
        }
        if need_tick_event:
            # 客户端 tick 事件，每秒 30 次
            self.engine_events["OnScriptTickClient"] = {"func": self.OnScriptTickClient}

        self.custom_events = {
            # customEventName : {mod_name,listen_system_name,func,priority}

        }
        self.register_finished_events = {}

        self.Register()

    def OnScriptTickClient(self):
        self.Update()

    def Update(self):
        self.TickCount += 1

    def _save_listen_event(self, mod_name, listen_system_name, event_name, listen_class, func, priority):
        self.register_finished_events[event_name] = {
            "func": func,
            "priority": priority,
            "listen_class": listen_class,
            "mod_name": mod_name,
            "listen_system_name": listen_system_name,
        }

    def RegisterEvent(self, mod_name, listen_system_name, event_name, listen_class, func, priority=0):
        if mod_name in self.register_finished_events:
            self.UnRegisterEvent(event_name)

        GetClientMainSystem().ListenForEvent(mod_name, listen_system_name, event_name, listen_class, func, priority)
        self._save_listen_event(mod_name, listen_system_name, event_name, listen_class, func, priority)

        SetDevelopmentMessage(logging.INFO, "监听 {}:{}:{}:{}:{}:{}", mod_name, listen_system_name, event_name, listen_class, func, priority)

    def UnRegisterEvent(self, event_name):
        if event_name in self.register_finished_events:
            event_value = self.register_finished_events[event_name]
            mod_name = event_value.get("mod_name", ModName)
            listen_system_name = event_value.get("listen_system_name", ServerSystemName)
            listen_class = event_value.get("listen_class", self)
            func = event_value["func"]
            priority = event_value.get("priority", 0)

            GetClientMainSystem().UnListenForEvent(mod_name, listen_system_name, event_name, listen_class, func, priority)

            SetDevelopmentMessage(logging.INFO, "反监听 {}:{}:{}:{}:{}:{}", mod_name, listen_system_name, event_name, listen_class, func, priority)

            del self.register_finished_events[event_name]

    def Register(self):
        for event_name, event_value in self.engine_events.iteritems():
            self.RegisterEvent(ClientEngineNamespace, ClientEngineSystemName, event_name, self, event_value["func"], event_value.get("priority", 0))

        for event_name, event_value in self.custom_events.iteritems():
            mod_name = event_value.get("mod_name", ModName)
            listen_system_name = event_value.get("listen_system_name", ServerSystemName)
            self.RegisterEvent(mod_name, listen_system_name, event_name, self, event_value["func"], event_value.get("priority", 0))

        SetDevelopmentMessage(logging.INFO, "%s 注册监听器完成", self.__class__.__name__)

    def UnRegister(self):
        for event_name in self.register_finished_events.keys():
            self.UnRegisterEvent(event_name)

        SetDevelopmentMessage(logging.INFO, "%s 反注册监听器完成", self.__class__.__name__)
