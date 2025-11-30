# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.api import EmptyQueryClientApi, EmptyAttributeClientApi
from fg_more_crabScripts.client.base_parent_class.ClientListener import *
from fg_more_crabScripts.config import QueryConfig, PlayerRenderConfig


class ClientPlayer(ClientListener):
    def __init__(self, player_id):
        self.PlayerId = player_id
        self.EntityTypeStr = "minecraft:player"
        self.LoadPosition = EmptyAttributeClientApi.GetEntityFootPos(self.PlayerId)
        self.IsLocalPlayer = bool(player_id == LocalPlayerId)

        self._in_add_render = False
        if self.IsLocalPlayer:
            self.RegisterModQuery()
        if not self.ModRenderLoadFinished and not PlayerRenderConfig.HasRenderData():
            self.ModRenderLoadFinished = True
        if self.ModRenderLoadFinished:
            self.UpdateEntityQueries()
        super(ClientPlayer, self).__init__(False)

    @property
    def ClientQueryMap(self):
        return ClientMain.ClientMobInstancesController.MobQueryValueMap.get(self.PlayerId, {})

    @property
    def ModRenderLoadFinished(self):
        return self.PlayerId in ClientMain.ClientMobInstancesController.LoadRenderFinishedPlayerList

    @ModRenderLoadFinished.setter
    def ModRenderLoadFinished(self, load_state):
        if load_state:
            if self.PlayerId not in ClientMain.ClientMobInstancesController.LoadRenderFinishedPlayerList:
                ClientMain.ClientMobInstancesController.LoadRenderFinishedPlayerList.append(self.PlayerId)
        else:
            if self.PlayerId in ClientMain.ClientMobInstancesController.LoadRenderFinishedPlayerList:
                ClientMain.ClientMobInstancesController.LoadRenderFinishedPlayerList.remove(self.PlayerId)

    def Update(self):
        if GlobalTickCount() % 15 == 0 and not self.ModRenderLoadFinished and not self._in_add_render:
            self.AddModRender()

    def AddModRender(self):
        if self.ModRenderLoadFinished:
            return
        self._in_add_render = True

        error_items = []
        comp_render = GetActorRenderComp(self.PlayerId)

        def add_render_items(render_items, add_function, can_check_load_success=True, extra_param=None):
            for item in render_items:
                (name, value) = item.items()[0]
                if extra_param is not None:
                    load_success = add_function(name, value, extra_param)
                else:
                    load_success = add_function(name, value)
                if can_check_load_success and not load_success:
                    print "%s is load error" % name
                    error_items.append((add_function, name, value))

        add_render_items(PlayerRenderConfig.RegisterParticleEffect, comp_render.AddPlayerParticleEffect)
        add_render_items(PlayerRenderConfig.RegisterRenderController, comp_render.AddPlayerRenderController, False)
        add_render_items(PlayerRenderConfig.RegisterAnimationController, comp_render.AddPlayerAnimationController)
        add_render_items(PlayerRenderConfig.RegisterActorScriptAnimate, comp_render.AddPlayerScriptAnimate, extra_param=True)
        add_render_items(PlayerRenderConfig.RegisterAnimation, comp_render.AddPlayerAnimation)
        add_render_items(PlayerRenderConfig.RegisterGeometry, comp_render.AddPlayerGeometry)
        add_render_items(PlayerRenderConfig.RegisterTexture, comp_render.AddPlayerTexture)
        add_render_items(PlayerRenderConfig.RegisterMaterial, comp_render.AddPlayerRenderMaterial)
        add_render_items(PlayerRenderConfig.RegisterSoundEffect, comp_render.AddPlayerSoundEffect)

        comp_render.RebuildPlayerRender()

        if error_items:
            if DEVELOPMENT:
                print error_items
        else:
            self.ModRenderLoadFinished = True
            ClientMain.NotifyToServer("PlayerLoadRenderFinishedEvent", {"load_finished_player_id": self.PlayerId})
            self.UpdateEntityQueries()

        self._in_add_render = False

    def RegisterModQuery(self):
        if self.IsLocalPlayer:
            EmptyQueryClientApi.RegisterQueryByMap(QueryConfig.GetAllRegisterDict())

    def GetAllServerEntityQueryMap(self):
        ClientMain.NotifyToServer("GetAllServerQueryMapEvent", {})

    def GetServerEntityQueryMap(self):
        ClientMain.NotifyToServer("GetServerQueryMapEvent", {"entity_id": self.PlayerId, "local_entity_query_dict": self.ClientQueryMap})

    def UpdateEntityQueries(self):
        print ("======================================")
        print self.PlayerId, self.ModRenderLoadFinished
        # 获取需要注册的查询字典
        query_dict = QueryConfig.GetEntityNeedRegisterDict(self.EntityTypeStr)

        if not query_dict:
            query_dict = {}

        # 将 ClientQueryMap 中的查询添加到 query_dict 中，如果存在相同的查询名称则覆盖
        for query_name, query_value in self.ClientQueryMap.iteritems():
            query_dict[query_name] = query_value

        # 设置查询
        for query_name, query_value in query_dict.iteritems():
            EmptyQueryClientApi.SetQuery(self.PlayerId, query_name, query_value)
        if self.IsLocalPlayer:
            self.GetAllServerEntityQueryMap()
        else:
            self.GetServerEntityQueryMap()
