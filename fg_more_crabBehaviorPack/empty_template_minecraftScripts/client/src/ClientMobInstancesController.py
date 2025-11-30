# -*- coding: utf-8 -*-
from fg_more_crabScripts.client.api import EmptyQueryClientApi, EmptyAttributeClientApi, EmptyGameClientApi, EmptyBlockClientApi
from fg_more_crabScripts.client.base_parent_class.ClientListener import *
from fg_more_crabScripts.client.src.ClientEntity import ClientEntity
from fg_more_crabScripts.client.src.ClientPlayer import ClientPlayer
from fg_more_crabScripts.config import EntityConfig


class ClientMobInstancesController(ClientListener):
    def __init__(self):
        super(ClientMobInstancesController, self).__init__(True)
        self.LoadRenderFinishedPlayerList = []
        self.PlayerInstancesMap = {}
        self.LoadRenderFinishedMobList = []
        self.MobInstancesMap = {}
        self.MobQueryValueMap = {}
        self.BlockPaletteGeometryList = []
        self.engine_events.update(
            {
                # engineEventName : {func,priority}
                # 玩家进入当前玩家所在的区块AOI后，玩家皮肤数据异步加载完成后触发的事件
                # 由于玩家皮肤是异步加载的原因，该事件触发时机比AddPlayerAOIClientEvent晚，触发该事件后可以对该玩家调用相关玩家渲染接口。
                # 当前客户端每加载好一个玩家的皮肤，就会触发一次该事件，比如刚进入世界时，localPlayer加载好会触发一次，周围的所有玩家加载好后也会分别触发一次。
                "AddPlayerCreatedClientEvent": {"func": self.AddPlayerCreatedClientEvent},
                # 客户端侧创建新实体时触发,创建玩家时不会触发该事件
                "AddEntityClientEvent": {"func": self.AddEntityClientEvent},
                # 客户端侧实体被移除时触发
                # 客户端接收到了服务端监测实体离开玩家视野时触发，原事件名 RemoveEntityPacketEvent
                "RemoveEntityClientEvent": {"func": self.RemoveEntityClientEvent}
            }
        )
        self.custom_events.update({
            # customEventName : {mod_name,listen_system_name,func,priority}
            # 玩家离开游戏时触发事件
            "PlayerIntendLeaveGameEvent": {"func": self.PlayerIntendLeaveGameEvent},
            "SyncServerEntityQueryMapEvent": {"func": self.SyncServerEntityQueryMapEvent},
            "SyncAllServerEntityQueryMapEvent": {"func": self.SyncAllServerEntityQueryMapEvent},
            "OnChangeEntityQueryToAllClientServerEvent": {"func": self.OnChangeEntityQueryToAllClientServerEvent},
            "CreateBreakBlockEntityEvent": {"func": self.CreateBreakBlockEntityEvent},
        })
        self.Register()

    def OnScriptTickClient(self):
        all_instances = list(self.PlayerInstancesMap.values()) + list(self.MobInstancesMap.values())
        for instance in all_instances:
            instance.Update()

    def AddPlayerCreatedClientEvent(self, args):
        player_id = args["playerId"]
        if player_id not in self.PlayerInstancesMap:
            self.PlayerInstancesMap[player_id] = ClientPlayer(player_id)
        # for i in range(1, 5):
        #     GetActorRenderComp(player_id).SetEntityExtraUniforms(i, (1.0, 1.0, 1.0, 1.0))

    def PlayerIntendLeaveGameEvent(self, args):
        player_id = args["playerId"]
        if player_id in self.PlayerInstancesMap:
            self.PlayerInstancesMap[player_id].UnRegister()
            self.PlayerInstancesMap.pop(player_id)

    def AddEntityClientEvent(self, args):
        # id	str	实体id
        # posX	float	位置x
        # posY	float	位置y
        # posZ	float	位置z
        # dimensionId	int	实体维度
        # isBaby	bool	是否为幼儿
        # engineTypeStr	str	实体类型
        # itemName	str	物品identifier（仅当物品实体时存在该字段）
        # auxValue	int	物品附加值（仅当物品实体时存在该字段）
        entity_id = args["id"]
        engineTypeStr = args["engineTypeStr"]
        if engineTypeStr not in EntityConfig.ClientLoadInstanceEntityMap and engineTypeStr in EntityConfig.DoNotInstanceEntityList:
            return
        if entity_id not in self.MobInstancesMap:
            instance = EntityConfig.ClientLoadInstanceEntityMap.get(engineTypeStr, ClientEntity)
            self.MobInstancesMap[entity_id] = instance(entity_id, args.get("itemName", None), args.get("auxValue", None))
        # if args.get("itemName", None) is None:
        #     for i in range(1, 5):
        #         GetActorRenderComp(entity_id).SetEntityExtraUniforms(i, (1.0, 1.0, 1.0, 1.0))

    def RemoveEntityClientEvent(self, args):
        # id	str	移除的实体id
        entity_id = args["id"]
        if entity_id in self.MobInstancesMap:
            self.MobInstancesMap[entity_id].UnRegister()
            self.MobInstancesMap.pop(entity_id)

    def SyncServerEntityQueryMapEvent(self, args):
        entity_id = args["entity_id"]
        entity_query_map = args["entity_query_map"]
        self.MobQueryValueMap.setdefault(entity_id, {}).update(entity_query_map)
        for query_name, query_value in entity_query_map.iteritems():
            EmptyQueryClientApi.SetQuery(entity_id, query_name, query_value)

    def SyncAllServerEntityQueryMapEvent(self, args):
        all_entity_query_map = args["all_entity_query_map"]
        self.MobQueryValueMap = all_entity_query_map
        for entity_id, entity_query_map in all_entity_query_map.iteritems():
            for query_name, query_value in entity_query_map.iteritems():
                EmptyQueryClientApi.SetQuery(entity_id, query_name, query_value)

    def OnChangeEntityQueryToAllClientServerEvent(self, args):
        client_id = args.get("__id__", None)
        entity_id = args["entity_id"]
        query_name = args["query_name"]
        query_value = args["query_value"]
        self.MobQueryValueMap.setdefault(entity_id, {})[query_name] = query_value
        if client_id == LocalPlayerId:
            return
        EmptyQueryClientApi.SetQuery(entity_id, query_name, query_value)

    def CreateBreakBlockEntityEvent(self, args):
        class TempClass(object):
            def __init__(self):
                self.retry_block_entity_id_count_dict = {}

            def AddActorBlockGeometry(self, block_entity_id, BlockPaletteName):
                self.retry_block_entity_id_count_dict[block_entity_id] = self.retry_block_entity_id_count_dict.setdefault(block_entity_id, 0) + 1
                if EmptyGameClientApi.GetEntityIsAlive(block_entity_id):
                    res = GetActorRenderComp(block_entity_id).AddActorBlockGeometry(BlockPaletteName)
                    if res:
                        return
                if self.retry_block_entity_id_count_dict[block_entity_id] < 10:
                    EmptyGameClientApi.AddTimer(0.03, self.AddActorBlockGeometry, block_entity_id, BlockPaletteName)

        temp_class_instance = TempClass()
        block_pos_palette_dict = args["block_pos_palette_dict"]
        block_pos_with_entity_id_dict = args["block_pos_with_entity_id_dict"]
        for block_pos, block_palette_dict in block_pos_palette_dict.iteritems():
            for block_dict in block_palette_dict["common"]:
                block_name, block_aux = block_dict
                block_palette_name = "%s%s" % (block_name, block_aux)
                if block_palette_name not in self.BlockPaletteGeometryList:
                    geometry_name = CompBlockGeometry.CombineBlockPaletteToGeometry(EmptyBlockClientApi.DeserializeBlockPalette(block_palette_dict),
                                                                                    block_palette_name, 1)
                    if geometry_name:
                        self.BlockPaletteGeometryList.append(geometry_name)
                entity_id = block_pos_with_entity_id_dict[block_pos]
                GetModelComp(entity_id).SetEntityShadowShow(False)
                temp_class_instance.AddActorBlockGeometry(entity_id, block_palette_name)
