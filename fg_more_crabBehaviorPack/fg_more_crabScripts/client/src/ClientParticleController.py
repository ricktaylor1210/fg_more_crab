# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.base_parent_class.ClientListener import *


class ClientParticleController(ClientListener):
    def __init__(self):
        super(ClientParticleController, self).__init__(False)
        # server_id:client_id
        self.particle_id_map = {}
        self.engine_events.update(
            {
                # engineEventName : {func,priority}
            }
        )
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            # 玩家离开游戏时触发事件
            "ServerCreateParticleEvent": {"func": self.ServerCreateParticleEvent},
            "ServerRemoveParticleEvent": {"func": self.ServerRemoveParticleEvent},
            "ServerPauseParticleEvent": {"func": self.ServerPauseParticleEvent},
            "ServerResumeParticleEvent": {"func": self.ServerResumeParticleEvent},
        })
        self.Register()

    def ServerCreateParticleEvent(self, args):
        # 服务端储存的id
        server_id = args.get("server_id", None)
        # 粒子发射器名称(粒子发射器json文件中的identifier)
        effect_name = args.get("effect_name", None)
        if effect_name is None:
            return
        # 三维 表示在某处创建粒子发射器 默认值为(0, 0, 0)
        offset = args.get("offset", (0.0, 0.0, 0.0))
        # 粒子发射器创建后使用的三维旋转(使用角度制，按照ZYX顺序旋转) 默认值为(0, 0, 0)
        rotation = args.get("rotation", (0.0, 0.0, 0.0))
        # 需要绑定的实体id
        entity_id = args.get("entity_id", None)
        # 需要绑定的骨骼名称(不区分大小写) 默认值为"body"
        bone_name = args.get("bone_name", "body")
        # 部分原版粒子使用了minecraft:emitter_rate_manual组件，需要额外调用EmitManually函数才能发射粒子
        if entity_id:
            particle_client_id = CompParticleSystem.CreateBindEntityNew(effect_name, entity_id, bone_name, offset, rotation)
        else:
            particle_client_id = CompParticleSystem.Create(effect_name, offset, rotation)
        # 变量字典
        variable_map = args.get("variable_map", {})
        if variable_map:
            for variable_name, variable_value in variable_map.items():
                CompParticleSystem.SetVariable(particle_client_id, variable_name, variable_value)
        if server_id:
            self.particle_id_map[server_id] = particle_client_id

    def ServerRemoveParticleEvent(self, args):
        # 服务端储存的id
        server_id = args.get("server_id", None)
        if server_id and server_id in self.particle_id_map:
            particle_client_id = self.particle_id_map[server_id]
            if CompParticleSystem.Exist(particle_client_id):
                CompParticleSystem.Remove(particle_client_id)
            self.particle_id_map.pop(server_id)
        # 粒子发射器名称(粒子发射器json文件中的identifier)
        effect_name = args.get("effect_name", None)
        if effect_name:
            CompParticleSystem.RemoveByName(effect_name)

    def ServerPauseParticleEvent(self, args):
        # 暂停粒子发射器的逻辑更新，但保持渲染状态
        # 服务端储存的id
        server_id = args.get("server_id", None)
        if server_id and server_id in self.particle_id_map:
            particle_client_id = self.particle_id_map[server_id]
            if CompParticleSystem.Exist(particle_client_id):
                CompParticleSystem.Pause(particle_client_id)

    def ServerResumeParticleEvent(self, args):
        # 恢复粒子发射器的逻辑更新，不影响渲染状态
        # 服务端储存的id
        server_id = args.get("server_id", None)
        if server_id and server_id in self.particle_id_map:
            particle_client_id = self.particle_id_map[server_id]
            if CompParticleSystem.Exist(particle_client_id):
                CompParticleSystem.Resume(particle_client_id)
