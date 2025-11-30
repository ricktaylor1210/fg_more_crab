# -*- coding: utf-8 -*-
from fg_more_crabScripts.config import EntityConfig
from fg_more_crabScripts.server.base_parent_class.ServerListener import *
from fg_more_crabScripts.server.src.ServerPlayer import ServerPlayer
from fg_more_crabScripts.server.src.ServerEntity import ServerEntity


class ServerMobInstancesController(ServerListener):
    def __init__(self):
        super(ServerMobInstancesController, self).__init__(True)
        self.PlayerInstancesMap = {}
        self.MobInstancesMap = {}
        self.MobQueryValueMap = {}
        self.PlayerLoadRenderFinishedMap = {}
        self.engine_events.update(
            {
                # engineEventName : {func,priority}
                "AddEntityServerEvent": {"func": self.AddEntityServerEvent},
                "EntityRemoveEvent": {"func": self.EntityRemoveEvent},
                "ChunkAcquireDiscardedServerEvent": {"func": self.ChunkAcquireDiscardedServerEvent},
                "ClientLoadAddonsFinishServerEvent": {"func": self.ClientLoadAddonsFinishServerEvent},
                "PlayerIntendLeaveServerEvent": {"func": self.PlayerIntendLeaveServerEvent}
            }
        )
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            "GetServerQueryMapEvent": {"func": self.GetServerQueryMapEvent},
            "GetAllServerQueryMapEvent": {"func": self.GetAllServerQueryMapEvent},
            "PlayerLoadRenderFinishedEvent": {"func": self.PlayerLoadRenderFinishedEvent},
            "OnChangeEntityQueryToAllClientEvent": {"func": self.OnChangeEntityQueryToAllClientEvent},
            "SyncPlayerMotionEvent": {"func": self.SyncPlayerMotionEvent}
        })
        self.Register()

    def OnScriptTickServer(self):
        all_instances = list(self.PlayerInstancesMap.values()) + list(self.MobInstancesMap.values())
        for instance in all_instances:
            instance.Update()

    def ClientLoadAddonsFinishServerEvent(self, args):
        # playerId	str	玩家id
        player_id = args["playerId"]
        if player_id not in self.PlayerInstancesMap:
            self.PlayerInstancesMap[player_id] = ServerPlayer(player_id)

    def PlayerIntendLeaveServerEvent(self, args):
        # 与【DelServerPlayerEvent】事件不同，此时可以通过各种API获取玩家的当前状态。
        # playerId	str	玩家id
        player_id = args["playerId"]
        if player_id in self.PlayerInstancesMap:
            self.PlayerInstancesMap[player_id].UnRegister()
            self.PlayerInstancesMap.pop(player_id)
        ServerMain.BroadcastToAllClient("PlayerIntendLeaveGameEvent", {"playerId": player_id})

    def AddEntityServerEvent(self, args):
        # id	str	实体id
        # posX	float	位置x
        # posY	float	位置y
        # posZ	float	位置z
        # dimensionId	int	实体维度
        # isBaby	bool	是否为幼儿
        # engineTypeStr	str	实体类型，即实体identifier
        # itemName	str	物品identifier（仅当物品实体时存在该字段）
        # auxValue	int	物品附加值（仅当物品实体时存在该字段）
        entity_id = args["id"]
        engineTypeStr = args["engineTypeStr"]
        if engineTypeStr not in EntityConfig.ServerLoadInstanceEntityMap and engineTypeStr in EntityConfig.DoNotInstanceEntityList:
            return
        if entity_id not in self.MobInstancesMap:
            instance = EntityConfig.ServerLoadInstanceEntityMap.get(engineTypeStr, ServerEntity)
            self.MobInstancesMap[entity_id] = instance(entity_id, args.get("itemName", None), args.get("auxValue", None))

    def EntityRemoveEvent(self, args):
        # id	str	移除的实体id
        entity_id = args["id"]
        if entity_id in self.MobInstancesMap:
            self.MobInstancesMap[entity_id].UnRegister()
            self.MobInstancesMap.pop(entity_id)

    def ChunkAcquireDiscardedServerEvent(self, args):
        # dimension	int	区块所在维度
        # chunkPosX	int	区块的x坐标，对应方块X坐标区间为[x * 16, x * 16 + 15]
        # chunkPosZ	int	区块的z坐标，对应方块Z坐标区间为[z * 16, z * 16 + 15]
        # entities	list(str)	随区块卸载而从世界移除的实体id的列表。注意事件触发时已经无法获取到这些实体的信息，仅供脚本资源回收用。
        # blockEntities	list(dict)	随区块卸载而从世界移除的自定义方块实体的坐标的列表，列表元素dict包含posX，posY，posZ三个int表示自定义方块实体的坐标，blockName表示方块的identifier，包含命名空间及名称。注意事件触发时已经无法获取到这些方块实体的信息，仅供脚本资源回收用。
        for entity_id in args.get("entities", []):
            if entity_id in self.MobInstancesMap:
                self.MobInstancesMap[entity_id].UnRegister()
                self.MobInstancesMap.pop(entity_id)

    def GetServerQueryMapEvent(self, args):
        player_id = args["__id__"]
        entity_id = args["entity_id"]
        local_entity_query_dict = args["local_entity_query_dict"]

        # 获取或初始化 entity_query_map
        entity_query_map = self.MobQueryValueMap.setdefault(entity_id, {})

        # 检查 local_entity_query_dict 是否等于 entity_query_map
        if local_entity_query_dict == entity_query_map:
            return

        # 去除 entity_query_map 中与 local_entity_query_dict 重复的项
        filtered_entity_query_map = {k: v for k, v in entity_query_map.items() if k not in local_entity_query_dict}

        # 通知客户端
        ServerMain.NotifyToClient(player_id, "SyncServerEntityQueryMapEvent",
                                  {"entity_id": entity_id, "entity_query_map": filtered_entity_query_map})

    def GetAllServerQueryMapEvent(self, args):
        player_id = args["__id__"]
        ServerMain.NotifyToClient(player_id, "SyncAllServerEntityQueryMapEvent", {"all_entity_query_map": self.MobQueryValueMap})

    def PlayerLoadRenderFinishedEvent(self, args):
        main_player_id = args["__id__"]
        load_player_id = args["load_finished_player_id"]
        if load_player_id not in self.PlayerLoadRenderFinishedMap.setdefault(main_player_id, []):
            self.PlayerLoadRenderFinishedMap[main_player_id].append(load_player_id)

    def OnChangeEntityQueryToAllClientEvent(self, args):
        entity_id = args["entity_id"]
        query_name = args["query_name"]
        query_value = args["query_value"]
        self.MobQueryValueMap.setdefault(entity_id, dict())[query_name] = query_value
        ServerMain.BroadcastToAllClient("OnChangeEntityQueryToAllClientServerEvent", args)

    def SyncPlayerMotionEvent(self, args):
        motion = args["motion"]
        playerId = args["__id__"]
        GetActionMotionComp(playerId).SetMotion(motion)
