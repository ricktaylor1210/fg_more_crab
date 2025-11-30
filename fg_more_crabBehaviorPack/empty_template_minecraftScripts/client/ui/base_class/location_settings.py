# coding=utf-8
from fg_more_crabScripts.client.ui.base_class.EmptyScreenNode import *
from fg_more_crabScripts.config import KeyBoartMap


class location_settings(EmptyScreenNode):

    def __init__(self, namespace, name, param):
        super(location_settings, self).__init__(namespace, name, param)
        self.adapt_scale = 1.0
        # default 1.0
        self.opacity_slider_percent_value = 1.0
        # default 0.5
        self.size_slider_percent_value = 0.5

        self.in_wait_key_bind_down = False

        self.buttonToFunctionMap = {
            BasePanel + "/location_settings_panel/line_1_panel/bind_key_button": self.bind_key_button,
            BasePanel + "/location_settings_panel/line_2_panel/cancel_bind_key_button": self.cancel_bind_key_button,
            BasePanel + "/location_settings_panel/set_controller_panel/save_button": self.save_button,
            BasePanel + "/location_settings_panel/set_controller_panel/reset_button": self.reset_button,
            BasePanel + "/location_settings_panel/set_controller_panel/reset_all_button": self.reset_all_button,
            BasePanel + "/location_settings_panel/set_controller_panel/exit_button": self.exit_button
        }

        self.controller_move_button_list_dict = {}
        self.setting_ui_open = False
        self.choice_button_class_instance = None
        self.choice_button_path = None
        self.custom_events.update({
            "playerUseButtonMoveItemEvent": {"func": self.playerUseButtonMoveItemEvent},
        })

    def Create(self):
        """
        当 UI 被创建后，会调用这个方法
        """
        super(location_settings, self).Create()
        self.adapt_panel_scale(self.adapt_scale)
        for button_path in self.buttonToFunctionMap:
            self.register_base_button(button_path, self.buttonToFunctionMap[button_path])

        self.ChangeButtonLabel(BasePanel + "/location_settings_panel/line_1_panel/bind_key_button", "按键绑定")
        self.close_setting_screen()

    def playerUseButtonMoveItemEvent(self, args):
        if not self.setting_ui_open:
            self.open_setting_screen()

    @ViewBinder.binding(ViewBinder.BF_SliderChanged | ViewBinder.BF_SliderFinished)
    def on_slider_change_event_1(self, value, isFinish, _unused):
        self.opacity_slider_percent_value = value
        if self.choice_button_class_instance and self.choice_button_path:
            self.choice_button_class_instance.set_button_opacity(self.choice_button_path, self.opacity_slider_percent_value, self.opacity_progress_to_value())
        return ViewRequest.Refresh

    @ViewBinder.binding(ViewBinder.BF_BindFloat)
    def return_slider_value_1(self):
        return self.opacity_slider_percent_value

    @ViewBinder.binding(ViewBinder.BF_BindString, "#slider_label_1")
    def return_slider_label_1(self):
        return str(round(self.opacity_progress_to_value() * 100, 2)) + "%%"

    def recover_opacity_slider_value(self):
        if self.choice_button_class_instance and self.choice_button_path:
            self.opacity_slider_percent_value = self.choice_button_class_instance.get_current_button_opacity(self.choice_button_path)
            self.return_slider_value_1()
            self.return_slider_label_1()

    @ViewBinder.binding(ViewBinder.BF_SliderChanged | ViewBinder.BF_SliderFinished)
    def on_slider_change_event_2(self, value, isFinish, _unused):
        self.size_slider_percent_value = value
        if self.choice_button_class_instance and self.choice_button_path:
            self.choice_button_class_instance.set_button_size(self.choice_button_path, self.size_slider_percent_value, self.size_progress_to_value())
        return ViewRequest.Refresh

    @ViewBinder.binding(ViewBinder.BF_BindFloat)
    def return_slider_value_2(self):
        return self.size_slider_percent_value

    @ViewBinder.binding(ViewBinder.BF_BindString, "#slider_label_2")
    def return_slider_label_2(self):
        return str(round(self.size_progress_to_value() * 100, 2)) + "%%"

    def recover_size_slider_value(self):
        if self.choice_button_class_instance and self.choice_button_path:
            self.size_slider_percent_value = self.choice_button_class_instance.get_current_button_size(self.choice_button_path)
            self.return_slider_value_2()
            self.return_slider_label_2()

    def bind_key_button(self, args):
        if self.choice_button_class_instance and self.choice_button_path and self.choice_button_path in self.choice_button_class_instance.can_bind_button_path_list:
            self.control_key_bind()

    def cancel_bind_key_button(self, args):
        if self.choice_button_class_instance and self.choice_button_path:
            self.choice_button_class_instance.remove_button_bind_key(self.choice_button_path)

    def check_can_show_bind_button(self):
        if PlatForm not in [1, 2]:
            self.GetBaseUIControl(BasePanel + "/location_settings_panel/line_1_panel/bind_key_button").SetVisible(True)
            self.GetBaseUIControl(BasePanel + "/location_settings_panel/line_2_panel/cancel_bind_key_button").SetVisible(True)
            self.ChangeButtonLabel(BasePanel + "/location_settings_panel/line_1_panel/bind_key_button", "按键绑定")
        else:
            self.GetBaseUIControl(BasePanel + "/location_settings_panel/line_1_panel/bind_key_button").SetVisible(False)
            self.GetBaseUIControl(BasePanel + "/location_settings_panel/line_2_panel/cancel_bind_key_button").SetVisible(False)

    def control_key_bind(self):
        if self.in_wait_key_bind_down:
            self.end_key_bind()
        else:
            self.start_key_bind()

    def start_key_bind(self):
        self.in_wait_key_bind_down = True
        ClientMain.ListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "OnKeyPressInGame", self, self.wait_key_bind_down_event, 10)
        self.ChangeButtonLabel(BasePanel + "/location_settings_panel/line_1_panel/bind_key_button", "取消绑定")

    def wait_key_bind_down_event(self, args):
        # screenName	str	当前screenName
        # key	str	键码（注：这里的int型被转成了str型，比如"1"对应的就是枚举值文档中的1），详见KeyBoardType枚举
        # isDown	str	是否按下，按下为1，弹起为0
        if args["key"] in KeyBoartMap.MinecraftUsedKeyList:
            self.end_key_bind()
            return
        if self.in_wait_key_bind_down and self.choice_button_class_instance and self.choice_button_path:
            self.choice_button_class_instance.set_button_bind_key(self.choice_button_path, args["key"])
        self.end_key_bind()

    def end_key_bind(self):
        self.in_wait_key_bind_down = False
        ClientMain.UnListenForEvent(ClientEngineNamespace, ClientEngineSystemName, "OnKeyPressInGame", self, self.wait_key_bind_down_event, 10)
        self.ChangeButtonLabel(BasePanel + "/location_settings_panel/line_1_panel/bind_key_button", "按键绑定")

    def save_button(self, args):
        self.end_key_bind()
        for class_instance, path_list in self.controller_move_button_list_dict.iteritems():
            for path in path_list:
                class_instance.set_current_button_full_pos_to_local(path)
                class_instance.set_current_button_opacity_to_local(path)
                class_instance.set_current_button_size_to_local(path)
        self.close_setting_screen()

    def reset_button(self, args):
        self.end_key_bind()
        if self.choice_button_class_instance and self.choice_button_path:
            self.choice_button_class_instance.reset_button_pos(self.choice_button_path)
            self.choice_button_class_instance.reset_button_opacity(self.choice_button_path)
            self.choice_button_class_instance.reset_button_size(self.choice_button_path)
            self.recover_opacity_slider_value()
            self.recover_size_slider_value()

    def reset_all_button(self, args):
        self.end_key_bind()
        for class_instance in self.controller_move_button_list_dict:
            class_instance.reset_all_button_pos()
            class_instance.reset_all_button_opacity()
            class_instance.reset_all_button_size()
        self.recover_opacity_slider_value()
        self.recover_size_slider_value()

    def exit_button(self, args):
        self.end_key_bind()
        for class_instance, path_list in self.controller_move_button_list_dict.iteritems():
            for path in path_list:
                class_instance.set_button_full_pos_by_current_local(path)
                class_instance.set_button_opacity_by_current_local(path)
                class_instance.set_button_size_by_current_local(path)
        self.recover_opacity_slider_value()
        self.recover_size_slider_value()
        self.close_setting_screen()

    def add_move_button_list_with_class_map(self, class_instance, button_path):
        if not self.controller_move_button_list_dict.get(class_instance):
            self.controller_move_button_list_dict[class_instance] = []
        self.controller_move_button_list_dict[class_instance].append(button_path)

    def get_move_choice_image(self, class_instance, button_path):
        if button_path:
            control = class_instance.GetBaseUIControl(button_path).GetChildByName("move_choice_image")
            return control if control else None
        else:
            return None

    def set_in_move_button_choice_button_path(self, class_instance, button_path):
        move_choice_image = self.get_move_choice_image(self.choice_button_class_instance, self.choice_button_path)
        if move_choice_image:
            move_choice_image.SetVisible(False)

        self.choice_button_class_instance = class_instance
        self.choice_button_path = button_path

        move_choice_image = self.get_move_choice_image(self.choice_button_class_instance, self.choice_button_path)
        if move_choice_image:
            move_choice_image.SetVisible(True)
        self.recover_opacity_slider_value()
        self.recover_size_slider_value()

    def cancel_in_move_button_choice_button(self):
        move_choice_image = self.get_move_choice_image(self.choice_button_class_instance, self.choice_button_path)
        if move_choice_image:
            move_choice_image.SetVisible(False)
        self.choice_button_class_instance = None
        self.choice_button_path = None
        self.recover_opacity_slider_value()
        self.recover_size_slider_value()

    def size_progress_to_value(self):
        progress = self.size_slider_percent_value
        if progress <= 0.5:
            # Interpolate between 0.1 and 1
            return 0.1 + progress * 2 * (1 - 0.1)
        else:
            # Interpolate between 1 and 2
            return 1 + (progress - 0.5) * 2 * (2 - 1)

    def opacity_progress_to_value(self):
        progress = self.opacity_slider_percent_value
        m1 = (0.5 - 0.1) / 0.5
        b1 = 0.1

        m2 = (1 - 0.5) / 0.5
        b2 = 0.5

        if progress <= 0.5:
            return progress * m1 + b1
        else:
            return progress * m2 + b2 - m2 * 0.5

    def open_setting_screen(self):
        for class_instance in self.controller_move_button_list_dict:
            class_instance.set_in_move_button(True)
        self.SetScreenVisible(True)
        self.setting_ui_open = True
        self.check_can_show_bind_button()

    def close_setting_screen(self):
        print ("5555555555555555555555555")
        for class_instance in self.controller_move_button_list_dict:
            class_instance.set_in_move_button(False)
        self.SetScreenVisible(False)
        self.setting_ui_open = False

    def adapt_panel_scale(self, scale):
        for children_path in self.GetAllChildrenPath(BasePanel):
            self.set_controller_scale(children_path, scale)

    def set_controller_scale(self, path, scale):
        if "label" in path.rsplit("/", 1)[-1]:
            self.GetBaseUIControl(path).asLabel().SetTextFontSize(scale)
        full_size_x = self.GetBaseUIControl(path).GetFullSize("x")
        if full_size_x and not full_size_x["fit"]:
            full_size_x["absoluteValue"] = full_size_x["absoluteValue"] * scale
            self.GetBaseUIControl(path).SetFullSize("x", full_size_x)
        full_size_y = self.GetBaseUIControl(path).GetFullSize("y")
        if full_size_y and not full_size_y["fit"]:
            full_size_y["absoluteValue"] = full_size_y["absoluteValue"] * scale
            self.GetBaseUIControl(path).SetFullSize("y", full_size_y)
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
