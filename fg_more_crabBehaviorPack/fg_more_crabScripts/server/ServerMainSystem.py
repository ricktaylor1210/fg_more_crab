# -*- coding: utf-8 -*-
import copy
import math
import random

from ..ModMainConfig import *

import mod.common.minecraftEnum as MinecraftEnum
import mod.server.extraServerApi as ServerApi


ServerSystem = ServerApi.GetServerSystemCls()
ServerEngineNameSpace = ServerApi.GetEngineNamespace()
ServerEngineSystemName = ServerApi.GetEngineSystemName()
CompFactory = ServerApi.GetEngineCompFactory()


SERVER_TICKS_PER_SECOND = 30

WATER_BLOCKS = set([
    "minecraft:water",
    "minecraft:flowing_water",
])

PASSABLE_BLOCKS = set([
    "minecraft:air",
    "minecraft:water",
    "minecraft:flowing_water",
    "minecraft:tall_grass",
    "minecraft:grass",
    "minecraft:seagrass",
    "minecraft:kelp",
    "minecraft:kelp_plant",
    "minecraft:snow_layer",
])

COAST_GROUND_BLOCKS = set([
    "minecraft:sand",
    "minecraft:red_sand",
    "minecraft:gravel",
    "minecraft:clay",
    "minecraft:mud",
])

STRUCTURE_BLOCKS = set([
    "minecraft:barrel",
    "minecraft:chest",
    "minecraft:trapped_chest",
    "minecraft:planks",
    "minecraft:wooden_planks",
    "minecraft:oak_planks",
    "minecraft:spruce_planks",
    "minecraft:birch_planks",
    "minecraft:jungle_planks",
    "minecraft:acacia_planks",
    "minecraft:dark_oak_planks",
    "minecraft:mangrove_planks",
    "minecraft:oak_log",
    "minecraft:spruce_log",
    "minecraft:birch_log",
    "minecraft:jungle_log",
    "minecraft:acacia_log",
    "minecraft:dark_oak_log",
    "minecraft:mangrove_log",
])

PIRATE_ENTITY_TYPES = set([
    "fg:pirate_crab_sailor",
    "fg:pirate_crab_captain",
    "fg:pirate_crab_artillery",
])

NORMAL_CRAB_ENTITY_TYPES = set([
    "fg:crab_sandy",
    "fg:crab_red_tide",
    "fg:crab_blue_tide",
    "fg:crab_frost_shell",
    "fg:crab_coral",
    "fg:crab_dusk_shell",
    "fg:crab_moss_shell",
])

NORMAL_CRAB_DEFAULT_NAMES = {
    "fg:crab_sandy": u"沙壳蟹",
    "fg:crab_red_tide": u"赤潮蟹",
    "fg:crab_blue_tide": u"蓝潮蟹",
    "fg:crab_frost_shell": u"霜壳蟹",
    "fg:crab_coral": u"珊瑚蟹",
    "fg:crab_dusk_shell": u"暮潮蟹",
    "fg:crab_moss_shell": u"潮苔蟹",
}

PIRATE_SPAWN_WEIGHTS = [
    ("fg:pirate_crab_sailor", 7),
    ("fg:pirate_crab_captain", 2),
    ("fg:pirate_crab_artillery", 1),
]

PIRATE_STEAL_PRIORITY = {
    "minecraft:diamond": 0,
    "minecraft:emerald": 1,
    "minecraft:gold_ingot": 2,
    "minecraft:raw_gold": 3,
    "minecraft:golden_apple": 4,
    "minecraft:enchanted_golden_apple": 5,
    "minecraft:gold_nugget": 6,
    "minecraft:filled_map": 7,
    "minecraft:map": 8,
}

PIRATE_HIDEOUT_LOOT = [
    ("minecraft:gold_nugget", 3, 7, 1.0),
    ("minecraft:bread", 1, 2, 0.7),
    ("minecraft:map", 1, 1, 0.55),
    ("minecraft:emerald", 1, 1, 0.18),
    ("fg:crab_shell_powder", 1, 2, 0.45),
]

BOSS_ENTITY_TYPES = set([
    "fg:crab_boss_lava",
    "fg:crab_boss_ice",
    "fg:crab_boss_poisonous_swamp",
    "fg:crab_boss_tidal",
    "fg:crab_boss_sound_guard",
])

BOSS_LAIR_CHEST_OFFSETS = [
    (-6, 0, -8),
    (6, 0, -8),
    (0, 0, 9),
]

BOSS_CRAB_CONFIG = {
    "fg:crab_boss_lava": {
        "skill_effects": [("weakness", 4, 0)],
        "skill_damage": 5,
        "skill_particle": "minecraft:basic_flame_particle",
        "minion": "fg:crab_aggressive",
    },
    "fg:crab_boss_ice": {
        "skill_effects": [("slowness", 5, 1), ("mining_fatigue", 4, 0)],
        "skill_damage": 3,
        "skill_particle": "minecraft:basic_crit_particle",
        "minion": "fg:crab_frost_shell",
    },
    "fg:crab_boss_poisonous_swamp": {
        "skill_effects": [("poison", 5, 0), ("slowness", 4, 0)],
        "skill_damage": 2,
        "skill_particle": "minecraft:basic_smoke_particle",
        "minion": "fg:crab_moss_shell",
    },
    "fg:crab_boss_tidal": {
        "skill_effects": [("slowness", 4, 1)],
        "skill_damage": 4,
        "skill_particle": "minecraft:water_evaporation_actor_emitter",
        "minion": "fg:crab_blue_tide",
    },
    "fg:crab_boss_sound_guard": {
        "skill_effects": [("nausea", 5, 0), ("weakness", 4, 0)],
        "skill_damage": 4,
        "skill_particle": "minecraft:sonic_explosion",
        "minion": "fg:crab_aggressive",
    },
}

BOSS_LAIR_CONFIG = [
    {
        "entity_type": "fg:crab_boss_lava",
        "structure": "fg_more_crab:boss_lair_lava",
        "structure_size": (33, 14, 33),
        "dimension": 0,
        "ground_blocks": set(["minecraft:netherrack", "minecraft:basalt", "minecraft:blackstone"]),
        "floor_block": "minecraft:blackstone",
        "marker_block": "minecraft:magma",
        "pillar_block": "minecraft:basalt",
        "hazard_block": "minecraft:fire",
        "chance": 0.14,
    },
    {
        "entity_type": "fg:crab_boss_ice",
        "structure": "fg_more_crab:boss_lair_ice",
        "structure_size": (33, 14, 33),
        "dimension": 0,
        "ground_blocks": set(["minecraft:snow", "minecraft:ice", "minecraft:packed_ice", "minecraft:grass", "minecraft:dirt"]),
        "floor_block": "minecraft:packed_ice",
        "marker_block": "minecraft:snow",
        "pillar_block": "minecraft:ice",
        "hazard_block": "minecraft:snow_layer",
        "chance": 0.10,
    },
    {
        "entity_type": "fg:crab_boss_poisonous_swamp",
        "structure": "fg_more_crab:boss_lair_poisonous_swamp",
        "structure_size": (33, 12, 33),
        "dimension": 0,
        "ground_blocks": set(["minecraft:mud", "minecraft:grass", "minecraft:dirt", "minecraft:clay"]),
        "floor_block": "minecraft:mud",
        "marker_block": "minecraft:moss_block",
        "pillar_block": "minecraft:clay",
        "hazard_block": "minecraft:slime_block",
        "chance": 0.10,
    },
    {
        "entity_type": "fg:crab_boss_tidal",
        "structure": "fg_more_crab:boss_lair_tidal",
        "structure_size": (35, 12, 35),
        "dimension": 0,
        "ground_blocks": set(["minecraft:sand", "minecraft:gravel", "minecraft:clay"]),
        "floor_block": "minecraft:prismarine",
        "marker_block": "minecraft:sea_lantern",
        "pillar_block": "minecraft:dark_prismarine",
        "hazard_block": "minecraft:water",
        "chance": 0.10,
    },
    {
        "entity_type": "fg:crab_boss_sound_guard",
        "structure": "fg_more_crab:boss_temple_sound_guard",
        "structure_size": (39, 16, 39),
        "dimension": 0,
        "ground_blocks": set(["minecraft:stone", "minecraft:deepslate", "minecraft:calcite", "minecraft:tuff"]),
        "floor_block": "minecraft:calcite",
        "marker_block": "minecraft:amethyst_block",
        "pillar_block": "minecraft:deepslate",
        "hazard_block": "minecraft:amethyst_block",
        "chance": 0.08,
    },
]

BOSS_LAIR_CHEST_LOOT_TABLES = {
    "fg:crab_boss_lava": "loot_tables/chests/fg_boss_lair_lava.json",
    "fg:crab_boss_ice": "loot_tables/chests/fg_boss_lair_ice.json",
    "fg:crab_boss_poisonous_swamp": "loot_tables/chests/fg_boss_lair_poisonous_swamp.json",
    "fg:crab_boss_tidal": "loot_tables/chests/fg_boss_lair_tidal.json",
    "fg:crab_boss_sound_guard": "loot_tables/chests/fg_boss_temple_sound_guard.json",
}

BOSS_LAIR_FALLBACK_LOOT = {
    "fg:crab_boss_lava": [
        ("minecraft:bread", 1, 3, 1.0),
        ("minecraft:blaze_rod", 1, 2, 0.40),
        ("fg:crab_shell_powder", 2, 4, 0.70),
        ("minecraft:map", 1, 1, 0.35),
    ],
    "fg:crab_boss_ice": [
        ("minecraft:bread", 1, 3, 1.0),
        ("minecraft:packed_ice", 2, 5, 0.55),
        ("fg:crab_shell_powder", 2, 4, 0.70),
        ("minecraft:map", 1, 1, 0.35),
    ],
    "fg:crab_boss_poisonous_swamp": [
        ("minecraft:bread", 1, 3, 1.0),
        ("minecraft:slime_ball", 2, 5, 0.55),
        ("fg:crab_shell_powder", 2, 4, 0.70),
        ("minecraft:map", 1, 1, 0.35),
    ],
    "fg:crab_boss_tidal": [
        ("minecraft:dried_kelp", 2, 5, 1.0),
        ("minecraft:prismarine_shard", 2, 5, 0.55),
        ("fg:crab_shell_powder", 2, 4, 0.70),
        ("minecraft:map", 1, 1, 0.35),
    ],
    "fg:crab_boss_sound_guard": [
        ("minecraft:bread", 1, 3, 1.0),
        ("minecraft:amethyst_shard", 2, 5, 0.55),
        ("fg:crab_shell_powder", 2, 4, 0.70),
        ("minecraft:map", 1, 1, 0.35),
    ],
}

CRAB_BACKPACK_ITEM = "fg:crab_backpack"
CRAB_BACKPACK_INVENTORY_SIZE = 27
CRAB_BACKPACK_NAME_DEBUG = False
CRAB_BACKPACK_CONTAINER_TITLE = u"蟹壳背包"
CRAB_BACKPACK_UNKNOWN_TITLE = u"未知"
SHEARS_ITEM = "minecraft:shears"
SHEARS_MAX_DAMAGE = 238

CRAB_SHELL_SHIELD_ITEM = "fg:crab_shell_shield"
CRAB_SHELL_SHIELD_DAMAGE_REDUCTION = 0.65
CRAB_SHELL_SHIELD_COOLDOWN_TICKS = SERVER_TICKS_PER_SECOND // 2
CRAB_SHELL_SHIELD_MAX_DAMAGE = 180
CRAB_SHELL_SHIELD_FRONT_DOT = 0.15
CRAB_SHELL_SHIELD_DEFENCE_LEFT = -90.0
CRAB_SHELL_SHIELD_DEFENCE_RIGHT = 90.0
BOSS_WEAPON_ACTIVE_COOLDOWN_TICKS = SERVER_TICKS_PER_SECOND * 12
BOSS_LAIR_RESPAWN_INTERVAL_TICKS = SERVER_TICKS_PER_SECOND * 60 * 20 * 3
BOSS_LAIR_COMBAT_RADIUS = 96.0

BOSS_WEAPON_EFFECTS = {
    "fg:frost_crystal_crab_spear": {
        "effects": [("slowness", 5, 2), ("mining_fatigue", 4, 0)],
        "extra_damage": 2.0,
        "particle": "minecraft:basic_crit_particle",
        "max_damage": 900,
    },
    "fg:swamp_poison_pliers": {
        "effects": [("poison", 6, 2)],
        "extra_damage": 1.0,
        "particle": "minecraft:basic_smoke_particle",
        "max_damage": 900,
    },
    "fg:tide_striker": {
        "effects": [("slowness", 3, 1)],
        "extra_damage": 1.5,
        "particle": "minecraft:water_evaporation_actor_emitter",
        "push": 0.28,
        "max_damage": 1000,
    },
    "fg:lava_battle_axe": {
        "effects": [("weakness", 3, 0)],
        "extra_damage": 3.0,
        "particle": "minecraft:basic_flame_particle",
        "fire_seconds": 4,
        "max_damage": 1100,
    },
    "fg:sound_following_giant_blade": {
        "effects": [("nausea", 4, 0), ("weakness", 3, 0)],
        "extra_damage": 2.5,
        "particle": "minecraft:sonic_explosion",
        "push": 0.34,
        "max_damage": 1200,
    },
}

BOSS_WEAPON_ACTIVE_EFFECTS = {
    "fg:lava_battle_axe": {
        "radius": 4.5,
        "damage": 5.0,
        "cause": "fire",
        "effects": [("weakness", 4, 0)],
        "particle": "minecraft:basic_flame_particle",
        "sound": "random.explode",
        "fire_seconds": 5,
        "temporary_block": "minecraft:fire",
        "max_damage": 1100,
    },
    "fg:frost_crystal_crab_spear": {
        "radius": 4.0,
        "damage": 3.5,
        "cause": "freezing",
        "effects": [("slowness", 5, 2), ("mining_fatigue", 4, 0)],
        "particle": "minecraft:basic_crit_particle",
        "sound": "random.glass",
        "temporary_block": "minecraft:snow_layer",
        "max_damage": 900,
    },
    "fg:swamp_poison_pliers": {
        "radius": 4.0,
        "damage": 2.5,
        "cause": "magic",
        "effects": [("poison", 6, 1), ("slowness", 4, 0)],
        "particle": "minecraft:basic_smoke_particle",
        "sound": "random.fizz",
        "temporary_block": "minecraft:slime_block",
        "max_damage": 900,
    },
    "fg:tide_striker": {
        "radius": 5.0,
        "damage": 3.5,
        "cause": "drowning",
        "effects": [("slowness", 4, 1)],
        "particle": "minecraft:water_evaporation_actor_emitter",
        "sound": "liquid.water",
        "pull": 0.30,
        "temporary_block": "minecraft:flowing_water",
        "max_damage": 1000,
    },
    "fg:sound_following_giant_blade": {
        "radius": 5.0,
        "damage": 5.0,
        "cause": "magic",
        "effects": [("nausea", 4, 0), ("weakness", 4, 0)],
        "particle": "minecraft:sonic_explosion",
        "sound": "mob.warden.sonic_boom",
        "push": 0.36,
        "max_damage": 1200,
    },
}

BOSS_ARMOR_SETS = {
    "frost": {
        "items": [
            "fg:frost_crab_helmet",
            "fg:frost_crab_chestplate",
            "fg:frost_crab_leggings",
            "fg:frost_crab_boots",
        ],
        "effects": [("resistance", 2, 0), ("speed", 2, 0)],
        "aura_effects": [("slowness", 2, 0)],
    },
    "venom": {
        "items": [
            "fg:poisonous_swamp_crab_helmet",
            "fg:poisonous_swamp_crab_chestplate",
            "fg:poisonous_swamp_crab_leggings",
            "fg:poisonous_swamp_crab_boots",
        ],
        "effects": [("regeneration", 2, 0)],
        "remove_effects": ["poison"],
    },
    "tidal": {
        "items": [
            "fg:tidal_crab_helmet",
            "fg:tidal_crab_chestplate",
            "fg:tidal_crab_leggings",
            "fg:tidal_crab_boots",
        ],
        "effects": [("water_breathing", 4, 0), ("night_vision", 4, 0), ("speed", 2, 0)],
        "push_aura": 0.24,
    },
    "blazing": {
        "items": [
            "fg:blazing_crab_helmet",
            "fg:blazing_crab_chestplate",
            "fg:blazing_crab_leggings",
            "fg:blazing_crab_boots",
        ],
        "effects": [("fire_resistance", 4, 0), ("strength", 2, 0)],
    },
    "echo": {
        "items": [
            "fg:abyssal_echo_crab_helmet",
            "fg:abyssal_echo_crab_chestplate",
            "fg:abyssal_echo_crab_leggings",
            "fg:abyssal_echo_crab_boots",
        ],
        "effects": [("night_vision", 4, 0), ("resistance", 2, 0)],
        "aura_effects": [("glowing", 2, 0)],
    },
}


MINERAL_CRAB_CONFIG = {
    "fg:mineral_crab_coal": {
        "ore_blocks": set(["minecraft:coal_ore", "minecraft:deepslate_coal_ore"]),
        "seek_speed": 0.13,
        "eat_distance": 1.75,
        "scan_radius": 5,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 16,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 24,
    },
    "fg:mineral_crab_copper": {
        "ore_blocks": set(["minecraft:copper_ore", "minecraft:deepslate_copper_ore"]),
        "seek_speed": 0.12,
        "eat_distance": 1.75,
        "scan_radius": 5,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 18,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 28,
        "damage_reduction": 0.20,
    },
    "fg:mineral_crab_iron": {
        "ore_blocks": set(["minecraft:iron_ore", "minecraft:deepslate_iron_ore"]),
        "seek_speed": 0.11,
        "eat_distance": 1.75,
        "scan_radius": 5,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 20,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 30,
        "damage_reduction": 0.35,
    },
    "fg:mineral_crab_gold": {
        "ore_blocks": set(["minecraft:gold_ore", "minecraft:deepslate_gold_ore", "minecraft:nether_gold_ore"]),
        "seek_speed": 0.15,
        "eat_distance": 1.75,
        "scan_radius": 5,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 18,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 32,
    },
    "fg:mineral_crab_redstone": {
        "ore_blocks": set([
            "minecraft:redstone_ore",
            "minecraft:lit_redstone_ore",
            "minecraft:deepslate_redstone_ore",
            "minecraft:lit_deepslate_redstone_ore",
        ]),
        "seek_speed": 0.15,
        "eat_distance": 1.75,
        "scan_radius": 6,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 16,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 34,
    },
    "fg:mineral_crab_lapis_lazuli": {
        "ore_blocks": set(["minecraft:lapis_ore", "minecraft:deepslate_lapis_ore"]),
        "seek_speed": 0.12,
        "eat_distance": 1.75,
        "scan_radius": 6,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 22,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 34,
    },
    "fg:mineral_crab_emerald": {
        "ore_blocks": set(["minecraft:emerald_ore", "minecraft:deepslate_emerald_ore"]),
        "seek_speed": 0.16,
        "eat_distance": 1.75,
        "scan_radius": 5,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 18,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 38,
        "heal": 4.0,
    },
    "fg:mineral_crab_diamond": {
        "ore_blocks": set(["minecraft:diamond_ore", "minecraft:deepslate_diamond_ore"]),
        "seek_speed": 0.10,
        "eat_distance": 1.75,
        "scan_radius": 5,
        "scan_y": 3,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 22,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 42,
        "damage_reduction": 0.55,
    },
    "fg:mineral_crab_quartz": {
        "ore_blocks": set(["minecraft:quartz_ore", "minecraft:nether_quartz_ore"]),
        "seek_speed": 0.14,
        "eat_distance": 1.75,
        "scan_radius": 6,
        "scan_y": 4,
        "buff_ticks": SERVER_TICKS_PER_SECOND * 20,
        "cooldown_ticks": SERVER_TICKS_PER_SECOND * 32,
        "heal": 3.0,
        "damage_reduction": 0.25,
    },
}


class ServerMainSystem(ServerSystem):
    def __init__(self, namespace, system_name):
        super(ServerMainSystem, self).__init__(namespace, system_name)
        self._destroyed = False
        self._tick = 0
        self._mineral_next_scan_tick = {}
        self._mineral_target_pos = {}
        self._mineral_target_stand_pos = {}
        self._mineral_buff_until_tick = {}
        self._pirate_next_steal_tick = {}
        self._pirate_stolen_item = {}
        self._pirate_escape_until_tick = {}
        self._pirate_home_pos = {}
        self._entity_last_pos = {}
        self._structure_spawn_cooldown = {}
        self._pirate_hideout_buckets = set()
        self._shield_cooldown_until = {}
        self._boss_weapon_active_cooldown_until = {}
        self._boss_phase = {}
        self._boss_next_skill_tick = {}
        self._boss_lair_buckets = set()
        self._boss_lair_anchor_by_bucket = {}
        self._boss_lair_next_respawn_tick = {}
        self._temporary_blocks = {}
        self._pending_backpack_unequip = {}
        self._normal_crab_default_named = set()
        self._backpack_name_debug_seen = set()
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 10)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "MobDieEvent", self, self.MobDieEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "EntityRemoveEvent", self, self.EntityRemoveEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "DamageEvent", self, self.DamageEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerInteractServerEvent", self, self.PlayerInteractServerEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerDoInteractServerEvent", self, self.PlayerDoInteractServerEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "ServerItemTryUseEvent", self, self.ServerItemTryUseEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnPlayerActiveShieldServerEvent", self, self.OnPlayerActiveShieldServerEvent, 0)
        self.ListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnPlayerBlockedByShieldAfterServerEvent", self, self.OnPlayerBlockedByShieldAfterServerEvent, 0)

    def DestroySystem(self):
        if self._destroyed:
            return
        self._destroyed = True
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnScriptTickServer", self, self.OnScriptTickServer, 10)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "MobDieEvent", self, self.MobDieEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "EntityRemoveEvent", self, self.EntityRemoveEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "DamageEvent", self, self.DamageEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerInteractServerEvent", self, self.PlayerInteractServerEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "PlayerDoInteractServerEvent", self, self.PlayerDoInteractServerEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "ServerItemTryUseEvent", self, self.ServerItemTryUseEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnPlayerActiveShieldServerEvent", self, self.OnPlayerActiveShieldServerEvent, 0)
        self.UnListenForEvent(ServerEngineNameSpace, ServerEngineSystemName, "OnPlayerBlockedByShieldAfterServerEvent", self, self.OnPlayerBlockedByShieldAfterServerEvent, 0)

    def _short_error_text(self, error):
        try:
            text = "%s: %s" % (error.__class__.__name__, error)
        except Exception:
            text = str(error.__class__.__name__)
        if len(text) > 160:
            text = text[:157] + "..."
        return text

    def _log_validation_failure(self, event_name, data=None):
        payload = data or {}
        try:
            SetDevelopmentMessage(logging.ERROR, "validation.%s %s", event_name, payload)
        except Exception:
            if IN_DEVELOPMENT:
                raise

    def OnScriptTickServer(self):
        if self._destroyed:
            return
        self._tick += 1
        if self._tick % 10 == 0:
            self._tick_active_crabs()
            self._tick_boss_armor_players()
            self._tick_temporary_blocks()
            self._tick_pending_backpack_unequip()
        if self._tick % 120 == 0:
            self._tick_pirate_structure_spawns()
        if self._tick % 240 == 0:
            self._tick_boss_lair_spawns()

    def MobDieEvent(self, args):
        entity_id = args.get("id", None)
        self._drop_pirate_stolen_item(entity_id)
        self._cleanup_entity_state(entity_id)

    def EntityRemoveEvent(self, args):
        entity_id = args.get("id", None)
        if entity_id in self._pirate_stolen_item:
            self._drop_pirate_stolen_item(entity_id)
        self._cleanup_entity_state(entity_id)

    def DamageEvent(self, args):
        entity_id = args.get("entityId", None)
        if not entity_id or args.get("damage", 0) <= 0:
            return

        self._apply_crab_shell_shield_damage_reduction(args)
        self._apply_boss_weapon_hit_effects(args)
        self._apply_boss_armor_damage_reactions(args)

        if self._tick >= self._mineral_buff_until_tick.get(entity_id, 0):
            return

        entity_type = self._get_entity_type(entity_id)
        config = MINERAL_CRAB_CONFIG.get(entity_type, None)
        if not config:
            return

        reduction = float(config.get("damage_reduction", 0.0) or 0.0)
        if reduction <= 0:
            return
        args["damage"] = max(0.0, float(args["damage"]) * (1.0 - reduction))
        if reduction >= 0.5:
            args["knock"] = False

    def PlayerInteractServerEvent(self, args):
        player_id = args.get("playerId", None)
        entity_id = self._get_interact_target_id(args)
        entity_type = self._get_entity_type(entity_id)
        if entity_type in NORMAL_CRAB_ENTITY_TYPES:
            self._debug_backpack_name("PlayerInteractServerEvent", entity_id, {
                "player_id": player_id,
                "entity_type": entity_type,
                "current_name": self._get_entity_custom_name(entity_id),
                "has_tamed_component": self._entity_has_component(entity_id, "minecraft:is_tamed"),
                "fg_is_tamed": self._get_entity_property_value(entity_id, "fg:is_tamed"),
                "has_inventory": self._entity_has_component(entity_id, "minecraft:inventory"),
            })
            self._ensure_tamed_normal_crab_default_name(entity_id, entity_type)
        self._ensure_crab_backpack_container_title(entity_id)
        if self._get_crab_backpack_unequip_shears_slot(player_id, entity_id) is None:
            return
        if not self._is_entity_owner(entity_id, player_id):
            args["cancel"] = True
            return
        inventory_empty = self._is_entity_inventory_empty(entity_id, CRAB_BACKPACK_INVENTORY_SIZE)
        if inventory_empty is not True:
            args["cancel"] = True
            self._show_backpack_blocked_particle(entity_id)
            return
        self._pending_backpack_unequip[(player_id, entity_id)] = self._tick + 8

    def PlayerDoInteractServerEvent(self, args):
        player_id = args.get("playerId", None)
        entity_id = self._get_interact_target_id(args)
        entity_type = self._get_entity_type(entity_id)
        if entity_type in NORMAL_CRAB_ENTITY_TYPES:
            self._debug_backpack_name("PlayerDoInteractServerEvent", entity_id, {
                "player_id": player_id,
                "entity_type": entity_type,
                "current_name": self._get_entity_custom_name(entity_id),
                "has_tamed_component": self._entity_has_component(entity_id, "minecraft:is_tamed"),
                "fg_is_tamed": self._get_entity_property_value(entity_id, "fg:is_tamed"),
                "has_inventory": self._entity_has_component(entity_id, "minecraft:inventory"),
            })
            self._ensure_tamed_normal_crab_default_name(entity_id, entity_type)
        self._ensure_crab_backpack_container_title(entity_id)
        pending_key = (player_id, entity_id)
        pending_until = self._pending_backpack_unequip.pop(pending_key, 0)
        if pending_until < self._tick:
            return
        shears_slot = self._get_crab_shears_interact_slot(player_id, entity_id)
        if shears_slot is None:
            return
        if not self._is_entity_owner(entity_id, player_id):
            return
        inventory_empty = self._is_entity_inventory_empty(entity_id, CRAB_BACKPACK_INVENTORY_SIZE)
        if inventory_empty is not True:
            self._show_backpack_blocked_particle(entity_id)
            return
        if self._trigger_entity_event(entity_id, "fg:unequip_backpack"):
            self._clear_crab_backpack_container_title(entity_id)
            self._damage_player_item(player_id, shears_slot, SHEARS_MAX_DAMAGE)
        else:
            self._show_backpack_blocked_particle(entity_id)

    def ServerItemTryUseEvent(self, args):
        player_id = args.get("playerId", None) or args.get("entityId", None)
        item_dict = args.get("itemDict", None) or {}
        item_name = self._get_item_name(item_dict)
        if item_name in BOSS_WEAPON_EFFECTS:
            if self._try_cast_boss_weapon_active_skill(player_id, item_name):
                args["cancel"] = True
            return
        if item_name == CRAB_SHELL_SHIELD_ITEM:
            self._refresh_crab_shell_shield_defence_angle(player_id)

    def OnPlayerActiveShieldServerEvent(self, args):
        player_id = args.get("playerId", None)
        item_dict = args.get("itemDict", None) or {}
        item_name = self._get_item_name(item_dict)
        if item_name != CRAB_SHELL_SHIELD_ITEM:
            return
        self._refresh_crab_shell_shield_defence_angle(player_id)

    def OnPlayerBlockedByShieldAfterServerEvent(self, args):
        player_id = args.get("playerId", None)
        item_dict = args.get("itemDict", None) or {}
        item_name = self._get_item_name(item_dict)
        if item_name != CRAB_SHELL_SHIELD_ITEM:
            return
        shield_slot = self._find_player_held_item(player_id, CRAB_SHELL_SHIELD_ITEM)
        if shield_slot is None:
            return
        self._shield_cooldown_until[player_id] = self._tick + CRAB_SHELL_SHIELD_COOLDOWN_TICKS
        self._damage_player_item(player_id, shield_slot, CRAB_SHELL_SHIELD_MAX_DAMAGE)

    def _tick_active_crabs(self):
        for entity_id, entity_type in self._iter_loaded_crab_entities():
            if entity_type in NORMAL_CRAB_ENTITY_TYPES:
                self._tick_normal_crab(entity_id, entity_type)
            elif entity_type in MINERAL_CRAB_CONFIG:
                self._tick_mineral_crab(entity_id, entity_type)
            elif entity_type in PIRATE_ENTITY_TYPES:
                self._tick_pirate_crab(entity_id, entity_type)
            elif entity_type in BOSS_CRAB_CONFIG:
                self._tick_boss_crab(entity_id, entity_type)

    def _iter_loaded_crab_entities(self):
        players = ServerApi.GetPlayerList() or []
        seen = set()
        for player_id in players:
            player_pos = self._get_entity_pos(player_id)
            dimension_id = self._get_entity_dimension(player_id)
            if player_pos is None or dimension_id is None:
                continue
            start_pos = (player_pos[0] - 48, player_pos[1] - 32, player_pos[2] - 48)
            end_pos = (player_pos[0] + 48, player_pos[1] + 32, player_pos[2] + 48)
            entity_list = self._get_entities_in_square(start_pos, end_pos, dimension_id) or []
            for entity_id in entity_list:
                if entity_id in seen:
                    continue
                seen.add(entity_id)
                entity_type = self._get_entity_type(entity_id)
                if entity_type in NORMAL_CRAB_ENTITY_TYPES or entity_type in MINERAL_CRAB_CONFIG or entity_type in PIRATE_ENTITY_TYPES or entity_type in BOSS_CRAB_CONFIG:
                    yield entity_id, entity_type

    def _tick_normal_crab(self, entity_id, entity_type):
        if not self._is_entity_alive(entity_id):
            self._cleanup_entity_state(entity_id)
            return
        self._ensure_tamed_normal_crab_default_name(entity_id, entity_type)

    def _tick_mineral_crab(self, entity_id, entity_type):
        if not self._is_entity_alive(entity_id):
            self._cleanup_entity_state(entity_id)
            return

        pos = self._get_entity_pos(entity_id)
        dimension_id = self._get_entity_dimension(entity_id)
        if pos is None or dimension_id is None:
            return
        self._entity_last_pos[entity_id] = (pos, dimension_id)

        buff_until = self._mineral_buff_until_tick.get(entity_id, 0)
        if buff_until and self._tick >= buff_until:
            self._trigger_entity_event(entity_id, "fg:clear_ore_energy")
            self._mineral_buff_until_tick.pop(entity_id, None)
            self._mineral_target_pos.pop(entity_id, None)
            self._mineral_target_stand_pos.pop(entity_id, None)
            self._mineral_next_scan_tick[entity_id] = self._tick + MINERAL_CRAB_CONFIG[entity_type]["cooldown_ticks"]
            return

        if buff_until:
            return

        if self._tick < self._mineral_next_scan_tick.get(entity_id, 0):
            return

        config = MINERAL_CRAB_CONFIG[entity_type]
        target_pos = self._mineral_target_pos.get(entity_id, None)
        target_stand_pos = self._mineral_target_stand_pos.get(entity_id, None)
        if (
                (not self._is_matching_block(target_pos, dimension_id, config["ore_blocks"])) or
                (not self._is_valid_entity_stand_pos(target_stand_pos, dimension_id)) or
                (not self._has_clear_path_to_stand(pos, target_stand_pos, dimension_id))
        ):
            target_info = self._find_nearest_ore_target(
                pos,
                dimension_id,
                config["ore_blocks"],
                config["scan_radius"],
                config["scan_y"]
            )
            if target_info is None:
                self._mineral_next_scan_tick[entity_id] = self._tick + SERVER_TICKS_PER_SECOND
                return
            target_pos, target_stand_pos = target_info
            self._mineral_target_pos[entity_id] = target_pos
            self._mineral_target_stand_pos[entity_id] = target_stand_pos

        target_center = (target_pos[0] + 0.5, target_pos[1] + 0.5, target_pos[2] + 0.5)
        if self._distance_sq(pos, target_center) <= config["eat_distance"] * config["eat_distance"]:
            if self._consume_matching_block(target_pos, dimension_id, config["ore_blocks"]):
                self._trigger_entity_event(entity_id, "fg:activate_ore_energy")
                self._mineral_buff_until_tick[entity_id] = self._tick + config["buff_ticks"]
                self._mineral_next_scan_tick[entity_id] = self._tick + config["buff_ticks"] + config["cooldown_ticks"]
                self._mineral_target_pos.pop(entity_id, None)
                self._mineral_target_stand_pos.pop(entity_id, None)
                self._heal_entity(entity_id, config.get("heal", 0.0))
            else:
                self._mineral_target_pos.pop(entity_id, None)
                self._mineral_target_stand_pos.pop(entity_id, None)
                self._mineral_next_scan_tick[entity_id] = self._tick + SERVER_TICKS_PER_SECOND
            return

        stand_center = (target_stand_pos[0] + 0.5, target_stand_pos[1], target_stand_pos[2] + 0.5)
        self._push_entity_towards(entity_id, pos, stand_center, config["seek_speed"])
        self._mineral_next_scan_tick[entity_id] = self._tick + 10

    def _tick_pirate_crab(self, entity_id, entity_type):
        if not self._is_entity_alive(entity_id):
            self._drop_pirate_stolen_item(entity_id)
            self._cleanup_entity_state(entity_id)
            return

        pos = self._get_entity_pos(entity_id)
        dimension_id = self._get_entity_dimension(entity_id)
        if pos is None or dimension_id is None:
            return
        self._entity_last_pos[entity_id] = (pos, dimension_id)

        if entity_id in self._pirate_stolen_item:
            escape_until = self._pirate_escape_until_tick.get(entity_id, 0)
            if escape_until and self._tick < escape_until:
                self._trigger_entity_event(entity_id, "fg:pirate_escape")
                self._move_pirate_to_escape_target(entity_id, pos, dimension_id)
            elif escape_until:
                self._trigger_entity_event(entity_id, "fg:clear_pirate_escape")
                self._pirate_escape_until_tick.pop(entity_id, None)
            return

        if self._tick < self._pirate_next_steal_tick.get(entity_id, 0):
            return

        player_id = self._find_nearest_player(pos, dimension_id, 5.0)
        if not player_id:
            return

        stolen_item = self._take_one_valuable_item(player_id)
        if not stolen_item:
            self._pirate_next_steal_tick[entity_id] = self._tick + SERVER_TICKS_PER_SECOND * 3
            return

        self._pirate_stolen_item[entity_id] = stolen_item
        self._pirate_escape_until_tick[entity_id] = self._tick + SERVER_TICKS_PER_SECOND * 24
        self._pirate_next_steal_tick[entity_id] = self._tick + SERVER_TICKS_PER_SECOND * 20
        self._trigger_entity_event(entity_id, "fg:pirate_escape")
        self._trigger_entity_event(entity_id, "fg:pirate_rally")
        self._move_pirate_to_escape_target(entity_id, pos, dimension_id)

    def _tick_pirate_structure_spawns(self):
        players = ServerApi.GetPlayerList() or []
        for player_id in players:
            pos = self._get_entity_pos(player_id)
            dimension_id = self._get_entity_dimension(player_id)
            if pos is None or dimension_id != 0:
                continue

            anchor_pos = self._find_pirate_structure_anchor(pos, dimension_id)
            is_existing_anchor = anchor_pos is not None
            if anchor_pos is None:
                anchor_pos = self._find_coast_hideout_anchor(pos, dimension_id)
                if anchor_pos is None:
                    continue

            bucket = (dimension_id, int(anchor_pos[0]) // 32, int(anchor_pos[2]) // 32)
            if self._tick < self._structure_spawn_cooldown.get(bucket, 0):
                continue

            hideout_created = False
            if (not is_existing_anchor) and bucket not in self._pirate_hideout_buckets:
                if random.random() > 0.25:
                    self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 40
                    continue
                hideout_created = self._create_pirate_hideout(anchor_pos, dimension_id)
                if hideout_created:
                    self._pirate_hideout_buckets.add(bucket)
                    self._spawn_hideout_loot(anchor_pos, dimension_id)

            if self._count_pirates_near(anchor_pos, dimension_id, 24) >= 4:
                self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 20
                continue

            if (not hideout_created) and random.random() > 0.35:
                self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 18
                continue

            spawn_count = 2 if hideout_created else 1
            spawned = 0
            for _idx in range(spawn_count):
                spawn_pos = self._find_pirate_spawn_pos(anchor_pos, dimension_id)
                if spawn_pos is None:
                    continue
                entity_type = self._choose_weighted(PIRATE_SPAWN_WEIGHTS)
                spawn_id = self.CreateEngineEntityByTypeStr(entity_type, spawn_pos, (0, 0), dimension_id, False, True)
                if spawn_id:
                    spawned += 1
                    self._pirate_home_pos[spawn_id] = anchor_pos
            self._structure_spawn_cooldown[bucket] = self._tick + (
                SERVER_TICKS_PER_SECOND * 45 if spawned else SERVER_TICKS_PER_SECOND * 18
            )

    def _tick_boss_crab(self, entity_id, entity_type):
        if not self._is_entity_alive(entity_id):
            self._cleanup_entity_state(entity_id)
            return

        pos = self._get_entity_pos(entity_id)
        dimension_id = self._get_entity_dimension(entity_id)
        if pos is None or dimension_id is None:
            return
        self._entity_last_pos[entity_id] = (pos, dimension_id)

        health_ratio = self._get_entity_health_ratio(entity_id)
        if health_ratio is not None:
            if health_ratio <= 0.33 and self._boss_phase.get(entity_id, 1) < 3:
                self._boss_phase[entity_id] = 3
                self._trigger_entity_event(entity_id, "fg:boss_phase_3")
                self._run_level_command("/particle minecraft:explosion_particle %s %s %s" % (pos[0], pos[1] + 1.0, pos[2]))
            elif health_ratio <= 0.66 and self._boss_phase.get(entity_id, 1) < 2:
                self._boss_phase[entity_id] = 2
                self._trigger_entity_event(entity_id, "fg:boss_phase_2")
                self._run_level_command("/particle minecraft:basic_crit_particle %s %s %s" % (pos[0], pos[1] + 1.0, pos[2]))

        if self._tick < self._boss_next_skill_tick.get(entity_id, 0):
            return

        player_id = self._find_nearest_player(pos, dimension_id, 18.0)
        if not player_id:
            self._boss_next_skill_tick[entity_id] = self._tick + SERVER_TICKS_PER_SECOND * 2
            return

        self._cast_boss_skill(entity_id, entity_type, player_id)
        phase = self._boss_phase.get(entity_id, 1)
        self._boss_next_skill_tick[entity_id] = self._tick + max(
            SERVER_TICKS_PER_SECOND * 4,
            SERVER_TICKS_PER_SECOND * 8 - phase * (SERVER_TICKS_PER_SECOND + SERVER_TICKS_PER_SECOND // 2)
        )

    def _cast_boss_skill(self, entity_id, entity_type, target_id):
        config = BOSS_CRAB_CONFIG.get(entity_type, None)
        if not config:
            return
        target_pos = self._get_entity_pos(target_id)
        boss_pos = self._get_entity_pos(entity_id)
        if target_pos is None or boss_pos is None:
            return

        dimension_id = self._get_entity_dimension(entity_id)
        phase = self._boss_phase.get(entity_id, 1)
        skill_effects = config.get("skill_effects", [])
        for effect_name, duration, amplifier in skill_effects:
            self._add_effect(target_id, effect_name, duration, amplifier, True)
            self._apply_effect_to_entities_near(
                target_pos,
                dimension_id,
                2.5 + phase,
                effect_name,
                duration,
                amplifier,
                set([entity_id, target_id]),
                True
            )
        self._hurt_entity(target_id, config.get("skill_damage", 0), "magic", entity_id, True)

        if phase >= 3:
            self._heal_entity(entity_id, 2.0)
            self._push_entity_towards(entity_id, boss_pos, target_pos, 0.12)
        if entity_type == "fg:crab_boss_tidal":
            self._push_entity_towards(target_id, target_pos, boss_pos, 0.22)
        elif entity_type == "fg:crab_boss_lava":
            self._add_effect(target_id, "wither", 2, 0, True)

        if entity_type == "fg:crab_boss_lava":
            self._cast_lava_boss_skill(entity_id, boss_pos, target_pos, target_id, dimension_id, phase)
        elif entity_type == "fg:crab_boss_ice":
            self._cast_ice_boss_skill(entity_id, boss_pos, target_pos, target_id, dimension_id, phase)
        elif entity_type == "fg:crab_boss_poisonous_swamp":
            self._cast_poisonous_swamp_boss_skill(entity_id, boss_pos, target_pos, target_id, dimension_id, phase)
        elif entity_type == "fg:crab_boss_tidal":
            self._cast_tidal_boss_skill(entity_id, boss_pos, target_pos, target_id, dimension_id, phase)
        elif entity_type == "fg:crab_boss_sound_guard":
            self._cast_sound_guard_boss_skill(entity_id, boss_pos, target_pos, target_id, dimension_id, phase)

        particle = config.get("skill_particle", None)
        if particle:
            self._run_level_command("/particle %s %s %s %s" % (particle, target_pos[0], target_pos[1] + 0.5, target_pos[2]))

    def _cast_lava_boss_skill(self, entity_id, boss_pos, target_pos, target_id, dimension_id, phase):
        self._set_entity_on_fire(target_id, 3 + phase, 1 + phase)
        self._hurt_entities_near(target_pos, dimension_id, 2.5 + phase, 1.5 * phase, "fire", entity_id, True, set([entity_id]))
        for pos in self._ring_block_positions(target_pos, 1 + min(phase, 2)):
            self._place_temporary_block_if_passable(pos, "minecraft:fire", 0, dimension_id, SERVER_TICKS_PER_SECOND * (4 + phase))
        if phase >= 2:
            self._place_temporary_ground_disc(target_pos, dimension_id, "minecraft:magma", 2 + min(phase, 2), SERVER_TICKS_PER_SECOND * 7)
            self._hurt_entities_near(target_pos, dimension_id, 3.5 + phase, 2.0, "fire", entity_id, True, set([entity_id]))
        if phase >= 3:
            self._place_temporary_ground_disc(boss_pos, dimension_id, "minecraft:magma", 4, SERVER_TICKS_PER_SECOND * 8)
            for pos in self._ring_block_positions(boss_pos, 4):
                self._place_temporary_block_if_passable(pos, "minecraft:fire", 0, dimension_id, SERVER_TICKS_PER_SECOND * 5)
            self._run_level_command("/particle minecraft:explosion_particle %s %s %s" % (target_pos[0], target_pos[1] + 0.5, target_pos[2]))
            self._try_spawn_boss_minions(entity_id, "fg:crab_aggressive", boss_pos, dimension_id, 1, 3)

    def _cast_ice_boss_skill(self, entity_id, boss_pos, target_pos, target_id, dimension_id, phase):
        self._push_entity_towards(target_id, target_pos, boss_pos, 0.12)
        try:
            self._set_entity_motion(target_id, (0.0, 0.0, 0.0))
        except Exception:
            if IN_DEVELOPMENT:
                raise
        for pos in self._disk_block_positions(target_pos, 1 + min(phase, 2)):
            ground_pos = (pos[0], pos[1] - 1, pos[2])
            ground_name = self._get_block_name(ground_pos, dimension_id)
            if ground_name in WATER_BLOCKS or ground_name in PASSABLE_BLOCKS:
                self._place_temporary_block(ground_pos, "minecraft:ice", 0, dimension_id, SERVER_TICKS_PER_SECOND * (5 + phase))
        if phase >= 2:
            self._place_temporary_ground_disc(target_pos, dimension_id, "minecraft:blue_ice", 2 + min(phase, 2), SERVER_TICKS_PER_SECOND * 7)
            self._apply_effect_to_entities_near(target_pos, dimension_id, 3.0 + phase, "slowness", 4 + phase, 1, set([entity_id]), True)
            for pos in self._ring_block_positions(target_pos, 2 + min(phase, 2)):
                self._place_temporary_block_if_passable(pos, "minecraft:ice", 0, dimension_id, SERVER_TICKS_PER_SECOND * 5)
        if phase >= 3:
            self._add_effect(entity_id, "resistance", 3, 1, True)
            self._run_level_command("/particle minecraft:basic_crit_particle %s %s %s" % (boss_pos[0], boss_pos[1] + 0.5, boss_pos[2]))
            self._try_spawn_boss_minions(entity_id, "fg:crab_frost_shell", boss_pos, dimension_id, 1, 3)

    def _cast_poisonous_swamp_boss_skill(self, entity_id, boss_pos, target_pos, target_id, dimension_id, phase):
        self._add_effect(target_id, "poison", 4 + phase, min(2, phase), True)
        self._add_effect(target_id, "nausea", 3 + phase, 0, True)
        self._hurt_entities_near(target_pos, dimension_id, 2.5 + phase, phase, "magic", entity_id, False, set([entity_id]))
        for pos in self._ring_block_positions(target_pos, 1):
            self._place_temporary_block_if_passable(pos, "minecraft:slime_block", 0, dimension_id, SERVER_TICKS_PER_SECOND * (4 + phase))
        if phase >= 2:
            self._place_temporary_ground_disc(target_pos, dimension_id, "minecraft:slime_block", 2 + min(phase, 2), SERVER_TICKS_PER_SECOND * 8)
            self._apply_effect_to_entities_near(target_pos, dimension_id, 3.5 + phase, "poison", 4 + phase, min(2, phase), set([entity_id]), True)
            self._heal_entity(entity_id, 1.5 + phase)
        if phase >= 3:
            self._place_temporary_ground_disc(boss_pos, dimension_id, "minecraft:moss_block", 4, SERVER_TICKS_PER_SECOND * 8)
            self._hurt_entities_near(boss_pos, dimension_id, 4.0, 2.0, "magic", entity_id, False, set([entity_id]))
        self._try_spawn_boss_minions(entity_id, "fg:crab_moss_shell", boss_pos, dimension_id, phase, 4)

    def _cast_tidal_boss_skill(self, entity_id, boss_pos, target_pos, target_id, dimension_id, phase):
        self._push_entities_near_towards(target_pos, dimension_id, 3.0 + phase, boss_pos, 0.14 + phase * 0.04, set([entity_id]))
        self._hurt_entities_near(target_pos, dimension_id, 2.5 + phase, 1.5 + phase, "drowning", entity_id, True, set([entity_id]))
        for pos in self._ring_block_positions(target_pos, 1 + min(phase, 2)):
            self._place_temporary_block_if_passable(pos, "minecraft:flowing_water", 0, dimension_id, SERVER_TICKS_PER_SECOND * (3 + phase))
        if phase >= 2:
            for pos in self._disk_block_positions(target_pos, 2 + min(phase, 2)):
                self._place_temporary_block_if_passable(pos, "minecraft:flowing_water", 0, dimension_id, SERVER_TICKS_PER_SECOND * 5)
            self._push_entities_near_towards(boss_pos, dimension_id, 5.0, boss_pos, 0.18, set([entity_id]))
        if phase >= 3:
            for pos in self._ring_block_positions(boss_pos, 4):
                self._place_temporary_block_if_passable(pos, "minecraft:flowing_water", 0, dimension_id, SERVER_TICKS_PER_SECOND * 6)
            self._push_entities_near_towards(boss_pos, dimension_id, 4.5, boss_pos, -0.22, set([entity_id]))
            self._try_spawn_boss_minions(entity_id, "fg:crab_blue_tide", boss_pos, dimension_id, 1, 3)

    def _cast_sound_guard_boss_skill(self, entity_id, boss_pos, target_pos, target_id, dimension_id, phase):
        self._add_effect(target_id, "blindness", 2 + phase, 0, True)
        self._push_entities_near_towards(target_pos, dimension_id, 3.5 + phase, target_pos, -0.18 - phase * 0.04, set([entity_id]))
        self._hurt_entities_near(target_pos, dimension_id, 3.0 + phase, 2.0 + phase, "magic", entity_id, True, set([entity_id]))
        if phase >= 2:
            self._place_temporary_ground_disc(target_pos, dimension_id, "minecraft:amethyst_block", 2 + min(phase, 2), SERVER_TICKS_PER_SECOND * 6)
            self._apply_effect_to_entities_near(target_pos, dimension_id, 4.0 + phase, "blindness", 2 + phase, 0, set([entity_id]), True)
            if target_id in (ServerApi.GetPlayerList() or []) and not self._is_player_sneaking(target_id):
                self._hurt_entity(target_id, 2.0 + phase, "magic", entity_id, True)
        if phase >= 3:
            self._place_temporary_ground_disc(boss_pos, dimension_id, "minecraft:calcite", 4, SERVER_TICKS_PER_SECOND * 7)
            self._run_level_command("/particle minecraft:sonic_explosion %s %s %s" % (boss_pos[0], boss_pos[1] + 0.5, boss_pos[2]))
            self._push_entities_near_towards(boss_pos, dimension_id, 5.5, boss_pos, -0.30, set([entity_id]))
        if phase >= 3:
            self._try_spawn_boss_minions(entity_id, "fg:crab_aggressive", boss_pos, dimension_id, 1, 3)

    def _tick_boss_lair_spawns(self):
        players = ServerApi.GetPlayerList() or []
        for player_id in players:
            player_pos = self._get_entity_pos(player_id)
            dimension_id = self._get_entity_dimension(player_id)
            if player_pos is None or dimension_id is None:
                continue

            for config in BOSS_LAIR_CONFIG:
                if config["dimension"] != dimension_id:
                    continue
                anchor_pos = self._find_recorded_boss_lair_anchor(player_pos, dimension_id, config)
                lair_exists = anchor_pos is not None
                if anchor_pos is None:
                    anchor_pos = self._find_boss_lair_anchor(player_pos, dimension_id, config)
                if anchor_pos is None:
                    continue

                bucket = self._get_boss_lair_bucket(config, anchor_pos, dimension_id)
                if bucket in self._boss_lair_buckets:
                    lair_exists = True
                    self._boss_lair_anchor_by_bucket.setdefault(bucket, ServerApi.GetIntPos(anchor_pos))
                if self._tick < self._structure_spawn_cooldown.get(bucket, 0):
                    continue

                if lair_exists:
                    next_respawn_tick = self._boss_lair_next_respawn_tick.get(bucket, 0)
                    if self._tick < next_respawn_tick:
                        continue
                    self._spawn_boss_at_lair(anchor_pos, dimension_id, config, bucket)
                    continue

                if self._is_boss_lair_in_combat(anchor_pos, dimension_id):
                    self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 60
                    continue
                if random.random() > config["chance"]:
                    self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 45
                    continue

                if self._create_boss_lair(anchor_pos, dimension_id, config):
                    self._boss_lair_buckets.add(bucket)
                    self._boss_lair_anchor_by_bucket[bucket] = ServerApi.GetIntPos(anchor_pos)
                    self._spawn_boss_lair_loot(anchor_pos, dimension_id, config)
                    self._spawn_boss_at_lair(anchor_pos, dimension_id, config, bucket)
                    self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 180
                else:
                    self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 30

    def _get_boss_lair_bucket(self, config, anchor_pos, dimension_id):
        anchor = ServerApi.GetIntPos(anchor_pos)
        return (
            config["entity_type"],
            dimension_id,
            int(anchor[0]) // 64,
            int(anchor[2]) // 64
        )

    def _find_recorded_boss_lair_anchor(self, player_pos, dimension_id, config):
        best_anchor = None
        best_distance = None
        for bucket, anchor_pos in self._boss_lair_anchor_by_bucket.items():
            if bucket[0] != config["entity_type"] or bucket[1] != dimension_id:
                continue
            distance = self._distance_sq(player_pos, anchor_pos)
            if distance > BOSS_LAIR_COMBAT_RADIUS * BOSS_LAIR_COMBAT_RADIUS:
                continue
            if best_distance is None or distance < best_distance:
                best_anchor = anchor_pos
                best_distance = distance
        return best_anchor

    def _is_boss_lair_in_combat(self, anchor_pos, dimension_id):
        return self._count_entities_near(anchor_pos, dimension_id, BOSS_LAIR_COMBAT_RADIUS, BOSS_ENTITY_TYPES) > 0

    def _spawn_boss_at_lair(self, anchor_pos, dimension_id, config, bucket):
        if self._is_boss_lair_in_combat(anchor_pos, dimension_id):
            self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 60
            return False
        spawn_pos = (anchor_pos[0] + 0.5, anchor_pos[1] + 1.0, anchor_pos[2] + 0.5)
        spawn_id = self.CreateEngineEntityByTypeStr(config["entity_type"], spawn_pos, (0, 0), dimension_id, False, True)
        if spawn_id:
            self._boss_lair_next_respawn_tick[bucket] = self._tick + BOSS_LAIR_RESPAWN_INTERVAL_TICKS
            self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 60
            return True
        self._boss_lair_next_respawn_tick[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 30
        self._structure_spawn_cooldown[bucket] = self._tick + SERVER_TICKS_PER_SECOND * 30
        self._log_validation_failure("boss_lair.boss_spawn_failed", {
            "entity_type": config.get("entity_type", ""),
            "dimension": dimension_id,
            "anchor": ServerApi.GetIntPos(anchor_pos),
        })
        return False

    def _find_boss_lair_anchor(self, center_pos, dimension_id, config):
        center = ServerApi.GetIntPos(center_pos)
        for _idx in range(28):
            x = center[0] + random.randint(-36, 36)
            z = center[2] + random.randint(-36, 36)
            for y in range(center[1] + 8, center[1] - 16, -1):
                ground_pos = (x, y - 1, z)
                if self._get_block_name(ground_pos, dimension_id) not in config["ground_blocks"]:
                    continue
                if not self._is_valid_entity_stand_pos((x, y, z), dimension_id):
                    continue
                if not self._can_place_boss_lair_at((x, y, z), dimension_id, config):
                    continue
                return (x, y, z)
        return None

    def _can_place_boss_lair_at(self, anchor_pos, dimension_id, config=None):
        anchor = ServerApi.GetIntPos(anchor_pos)
        radius = 1
        if config is not None:
            size = config.get("structure_size", (9, 5, 9))
            radius = min(6, max(2, int(min(size[0], size[2]) // 6)))
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                pos = (anchor[0] + dx, anchor[1], anchor[2] + dz)
                head_pos = (pos[0], pos[1] + 1, pos[2])
                if not self._is_passable_block(self._get_block_name(pos, dimension_id)):
                    return False
                if not self._is_passable_block(self._get_block_name(head_pos, dimension_id)):
                    return False
        return True

    def _create_boss_lair(self, anchor_pos, dimension_id, config):
        if self._place_boss_lair_structure(anchor_pos, dimension_id, config):
            return True
        return self._create_script_boss_lair(anchor_pos, dimension_id, config)

    def _place_boss_lair_structure(self, anchor_pos, dimension_id, config):
        structure_name = config.get("structure", None)
        size = config.get("structure_size", None)
        if not structure_name or not size:
            self._log_validation_failure("boss_lair.structure_config_missing", {
                "entity_type": config.get("entity_type", ""),
                "structure": structure_name,
                "size": size,
            })
            return False
        game_comp = self._get_game_comp()
        if game_comp is None:
            self._log_validation_failure("boss_lair.game_component_missing", {
                "entity_type": config.get("entity_type", ""),
                "structure": structure_name,
                "dimension": dimension_id,
            })
            return False
        if not hasattr(game_comp, "PlaceStructure"):
            self._log_validation_failure("boss_lair.place_structure_api_missing", {
                "entity_type": config.get("entity_type", ""),
                "structure": structure_name,
                "dimension": dimension_id,
            })
            return False
        anchor = ServerApi.GetIntPos(anchor_pos)
        place_pos = (
            anchor[0] - int(size[0] // 2),
            anchor[1] - 1,
            anchor[2] - int(size[2] // 2),
        )
        try:
            return bool(game_comp.PlaceStructure(
                None,
                place_pos,
                structure_name,
                dimension_id,
                0,
                0,
                0,
                False,
                False,
                0,
                100.0,
                -1
            ))
        except TypeError:
            try:
                return bool(game_comp.PlaceStructure(None, place_pos, structure_name, dimension_id))
            except Exception as error:
                if IN_DEVELOPMENT:
                    raise
                self._log_validation_failure("boss_lair.place_structure_failed", {
                    "entity_type": config.get("entity_type", ""),
                    "structure": structure_name,
                    "dimension": dimension_id,
                    "pos": place_pos,
                    "signature": "short",
                    "error": self._short_error_text(error),
                })
        except Exception as error:
            if IN_DEVELOPMENT:
                raise
            self._log_validation_failure("boss_lair.place_structure_failed", {
                "entity_type": config.get("entity_type", ""),
                "structure": structure_name,
                "dimension": dimension_id,
                "pos": place_pos,
                "signature": "full",
                "error": self._short_error_text(error),
            })
        return False

    def _create_script_boss_lair(self, anchor_pos, dimension_id, config):
        anchor = ServerApi.GetIntPos(anchor_pos)
        placed = 0
        fallback_radius = 9
        for dx in range(-fallback_radius, fallback_radius + 1):
            for dz in range(-fallback_radius, fallback_radius + 1):
                if dx * dx + dz * dz > fallback_radius * fallback_radius:
                    continue
                block_name = config["marker_block"] if max(abs(dx), abs(dz)) >= fallback_radius - 1 else config["floor_block"]
                pos = (anchor[0] + dx, anchor[1] - 1, anchor[2] + dz)
                if self._set_block(pos, block_name, 0, dimension_id):
                    placed += 1
                if abs(dx) == 7 and abs(dz) == 7:
                    self._set_block((anchor[0] + dx, anchor[1], anchor[2] + dz), config["pillar_block"], 0, dimension_id)
                    self._set_block((anchor[0] + dx, anchor[1] + 1, anchor[2] + dz), config["pillar_block"], 0, dimension_id)
                    self._set_block((anchor[0] + dx, anchor[1] + 2, anchor[2] + dz), config["pillar_block"], 0, dimension_id)
                elif (abs(dx) in (2, 4) and dz == 0) or (abs(dz) in (2, 4) and dx == 0):
                    self._set_block((anchor[0] + dx, anchor[1], anchor[2] + dz), config["hazard_block"], 0, dimension_id)
        for offset in BOSS_LAIR_CHEST_OFFSETS:
            self._set_block((anchor[0] + offset[0], anchor[1] + offset[1], anchor[2] + offset[2]), "minecraft:chest", 0, dimension_id)
        return placed >= 160

    def _spawn_boss_lair_loot(self, anchor_pos, dimension_id, config):
        entity_type = config.get("entity_type", "")
        loot_table = BOSS_LAIR_CHEST_LOOT_TABLES.get(entity_type, None)
        if not loot_table:
            return
        anchor = ServerApi.GetIntPos(anchor_pos)
        success_count = 0
        for offset in BOSS_LAIR_CHEST_OFFSETS:
            chest_pos = (anchor[0] + offset[0], anchor[1] + offset[1], anchor[2] + offset[2])
            chest_ready = self._set_block(chest_pos, "minecraft:chest", 0, dimension_id)
            chest_ready = chest_ready or self._get_block_name(chest_pos, dimension_id) == "minecraft:chest"
            if chest_ready and self._set_chest_loot_table(chest_pos, dimension_id, loot_table):
                success_count += 1
        if success_count <= 0:
            self._log_validation_failure("boss_lair.chest_loot_all_failed", {
                "entity_type": entity_type,
                "loot_table": loot_table,
                "dimension": dimension_id,
                "anchor": anchor,
            })
            self._spawn_boss_lair_fallback_loot(anchor, dimension_id, entity_type)
        elif success_count < len(BOSS_LAIR_CHEST_OFFSETS):
            self._log_validation_failure("boss_lair.chest_loot_partial_failed", {
                "entity_type": entity_type,
                "loot_table": loot_table,
                "dimension": dimension_id,
                "anchor": anchor,
                "success_count": success_count,
            })

    def _set_chest_loot_table(self, chest_pos, dimension_id, loot_table):
        block_info = self._get_block_info_comp()
        if block_info is None:
            self._log_validation_failure("boss_lair.block_info_component_missing", {
                "loot_table": loot_table,
                "dimension": dimension_id,
                "pos": ServerApi.GetIntPos(chest_pos),
            })
            return False
        try:
            return bool(block_info.SetChestLootTable(ServerApi.GetIntPos(chest_pos), dimension_id, loot_table))
        except TypeError:
            try:
                return bool(block_info.SetChestLootTable(ServerApi.GetIntPos(chest_pos), dimension_id, loot_table, False))
            except Exception as error:
                if IN_DEVELOPMENT:
                    raise
                self._log_validation_failure("boss_lair.set_chest_loot_failed", {
                    "loot_table": loot_table,
                    "dimension": dimension_id,
                    "pos": ServerApi.GetIntPos(chest_pos),
                    "signature": "extended",
                    "error": self._short_error_text(error),
                })
        except Exception as error:
            if IN_DEVELOPMENT:
                raise
            self._log_validation_failure("boss_lair.set_chest_loot_failed", {
                "loot_table": loot_table,
                "dimension": dimension_id,
                "pos": ServerApi.GetIntPos(chest_pos),
                "signature": "base",
                "error": self._short_error_text(error),
            })
        return False

    def _spawn_boss_lair_fallback_loot(self, anchor_pos, dimension_id, entity_type):
        for item_name, min_count, max_count, chance in BOSS_LAIR_FALLBACK_LOOT.get(entity_type, []):
            if random.random() > chance:
                continue
            item_dict = {
                "newItemName": item_name,
                "newAuxValue": 0,
                "count": random.randint(min_count, max_count),
            }
            spawn_pos = (
                float(anchor_pos[0]) + random.uniform(-2.0, 2.0),
                float(anchor_pos[1]) + 1.15,
                float(anchor_pos[2]) + random.uniform(-2.0, 2.0),
            )
            try:
                self.CreateEngineItemEntity(item_dict, dimension_id, spawn_pos)
            except Exception:
                if IN_DEVELOPMENT:
                    raise

    def _find_nearest_ore_target(self, center_pos, dimension_id, block_names, radius, y_radius):
        center = ServerApi.GetIntPos(center_pos)
        best_info = None
        best_distance = None
        for dy in range(-y_radius, y_radius + 1):
            y = center[1] + dy
            for dx in range(-radius, radius + 1):
                x = center[0] + dx
                for dz in range(-radius, radius + 1):
                    z = center[2] + dz
                    block_pos = (x, y, z)
                    if not self._is_matching_block(block_pos, dimension_id, block_names):
                        continue
                    stand_pos = self._find_stand_pos_for_block(block_pos, center_pos, dimension_id)
                    if stand_pos is None:
                        continue
                    distance = self._distance_sq(center_pos, (stand_pos[0] + 0.5, stand_pos[1], stand_pos[2] + 0.5))
                    if best_distance is None or distance < best_distance:
                        best_info = (block_pos, stand_pos)
                        best_distance = distance
        return best_info

    def _find_nearest_matching_block(self, center_pos, dimension_id, block_names, radius, y_radius):
        center = ServerApi.GetIntPos(center_pos)
        best_pos = None
        best_distance = None
        for dy in range(-y_radius, y_radius + 1):
            y = center[1] + dy
            for dx in range(-radius, radius + 1):
                x = center[0] + dx
                for dz in range(-radius, radius + 1):
                    z = center[2] + dz
                    block_pos = (x, y, z)
                    if not self._is_matching_block(block_pos, dimension_id, block_names):
                        continue
                    distance = dx * dx + dy * dy + dz * dz
                    if best_distance is None or distance < best_distance:
                        best_pos = block_pos
                        best_distance = distance
        return best_pos

    def _find_stand_pos_for_block(self, block_pos, center_pos, dimension_id):
        offsets = [
            (1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1),
            (1, 0, 1), (1, 0, -1), (-1, 0, 1), (-1, 0, -1),
            (0, 1, 0), (1, 1, 0), (-1, 1, 0), (0, 1, 1), (0, 1, -1),
            (1, -1, 0), (-1, -1, 0), (0, -1, 1), (0, -1, -1),
        ]
        candidates = []
        for dx, dy, dz in offsets:
            stand_pos = (block_pos[0] + dx, block_pos[1] + dy, block_pos[2] + dz)
            if not self._is_valid_entity_stand_pos(stand_pos, dimension_id):
                continue
            if not self._has_clear_path_to_stand(center_pos, stand_pos, dimension_id):
                continue
            distance = self._distance_sq(center_pos, (stand_pos[0] + 0.5, stand_pos[1], stand_pos[2] + 0.5))
            candidates.append((distance, stand_pos))
        if not candidates:
            return None
        candidates.sort(key=lambda item: item[0])
        return candidates[0][1]

    def _consume_matching_block(self, block_pos, dimension_id, block_names):
        if not self._is_matching_block(block_pos, dimension_id, block_names):
            return False
        block_info = self._get_block_info_comp()
        if block_info is None:
            return False
        try:
            return bool(block_info.SetBlockNew(
                ServerApi.GetIntPos(block_pos),
                {"name": "minecraft:air", "aux": 0},
                0,
                dimension_id,
                True,
                True
            ))
        except Exception:
            if IN_DEVELOPMENT:
                raise
            return False

    def _is_matching_block(self, block_pos, dimension_id, block_names):
        if block_pos is None:
            return False
        return self._get_block_name(block_pos, dimension_id) in block_names

    def _find_nearest_player(self, pos, dimension_id, radius):
        best_player = None
        best_distance = None
        for player_id in ServerApi.GetPlayerList() or []:
            if self._get_entity_dimension(player_id) != dimension_id:
                continue
            player_pos = self._get_entity_pos(player_id)
            if player_pos is None:
                continue
            distance = self._distance_sq(pos, player_pos)
            if distance > radius * radius:
                continue
            if best_distance is None or distance < best_distance:
                best_player = player_id
                best_distance = distance
        return best_player

    def _take_one_valuable_item(self, player_id):
        item_comp = CompFactory.CreateItem(player_id)
        candidates = []
        for pos_type, slot_list in self._iter_player_item_slots(item_comp):
            for slot_pos, item_dict in slot_list:
                if not item_dict:
                    continue
                normalized_name = self._get_item_name(item_dict)
                priority = PIRATE_STEAL_PRIORITY.get(normalized_name, None)
                if priority is None:
                    continue
                candidates.append((priority, pos_type, slot_pos, item_dict))

        if not candidates:
            return None

        candidates.sort(key=lambda item: item[0])
        _priority, pos_type, slot_pos, item_dict = candidates[0]
        stolen_item = copy.deepcopy(item_dict)
        stolen_item["newItemName"] = self._get_item_name(stolen_item)
        stolen_item["newAuxValue"] = stolen_item.get("newAuxValue", 0)
        stolen_item["count"] = 1

        left_count = int(item_dict.get("count", 1)) - 1
        if left_count <= 0:
            result = item_comp.SetEntityItem(pos_type, None, slot_pos)
        else:
            item_dict = copy.deepcopy(item_dict)
            item_dict["count"] = left_count
            result = item_comp.SetEntityItem(pos_type, item_dict, slot_pos)
        return stolen_item if result is not False else None

    def _iter_player_item_slots(self, item_comp):
        slots = []
        carried_type = getattr(MinecraftEnum.ItemPosType, "CARRIED", None)
        offhand_type = getattr(MinecraftEnum.ItemPosType, "OFFHAND", None)
        inventory_type = getattr(MinecraftEnum.ItemPosType, "INVENTORY", None)

        for pos_type in (carried_type, offhand_type):
            if pos_type is None:
                continue
            try:
                item_dict = item_comp.GetPlayerItem(pos_type, 0, True)
            except Exception:
                item_dict = item_comp.GetPlayerItem(pos_type, 0)
            slots.append((pos_type, [(0, item_dict)]))

        if inventory_type is not None:
            try:
                inventory_items = item_comp.GetPlayerAllItems(inventory_type, True) or []
            except Exception:
                inventory_items = item_comp.GetPlayerAllItems(inventory_type) or []
            slots.append((inventory_type, list(enumerate(inventory_items))))
        return slots

    def _apply_crab_shell_shield_damage_reduction(self, args):
        player_id = args.get("entityId", None)
        if player_id not in (ServerApi.GetPlayerList() or []):
            return
        if self._tick < self._shield_cooldown_until.get(player_id, 0):
            return

        shield_slot = self._find_player_held_item(player_id, CRAB_SHELL_SHIELD_ITEM)
        if shield_slot is None:
            return
        blocking = self._is_player_blocking(player_id)
        if blocking is True:
            return
        if not self._is_player_sneaking(player_id):
            return
        attacker_id = args.get("srcId", None)
        if not attacker_id or str(attacker_id) == "-1":
            return
        if not self._is_damage_from_front(player_id, attacker_id):
            return

        args["damage"] = max(0.0, float(args.get("damage", 0)) * (1.0 - CRAB_SHELL_SHIELD_DAMAGE_REDUCTION))
        args["knock"] = False
        self._shield_cooldown_until[player_id] = self._tick + CRAB_SHELL_SHIELD_COOLDOWN_TICKS
        self._damage_player_item(player_id, shield_slot, CRAB_SHELL_SHIELD_MAX_DAMAGE)

    def _apply_boss_weapon_hit_effects(self, args):
        attacker_id = args.get("srcId", None)
        target_id = args.get("entityId", None)
        if attacker_id not in (ServerApi.GetPlayerList() or []):
            return
        if not target_id or target_id == attacker_id:
            return

        weapon_slot = None
        for item_name in BOSS_WEAPON_EFFECTS:
            weapon_slot = self._find_player_held_item(attacker_id, item_name)
            if weapon_slot is not None:
                break
        if weapon_slot is None:
            return

        item_name = self._get_item_name(weapon_slot[2])
        config = BOSS_WEAPON_EFFECTS.get(item_name, None)
        if not config:
            return

        for effect_name, duration, amplifier in config.get("effects", []):
            self._add_effect(target_id, effect_name, duration, amplifier, True)
        if config.get("extra_damage", 0) > 0:
            args["damage"] = float(args.get("damage", 0)) + float(config["extra_damage"])
        if config.get("fire_seconds", 0) > 0:
            self._set_entity_on_fire(target_id, config["fire_seconds"], 1)
        if config.get("push", 0) > 0:
            attacker_pos = self._get_entity_pos(attacker_id)
            target_pos = self._get_entity_pos(target_id)
            if attacker_pos is not None and target_pos is not None:
                self._push_entity_towards(target_id, attacker_pos, target_pos, config["push"])

        target_pos = self._get_entity_pos(target_id)
        if target_pos is not None and config.get("particle", None):
            self._run_level_command("/particle %s %s %s %s" % (
                config["particle"],
                target_pos[0],
                target_pos[1] + 0.5,
                target_pos[2]
            ))
        self._damage_player_item(attacker_id, weapon_slot, config.get("max_damage", 900))

    def _try_cast_boss_weapon_active_skill(self, player_id, item_name):
        if not player_id:
            return False
        config = BOSS_WEAPON_ACTIVE_EFFECTS.get(item_name, None)
        if not config:
            return False
        if self._tick < self._boss_weapon_active_cooldown_until.get(player_id, 0):
            return False
        weapon_slot = self._find_player_held_item(player_id, item_name)
        if weapon_slot is None:
            return False
        player_pos = self._get_entity_pos(player_id)
        dimension_id = self._get_entity_dimension(player_id)
        if player_pos is None or dimension_id is None:
            return False

        center_pos = self._get_player_forward_skill_pos(player_id, player_pos, 4.0)
        radius = float(config.get("radius", 4.0))
        exclude_ids = set([player_id])
        for effect_name, duration, amplifier in config.get("effects", []):
            self._apply_effect_to_entities_near(center_pos, dimension_id, radius, effect_name, duration, amplifier, exclude_ids)
        if config.get("damage", 0) > 0:
            self._hurt_entities_near(center_pos, dimension_id, radius, float(config["damage"]), config.get("cause", "magic"), player_id, True, exclude_ids)
        if config.get("fire_seconds", 0) > 0:
            for target_id in self._iter_entities_near(center_pos, dimension_id, radius, exclude_ids):
                self._set_entity_on_fire(target_id, config["fire_seconds"], 1)
        if config.get("pull", 0) > 0:
            self._push_entities_near_towards(center_pos, dimension_id, radius, center_pos, float(config["pull"]), exclude_ids)
        if config.get("push", 0) > 0:
            self._push_entities_near_towards(center_pos, dimension_id, radius, center_pos, -float(config["push"]), exclude_ids)
        if config.get("temporary_block", None):
            self._place_active_skill_temporary_blocks(center_pos, dimension_id, config["temporary_block"])
        if config.get("particle", None):
            if not self._run_level_command("/particle %s %s %s %s" % (
                config["particle"],
                center_pos[0],
                center_pos[1] + 0.5,
                center_pos[2]
            )):
                self._log_validation_failure("boss_weapon.particle_command_failed", {
                    "player_id": player_id,
                    "item": item_name,
                    "particle": config["particle"],
                    "dimension": dimension_id,
                    "pos": center_pos,
                })
        if config.get("sound", None):
            if not self._play_sound_at(config["sound"], center_pos, 1.0, 1.0):
                self._log_validation_failure("boss_weapon.sound_command_failed", {
                    "player_id": player_id,
                    "item": item_name,
                    "sound": config["sound"],
                    "dimension": dimension_id,
                    "pos": center_pos,
                })
        if not self._damage_player_item(player_id, weapon_slot, config.get("max_damage", 900)):
            self._log_validation_failure("boss_weapon.damage_item_failed", {
                "player_id": player_id,
                "item": item_name,
                "slot_type": weapon_slot[0],
                "slot": weapon_slot[1],
            })
        self._boss_weapon_active_cooldown_until[player_id] = self._tick + BOSS_WEAPON_ACTIVE_COOLDOWN_TICKS
        return True

    def _get_player_forward_skill_pos(self, player_id, player_pos, distance):
        direction = self._get_entity_forward_dir(player_id)
        if direction is None:
            return player_pos
        return (
            float(player_pos[0]) + direction[0] * distance,
            float(player_pos[1]),
            float(player_pos[2]) + direction[2] * distance,
        )

    def _place_active_skill_temporary_blocks(self, center_pos, dimension_id, block_name):
        duration = SERVER_TICKS_PER_SECOND * 4
        for pos in self._disk_block_positions(ServerApi.GetIntPos(center_pos), 2):
            self._place_temporary_block_if_passable(pos, block_name, 0, dimension_id, duration)

    def _iter_entities_near(self, center_pos, dimension_id, radius, exclude_ids):
        for entity_id in self._get_entities_in_square(
                (center_pos[0] - radius, center_pos[1] - 3, center_pos[2] - radius),
                (center_pos[0] + radius, center_pos[1] + 3, center_pos[2] + radius),
                dimension_id
        ) or []:
            if entity_id in exclude_ids:
                continue
            entity_pos = self._get_entity_pos(entity_id)
            if entity_pos is None or self._distance_sq(center_pos, entity_pos) > radius * radius:
                continue
            yield entity_id

    def _apply_boss_armor_damage_reactions(self, args):
        player_id = args.get("entityId", None)
        attacker_id = args.get("srcId", None)
        if player_id not in (ServerApi.GetPlayerList() or []):
            return
        set_name = self._get_player_full_boss_armor_set(player_id)
        if not set_name or not attacker_id or str(attacker_id) == "-1":
            return
        if set_name == "frost":
            self._add_effect(attacker_id, "slowness", 3, 1, True)
            if random.random() < 0.25:
                self._add_effect(attacker_id, "mining_fatigue", 3, 0, True)
        elif set_name == "echo":
            player_pos = self._get_entity_pos(player_id)
            attacker_pos = self._get_entity_pos(attacker_id)
            if player_pos is not None and attacker_pos is not None:
                self._push_entity_towards(attacker_id, player_pos, attacker_pos, 0.28)
                self._hurt_entity(attacker_id, 2.0, "magic", player_id, True)
        elif set_name == "blazing":
            self._set_entity_on_fire(attacker_id, 3, 1)
        elif set_name == "venom":
            self._add_effect(attacker_id, "poison", 4, 0, True)

    def _find_player_held_item(self, player_id, item_name):
        item_comp = CompFactory.CreateItem(player_id)
        for pos_type_name in ("OFFHAND", "CARRIED"):
            pos_type = getattr(MinecraftEnum.ItemPosType, pos_type_name, None)
            if pos_type is None:
                continue
            try:
                item_dict = item_comp.GetPlayerItem(pos_type, 0, True)
            except Exception:
                item_dict = item_comp.GetPlayerItem(pos_type, 0)
            if item_dict and self._get_item_name(item_dict) == item_name:
                return pos_type, 0, item_dict
        return None

    def _damage_player_item(self, player_id, slot_info, max_damage):
        pos_type, slot_pos, item_dict = slot_info
        if not item_dict:
            return False
        item_dict = copy.deepcopy(item_dict)
        old_damage = int(item_dict.get("newAuxValue", 0) or 0)
        new_damage = old_damage + 1
        next_item = None if new_damage >= max_damage else item_dict
        if next_item is not None:
            next_item["newAuxValue"] = new_damage
        try:
            return CompFactory.CreateItem(player_id).SetEntityItem(pos_type, next_item, slot_pos) is not False
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _tick_boss_armor_players(self):
        for player_id in ServerApi.GetPlayerList() or []:
            set_name = self._get_player_full_boss_armor_set(player_id)
            if not set_name:
                continue
            config = BOSS_ARMOR_SETS.get(set_name, None)
            if not config:
                continue
            for effect_name, duration, amplifier in config.get("effects", []):
                self._add_effect(player_id, effect_name, duration, amplifier, False)
            self._remove_effects(player_id, config.get("remove_effects", []))
            player_pos = self._get_entity_pos(player_id)
            dimension_id = self._get_entity_dimension(player_id)
            if player_pos is None or dimension_id is None:
                continue
            for effect_name, duration, amplifier in config.get("aura_effects", []):
                self._apply_effect_to_entities_near(player_pos, dimension_id, 4.0, effect_name, duration, amplifier, player_id)
            if config.get("push_aura", 0) > 0:
                self._push_entities_near_towards(player_pos, dimension_id, 4.0, player_pos, -float(config["push_aura"]), set([player_id]))

    def _get_player_full_boss_armor_set(self, player_id):
        armor_type = getattr(MinecraftEnum.ItemPosType, "ARMOR", None)
        if armor_type is None:
            return None
        item_comp = CompFactory.CreateItem(player_id)
        armor_names = []
        for slot in range(4):
            try:
                item_dict = item_comp.GetPlayerItem(armor_type, slot, True)
            except Exception:
                item_dict = item_comp.GetPlayerItem(armor_type, slot)
            armor_names.append(self._get_item_name(item_dict) if item_dict else "")
        for set_name, config in BOSS_ARMOR_SETS.items():
            if armor_names == config["items"]:
                return set_name
        return None

    def _get_interact_target_id(self, args):
        for key in ("interactEntityId", "entityId", "targetId", "victimId", "id"):
            entity_id = args.get(key, None)
            if entity_id and entity_id != args.get("playerId", None):
                return entity_id
        return None

    def _get_crab_backpack_unequip_shears_slot(self, player_id, entity_id):
        shears_slot = self._get_crab_shears_interact_slot(player_id, entity_id)
        if shears_slot is None:
            return None
        if not self._entity_has_component(entity_id, "minecraft:inventory"):
            return None
        return shears_slot

    def _get_crab_shears_interact_slot(self, player_id, entity_id):
        if not player_id or not entity_id:
            return None
        if self._get_entity_type(entity_id) not in NORMAL_CRAB_ENTITY_TYPES:
            return None
        if not self._is_player_sneaking(player_id):
            return None
        shears_slot = self._find_player_held_item(player_id, SHEARS_ITEM)
        if shears_slot is None:
            return None
        return shears_slot

    def _tick_pending_backpack_unequip(self):
        if not self._pending_backpack_unequip:
            return
        for key, expire_tick in list(self._pending_backpack_unequip.items()):
            if expire_tick < self._tick:
                del self._pending_backpack_unequip[key]

    def _ensure_crab_backpack_container_title(self, entity_id):
        if not entity_id:
            return False
        entity_type = self._get_entity_type(entity_id)
        if entity_type not in NORMAL_CRAB_ENTITY_TYPES:
            return False
        if not self._entity_has_component(entity_id, "minecraft:inventory"):
            self._debug_backpack_name("container_title_skip_no_inventory", entity_id, {
                "entity_type": entity_type,
                "current_name": self._get_entity_custom_name(entity_id),
            }, ("container_title_skip_no_inventory", entity_id))
            return False
        if self._ensure_tamed_normal_crab_default_name(entity_id, entity_type):
            self._debug_backpack_name("container_title_default_name_ready", entity_id, {
                "entity_type": entity_type,
                "current_name": self._get_entity_custom_name(entity_id),
            })
            return True
        current_name = self._get_entity_custom_name(entity_id)
        if current_name and current_name not in (CRAB_BACKPACK_UNKNOWN_TITLE, "Unknown"):
            self._debug_backpack_name("container_title_custom_name_ready", entity_id, {
                "entity_type": entity_type,
                "current_name": current_name,
            })
            return True
        result = self._set_entity_custom_name(entity_id, CRAB_BACKPACK_CONTAINER_TITLE)
        self._debug_backpack_name("container_title_set_fallback", entity_id, {
            "entity_type": entity_type,
            "name_before": current_name,
            "target_name": CRAB_BACKPACK_CONTAINER_TITLE,
            "result": result,
            "name_after": self._get_entity_custom_name(entity_id),
        })
        return result

    def _clear_crab_backpack_container_title(self, entity_id):
        if not entity_id:
            return False
        current_name = self._get_entity_custom_name(entity_id)
        if current_name != CRAB_BACKPACK_CONTAINER_TITLE:
            return False
        return self._set_entity_custom_name(entity_id, "")

    def _ensure_tamed_normal_crab_default_name(self, entity_id, entity_type=None):
        if not entity_id:
            return False
        if entity_id in self._normal_crab_default_named:
            return True
        entity_type = entity_type or self._get_entity_type(entity_id)
        if entity_type not in NORMAL_CRAB_ENTITY_TYPES:
            return False
        has_tamed_component = self._entity_has_component(entity_id, "minecraft:is_tamed")
        fg_is_tamed = self._get_entity_property_value(entity_id, "fg:is_tamed")
        if not has_tamed_component:
            self._debug_backpack_name("default_name_skip_not_tamed", entity_id, {
                "entity_type": entity_type,
                "current_name": self._get_entity_custom_name(entity_id),
                "has_tamed_component": has_tamed_component,
                "fg_is_tamed": fg_is_tamed,
                "has_inventory": self._entity_has_component(entity_id, "minecraft:inventory"),
            }, ("default_name_skip_not_tamed", entity_id))
            return False
        current_name = self._get_entity_custom_name(entity_id)
        if current_name and current_name not in (CRAB_BACKPACK_UNKNOWN_TITLE, "Unknown", CRAB_BACKPACK_CONTAINER_TITLE):
            self._normal_crab_default_named.add(entity_id)
            self._debug_backpack_name("default_name_keep_existing", entity_id, {
                "entity_type": entity_type,
                "current_name": current_name,
                "has_tamed_component": has_tamed_component,
                "fg_is_tamed": fg_is_tamed,
            }, ("default_name_keep_existing", entity_id))
            return True
        default_name = NORMAL_CRAB_DEFAULT_NAMES.get(entity_type, None)
        if not default_name:
            self._debug_backpack_name("default_name_missing_config", entity_id, {
                "entity_type": entity_type,
            }, ("default_name_missing_config", entity_id))
            return False
        result = self._set_entity_custom_name(entity_id, default_name)
        self._debug_backpack_name("default_name_set", entity_id, {
            "entity_type": entity_type,
            "name_before": current_name,
            "target_name": default_name,
            "result": result,
            "name_after": self._get_entity_custom_name(entity_id),
            "has_tamed_component": has_tamed_component,
            "fg_is_tamed": fg_is_tamed,
        })
        if result:
            self._normal_crab_default_named.add(entity_id)
            return True
        return False

    def _get_entity_custom_name(self, entity_id):
        try:
            getter = getattr(CompFactory.CreateName(entity_id), "GetName", None)
            if getter is None:
                self._debug_backpack_name("get_name_api_missing", entity_id, {}, ("get_name_api_missing", entity_id))
                return ""
            name = getter() or ""
            try:
                if not isinstance(name, unicode):
                    name = name.decode("utf-8")
            except NameError:
                pass
            except Exception:
                pass
            return name
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return ""

    def _encode_name_for_set_name(self, name):
        try:
            if isinstance(name, unicode):
                return name.encode("utf-8")
        except NameError:
            pass
        except Exception:
            pass
        return name

    def _set_entity_custom_name(self, entity_id, name):
        try:
            name_comp = CompFactory.CreateName(entity_id)
            setter = getattr(name_comp, "SetName", None)
            if setter is None:
                self._debug_backpack_name("set_name_api_missing", entity_id, {
                    "target_name": name,
                }, ("set_name_api_missing", entity_id))
                return False
            encoded_name = self._encode_name_for_set_name(name)
            result = bool(setter(encoded_name))
            self._debug_backpack_name("set_name_call", entity_id, {
                "target_name": name,
                "encoded_name": encoded_name,
                "encoded_type": type(encoded_name).__name__,
                "result": result,
            })
            return result
        except Exception as error:
            self._debug_backpack_name("set_name_exception", entity_id, {
                "target_name": name,
                "error": self._short_error_text(error),
            })
            if IN_DEVELOPMENT:
                raise
        return False

    def _get_entity_property_value(self, entity_id, property_name):
        try:
            comp = CompFactory.CreateQueryVariable(entity_id)
            evaluator = getattr(comp, "EvalMolangExpression", None)
            if evaluator is None:
                return None
            return evaluator("query.property('%s')" % property_name)
        except Exception as error:
            self._debug_backpack_name("property_read_exception", entity_id, {
                "property": property_name,
                "error": self._short_error_text(error),
            }, ("property_read_exception", entity_id, property_name))
        return None

    def _debug_backpack_name(self, reason, entity_id, data=None, once_key=None):
        if not CRAB_BACKPACK_NAME_DEBUG:
            return
        if once_key is not None:
            if once_key in self._backpack_name_debug_seen:
                return
            self._backpack_name_debug_seen.add(once_key)
        payload = {
            "tick": self._tick,
            "entity_id": entity_id,
        }
        if data:
            payload.update(data)
        try:
            print("[fg_more_crab][backpack_name][%s] %s" % (
                reason,
                self._debug_payload_text(payload)
            ))
        except Exception:
            if IN_DEVELOPMENT:
                raise

    def _debug_payload_text(self, payload):
        parts = []
        for key in sorted(payload.keys()):
            parts.append("%s=%s" % (key, self._debug_value_text(payload.get(key, None))))
        return ", ".join(parts)

    def _debug_value_text(self, value):
        if value is None:
            return "None"
        try:
            if isinstance(value, unicode):
                return value.encode("utf-8")
        except NameError:
            pass
        except Exception:
            pass
        try:
            return str(value)
        except Exception:
            return "<unprintable>"

    def _is_player_sneaking(self, player_id):
        try:
            return bool(CompFactory.CreatePlayer(player_id).isSneaking())
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _is_player_blocking(self, player_id):
        try:
            player_comp = CompFactory.CreatePlayer(player_id)
            getter = getattr(player_comp, "GetIsBlocking", None)
            if getter is None:
                return None
            return bool(getter())
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _refresh_crab_shell_shield_defence_angle(self, player_id):
        if not player_id:
            return False
        item_comp = CompFactory.CreateItem(player_id)
        refreshed = False
        for pos_type_name in ("OFFHAND", "CARRIED"):
            pos_type = getattr(MinecraftEnum.ItemPosType, pos_type_name, None)
            if pos_type is None:
                continue
            try:
                item_dict = item_comp.GetPlayerItem(pos_type, 0, True)
            except Exception:
                item_dict = item_comp.GetPlayerItem(pos_type, 0)
            if not item_dict:
                continue
            item_name = self._get_item_name(item_dict)
            if item_name != CRAB_SHELL_SHIELD_ITEM:
                continue
            setter = getattr(item_comp, "SetItemDefenceAngle", None)
            if setter is None:
                continue
            try:
                if setter(pos_type, 0, CRAB_SHELL_SHIELD_DEFENCE_LEFT, CRAB_SHELL_SHIELD_DEFENCE_RIGHT) is not False:
                    refreshed = True
            except Exception:
                if IN_DEVELOPMENT:
                    raise
        return refreshed

    def _entity_has_component(self, entity_id, component_name):
        try:
            components = CompFactory.CreateEntityEvent(entity_id).GetComponents() or {}
            return component_name in components
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _is_entity_owner(self, entity_id, player_id):
        owner_id = self._resolve_entity_owner_id(entity_id)
        return owner_id == player_id

    def _resolve_entity_owner_id(self, entity_id):
        for factory_name, getter_names in (
                ("CreateTame", ("GetOwnerId", "GetEntityOwner", "GetOwner", "GetEntityOwnerId", "GetTamingPlayerId")),
                ("CreateActorOwner", ("GetOwnerId", "GetEntityOwner", "GetOwner", "GetEntityOwnerId")),
        ):
            factory = getattr(CompFactory, factory_name, None)
            if factory is None:
                continue
            try:
                comp = factory(entity_id)
            except Exception:
                continue
            for getter_name in getter_names:
                getter = getattr(comp, getter_name, None)
                if getter is None:
                    continue
                try:
                    owner_id = self._normalize_possible_entity_id(getter())
                except Exception:
                    owner_id = None
                if owner_id:
                    return owner_id
        return None

    def _normalize_possible_entity_id(self, value):
        if not value:
            return None
        if isinstance(value, dict):
            for key in ("playerId", "ownerId", "entityId", "id"):
                owner_id = self._normalize_possible_entity_id(value.get(key, None))
                if owner_id:
                    return owner_id
            return None
        if isinstance(value, (list, tuple)):
            for item in value:
                owner_id = self._normalize_possible_entity_id(item)
                if owner_id:
                    return owner_id
            return None
        try:
            if int(value) == -1:
                return None
        except Exception:
            pass
        return value

    def _is_entity_inventory_empty(self, entity_id, size):
        inventory_type = getattr(MinecraftEnum.ItemPosType, "INVENTORY", None)
        if inventory_type is None:
            self._log_validation_failure("backpack.inventory_pos_type_missing", {
                "entity_id": entity_id,
                "size": size,
            })
            return None
        item_comp = CompFactory.CreateItem(entity_id)
        if not hasattr(item_comp, "GetEntityItem"):
            self._log_validation_failure("backpack.get_entity_item_missing", {
                "entity_id": entity_id,
                "size": size,
            })
            return None
        for slot in range(size):
            try:
                item_dict = item_comp.GetEntityItem(inventory_type, slot)
            except Exception as error:
                if IN_DEVELOPMENT:
                    raise
                self._log_validation_failure("backpack.inventory_read_failed", {
                    "entity_id": entity_id,
                    "slot": slot,
                    "size": size,
                    "error": self._short_error_text(error),
                })
                return None
            if self._item_dict_has_item(item_dict):
                return False
        return True

    def _show_backpack_blocked_particle(self, entity_id):
        pos = self._get_entity_pos(entity_id)
        if pos is None:
            return
        self._run_level_command("/particle minecraft:basic_smoke_particle %s %s %s" % (
            pos[0],
            pos[1] + 0.8,
            pos[2]
        ))

    def _item_dict_has_item(self, item_dict):
        if not item_dict:
            return False
        item_name = self._get_item_name(item_dict)
        if not item_name:
            return False
        try:
            return int(item_dict.get("count", 1) or 0) > 0
        except Exception:
            return True

    def _is_damage_from_front(self, player_id, attacker_id):
        if not attacker_id or str(attacker_id) == "-1":
            return False
        player_pos = self._get_entity_pos(player_id)
        attacker_pos = self._get_entity_pos(attacker_id)
        if player_pos is None or attacker_pos is None:
            return False
        direction = self._get_entity_forward_dir(player_id)
        if direction is None:
            return False
        to_attacker = (
            float(attacker_pos[0]) - float(player_pos[0]),
            0.0,
            float(attacker_pos[2]) - float(player_pos[2])
        )
        length = math.sqrt(to_attacker[0] * to_attacker[0] + to_attacker[2] * to_attacker[2])
        if length <= 0.001:
            return True
        dot = direction[0] * (to_attacker[0] / length) + direction[2] * (to_attacker[2] / length)
        return dot >= CRAB_SHELL_SHIELD_FRONT_DOT

    def _get_entity_forward_dir(self, entity_id):
        try:
            rot = CompFactory.CreateRot(entity_id).GetRot()
            direction = ServerApi.GetDirFromRot((0, rot[1]))
            horizontal = math.sqrt(direction[0] * direction[0] + direction[2] * direction[2])
            if horizontal <= 0.001:
                return None
            return (direction[0] / horizontal, 0.0, direction[2] / horizontal)
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _tick_temporary_blocks(self):
        if not self._temporary_blocks:
            return
        for key, data in list(self._temporary_blocks.items()):
            if self._tick < data["expire_tick"]:
                continue
            dimension_id, pos = key
            current_name = self._get_block_name(pos, dimension_id)
            if current_name == data["block_name"]:
                if not self._set_block(pos, data["old_name"], data["old_aux"], dimension_id):
                    self._log_validation_failure("temporary_block.restore_failed", {
                        "dimension": dimension_id,
                        "pos": pos,
                        "block": data["block_name"],
                        "old_block": data["old_name"],
                    })
            self._temporary_blocks.pop(key, None)

    def _place_temporary_block_if_passable(self, pos, block_name, aux, dimension_id, duration_ticks):
        if not self._is_passable_block(self._get_block_name(pos, dimension_id)):
            return False
        return self._place_temporary_block(pos, block_name, aux, dimension_id, duration_ticks)

    def _place_temporary_ground_disc(self, center_pos, dimension_id, block_name, radius, duration_ticks):
        placed = 0
        for pos in self._disk_block_positions(center_pos, radius):
            ground_pos = (pos[0], pos[1] - 1, pos[2])
            old_name = self._get_block_name(ground_pos, dimension_id)
            if old_name in ("minecraft:bedrock", "minecraft:chest", "minecraft:barrel", "minecraft:trapped_chest"):
                continue
            if self._is_passable_block(old_name):
                continue
            if self._place_temporary_block(ground_pos, block_name, 0, dimension_id, duration_ticks):
                placed += 1
        return placed

    def _place_temporary_block(self, pos, block_name, aux, dimension_id, duration_ticks):
        int_pos = ServerApi.GetIntPos(pos)
        old_block = self._get_block_dict(int_pos, dimension_id) or {"name": "minecraft:air", "aux": 0}
        old_name = old_block.get("name", "minecraft:air")
        old_aux = old_block.get("aux", 0)
        if old_name == block_name:
            return False
        if not self._set_block(int_pos, block_name, aux, dimension_id):
            return False
        self._temporary_blocks[(dimension_id, int_pos)] = {
            "block_name": block_name,
            "old_name": old_name,
            "old_aux": old_aux,
            "expire_tick": self._tick + duration_ticks,
        }
        return True

    def _disk_block_positions(self, center_pos, radius):
        center = ServerApi.GetIntPos(center_pos)
        result = []
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if dx * dx + dz * dz <= radius * radius:
                    result.append((center[0] + dx, center[1], center[2] + dz))
        return result

    def _ring_block_positions(self, center_pos, radius):
        center = ServerApi.GetIntPos(center_pos)
        result = []
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                if max(abs(dx), abs(dz)) == radius:
                    result.append((center[0] + dx, center[1], center[2] + dz))
        return result

    def _try_spawn_boss_minions(self, boss_id, entity_type, boss_pos, dimension_id, count, max_near):
        if self._count_entities_near(boss_pos, dimension_id, 16, set([entity_type])) >= max_near:
            return 0
        spawned = 0
        for _idx in range(count):
            spawn_pos = (
                boss_pos[0] + random.uniform(-3.0, 3.0),
                boss_pos[1],
                boss_pos[2] + random.uniform(-3.0, 3.0),
            )
            if self.CreateEngineEntityByTypeStr(entity_type, spawn_pos, (0, 0), dimension_id, False, True):
                spawned += 1
        return spawned

    def _hurt_entities_near(self, center_pos, dimension_id, radius, damage, cause_name, attacker_id, knocked, exclude_ids):
        for entity_id in self._get_entities_in_square(
                (center_pos[0] - radius, center_pos[1] - 3, center_pos[2] - radius),
                (center_pos[0] + radius, center_pos[1] + 3, center_pos[2] + radius),
                dimension_id
        ) or []:
            if entity_id in exclude_ids:
                continue
            entity_pos = self._get_entity_pos(entity_id)
            if entity_pos is None or self._distance_sq(center_pos, entity_pos) > radius * radius:
                continue
            self._hurt_entity(entity_id, damage, cause_name, attacker_id, knocked)

    def _push_entities_near_towards(self, center_pos, dimension_id, radius, target_pos, speed, exclude_ids):
        for entity_id in self._get_entities_in_square(
                (center_pos[0] - radius, center_pos[1] - 3, center_pos[2] - radius),
                (center_pos[0] + radius, center_pos[1] + 3, center_pos[2] + radius),
                dimension_id
        ) or []:
            if entity_id in exclude_ids:
                continue
            entity_pos = self._get_entity_pos(entity_id)
            if entity_pos is None or self._distance_sq(center_pos, entity_pos) > radius * radius:
                continue
            self._push_entity_towards(entity_id, entity_pos, target_pos, speed)

    def _apply_effect_to_entities_near(self, center_pos, dimension_id, radius, effect_name, duration, amplifier, exclude_id, include_players=False):
        player_ids = set(ServerApi.GetPlayerList() or [])
        exclude_ids = exclude_id if isinstance(exclude_id, set) else set([exclude_id])
        for entity_id in self._get_entities_in_square(
                (center_pos[0] - radius, center_pos[1] - 3, center_pos[2] - radius),
                (center_pos[0] + radius, center_pos[1] + 3, center_pos[2] + radius),
                dimension_id
        ) or []:
            if entity_id in exclude_ids:
                continue
            if not include_players and entity_id in player_ids:
                continue
            entity_pos = self._get_entity_pos(entity_id)
            if entity_pos is None or self._distance_sq(center_pos, entity_pos) > radius * radius:
                continue
            self._add_effect(entity_id, effect_name, duration, amplifier, True)

    def _remove_effects(self, entity_id, effect_names):
        if not effect_names:
            return
        try:
            comp_effect = CompFactory.CreateEffect(entity_id)
            for effect_name in effect_names:
                if comp_effect.HasEffect(effect_name):
                    comp_effect.RemoveEffectFromEntity(effect_name)
        except Exception:
            if IN_DEVELOPMENT:
                raise

    def _set_entity_on_fire(self, entity_id, seconds, burn_damage):
        try:
            return bool(CompFactory.CreateAttr(entity_id).SetEntityOnFire(seconds, burn_damage))
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _move_pirate_to_escape_target(self, entity_id, pos, dimension_id):
        target_pos = self._find_nearest_water(pos, dimension_id, 8)
        if target_pos is None:
            target_pos = self._pirate_home_pos.get(entity_id, None)
        if target_pos is None:
            nearest_player = self._find_nearest_player(pos, dimension_id, 12.0)
            player_pos = self._get_entity_pos(nearest_player) if nearest_player else None
            if player_pos is not None:
                target_pos = (
                    pos[0] + (pos[0] - player_pos[0]),
                    pos[1],
                    pos[2] + (pos[2] - player_pos[2])
                )
        if target_pos is None:
            return
        self._push_entity_towards(entity_id, pos, target_pos, 0.20)

    def _find_nearest_water(self, center_pos, dimension_id, radius):
        return self._find_nearest_matching_block(center_pos, dimension_id, WATER_BLOCKS, radius, 2)

    def _drop_pirate_stolen_item(self, entity_id):
        if not entity_id:
            return
        item_dict = self._pirate_stolen_item.pop(entity_id, None)
        if not item_dict:
            return
        last = self._entity_last_pos.get(entity_id, None)
        if not last:
            return
        pos, dimension_id = last
        spawn_pos = (pos[0], pos[1] + 0.35, pos[2])
        try:
            self.CreateEngineItemEntity(item_dict, dimension_id, spawn_pos)
        except Exception:
            if IN_DEVELOPMENT:
                raise

    def _find_pirate_structure_anchor(self, center_pos, dimension_id):
        center = ServerApi.GetIntPos(center_pos)
        structure_hits = []
        water_hits = 0
        coast_hits = 0
        for dy in range(-5, 6):
            y = center[1] + dy
            for dx in range(-12, 13):
                x = center[0] + dx
                for dz in range(-12, 13):
                    z = center[2] + dz
                    block_name = self._get_block_name((x, y, z), dimension_id)
                    if self._is_structure_block(block_name):
                        structure_hits.append((x, y, z))
                    elif block_name in WATER_BLOCKS:
                        water_hits += 1
                    elif block_name in COAST_GROUND_BLOCKS:
                        coast_hits += 1
        if len(structure_hits) < 3 or water_hits < 6 or coast_hits < 3:
            return None
        return structure_hits[0]

    def _find_coast_hideout_anchor(self, center_pos, dimension_id):
        center = ServerApi.GetIntPos(center_pos)
        for dx in range(-16, 17, 2):
            for dz in range(-16, 17, 2):
                x = center[0] + dx
                z = center[2] + dz
                for y in range(center[1] + 5, center[1] - 9, -1):
                    ground_name = self._get_block_name((x, y - 1, z), dimension_id)
                    if ground_name not in COAST_GROUND_BLOCKS:
                        continue
                    if not self._is_valid_entity_stand_pos((x, y, z), dimension_id):
                        continue
                    if self._count_water_blocks_near((x, y, z), dimension_id, 7) < 8:
                        continue
                    if not self._can_place_hideout_at((x, y, z), dimension_id):
                        continue
                    return (x, y, z)
        return None

    def _create_pirate_hideout(self, anchor_pos, dimension_id):
        anchor = ServerApi.GetIntPos(anchor_pos)
        placements = [
            ((0, 0, 0), "minecraft:oak_planks", 0),
            ((1, 0, 0), "minecraft:oak_planks", 0),
            ((-1, 0, 0), "minecraft:oak_planks", 0),
            ((0, 0, 1), "minecraft:oak_planks", 0),
            ((0, 0, -1), "minecraft:oak_planks", 0),
            ((1, 0, 1), "minecraft:oak_planks", 0),
            ((-1, 0, -1), "minecraft:oak_planks", 0),
            ((1, 1, 0), "minecraft:barrel", 0),
            ((-1, 1, 0), "minecraft:chest", 0),
            ((0, 1, -1), "minecraft:oak_fence", 0),
        ]
        placed = 0
        for offset, block_name, aux in placements:
            pos = (anchor[0] + offset[0], anchor[1] + offset[1], anchor[2] + offset[2])
            if not self._can_replace_for_hideout(pos, dimension_id):
                continue
            if self._set_block(pos, block_name, aux, dimension_id):
                placed += 1
        return placed >= 5

    def _spawn_hideout_loot(self, anchor_pos, dimension_id):
        for item_name, min_count, max_count, chance in PIRATE_HIDEOUT_LOOT:
            if random.random() > chance:
                continue
            item_dict = {
                "newItemName": item_name,
                "newAuxValue": 0,
                "count": random.randint(min_count, max_count),
            }
            spawn_pos = (
                float(anchor_pos[0]) + random.uniform(-0.6, 0.6),
                float(anchor_pos[1]) + 1.15,
                float(anchor_pos[2]) + random.uniform(-0.6, 0.6),
            )
            try:
                self.CreateEngineItemEntity(item_dict, dimension_id, spawn_pos)
            except Exception:
                if IN_DEVELOPMENT:
                    raise

    def _can_place_hideout_at(self, anchor_pos, dimension_id):
        anchor = ServerApi.GetIntPos(anchor_pos)
        for dx, dz in ((0, 0), (1, 0), (-1, 0), (0, 1), (0, -1)):
            pos = (anchor[0] + dx, anchor[1], anchor[2] + dz)
            if not self._can_replace_for_hideout(pos, dimension_id):
                return False
        return True

    def _can_replace_for_hideout(self, pos, dimension_id):
        block_name = self._get_block_name(pos, dimension_id)
        return self._is_passable_block(block_name) or block_name in WATER_BLOCKS

    def _count_water_blocks_near(self, center_pos, dimension_id, radius):
        center = ServerApi.GetIntPos(center_pos)
        count = 0
        for dx in range(-radius, radius + 1):
            for dz in range(-radius, radius + 1):
                for dy in range(-1, 2):
                    if self._get_block_name((center[0] + dx, center[1] + dy, center[2] + dz), dimension_id) in WATER_BLOCKS:
                        count += 1
        return count

    def _count_pirates_near(self, center_pos, dimension_id, radius):
        return self._count_entities_near(center_pos, dimension_id, radius, PIRATE_ENTITY_TYPES)

    def _count_entities_near(self, center_pos, dimension_id, radius, entity_types):
        start_pos = (center_pos[0] - radius, center_pos[1] - 8, center_pos[2] - radius)
        end_pos = (center_pos[0] + radius, center_pos[1] + 8, center_pos[2] + radius)
        count = 0
        for entity_id in self._get_entities_in_square(start_pos, end_pos, dimension_id) or []:
            if self._get_entity_type(entity_id) in entity_types:
                count += 1
        return count

    def _find_pirate_spawn_pos(self, anchor_pos, dimension_id):
        anchor = ServerApi.GetIntPos(anchor_pos)
        for _idx in range(16):
            x = anchor[0] + random.randint(-8, 8)
            z = anchor[2] + random.randint(-8, 8)
            for y in range(anchor[1] + 5, anchor[1] - 8, -1):
                ground_name = self._get_block_name((x, y - 1, z), dimension_id)
                feet_name = self._get_block_name((x, y, z), dimension_id)
                head_name = self._get_block_name((x, y + 1, z), dimension_id)
                if not self._is_spawn_ground(ground_name):
                    continue
                if feet_name not in PASSABLE_BLOCKS or head_name not in PASSABLE_BLOCKS:
                    continue
                return (x + 0.5, y, z + 0.5)
        return None

    def _is_spawn_ground(self, block_name):
        return block_name in COAST_GROUND_BLOCKS or self._is_structure_block(block_name)

    def _is_structure_block(self, block_name):
        if not block_name:
            return False
        if block_name in STRUCTURE_BLOCKS:
            return True
        return block_name.startswith("minecraft:") and (
            block_name.endswith("_planks") or
            block_name.endswith("_log") or
            block_name.endswith("_wood") or
            block_name.endswith("_stairs") or
            block_name.endswith("_fence") or
            block_name.endswith("_slab")
        )

    def _push_entity_towards(self, entity_id, current_pos, target_pos, speed):
        dx = float(target_pos[0]) - float(current_pos[0])
        dz = float(target_pos[2]) - float(current_pos[2])
        horizontal_length = math.sqrt(dx * dx + dz * dz)
        if horizontal_length <= 0.001:
            return
        dy = max(min((float(target_pos[1]) - float(current_pos[1])) * 0.08, 0.08), -0.08)
        motion = (dx / horizontal_length * speed, dy, dz / horizontal_length * speed)
        try:
            self._set_entity_motion(entity_id, motion)
        except Exception:
            if IN_DEVELOPMENT:
                raise

    def _set_entity_motion(self, entity_id, motion):
        motion_comp = CompFactory.CreateActorMotion(entity_id)
        if entity_id in (ServerApi.GetPlayerList() or []) and hasattr(motion_comp, "SetPlayerMotion"):
            motion_comp.SetPlayerMotion(motion)
            return
        motion_comp.SetMotion(motion)

    def _is_valid_entity_stand_pos(self, stand_pos, dimension_id):
        if stand_pos is None:
            return False
        foot_name = self._get_block_name(stand_pos, dimension_id)
        head_name = self._get_block_name((stand_pos[0], stand_pos[1] + 1, stand_pos[2]), dimension_id)
        below_name = self._get_block_name((stand_pos[0], stand_pos[1] - 1, stand_pos[2]), dimension_id)
        if not self._is_passable_block(foot_name):
            return False
        if not self._is_passable_block(head_name):
            return False
        return (not self._is_passable_block(below_name)) or foot_name in WATER_BLOCKS

    def _has_clear_path_to_stand(self, current_pos, stand_pos, dimension_id):
        if current_pos is None or stand_pos is None:
            return False
        target_pos = (stand_pos[0] + 0.5, stand_pos[1], stand_pos[2] + 0.5)
        dx = float(target_pos[0]) - float(current_pos[0])
        dy = float(target_pos[1]) - float(current_pos[1])
        dz = float(target_pos[2]) - float(current_pos[2])
        step_count = int(max(abs(dx), abs(dy), abs(dz)) * 2)
        if step_count <= 1:
            return True
        for step in range(1, step_count):
            scale = float(step) / float(step_count)
            check_pos = ServerApi.GetIntPos((
                float(current_pos[0]) + dx * scale,
                float(current_pos[1]) + dy * scale,
                float(current_pos[2]) + dz * scale,
            ))
            if not self._is_passable_block(self._get_block_name(check_pos, dimension_id)):
                return False
            head_pos = (check_pos[0], check_pos[1] + 1, check_pos[2])
            if not self._is_passable_block(self._get_block_name(head_pos, dimension_id)):
                return False
        return True

    def _is_passable_block(self, block_name):
        if not block_name:
            return False
        if block_name in PASSABLE_BLOCKS:
            return True
        return block_name.startswith("minecraft:") and (
            block_name.endswith("_carpet") or
            block_name.endswith("_button") or
            block_name.endswith("_torch") or
            block_name.endswith("_sapling") or
            block_name.endswith("_sign")
        )

    def _set_block(self, pos, block_name, aux, dimension_id):
        block_info = self._get_block_info_comp()
        if block_info is None:
            return False
        try:
            return bool(block_info.SetBlockNew(
                ServerApi.GetIntPos(pos),
                {"name": block_name, "aux": aux},
                0,
                dimension_id,
                True,
                True
            ))
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _heal_entity(self, entity_id, amount):
        if amount <= 0:
            return
        try:
            attr_comp = CompFactory.CreateAttr(entity_id)
            health_type = MinecraftEnum.AttrType.HEALTH
            current_health = attr_comp.GetAttrValue(health_type)
            max_health = attr_comp.GetAttrMaxValue(health_type)
            if current_health is None or max_health is None:
                return
            attr_comp.SetAttrValue(health_type, min(float(current_health) + amount, float(max_health)), 0)
        except Exception:
            if IN_DEVELOPMENT:
                raise

    def _get_entity_health_ratio(self, entity_id):
        try:
            attr_comp = CompFactory.CreateAttr(entity_id)
            health_type = MinecraftEnum.AttrType.HEALTH
            current_health = attr_comp.GetAttrValue(health_type)
            max_health = attr_comp.GetAttrMaxValue(health_type)
            if current_health is None or max_health in (None, 0):
                return None
            return max(0.0, min(1.0, float(current_health) / float(max_health)))
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _add_effect(self, entity_id, effect_name, duration, amplifier, show_particles):
        if not entity_id or not effect_name or duration <= 0:
            return False
        try:
            return bool(CompFactory.CreateEffect(entity_id).AddEffectToEntity(
                effect_name,
                int(duration),
                int(amplifier),
                bool(show_particles)
            ))
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _hurt_entity(self, entity_id, damage, cause_name, attacker_id, knocked):
        if not entity_id or damage <= 0:
            return False
        cause = getattr(MinecraftEnum.ActorDamageCause, str(cause_name).capitalize(), cause_name)
        try:
            CompFactory.CreateHurt(entity_id).Hurt(damage, cause, attacker_id, None, knocked, "fg_crab_boss_skill")
            return True
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _run_level_command(self, command):
        if not command:
            return False
        try:
            return bool(CompFactory.CreateCommand(ServerApi.GetLevelId()).SetCommand(command))
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _play_sound_at(self, sound_name, pos, volume, pitch):
        if not sound_name or pos is None:
            return False
        return self._run_level_command("/playsound %s @a %s %s %s %s %s" % (
            sound_name,
            pos[0],
            pos[1],
            pos[2],
            volume,
            pitch
        ))

    def _cleanup_entity_state(self, entity_id):
        if not entity_id:
            return
        self._mineral_next_scan_tick.pop(entity_id, None)
        self._mineral_target_pos.pop(entity_id, None)
        self._mineral_target_stand_pos.pop(entity_id, None)
        self._mineral_buff_until_tick.pop(entity_id, None)
        self._pirate_next_steal_tick.pop(entity_id, None)
        self._pirate_stolen_item.pop(entity_id, None)
        self._pirate_escape_until_tick.pop(entity_id, None)
        self._pirate_home_pos.pop(entity_id, None)
        self._shield_cooldown_until.pop(entity_id, None)
        self._boss_weapon_active_cooldown_until.pop(entity_id, None)
        self._boss_phase.pop(entity_id, None)
        self._boss_next_skill_tick.pop(entity_id, None)
        self._entity_last_pos.pop(entity_id, None)
        self._normal_crab_default_named.discard(entity_id)
        self._backpack_name_debug_seen = set([
            key for key in self._backpack_name_debug_seen
            if not isinstance(key, tuple) or len(key) < 2 or key[1] != entity_id
        ])

    def _trigger_entity_event(self, entity_id, event_name):
        try:
            CompFactory.CreateEntityEvent(entity_id).TriggerCustomEvent(entity_id, event_name)
            return True
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return False

    def _get_block_name(self, block_pos, dimension_id):
        block_dict = self._get_block_dict(block_pos, dimension_id)
        return block_dict.get("name", None) if block_dict else None

    def _get_block_dict(self, block_pos, dimension_id):
        block_info = self._get_block_info_comp()
        if block_info is None:
            return None
        try:
            block_dict = block_info.GetBlockNew(ServerApi.GetIntPos(block_pos), dimension_id)
        except Exception:
            if IN_DEVELOPMENT:
                raise
            return None
        return block_dict

    def _get_entities_in_square(self, start_pos, end_pos, dimension_id):
        game_comp = self._get_game_comp()
        if game_comp is None:
            return []
        min_pos = (
            int(min(start_pos[0], end_pos[0])),
            int(min(start_pos[1], end_pos[1])),
            int(min(start_pos[2], end_pos[2])),
        )
        max_pos = (
            int(max(start_pos[0], end_pos[0])),
            int(max(start_pos[1], end_pos[1])),
            int(max(start_pos[2], end_pos[2])),
        )
        try:
            return game_comp.GetEntitiesInSquareArea(None, min_pos, max_pos, dimension_id) or []
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return []

    def _get_entity_type(self, entity_id):
        try:
            return CompFactory.CreateEngineType(entity_id).GetEngineTypeStr()
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _get_entity_pos(self, entity_id):
        if not entity_id:
            return None
        try:
            pos_comp = CompFactory.CreatePos(entity_id)
            pos = pos_comp.GetFootPos()
            return pos if pos is not None else pos_comp.GetPos()
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _get_entity_dimension(self, entity_id):
        if not entity_id:
            return None
        try:
            return CompFactory.CreateDimension(entity_id).GetEntityDimensionId()
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _is_entity_alive(self, entity_id):
        game_comp = self._get_game_comp()
        if game_comp is None:
            return False
        try:
            return bool(game_comp.IsEntityAlive(entity_id))
        except Exception:
            return False

    def _get_game_comp(self):
        try:
            return CompFactory.CreateGame(ServerApi.GetLevelId())
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _get_block_info_comp(self):
        try:
            return CompFactory.CreateBlockInfo(ServerApi.GetLevelId())
        except Exception:
            if IN_DEVELOPMENT:
                raise
        return None

    def _get_item_name(self, item_dict):
        if not item_dict:
            return ""
        return self._normalize_item_name(item_dict.get("newItemName", None) or item_dict.get("itemName", ""))

    def _normalize_item_name(self, item_name):
        if not item_name:
            return ""
        item_name = str(item_name)
        if ":" not in item_name:
            return "minecraft:%s" % item_name
        return item_name

    def _distance_sq(self, start_pos, end_pos):
        dx = float(start_pos[0]) - float(end_pos[0])
        dy = float(start_pos[1]) - float(end_pos[1])
        dz = float(start_pos[2]) - float(end_pos[2])
        return dx * dx + dy * dy + dz * dz

    def _choose_weighted(self, weighted_items):
        total_weight = sum(item[1] for item in weighted_items)
        roll = random.uniform(0, total_weight)
        current = 0
        for value, weight in weighted_items:
            current += weight
            if roll <= current:
                return value
        return weighted_items[0][0]
