# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.api.EmptyBaseClientApi import *


from fg_more_crabScripts.client.ui.base_class import EmptyScreenNode


class UIManager(object):

    def __init__(self):
        self.open_screen_instance_list = []
        self.ui_instance = {}
        self.ui_register_list = [
        ]
        self.ui_data = {
            # key:{
            #   "ui_name":key,
            #   "class_path":UI类路径,
            #   "json_path":"namespace.screenName",
            #   "create_params":{'isHud': 1}
            # }
        }
        ClientMain.ListenForEvent(ClientEngineNamespace, ClientEngineSystemName, 'UiInitFinished', self, self.init_ui)

    # noinspection PyUnusedLocal
    def init_ui(self, args):
        for key in self.ui_register_list:
            data = self.ui_data.get(key, {'ui_name': key, "class_path": ModScriptFilePath + '.client.ui.' + key + '.' + key, 'json_path': '%s.main' % key,
                                          'create_params': {'isHud': 1}, "only_register": False})
            class_path = data.get("class_path", ModScriptFilePath + '.client.ui.' + key + '.' + key)
            ui_name = data.get('ui_name', key)
            json_path = data.get("json_path", key + ".main")
            create_params = data.get("create_params", {'isHud': 1})
            ClientApi.RegisterUI(ModName, ui_name, class_path, json_path)
            print('已注册UI ' + key)
            if data.get("only_register", False):
                continue
            self.ui_instance[key] = ClientApi.CreateUI(ModName, ui_name, create_params)
            print('已创建UI ' + key)
        print("UI全部注册完成")

    def OpenScreen(self, screen_instance, only=True, exclude_screen=False):
        """

        :param screen_instance: EmptyScreenNode
        :type screen_instance: ()
        :param only:only screen
        :type only:bool
        :param exclude_screen:exclude_screen 排除在only的逻辑之外
        :type exclude_screen:bool

        :return res
        :rtype bool
        """
        if not exclude_screen:
            if screen_instance in self.open_screen_instance_list:
                return False
            if only:
                for old_screen_instance in self.open_screen_instance_list:
                    old_screen_instance.CloseScreen()
            if screen_instance not in self.open_screen_instance_list:
                self.open_screen_instance_list.append(screen_instance)
        screen_instance.SetScreenVisible(True)

        return True

    def CloseScreen(self, screen_instance):
        """

        :param screen_instance: EmptyScreenNode
        :type screen_instance: ()

        :return res
        :rtype bool
        """
        if screen_instance in self.open_screen_instance_list:
            self.open_screen_instance_list.remove(screen_instance)
        screen_instance.SetScreenVisible(False)
        return True
