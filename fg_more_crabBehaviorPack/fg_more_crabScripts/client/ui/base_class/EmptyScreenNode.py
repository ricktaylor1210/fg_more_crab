# -*- coding: utf-8 -*-

from fg_more_crabScripts.client.api.EmptyBaseClientApi import *
from fg_more_crabScripts.config import KeyBoartMap


class EmptyScreenNode(ScreenNode):
    def __init__(self, namespace, name, param):
        super(EmptyScreenNode, self).__init__(namespace, name, param)
        self.TickCount = 0
        self.ScreenIsOpen = False
        self.in_move_button = False

        self.engine_events = {
            # engineEventName : {func,priority}
        }
        self.custom_events = {
            # customEventName : {mod_name,listen_system_name,func,priority}
        }
        self.lock_button_list = []
        self.register_finished_events = {}
        self.can_bind_button_path_list = []
        self.button_bind_key_map = {}
        self.key_bind_button_map = {}

        self.button_path_callback_map = {}
        self.engine_events.update(
            {
                # engineEventName : {func,priority}
                "OnKeyPressInGame": {"func": self.OnKeyPressInGame}
            }
        )
        self.Register()

    def Create(self):
        """
        当 UI 被创建后，会调用这个方法
        """
        self.Register()

    def Update(self):
        self.TickCount += 1

    def Destroy(self):
        self.UnRegister()

    def OpenScreen(self, *args, **kwargs):
        self.ScreenIsOpen = True
        only = kwargs.get("only", True)
        exclude_screen = kwargs.get("exclude_screen", False)
        return ClientMain.UIManager.OpenScreen(self, only, exclude_screen)

    def CloseScreen(self, *args, **kwargs):
        self.ScreenIsOpen = False
        return ClientMain.UIManager.CloseScreen(self)

    def GetScrollViewContentPath(self, scroll_view_path):
        """
        获取ScrollViewContentPath
        :param scroll_view_path scroll_view_path
        :type scroll_view_path str
        :return ScrollViewContentPath
        :rtype str
        """
        return self.GetBaseUIControl(scroll_view_path).asScrollView().GetScrollViewContentPath()

    def SetPanelVisible(self, panel_path, visible):
        """
        设置panel是否显示
        :param panel_path panel_path
        :param visible 是否显示
        """
        self.GetBaseUIControl(panel_path).SetVisible(visible)

    def SetSpriteClipRatio(self, image_path, progress):
        """
        设置图片
        :param image_path image_path
        :type image_path str
        :param progress 裁剪比例
        :type progress int or float
        """
        self.GetBaseUIControl(image_path).asImage().SetSpriteClipRatio(progress)

    def SetImageSprite(self, image_path, texture_path):
        """
        设置图片
        :param image_path image_path
        :param texture_path 图片路径
        """
        self.GetBaseUIControl(image_path).asImage().SetSprite(texture_path)

    def SetImageToGray(self, image_path, gray):
        """
        设置图片是否置灰
        :param image_path image_path
        :param gray 是否置灰 True为将图片置灰，False为恢复原色
        """
        self.GetBaseUIControl(image_path).SetSpriteGray(gray)

    def SetButtonTexturesToGary(self, button_path, gray):
        """
        设置按钮是否置灰
        :param button_path button_path
        :param gray 是否置灰 True为将图片置灰，False为恢复原色
        """
        for child_path in ["default", "hover", "pressed"]:
            self.GetBaseUIControl(button_path).GetChildByName(child_path).asImage().SetSpriteGray(gray)

    def SetButtonTexturesToSamePng(self, button_path, texture_path):
        """
        设置按钮图片为传入图片路径
        :param button_path button_path
        :param texture_path 传入图片路径
        """
        for child_path in ["default", "hover", "pressed"]:
            self.GetBaseUIControl(button_path).GetChildByName(child_path).asImage().SetSprite(texture_path)

    def ChangeButtonLabel(self, button_path, label):
        """
        改变按钮文字为传入文本
        :param button_path button_path
        :param label 传入图片路径
        """
        self.GetBaseUIControl(button_path).GetChildByName("button_label").asLabel().SetText(label)

    def GetButtonLabel(self, button_path):
        """
        获取按钮文字
        :param button_path button_path
        """
        return self.GetBaseUIControl(button_path).GetChildByName("button_label").asLabel().GetText()

    def SetLabelNumberDiff(self, label_path, diff, absolute=False, need_int=False, need_max=False, max_count=65535, need_min=False,
                           min_count=-65535):
        """
        修改或设置label上的number

        :param label_path: label_path
        :type label_path: str
        :param diff: diff number
        :type diff: int or float
        :param absolute: 是否绝对值
        :type absolute: bool
        :param need_int: 需要int
        :type need_int: bool
        :param need_max: 需要限制最大值
        :type need_max: bool
        :param max_count: 最大值
        :type max_count: int or float
        :param need_min: 需要限制最小值
        :type need_min: bool
        :param min_count: 最小值
        :type min_count: int or float
        :return: new_number
        :rtype: int or float
        """
        if absolute:
            new_number = diff
        else:
            new_number = self.get_label_number(label_path) + diff
        if need_int:
            new_number = int(new_number)
        if need_max:
            new_number = min(new_number, max_count)
        if need_min:
            new_number = max(new_number, min_count)
        self.GetBaseUIControl(label_path).asLabel().SetText(str(new_number))
        return new_number

    def get_label_number(self, label_path):
        return float(self.GetBaseUIControl(label_path).asLabel().GetText())

    def GetLabelNumber(self, label_path, need_int=False):
        """
        获取label的number，返回为数字格式

        :param label_path: label_path
        :type label_path: str
        :param need_int: 是否需要int
        :type need_int: bool
        :return: number
        :rtype: int or float
        """
        return int(self.GetBaseUIControl(label_path).asLabel().GetText()) if need_int else float(
            self.GetBaseUIControl(label_path).asLabel().GetText())

    def get_button_active(self, button_path):
        """
        获取按钮是否可用
        :param button_path button_path
        :type button_path str
        """
        return button_path not in self.lock_button_list

    def set_button_active(self, button_path, active):
        """
        设置按钮是否可用
        :param button_path button_path
        :type button_path str
        :param active 是否可用
        :type active bool
        """
        # 检测当前状态是否已经符合期望，如果是，则直接返回
        current_active = button_path not in self.lock_button_list
        if current_active == active:
            return

        # 更新按钮状态
        if active:
            self.lock_button_list.remove(button_path) if button_path in self.lock_button_list else None
        else:
            if button_path not in self.lock_button_list:
                self.lock_button_list.append(button_path)

        # 根据按钮状态设置置灰状态
        gray = not active
        self.SetButtonTexturesToGary(button_path, gray)

    def register_base_button(self, path, TouchUpCallBack, isSwallow=True):
        def button_call_back(args):
            if path in self.lock_button_list and not self.in_move_button:
                return
            if args.get("TouchEvent", 0) == 0:
                TouchUpCallBack(args)

        button_controller = self.GetBaseUIControl(path).asButton()
        # isSwallow     bool	默认为True, 按钮是否吞噬事件；或为Ture时，点击按钮时，点击事件不会穿透到世界。如破坏方块、镜头转向不会被响应
        button_controller.AddTouchEventParams({"isSwallow": isSwallow})
        button_controller.SetButtonTouchUpCallback(button_call_back)
        self.button_path_callback_map[path] = {"callback_func": button_call_back, "bind_args": {"isSwallow": isSwallow}}
        return button_controller

    def OnKeyPressInGame(self, args):
        # screenName	str	当前screenName
        # key	str	键码（注：这里的int型被转成了str型，比如"1"对应的就是枚举值文档中的1），详见KeyBoardType枚举
        # isDown	str	是否按下，按下为1，弹起为0
        if self.ScreenIsOpen:
            if args["key"] in KeyBoartMap.MinecraftUsedKeyList:
                return
            key = args["key"]
            key_bind_button_path = self.key_bind_button_map.get(key, None)
            if key_bind_button_path is None:
                return
            button_bind_callback = self.button_path_callback_map.get(key_bind_button_path, None)
            if button_bind_callback is None:
                return
            button_callback_func = self.button_path_callback_map[key_bind_button_path].get("callback_func", None)
            button_bind_args = self.button_path_callback_map[key_bind_button_path].get("bind_args", None)
            if button_bind_callback is None or button_bind_args is None:
                return
            isDown = args["isDown"]
            if isDown == "1":
                button_callback_func(
                    {"ButtonState": 1, "TouchEvent": 1, "PrevButtonDownID": "-1", "ButtonPath": key_bind_button_path, "AddTouchEventParams": button_bind_args})
            else:
                button_callback_func(
                    {"ButtonState": 0, "TouchEvent": 0, "PrevButtonDownID": "-1", "ButtonPath": key_bind_button_path, "AddTouchEventParams": button_bind_args})

    def set_button_bind_key(self, path, key):
        if key in KeyBoartMap.MinecraftUsedKeyList:
            return
        if path not in self.can_bind_button_path_list:
            return
        for old_key, old_path in self.key_bind_button_map.iteritems():
            if old_path == path:
                self.key_bind_button_map.pop(old_key)
        for old_path, old_key in self.button_bind_key_map.iteritems():
            if old_key == key:
                self.remove_button_bind_key_label(old_path)
                self.button_bind_key_map.pop(old_path)
        if key in self.key_bind_button_map:
            self.key_bind_button_map.pop(key)
        if path in self.key_bind_button_map:
            self.button_bind_key_map.pop(path)
        self.button_bind_key_map[path] = key
        self.key_bind_button_map[key] = path
        self.set_button_bind_key_label(path, key)
        self.set_current_button_bind_key_to_local()

    def get_current_button_bind_key(self, path):
        return ConfigClient.GetConfigData("empty_button_bind_key_map" + self.__class__.__name__  + ModName + ConfigVersion, True).get(path, None)

    def set_current_button_bind_key_to_local(self):
        ConfigClient.SetConfigData("empty_button_bind_key_map" + self.__class__.__name__  + ModName + ConfigVersion, self.button_bind_key_map, True)

    def set_button_bind_key_by_current_local(self, path):
        if path not in self.can_bind_button_path_list:
            self.can_bind_button_path_list.append(path)
        local_bind_key = self.get_current_button_bind_key(path)
        if local_bind_key:
            self.set_button_bind_key_label(path, local_bind_key)
            self.button_bind_key_map[path] = local_bind_key
            self.key_bind_button_map[local_bind_key] = path

    def set_button_bind_key_label(self, path, key):
        if "/key_bind_label" not in path:
            path += "/key_bind_label"
        try:
            if PlatForm in [1, 2]:
                self.GetBaseUIControl(path).asLabel().SetText("")
                return

            if key in KeyBoartMap.KeyIntTypeToStringMap:
                self.GetBaseUIControl(path).asLabel().SetText(KeyBoartMap.KeyIntTypeToStringMap[key])
            else:
                self.GetBaseUIControl(path).asLabel().SetText("error")
        except Exception:
            print "[custom get error],error is ->", traceback.format_exc()

    def remove_button_bind_key(self, path):
        current_bind_key = self.button_bind_key_map.get(path, None)
        if current_bind_key:
            self.button_bind_key_map.pop(path)
            self.key_bind_button_map.pop(current_bind_key)
            self.remove_button_bind_key_label(path)
            self.set_current_button_bind_key_to_local()

    def remove_button_bind_key_label(self, path):
        if "/key_bind_label" not in path:
            path += "/key_bind_label"
        try:
            self.GetBaseUIControl(path).asLabel().SetText("")
        except Exception:
            print "[custom get error],error is ->", traceback.format_exc()

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
        ClientMain.ListenForEvent(mod_name, listen_system_name, event_name, listen_class, func, priority)
        self.save_listen_event(mod_name, listen_system_name, event_name, listen_class, func, priority)
        if DEVELOPMENT:
            print("监听 {}:{}:{}:{}:{}:{}".format(mod_name, listen_system_name, event_name, listen_class, func, priority))

    def Register(self):
        for event_name, event_value in self.engine_events.iteritems():
            func, priority = event_value["func"], event_value.get("priority", 0)
            self.RegisterEvent(ClientEngineNamespace, ClientEngineSystemName, event_name, self, func, priority)
        for event_name, event_value in self.custom_events.iteritems():
            mod_name, listen_system_name = event_value.get("mod_name", ModName), event_value.get("listen_system_name", ServerSystemName)
            func, priority = event_value["func"], event_value.get("priority", 0)
            self.RegisterEvent(mod_name, listen_system_name, event_name, self, func, priority)
        print("%s 注册监听器完成" % self.__class__.__name__)

    def UnRegister(self):
        for event_name, event_value in self.register_finished_events.iteritems():
            mod_name, listen_system_name = event_value.get("mod_name", ModName), event_value.get("listen_system_name", ServerSystemName)
            listen_class, func, priority = event_value.get("listen_class", self), event_value["func"], event_value.get("priority", 0)
            ClientMain.UnListenForEvent(mod_name, listen_system_name, event_name, listen_class, func, priority)
            if DEVELOPMENT:
                print("反监听 {}:{}:{}:{}:{}:{}".format(mod_name, listen_system_name, event_name, listen_class, func, priority))
        self.register_finished_events = {}
        print("%s 反注册监听器完成" % self.__class__.__name__)