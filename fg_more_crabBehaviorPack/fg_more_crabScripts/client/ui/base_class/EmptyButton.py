# coding=utf-8
from fg_more_crabScripts.client.ui.base_class.EmptyScreenNode import *
from fg_more_crabScripts.client.api import EmptyGameClientApi as GameApi


class EmptyButton(EmptyScreenNode):
    def __init__(self, namespace, name, param):
        super(EmptyButton, self).__init__(namespace, name, param)
        self.buttonToFunctionMap = {
            # button_path: {"TouchUpCallBack": function, "isSwallow": False, "is_move_button": True}
        }
        self.screen_size = GameCompLevel.GetScreenSize()
        self.init_screen_size()
        self.register_move_button_list = []
        self.button_down_list = list()
        self.button_down_time_map = {}
        self.button_up_time_map = {}

        self.button_down_touch_pos_dict = {}
        self.button_down_full_pos_dict = {}
        self.button_down_center_diff_pos_dict = {}

        self.button_current_opacity_dict = {}
        self.button_current_size_dict = {}
        self.engine_events.update(
            {
                # engineEventName : {func,priority}
                "StartDestroyBlockClientEvent": {"func": self.CancelTouch},
                "PlayerTryDestroyBlockClientEvent": {"func": self.CancelTouch},
                "ShearsDestoryBlockBeforeClientEvent": {"func": self.CancelShearsTouch},
                "TapBeforeClientEvent": {"func": self.CancelTouch},
                "HoldBeforeClientEvent": {"func": self.CancelTouch},
            }
        )
        self.Register()

    def get_touch_pos_has_button(self):
        if not self.ScreenIsOpen:
            return False
        touch_x, touch_y = ClientApi.GetTouchPos()
        if touch_x == 0.0 or touch_y == 0.0:
            return True
        for button_path in self.register_move_button_list:
            try:
                button_x, button_y = self.GetBaseUIControl(button_path).GetGlobalPosition()
                button_size_x, button_size_y = self.GetBaseUIControl(button_path).GetSize()
                min_x = button_x
                max_x = button_x + button_size_x
                min_y = button_y
                max_y = button_y + button_size_y
                if min_x <= touch_x <= max_x and min_y <= touch_y <= max_y:
                    return True
            except:
                continue
        return False

    def CancelTouch(self, touch_args):
        # print self.button_down_list
        # print self.get_touch_pos_has_button()
        if len(self.button_down_list) > 0 or self.get_touch_pos_has_button():
            touch_args["cancel"] = True

    def CancelShearsTouch(self, touch_args):
        if len(self.button_down_list) > 0 or self.get_touch_pos_has_button():
            touch_args["cancelShears"] = True

    def Create(self):
        """
        当 UI 被创建后, 会调用这个方法
        """
        super(EmptyButton, self).Create()

    def init_screen_size(self):
        if self.screen_size == (0, 0):
            self.screen_size = GameCompLevel.GetScreenSize()
            GameCompLevel.AddTimer(0.1, self.init_screen_size)

    def get_button_touch_time(self, button_path):
        if button_path in self.button_down_time_map and button_path in self.button_up_time_map:
            return self.button_up_time_map[button_path] - self.button_down_time_map[button_path]
        else:
            return None

    def register_button(self, path, **options):

        # 提取参数从options字典

        TouchUpCallBack = options.get("TouchUpCallBack", None)
        TouchCancelCallBack = options.get("TouchCancelCallBack", None)
        TouchDownCallBack = options.get("TouchDownCallBack", None)
        TouchMoveInCallBack = options.get("TouchMoveInCallBack", None)
        TouchMoveCallBack = options.get("TouchMoveCallBack", None)
        TouchMoveOutCallBack = options.get("TouchMoveOutCallBack", None)

        can_bind_key = options.get("can_bind_key", False)
        is_move_button = options.get("is_move_button", False)
        set_parent = options.get("set_parent", False)
        if set_parent:
            path = path.rsplit("/", 1)[0]
        if is_move_button:
            button_class = options.get("button_class", self)
            if ClientMain.UIManager.location_settings:
                ClientMain.UIManager.location_settings.add_move_button_list_with_class_map(button_class, path)

        range_move = options.get("range_move", False)
        range_x = options.get("range_x", 30)
        range_y = options.get("range_y", 30)

        isSwallow = options.get("isSwallow", True)

        if is_move_button:
            TouchUp = TouchCancel = TouchDown = TouchMoveIn = TouchMove = TouchMoveOut = True
        else:
            TouchUp = bool(TouchUpCallBack)
            TouchCancel = bool(TouchCancelCallBack)
            TouchDown = bool(TouchDownCallBack)
            TouchMoveIn = bool(TouchMoveInCallBack)
            TouchMove = bool(TouchMoveCallBack)
            TouchMoveOut = bool(TouchMoveOutCallBack)

        button_controller = self.GetBaseUIControl(path).asButton()
        # isSwallow     bool	默认为True, 按钮是否吞噬事件；或为Ture时, 点击按钮时, 点击事件不会穿透到世界. 如破坏方块、镜头转向不会被响应
        button_controller.AddTouchEventParams({"isSwallow": isSwallow})
        if is_move_button:
            self.register_move_button_list.append(path)
            origin_button_local_full_pos = self.get_origin_button_local_full_pos(path)
            if not origin_button_local_full_pos:
                self.set_origin_button_full_pos_to_local(path)
                self.set_current_button_full_pos_to_local(path)

            self.set_button_full_pos_by_current_local(path)
            self.set_button_opacity_by_current_local(path)
            self.set_button_size_by_current_local(path)
        if can_bind_key:
            self.set_button_bind_key_by_current_local(path)

        def button_callback(args):
            # args
            # #collection_name	str	按钮所属的集合名称
            # #collection_index	int	按钮在集合所属的集合序号
            # ButtonState	int	按钮的状态：Up为0, Down为1, 默认是-1, 建议使用New
            # TouchEvent	int	按钮的状态新版本：Up为0, Down为1, Cancel为3, Move为4, 默认是-1
            # PrevButtonDownID	str	上一个被点击Down的按钮的ID, 如果没有取值为"-1"
            # TouchPosX	float	按钮被点击时屏幕上的UI坐标X值
            # TouchPosY	float	按钮被点击时屏幕上的UI坐标Y值
            # ButtonPath	str	被点击的按钮的ComponentPath
            # AddTouchEventParams	dict	在调用AddTouchEventParams接口时传入的参数字典

            TouchEvent = args["TouchEvent"]
            ButtonPath = args["ButtonPath"]
            if ButtonPath in self.lock_button_list and not self.in_move_button:
                return
            TouchPosX, TouchPosY = args.get("TouchPosX", None), args.get("TouchPosY", None)
            button_control = self.GetBaseUIControl(ButtonPath)
            if TouchPosX is None or TouchPosY is None:
                TouchPosX, TouchPosY = button_control.GetGlobalPosition()
            current_pos_x, current_pos_y = button_control.GetGlobalPosition()
            # 在按钮范围内弹起时触发
            if TouchEvent == 0:
                self.button_up_time_map[ButtonPath] = time.time()
                if ButtonPath in self.button_down_list:
                    self.button_down_list.remove(ButtonPath)
                if is_move_button and self.in_move_button:
                    if ClientMain.UIManager.location_settings.choice_button_path != ButtonPath:
                        ClientMain.UIManager.location_settings.set_in_move_button_choice_button_path(self, ButtonPath)
                    else:
                        center_diff_x, center_diff_y = self.button_down_center_diff_pos_dict[ButtonPath]
                        diff_x, diff_y = TouchPosX - current_pos_x - center_diff_x, TouchPosY - current_pos_y - center_diff_y
                        self.set_button_pos_absolute(ButtonPath, diff_x, diff_y)
                else:
                    if range_move and self.button_down_full_pos_dict.get(ButtonPath):
                        full_pos_x, full_pos_y = self.button_down_full_pos_dict[ButtonPath][0], self.button_down_full_pos_dict[ButtonPath][1]
                        self.set_button_full_pos(ButtonPath, full_pos_x, full_pos_y)
                    if TouchUpCallBack:
                        TouchUpCallBack(args)
            # 按钮按下时触发
            elif TouchEvent == 1:
                self.button_down_touch_pos_dict[ButtonPath] = (TouchPosX, TouchPosY)
                self.button_down_full_pos_dict[ButtonPath] = self.get_button_full_pos(ButtonPath)
                self.button_down_center_diff_pos_dict[ButtonPath] = (TouchPosX - current_pos_x, TouchPosY - current_pos_y)
                self.button_down_time_map[ButtonPath] = time.time()
                if ButtonPath not in self.button_down_list:
                    self.button_down_list.append(ButtonPath)
                if is_move_button and self.in_move_button:
                    if ClientMain.UIManager.location_settings.choice_button_path != ButtonPath:
                        pass
                else:
                    if TouchDownCallBack:
                        TouchDownCallBack(args)
            # 触控在按钮范围外弹起时触发
            elif TouchEvent == 3:
                self.button_up_time_map[ButtonPath] = time.time()
                if ButtonPath in self.button_down_list:
                    self.button_down_list.remove(ButtonPath)
                if is_move_button and self.in_move_button:
                    if ClientMain.UIManager.location_settings.choice_button_path != ButtonPath:
                        pass
                else:
                    if range_move and self.button_down_full_pos_dict.get(ButtonPath):
                        full_pos_x, full_pos_y = self.button_down_full_pos_dict[ButtonPath][0], self.button_down_full_pos_dict[ButtonPath][1]
                        self.set_button_full_pos(ButtonPath, full_pos_x, full_pos_y)
                    if TouchCancelCallBack:
                        TouchCancelCallBack(args)
            # 按下后触控移动时触发
            elif TouchEvent == 4:
                if is_move_button and self.in_move_button:
                    if ClientMain.UIManager.location_settings.choice_button_path != ButtonPath:
                        pass
                    else:
                        center_diff_pos_dict = self.button_down_center_diff_pos_dict[ButtonPath]
                        center_diff_x, center_diff_y = center_diff_pos_dict[0], center_diff_pos_dict[1]
                        diff_x, diff_y = TouchPosX - current_pos_x - center_diff_x, TouchPosY - current_pos_y - center_diff_y
                        self.set_button_pos_absolute(ButtonPath, diff_x, diff_y)
                else:
                    if range_move:
                        center_diff_pos_dict = self.button_down_center_diff_pos_dict[ButtonPath]
                        center_diff_x, center_diff_y = center_diff_pos_dict[0], center_diff_pos_dict[1]
                        diff_x, diff_y = TouchPosX - current_pos_x - center_diff_x, TouchPosY - current_pos_y - center_diff_y
                        self.set_button_pos_absolute(ButtonPath, diff_x, diff_y, range_move, range_x, range_y)
                    if TouchMoveCallBack:
                        TouchMoveCallBack(args)
            # 按下按钮后进入控件时触发
            elif TouchEvent == 5:
                if is_move_button and self.in_move_button:
                    if ClientMain.UIManager.location_settings.choice_button_path != ButtonPath:
                        pass
                else:
                    if TouchMoveInCallBack:
                        TouchMoveInCallBack(args)
            # 按下按钮后退出控件时触发
            elif TouchEvent == 6:
                if is_move_button and self.in_move_button:
                    if ClientMain.UIManager.location_settings.choice_button_path != ButtonPath:
                        pass
                else:
                    if TouchMoveOutCallBack:
                        TouchMoveOutCallBack(args)
            # 意外情况
            else:
                self.button_up_time_map[ButtonPath] = time.time()
                if ButtonPath in self.button_down_list:
                    self.button_down_list.remove(ButtonPath)

        # 设置触控在按钮范围内弹起时触发的回调函数    TouchEvent->0
        if TouchUp:
            button_controller.SetButtonTouchUpCallback(button_callback)
        # 设置按钮按下时触发的回调函数    TouchEvent->1
        if TouchDown:
            button_controller.SetButtonTouchDownCallback(button_callback)
        # 设置触控在按钮范围外弹起时触发的回调函数    TouchEvent->3
        if TouchCancel:
            button_controller.SetButtonTouchCancelCallback(button_callback)
        # 设置按下后触控移动时触发的回调函数    TouchEvent->4
        if TouchMove:
            button_controller.SetButtonTouchMoveCallback(button_callback)
        # 设置按下按钮后进入控件时触发的回调函数    TouchEvent->5  当按钮按下时, 会比按钮按下时触发的回调函数先触发   (TouchPosX,TouchPosY)->(0,0)
        if TouchMoveIn:
            button_controller.SetButtonTouchMoveInCallback(button_callback)
        # 设置按下按钮后退出控件时触发的回调函数    TouchEvent->6 当按钮在按钮范围内弹起时, 会比按钮按下时触`发的回调函数后触发   (TouchPosX,TouchPosY)->(0,0)
        if TouchMoveOut:
            button_controller.SetButtonTouchMoveOutCallback(button_callback)
        self.button_path_callback_map[path] = {"callback_func": button_callback, "bind_args": {"isSwallow": isSwallow}}

    def reset_button_size(self, path):
        self.set_button_size(path, 0.5, 1.0)
        self.set_current_button_size_to_local(path)

    def reset_all_button_size(self):
        button_local_size = ConfigClient.GetConfigData("empty_size_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True)
        for path in self.register_move_button_list:
            self.set_button_size(path, 0.5, 1.0)
            button_local_size[path] = 0.5
        ConfigClient.SetConfigData("empty_size_dict_" + self.__class__.__name__ + ModName + ConfigVersion, button_local_size, True)

    def get_current_button_size(self, path):
        temp_size = self.button_current_size_dict.get(path, None)
        size = temp_size if temp_size else self.get_current_button_local_size(path)
        return size

    def get_current_button_local_size(self, path):
        return ConfigClient.GetConfigData("empty_size_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True).get(path, 0.5)

    def set_current_button_size_to_local(self, path):
        current_button_client_config = ConfigClient.GetConfigData("empty_size_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True)
        current_button_client_config[path] = self.button_current_size_dict.get(path, 0.5)
        ConfigClient.SetConfigData("empty_size_dict_" + self.__class__.__name__ + ModName + ConfigVersion, current_button_client_config, True)

    def set_button_size_by_current_local(self, path):
        local_size = self.get_current_button_local_size(path)
        need_change_size = local_size / self.button_current_size_dict.get(path, 0.5)
        self.set_button_scale(path, need_change_size, False)
        self.button_current_size_dict[path] = local_size

    def set_button_size(self, path, percent_value, size):
        need_change_size = size / self.size_progress_to_value(self.button_current_size_dict[path])
        self.set_button_scale(path, need_change_size, False)
        self.button_current_size_dict[path] = percent_value

    def size_progress_to_value(self, progress):
        if progress <= 0.5:
            # Interpolate between 0.1 and 1
            return 0.1 + progress * 2 * (1 - 0.1)
        else:
            # Interpolate between 1 and 2
            return 1 + (progress - 0.5) * 2 * (2 - 1)

    def reset_button_opacity(self, path):
        self.set_button_opacity(path, 1.0, 1.0)
        self.set_current_button_opacity_to_local(path)

    def reset_all_button_opacity(self):
        button_local_opacity = ConfigClient.GetConfigData("empty_opacity_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True)
        for path in self.register_move_button_list:
            self.set_button_opacity(path, 1.0, 1.0)
            button_local_opacity[path] = 1.0
        ConfigClient.SetConfigData("empty_opacity_dict_" + self.__class__.__name__ + ModName + ConfigVersion, button_local_opacity, True)

    def get_current_button_opacity(self, path):
        temp_opacity = self.button_current_opacity_dict.get(path, None)
        opacity = temp_opacity if temp_opacity else self.get_current_button_local_opacity(path)
        return opacity

    def get_current_button_local_opacity(self, path):
        return ConfigClient.GetConfigData("empty_opacity_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True).get(path, 1.0)

    def set_current_button_opacity_to_local(self, path):
        current_button_client_config = ConfigClient.GetConfigData("empty_opacity_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True)
        current_button_client_config[path] = self.button_current_opacity_dict.get(path, 1.0)
        ConfigClient.SetConfigData("empty_opacity_dict_" + self.__class__.__name__ + ModName + ConfigVersion, current_button_client_config, True)

    def set_button_opacity_by_current_local(self, path):
        self.button_current_opacity_dict[path] = self.get_current_button_local_opacity(path)
        self.GetBaseUIControl(path).SetAlpha(self.opacity_progress_to_value(self.button_current_opacity_dict[path]))

    def set_button_opacity(self, path, percent_value, opacity):
        self.button_current_opacity_dict[path] = percent_value
        self.GetBaseUIControl(path).SetAlpha(opacity)

    def opacity_progress_to_value(self, progress):
        m1 = (0.5 - 0.1) / 0.5
        b1 = 0.1

        m2 = (1 - 0.5) / 0.5
        b2 = 0.5

        if progress <= 0.5:
            return progress * m1 + b1
        else:
            return progress * m2 + b2 - m2 * 0.5

    def reset_button_pos(self, path):
        current_button_local_full_pos = self.get_button_local_full_pos_dict()
        if current_button_local_full_pos.get("origin_full_pos_" + path):
            origin_full_pos_x, origin_full_pos_y = current_button_local_full_pos["origin_full_pos_" + path]
            self.GetBaseUIControl(path).SetFullPosition("x", origin_full_pos_x)
            self.GetBaseUIControl(path).SetFullPosition("y", origin_full_pos_y)
            current_button_local_full_pos[path] = current_button_local_full_pos["origin_full_pos_" + path]
            new_full_pos_x, new_full_pos_y = self.get_button_full_pos(path)
            if (new_full_pos_x, new_full_pos_y) != (origin_full_pos_x, origin_full_pos_y):
                GameCompLevel.AddTimer(0.1, self.reset_button_pos)
        ConfigClient.SetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, current_button_local_full_pos, True)
        self.UpdateScreen()

    def reset_all_button_pos(self):
        current_button_local_full_pos = self.get_button_local_full_pos_dict()
        for path in self.register_move_button_list:
            if current_button_local_full_pos.get("origin_full_pos_" + path):
                origin_full_pos_x, origin_full_pos_y = current_button_local_full_pos["origin_full_pos_" + path]
                self.GetBaseUIControl(path).SetFullPosition("x", origin_full_pos_x)
                self.GetBaseUIControl(path).SetFullPosition("y", origin_full_pos_y)
                current_button_local_full_pos[path] = current_button_local_full_pos["origin_full_pos_" + path]
                new_full_pos_x, new_full_pos_y = self.get_button_full_pos(path)
                if (new_full_pos_x, new_full_pos_y) != (origin_full_pos_x, origin_full_pos_y):
                    GameCompLevel.AddTimer(0.1, self.reset_button_pos)
                    return
        ConfigClient.SetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, current_button_local_full_pos, True)
        self.UpdateScreen()

    def get_button_full_pos(self, path):
        full_pos_x = self.GetBaseUIControl(path).GetFullPosition("x")
        full_pos_y = self.GetBaseUIControl(path).GetFullPosition("y")
        if not full_pos_x:
            full_pos_x = {
                "absoluteValue": 0.0,
                "followType": "none",
                "relativeValue": 0.0
            }
        if not full_pos_y:
            full_pos_y = {
                "absoluteValue": 0.0,
                "followType": "none",
                "relativeValue": 0.0
            }
        return full_pos_x, full_pos_y

    def set_button_full_pos(self, path, full_pos_x, full_pos_y):
        self.GetBaseUIControl(path).SetFullPosition("x", full_pos_x)
        self.GetBaseUIControl(path).SetFullPosition("y", full_pos_y)

    def set_button_full_pos_by_current_local(self, path):
        current_button_local_full_pos = self.get_current_button_local_full_pos(path)
        if current_button_local_full_pos:
            local_full_pos_x, local_full_pos_y = current_button_local_full_pos
            self.set_button_full_pos(path, local_full_pos_x, local_full_pos_y)

    def set_current_button_full_pos_to_local(self, button_path):
        current_button_client_config = ConfigClient.GetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True)
        current_button_client_config[button_path] = self.get_button_full_pos(button_path)
        ConfigClient.SetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, current_button_client_config, True)

    def set_origin_button_full_pos_to_local(self, button_path):
        current_button_client_config = ConfigClient.GetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True)
        current_button_client_config["origin_full_pos_" + button_path] = self.get_button_full_pos(button_path)
        ConfigClient.SetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, current_button_client_config, True)

    def get_origin_button_local_full_pos(self, button_path):
        return ConfigClient.GetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True).get(
            "origin_full_pos_" + button_path)

    def get_current_button_local_full_pos(self, button_path):
        return ConfigClient.GetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True).get(button_path)

    def get_button_local_full_pos_dict(self):
        return ConfigClient.GetConfigData("empty_full_pos_dict_" + self.__class__.__name__ + ModName + ConfigVersion, True)

    def set_button_pos_absolute(self, path, diff_x=0, diff_y=0, range_move=False, range_x=30, range_y=30):
        if range_move:
            if self.button_down_full_pos_dict.get(path):
                down_full_pos_x, down_full_pos_y = self.button_down_full_pos_dict[path][0], self.button_down_full_pos_dict[path][1]
                full_pos_x = self.GetBaseUIControl(path).GetFullPosition("x")
                if not full_pos_x:
                    full_pos_x = {
                        "absoluteValue": 0.0,
                        "followType": "none",
                        "relativeValue": 0.0
                    }
                full_pos_x["absoluteValue"] = full_pos_x["absoluteValue"] + diff_x
                current_diff_x = down_full_pos_x["absoluteValue"] - full_pos_x["absoluteValue"]
                if -range_x <= current_diff_x <= range_x:
                    self.GetBaseUIControl(path).SetFullPosition("x", full_pos_x)
                full_pos_y = self.GetBaseUIControl(path).GetFullPosition("y")
                if not full_pos_y:
                    full_pos_y = {
                        "absoluteValue": 0.0,
                        "followType": "none",
                        "relativeValue": 0.0
                    }
                full_pos_y["absoluteValue"] = full_pos_y["absoluteValue"] + diff_y
                current_diff_y = down_full_pos_y["absoluteValue"] - full_pos_y["absoluteValue"]
                if -range_y <= current_diff_y <= range_y:
                    self.GetBaseUIControl(path).SetFullPosition("y", full_pos_y)
        else:
            full_pos_x = self.GetBaseUIControl(path).GetFullPosition("x")
            if not full_pos_x:
                full_pos_x = {
                    "absoluteValue": 0.0,
                    "followType": "none",
                    "relativeValue": 0.0
                }
            full_pos_x["absoluteValue"] = full_pos_x["absoluteValue"] + diff_x
            self.GetBaseUIControl(path).SetFullPosition("x", full_pos_x)
            full_pos_y = self.GetBaseUIControl(path).GetFullPosition("y")
            if not full_pos_y:
                full_pos_y = {
                    "absoluteValue": 0.0,
                    "followType": "none",
                    "relativeValue": 0.0
                }
            full_pos_y["absoluteValue"] = full_pos_y["absoluteValue"] + diff_y
            self.GetBaseUIControl(path).SetFullPosition("y", full_pos_y)

    def set_button_scale(self, button_path, scale, set_parent_pos=True):
        self.set_controller_scale(button_path, scale, set_parent_pos)
        for children_path in self.GetAllChildrenPath(button_path):
            self.set_controller_scale(children_path, scale)
        self.UpdateScreen()

    def set_controller_scale(self, path, scale, set_pos=True):
        if "label" in path and "label" in path.rsplit("/", 1)[-1]:
            full_size_y = self.GetBaseUIControl(path).GetFullSize("y")
            if full_size_y["fit"]:
                full_size_y = self.GetBaseUIControl(path.rsplit("/", 1)[0]).GetFullSize("y")
            self.GetBaseUIControl(path).asLabel().SetTextFontSize(full_size_y["absoluteValue"] * scale / 11.67)

        full_size_x = self.GetBaseUIControl(path).GetFullSize("x")
        if full_size_x and not full_size_x["fit"]:
            full_size_x["absoluteValue"] = full_size_x["absoluteValue"] * scale
            self.GetBaseUIControl(path).SetFullSize("x", full_size_x)
        full_size_y = self.GetBaseUIControl(path).GetFullSize("y")
        if full_size_y and not full_size_y["fit"]:
            full_size_y["absoluteValue"] = full_size_y["absoluteValue"] * scale
            self.GetBaseUIControl(path).SetFullSize("y", full_size_y)
        if set_pos:
            full_pos_x = self.GetBaseUIControl(path).GetFullPosition("x")
            if not full_pos_x:
                full_pos_x = {
                    "absoluteValue": 0.0,
                    "followType": "none",
                    "relativeValue": 0.0
                }
            full_pos_x["absoluteValue"] = full_pos_x["absoluteValue"] * scale
            self.GetBaseUIControl(path).SetFullPosition("x", full_pos_x)
            full_pos_y = self.GetBaseUIControl(path).GetFullPosition("y")
            if not full_pos_y:
                full_pos_y = {
                    "absoluteValue": 0.0,
                    "followType": "none",
                    "relativeValue": 0.0
                }
            full_pos_y["absoluteValue"] = full_pos_y["absoluteValue"] * scale
            self.GetBaseUIControl(path).SetFullPosition("y", full_pos_y)

    def set_in_move_button(self, state):
        self.in_move_button = state
        if ClientMain.UIManager.location_settings.choice_button_class_instance == self:
            ClientMain.UIManager.location_settings.cancel_in_move_button_choice_button()
