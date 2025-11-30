# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.api import EmptyQueryClientApi, EmptyAttributeClientApi
from fg_more_crabScripts.client.base_parent_class.ClientListener import *
from fg_more_crabScripts.config import QueryConfig, EntityRenderConfig


class ClientEntity(ClientListener):
    def __init__(self, entity_id, itemName=None, auxValue=None):
        self.EntityId = entity_id
        self.itemName = itemName
        self.auxValue = auxValue
        self.IsItem = bool(self.itemName)

        # 获取实体类型字符串和位置
        self.EntityTypeStr = EmptyAttributeClientApi.GetEngineTypeStr(self.EntityId)
        self.LoadPosition = EmptyAttributeClientApi.GetEntityFootPos(self.EntityId)

        # 初始值
        self._in_add_render = False
        self.ModRenderLoadFinished = False

        # 检查是否存在渲染数据或渲染排除
        render_data_exists = EntityRenderConfig.HasRenderDataEntity() or EntityRenderConfig.HasRenderDataEntity(self.EntityTypeStr)
        render_data_exclude = self.EntityTypeStr in EntityRenderConfig.RegisterAllEntityRenderExcludeList

        # 确定是否完成渲染加载
        if self.IsItem or (not render_data_exists and render_data_exclude):
            self.ModRenderLoadFinished = True

        # 如果渲染加载完成，更新实体查询
        if not self.IsItem and self.ModRenderLoadFinished:
            self.UpdateEntityQueries()

        super(ClientEntity, self).__init__(False)


    @property
    def ClientQueryMap(self):
        return ClientMain.ClientMobInstancesController.MobQueryValueMap.get(self.EntityId, {})

    @property
    def ModRenderLoadFinished(self):
        return self.EntityId in ClientMain.ClientMobInstancesController.LoadRenderFinishedMobList

    @ModRenderLoadFinished.setter
    def ModRenderLoadFinished(self, load_state):
        if load_state:
            if self.EntityId not in ClientMain.ClientMobInstancesController.LoadRenderFinishedMobList:
                ClientMain.ClientMobInstancesController.LoadRenderFinishedMobList.append(self.EntityId)
        else:
            if self.EntityId in ClientMain.ClientMobInstancesController.LoadRenderFinishedMobList:
                ClientMain.ClientMobInstancesController.LoadRenderFinishedMobList.remove(self.EntityId)

    def Update(self):
        if GlobalTickCount() % 15 == 0 and not self.ModRenderLoadFinished and not self._in_add_render:
            self.AddModRender()

    def AddModRender(self):
        self._in_add_render = True
        error_items = []

        comp_render = GetActorRenderComp(LevelId)

        def add_render_items(render_items, add_function, can_check_load_success=True, extra_param=None):
            for item in render_items:
                (name, value) = item.items()[0]
                if extra_param is not None:
                    load_success = add_function(self.EntityTypeStr, name, value, extra_param)
                else:
                    load_success = add_function(self.EntityTypeStr, name, value)
                if can_check_load_success and not load_success:
                    print "%s is load error" % name
                    error_items.append((add_function, name, value))

        # if EntityRenderConfig.AllRenderNeedAddVariable:
        #     current_render_list = comp_render.GetActorRenderParams(self.EntityId, "render_controllers")
        #     if current_render_list:
        #         for render_str in current_render_list:
        #             if render_str not in EntityRenderConfig.RegisterEntityRenderController["all"]:
        #                 comp_render.RemoveActorRenderController(self.EntityTypeStr, render_str)
        #                 comp_render.AddActorRenderController(self.EntityTypeStr, render_str, EntityRenderConfig.AllRenderNeedAddVariable)

        if EntityRenderConfig.HasRenderDataEntity():
            add_render_items(EntityRenderConfig.RegisterEntityParticleEffect["all"], comp_render.AddActorParticleEffect)
            add_render_items(EntityRenderConfig.RegisterEntityRenderController["all"], comp_render.AddActorRenderController, False)
            add_render_items(EntityRenderConfig.RegisterEntityAnimation["all"], comp_render.AddActorAnimation)
            add_render_items(EntityRenderConfig.RegisterEntityActorScriptAnimate["all"], comp_render.AddActorScriptAnimate, extra_param=True)
            add_render_items(EntityRenderConfig.RegisterEntityAnimationController["all"], comp_render.AddActorAnimationController)
            add_render_items(EntityRenderConfig.RegisterEntityGeometry["all"], comp_render.AddActorGeometry)
            add_render_items(EntityRenderConfig.RegisterEntityTexture["all"], comp_render.AddActorTexture)
            add_render_items(EntityRenderConfig.RegisterEntityMaterial["all"], comp_render.AddActorRenderMaterial)
            add_render_items(EntityRenderConfig.RegisterEntitySoundEffect["all"], comp_render.AddActorSoundEffect)

        if EntityRenderConfig.HasRenderDataEntity(self.EntityTypeStr):
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityParticleEffect:
                add_render_items(EntityRenderConfig.RegisterEntityParticleEffect[self.EntityTypeStr], comp_render.AddActorParticleEffect)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityRenderController:
                add_render_items(EntityRenderConfig.RegisterEntityRenderController[self.EntityTypeStr], comp_render.AddActorRenderController, False)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityAnimation:
                add_render_items(EntityRenderConfig.RegisterEntityAnimation[self.EntityTypeStr], comp_render.AddActorAnimation)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityActorScriptAnimate:
                add_render_items(EntityRenderConfig.RegisterEntityActorScriptAnimate[self.EntityTypeStr], comp_render.AddActorScriptAnimate, extra_param=True)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityAnimationController:
                add_render_items(EntityRenderConfig.RegisterEntityAnimationController[self.EntityTypeStr], comp_render.AddActorAnimationController)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityGeometry:
                add_render_items(EntityRenderConfig.RegisterEntityGeometry[self.EntityTypeStr], comp_render.AddActorGeometry)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityTexture:
                add_render_items(EntityRenderConfig.RegisterEntityTexture[self.EntityTypeStr], comp_render.AddActorTexture)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntityMaterial:
                add_render_items(EntityRenderConfig.RegisterEntityMaterial[self.EntityTypeStr], comp_render.AddActorRenderMaterial)
            if self.EntityTypeStr in EntityRenderConfig.RegisterEntitySoundEffect:
                add_render_items(EntityRenderConfig.RegisterEntitySoundEffect[self.EntityTypeStr], comp_render.AddActorSoundEffect)

        comp_render.RebuildActorRender(self.EntityTypeStr)

        if error_items:
            if DEVELOPMENT:
                print error_items
        else:
            self.ModRenderLoadFinished = True
            ClientMain.NotifyToServer("EntityLoadRenderFinishedEvent", {"load_finished_entity_id": self.EntityId})
            self.UpdateEntityQueries()

        self._in_add_render = False

    def GetServerEntityQueryMap(self):
        ClientMain.NotifyToServer("GetServerQueryMapEvent", {"entity_id": self.EntityId, "local_entity_query_dict": self.ClientQueryMap})

    def UpdateEntityQueries(self):
        print ("======================================")
        print self.EntityId, self.ModRenderLoadFinished
        # 获取需要注册的查询字典
        query_dict = QueryConfig.GetEntityNeedRegisterDict(self.EntityTypeStr)

        if not query_dict:
            query_dict = {}

        # 将 ClientQueryMap 中的查询添加到 query_dict 中，如果存在相同的查询名称则覆盖
        for query_name, query_value in self.ClientQueryMap.iteritems():
            query_dict[query_name] = query_value

        # 设置查询
        for query_name, query_value in query_dict.iteritems():
            EmptyQueryClientApi.SetQuery(self.EntityId, query_name, query_value)
        self.GetServerEntityQueryMap()
