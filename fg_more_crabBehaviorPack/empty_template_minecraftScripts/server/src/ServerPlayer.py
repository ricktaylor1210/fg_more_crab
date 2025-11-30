# -*- coding: utf-8 -*-
from fg_more_crabScripts.server.api import EmptyGameServerApi
from fg_more_crabScripts.server.base_parent_class.ServerListener import *


class ServerPlayer(ServerListener):
    def __init__(self, player_id):
        self.PlayerId = player_id
        super(ServerPlayer, self).__init__(False)

    def Update(self):
        pass
