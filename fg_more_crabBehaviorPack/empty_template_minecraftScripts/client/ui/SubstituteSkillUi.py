# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.api.EmptyBaseClientApi import *
from fg_more_crabScripts.client.ui.base_class.EmptyButton import EmptyButton


class SubstituteSkillUi(EmptyButton):

    def __init__(self, namespace, name, param):
        super(SubstituteSkillUi, self).__init__(namespace, name, param)
        self.adapt_scale = 1.0

        self.actor_name = None
        self.SkillInLock = False
        self.RecoverSkillActiveTime = time.time()

        self.SkillDetail = SkillConfig.SkillDetail.get(self.actor_name, {})

        self.FunctionButtonPathMap = {
            # "attack": BasePanel + "/attack_button",
            # "skill_1": BasePanel + "/skill_button_1",
        }
        self.skill_button_to_index_map = {
            # self.FunctionButtonPathMap["skill_1"]: 1,
        }
        self.buttonToFunctionMap = {
            # self.FunctionButtonPathMap["attack"]: {"TouchUpCallBack": self.attack_button, "isSwallow": False, "is_move_button": True},
            # self.FunctionButtonPathMap["skill_1"]: {"TouchUpCallBack": self.skill_button_up, "TouchDownCallBack": self.skill_button_down,
            #                                         "isSwallow": False, "is_move_button": True,
            #                                         "TouchCancelCallBack": self.skill_button_up if self.SkillDetail["skill_effect"][4][
            #                                                                                            "active"] in ["touch_hold", "setting"] else None}
        }

        # 技能退出冷却时间
        self.skill_exit_cold_map = {
            # 1: time.time(), 2: time.time(), 3: time.time(), 4: time.time(), 5: time.time()
        }
        # 技能冷却状态
        self.skill_in_cold_map = {
            # 1: False, 2: False, 3: False, 4: False, 5: False
        }

    def Create(self):
        """
        当 ui 被创建后，会调用这个方法
        """
        super(SubstituteSkillUi, self).Create()
        for children_path in self.GetAllChildrenPath(BasePanel):
            self.set_controller_scale(children_path, self.adapt_scale)
        for button_path, button_options in self.buttonToFunctionMap.iteritems():
            self.register_button(button_path, **button_options)
        self.CloseScreen()
        if ClientMain.ClientSubstituteController and ClientMain.ClientSubstituteController.LocalSubstitute and ClientMain.ClientSubstituteController.LocalSubstitute.control_name == self.actor_name:
            self.OpenScreen()

    def Update(self):
        if ClientMain.ClientSubstituteController and ClientMain.ClientSubstituteController.LocalSubstitute and ClientMain.ClientSubstituteController.LocalSubstitute.control_name == self.actor_name:
            self.set_skill_cold_show()
            if self.SkillInLock and time.time() > self.RecoverSkillActiveTime:
                self.RecoverSkillActive()

    def set_in_move_button(self, state):
        if state:
            if ClientMain.ClientSubstituteController.lastChooseSubstitute == self.actor_name or (
                    ClientMain.ClientSubstituteController.LocalSubstitute and ClientMain.ClientSubstituteController.LocalSubstitute.SkillUi == self):
                self.OpenScreen(exclude_screen=True)
        else:
            if ClientMain.ClientSubstituteController.LocalSubstitute and ClientMain.ClientSubstituteController.LocalSubstitute.SkillUi == self:
                self.OpenScreen(exclude_screen=True)
            else:
                self.CloseScreen()
        super(SubstituteSkillUi, self).set_in_move_button(state)

    def attack_button(self, args):
        ButtonPath = args.get("ButtonPath", None)
        if ButtonPath is None:
            return
        ClientMain.NotifyToServer("SubstituteAttackEvent", {})

    def skill_button_down(self, args):
        ButtonPath = args.get("ButtonPath", None)
        if ButtonPath is None:
            return
        skill_index = self.skill_button_to_index_map.get(args.get("ButtonPath", None), None)
        if skill_index:
            ClientMain.NotifyToServer("SubstituteSkillButtonDownEvent", {"skill": skill_index, "pick_data": self.CheckPickData()})

    def skill_button_up(self, args):
        TouchEvent = args["TouchEvent"]
        if TouchEvent == 3 and ClientMain.ClientSetting.TriggerBurstByClick:
            return
        ButtonPath = args.get("ButtonPath", None)
        if ButtonPath is None:
            return
        skill_index = self.skill_button_to_index_map.get(ButtonPath, None)
        if skill_index:
            ClientMain.NotifyToServer("SubstituteSkillButtonUpEvent",
                                      {"skill": skill_index, "touch_hold_time": self.get_button_touch_time(ButtonPath), "pick_data": self.CheckPickData()})

    def CheckPickData(self):
        return CompFactory.CreateCamera(LocalPlayerId).PickFacing()

    def start_skill_cold(self, skill_index, skill_exit_cold_time):
        self.skill_exit_cold_map[skill_index] = skill_exit_cold_time
        self.skill_in_cold_map[skill_index] = True
        self.SetButtonTexturesToGary(self.FunctionButtonPathMap["skill_%s" % skill_index], True)

    def set_skill_cold_show(self):
        for skill_index in self.skill_exit_cold_map:
            if self.get_skill_in_cold(skill_index):
                remaining_cold = time.time() - self.skill_exit_cold_map[skill_index]
                if remaining_cold > 0:
                    self.skill_in_cold_map[skill_index] = False
                    self.set_skill_cold_image_clip_ratio(skill_index, 1)
                    if self.get_button_active(self.FunctionButtonPathMap["skill_%s" % skill_index]):
                        self.SetButtonTexturesToGary(self.FunctionButtonPathMap["skill_%s" % skill_index], False)
                else:
                    self.set_skill_cold_image_clip_ratio(skill_index, -remaining_cold / self.SkillDetail["skill_effect"][skill_index]["skill_cold"])

    def get_skill_in_cold(self, skill_index):
        return self.skill_in_cold_map.get(skill_index, True)

    def set_skill_cold_image_clip_ratio(self, skill_index, progress):
        self.SetSpriteClipRatio(self.FunctionButtonPathMap["skill_%s" % skill_index] + "/cold_image", progress)

    def LockSkillAndAutoRecover(self, recover_time):
        self.LockSkillActive()
        self.RecoverSkillActiveTime = time.time() + recover_time

    def LockSkillActive(self):
        self.SkillInLock = True
        for _, button_path in self.FunctionButtonPathMap.iteritems():
            self.set_button_active(button_path, False)

    def RecoverSkillActive(self):
        self.SkillInLock = False
        for _, button_path in self.FunctionButtonPathMap.iteritems():
            self.set_button_active(button_path, True)
