# -*- coding: utf-8 -*-
from __future__ import print_function

import ast
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
BP = ROOT / "fg_more_crabBehaviorPack"
RP = ROOT / "fg_more_crabResourcePack"

BOSS_SPECS = [
    {
        "entity": "fg:crab_boss_lava",
        "loot_file": "fg_crab_boss_lava.json",
        "core": "fg:crab_boss_lava_core",
        "chest": "fg_boss_lair_lava.json",
        "structure": "boss_lair_lava.mcstructure",
        "weapon": "fg_lava_battle_axe.json",
    },
    {
        "entity": "fg:crab_boss_ice",
        "loot_file": "fg_crab_boss_ice.json",
        "core": "fg:crab_boss_ice_core",
        "chest": "fg_boss_lair_ice.json",
        "structure": "boss_lair_ice.mcstructure",
        "weapon": "fg_frost_crystal_crab_spear.json",
    },
    {
        "entity": "fg:crab_boss_poisonous_swamp",
        "loot_file": "fg_crab_boss_poisonous_swamp.json",
        "core": "fg:crab_boss_poisonous_swamp_core",
        "chest": "fg_boss_lair_poisonous_swamp.json",
        "structure": "boss_lair_poisonous_swamp.mcstructure",
        "weapon": "fg_swamp_poison_pliers.json",
    },
    {
        "entity": "fg:crab_boss_tidal",
        "loot_file": "fg_crab_boss_tidal.json",
        "core": "fg:crab_boss_tidal_core",
        "chest": "fg_boss_lair_tidal.json",
        "structure": "boss_lair_tidal.mcstructure",
        "weapon": "fg_tide_striker.json",
    },
    {
        "entity": "fg:crab_boss_sound_guard",
        "loot_file": "fg_crab_boss_sound_guard.json",
        "core": "fg:crab_boss_sound_guard_core",
        "chest": "fg_boss_temple_sound_guard.json",
        "structure": "boss_temple_sound_guard.mcstructure",
        "weapon": "fg_sound_following_giant_blade.json",
    },
]

CRAB_POT_ENTITIES = [
    "fg_crab_pots_ordinary.json",
    "fg_crab_pots_copper.json",
    "fg_crab_pots_iron.json",
    "fg_crab_pots_gold.json",
    "fg_crab_pots_diamond.json",
]

NORMAL_CRAB_ENTITIES = [
    "fg_crab_sandy.json",
    "fg_crab_red_tide.json",
    "fg_crab_blue_tide.json",
    "fg_crab_frost_shell.json",
    "fg_crab_coral.json",
    "fg_crab_dusk_shell.json",
    "fg_crab_moss_shell.json",
]

BACKPACK_BEHAVIOR_TOKENS = [
    '"fg:equip_backpack"',
    '"fg:unequip_backpack"',
    '"fg:request_unequip_backpack"',
    '"groups:crab_backpack_inventory"',
    '"fg:crab_backpack"',
]


def _read_text(path):
    return path.read_text(encoding="utf-8-sig")


def _load_json(path):
    return json.loads(_read_text(path))


def _walk_values(value):
    yield value
    if isinstance(value, dict):
        for child in value.values():
            for item in _walk_values(child):
                yield item
    elif isinstance(value, list):
        for child in value:
            for item in _walk_values(child):
                yield item


def _collect_item_names(value):
    names = set()
    for item in _walk_values(value):
        if not isinstance(item, dict):
            continue
        name = item.get("name", None) or item.get("newItemName", None) or item.get("itemName", None)
        if isinstance(name, str):
            names.add(name)
    return names


def _entity_description(data):
    return data.get("minecraft:entity", {}).get("description", {})


def _client_entity_description(data):
    return data.get("minecraft:client_entity", {}).get("description", {})


def _item_description(data):
    return data.get("minecraft:item", {}).get("description", {})


def _find_key(value, key_name):
    found = []
    if isinstance(value, dict):
        for key, child in value.items():
            if key == key_name:
                found.append(child)
            found.extend(_find_key(child, key_name))
    elif isinstance(value, list):
        for child in value:
            found.extend(_find_key(child, key_name))
    return found


def _recipe_result_names(data):
    result_names = []
    for recipe_key in ("minecraft:recipe_shaped", "minecraft:recipe_shapeless"):
        recipe = data.get(recipe_key, None)
        if not isinstance(recipe, dict):
            continue
        results = recipe.get("result", None)
        if not isinstance(results, list):
            results = [results]
        for item in results:
            if isinstance(item, dict):
                name = item.get("item", None) or item.get("name", None)
                if isinstance(name, str):
                    result_names.append(name)
            elif isinstance(item, str):
                result_names.append(item)
    furnace = data.get("minecraft:recipe_furnace", None)
    if isinstance(furnace, dict) and isinstance(furnace.get("output", None), str):
        result_names.append(furnace["output"])
    return result_names


def check_all_json():
    json_roots = [BP, RP]
    count = 0
    for base in json_roots:
        for path in sorted(base.rglob("*.json")):
            _load_json(path)
            count += 1
    return "parsed %s json files" % count


def check_interact_filter_schema():
    offenders = []

    def visit(value, path, current_path):
        if isinstance(value, dict):
            if isinstance(value.get("on_interact"), dict) and "filters" in value:
                offenders.append("%s:%s" % (path.relative_to(ROOT), current_path))
            for key, child in value.items():
                visit(child, path, current_path + "/" + key)
        elif isinstance(value, list):
            for index, child in enumerate(value):
                visit(child, path, current_path + "/%s" % index)

    for path in sorted((BP / "entities").glob("*.json")):
        visit(_load_json(path), path, "")
    if offenders:
        raise AssertionError("filters must live inside on_interact, not on interact entries: %s" % offenders)
    return "minecraft:interact filters are nested under on_interact"


def check_render_controller_molang_quotes():
    bad = []
    for path in sorted((RP / "render_controllers").glob("*.json")):
        data = _load_json(path)
        for value in _walk_values(data):
            if isinstance(value, str) and 'query.property("' in value:
                bad.append(str(path.relative_to(ROOT)))
                break
    if bad:
        raise AssertionError("render controller query.property should use single quotes: %s" % bad)
    return "render controller query.property strings use single quotes"


def check_client_animation_references():
    animation_ids = set()
    controller_ids = set()
    missing = []

    for path in sorted((RP / "animations").rglob("*.json")):
        animations = _load_json(path).get("animations", {})
        if isinstance(animations, dict):
            animation_ids.update(animations.keys())

    for path in sorted((RP / "animation_controllers").rglob("*.json")):
        controllers = _load_json(path).get("animation_controllers", {})
        if isinstance(controllers, dict):
            controller_ids.update(controllers.keys())

    for path in sorted((RP / "entity").glob("*.json")):
        animations = _client_entity_description(_load_json(path)).get("animations", {})
        if not isinstance(animations, dict):
            continue
        for alias, target in animations.items():
            if not isinstance(target, str):
                continue
            if target.startswith("controller.animation.") and target not in controller_ids:
                missing.append("%s:%s -> %s" % (path.name, alias, target))
            elif target.startswith("animation.") and target not in animation_ids:
                missing.append("%s:%s -> %s" % (path.name, alias, target))

    if missing:
        raise AssertionError("client animation targets are missing: %s" % missing)
    return "client entity animation aliases resolve to defined animations and controllers"


def check_sound_definition_files():
    path = RP / "sounds" / "sound_definitions.json"
    if not path.exists():
        return "no custom sound definitions file"

    missing = []
    for event_name, definition in _load_json(path).items():
        if not isinstance(definition, dict):
            continue
        for sound in definition.get("sounds", []):
            sound_name = sound.get("name") if isinstance(sound, dict) else sound
            if not isinstance(sound_name, str):
                continue
            sound_path = ROOT / "fg_more_crabResourcePack" / sound_name
            if sound_path.suffix:
                exists = sound_path.exists()
            else:
                exists = any(sound_path.with_suffix(extension).exists() for extension in (".ogg", ".wav", ".mp3", ".fsb"))
            if not exists:
                missing.append("%s -> %s" % (event_name, sound_name))

    if missing:
        raise AssertionError("sound definitions reference missing audio files: %s" % missing)
    return "custom sound definitions reference existing audio files"


def check_no_double_fg_namespace_prefix():
    bad_prefix = "fg:" + "fg_"
    offenders = []
    for base in (ROOT,):
        for path in sorted(base.rglob("*")):
            if not path.is_file() or "__pycache__" in path.parts or ".git" in path.parts:
                continue
            try:
                text = _read_text(path)
            except UnicodeDecodeError:
                continue
            if bad_prefix in text:
                offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        raise AssertionError("duplicate fg namespace prefix remains: %s" % offenders)
    return "no duplicate fg namespace prefixes remain"


def check_behavior_resource_id_links():
    bad = []

    bp_entities = set()
    for path in sorted((BP / "entities").glob("*.json")):
        identifier = _entity_description(_load_json(path)).get("identifier", None)
        if isinstance(identifier, str):
            bp_entities.add(identifier)

    rp_entities = set()
    for path in sorted((RP / "entity").glob("*.json")):
        identifier = _client_entity_description(_load_json(path)).get("identifier", None)
        if isinstance(identifier, str):
            rp_entities.add(identifier)

    bp_items = set()
    for path in sorted((BP / "netease_items_beh").glob("*.json")):
        identifier = _item_description(_load_json(path)).get("identifier", None)
        if isinstance(identifier, str):
            bp_items.add(identifier)

    rp_items = set()
    for path in sorted((RP / "netease_items_res").glob("*.json")):
        identifier = _item_description(_load_json(path)).get("identifier", None)
        if isinstance(identifier, str):
            rp_items.add(identifier)

    missing_entity_resources = sorted(bp_entities - rp_entities)
    missing_item_resources = sorted(bp_items - rp_items)
    if missing_entity_resources:
        bad.append("missing entity resources=%s" % missing_entity_resources)
    if missing_item_resources:
        bad.append("missing item resources=%s" % missing_item_resources)

    missing_recipe_results = []
    for path in sorted((BP / "netease_recipes").glob("*.json")):
        for name in _recipe_result_names(_load_json(path)):
            if name.startswith("fg:") and name not in bp_items:
                missing_recipe_results.append("%s -> %s" % (path.relative_to(ROOT), name))
    if missing_recipe_results:
        bad.append("missing recipe results=%s" % missing_recipe_results)

    if bad:
        raise AssertionError("; ".join(bad))
    return "behavior/resource entity and item ids are linked"


def check_python_ast():
    count = 0
    roots = [BP / "fg_more_crabScripts", ROOT / "tools"]
    for base in roots:
        if not base.exists():
            continue
        for path in sorted(base.rglob("*.py")):
            if "__pycache__" in path.parts:
                continue
            ast.parse(_read_text(path), filename=str(path))
            count += 1
    return "parsed %s python files" % count


def check_structures_exist():
    out = BP / "structures" / "fg_more_crab"
    missing = []
    empty = []
    for spec in BOSS_SPECS:
        path = out / spec["structure"]
        if not path.exists():
            missing.append(spec["structure"])
        elif path.stat().st_size <= 0:
            empty.append(spec["structure"])
    if missing or empty:
        raise AssertionError("missing=%s empty=%s" % (missing, empty))
    return "all boss structures exist"


def check_no_boss_spawn_rules():
    boss_ids = set(spec["entity"] for spec in BOSS_SPECS)
    offenders = []
    spawn_dir = BP / "spawn_rules"
    for path in sorted(spawn_dir.glob("*.json")):
        data = _load_json(path)
        identifier = data.get("minecraft:spawn_rules", {}).get("description", {}).get("identifier", "")
        if identifier in boss_ids or "boss" in path.stem:
            offenders.append(str(path.relative_to(ROOT)))
    if offenders:
        raise AssertionError("boss spawn rules present: %s" % offenders)
    return "boss natural spawn rules disabled"


def check_boss_entity_spawn_flags():
    bad = []
    for spec in BOSS_SPECS:
        path = BP / "entities" / spec["loot_file"]
        data = _load_json(path)
        desc = _entity_description(data)
        if desc.get("is_spawnable", None) is not False or desc.get("is_summonable", None) is not True:
            bad.append("%s spawnable=%s summonable=%s" % (
                spec["loot_file"],
                desc.get("is_spawnable", None),
                desc.get("is_summonable", None),
            ))
    if bad:
        raise AssertionError("boss release spawn flags invalid: %s" % bad)
    return "boss spawn eggs disabled while summon remains available"


def check_crab_pots_not_spawnable():
    bad = []
    for file_name in CRAB_POT_ENTITIES:
        path = BP / "entities" / file_name
        desc = _entity_description(_load_json(path))
        if desc.get("is_spawnable", None) is not False or desc.get("is_summonable", None) is not False:
            bad.append(file_name)
    if bad:
        raise AssertionError("crab pot spawn flags should both be false: %s" % bad)
    return "crab pots are item-placement only"


def check_crab_pot_health():
    bad = []
    for file_name in CRAB_POT_ENTITIES:
        path = BP / "entities" / file_name
        health = _load_json(path).get("minecraft:entity", {}).get("components", {}).get("minecraft:health", {})
        if health.get("value", None) != 3 or health.get("max", None) != 3:
            bad.append("%s value=%s max=%s" % (file_name, health.get("value", None), health.get("max", None)))
    if bad:
        raise AssertionError("all crab pots should have 3 health: %s" % bad)
    return "all crab pots have 3 health"


def check_crab_pot_ready_harvest_is_not_empty():
    bad = []
    for file_name in CRAB_POT_ENTITIES:
        path = BP / "entities" / file_name
        text = _read_text(path)
        if "fg:no_catch" in text:
            bad.append(file_name)
    if bad:
        raise AssertionError("ready crab pot harvest should not have empty no-catch branch: %s" % bad)
    return "ready crab pot harvest always yields loot or a caught crab"


def check_normal_crab_taming_uses_engine_owner():
    bad = []
    for file_name in NORMAL_CRAB_ENTITIES:
        path = BP / "entities" / file_name
        data = _load_json(path)
        text = _read_text(path)
        entity = data.get("minecraft:entity", {})
        desc = _entity_description(data)
        expected_display_name = "entity.%s.name" % desc.get("identifier", "")
        if desc.get("display_name", None) != expected_display_name:
            bad.append("%s missing description.display_name" % file_name)
        if "fg:try_tame" in text or "fg:on_tame_failed" in text:
            bad.append("%s has custom tame bypass event" % file_name)
        tameable = entity.get("components", {}).get("minecraft:tameable", {})
        tame_items = tameable.get("tame_items", [])
        tame_event = tameable.get("tame_event", {})
        if tame_event.get("event") != "fg:on_tame" or tame_event.get("target") != "self":
            bad.append("%s tameable does not route to fg:on_tame" % file_name)
        on_tame_text = json.dumps(entity.get("events", {}).get("fg:on_tame", {}), ensure_ascii=False)
        if "groups:tamed_follow" not in on_tame_text:
            bad.append("%s fg:on_tame does not add follow group" % file_name)
        if "groups:tamed_stay" not in on_tame_text:
            bad.append("%s fg:on_tame does not clear stay group" % file_name)
        interactions = entity.get("components", {}).get("minecraft:interact", {}).get("interactions", [])
        for interaction in interactions:
            on_interact = interaction.get("on_interact", {}) if isinstance(interaction, dict) else {}
            event = on_interact.get("event", None)
            if event not in ("fg:set_stay", "fg:set_follow"):
                continue
            all_of = on_interact.get("filters", {}).get("all_of", [])
            blocked_items = set()
            for item in all_of:
                if not isinstance(item, dict):
                    continue
                if item.get("test") == "has_equipment" and item.get("operator") == "not":
                    blocked_items.add(item.get("value", None))
            missing_items = sorted(set(tame_items) - blocked_items)
            if missing_items:
                bad.append("%s %s can still trigger while holding tame items %s" % (file_name, event, missing_items))
    if bad:
        raise AssertionError("normal crab taming must use minecraft:tameable owner path: %s" % bad)
    return "normal crab taming uses minecraft:tameable owner path"


def check_backpack_container_policy():
    bad = []
    horse_refs = []
    for path in sorted((BP / "entities").glob("*.json")):
        text = _read_text(path)
        if '"container_type": "horse"' in text or '"minecraft:is_chested"' in text:
            horse_refs.append(str(path.relative_to(ROOT)))
    for file_name in NORMAL_CRAB_ENTITIES:
        path = BP / "entities" / file_name
        data = _load_json(path)
        inventories = _find_key(data, "minecraft:inventory")
        matched = False
        for inventory in inventories:
            if not isinstance(inventory, dict):
                continue
            if inventory.get("container_type") == "container" and inventory.get("restrict_to_owner") is True:
                if int(inventory.get("inventory_size", 0) or 0) == 27:
                    matched = True
        if not matched:
            bad.append(file_name)
    if horse_refs or bad:
        raise AssertionError("horse_refs=%s missing_container=%s" % (horse_refs, bad))
    return "backpack keeps 27-slot owner-restricted container policy"


def check_backpack_only_normal_crabs():
    bad = []
    missing = []
    normal_files = set(NORMAL_CRAB_ENTITIES)
    for path in sorted((BP / "entities").glob("*.json")):
        text = _read_text(path)
        found = [token for token in BACKPACK_BEHAVIOR_TOKENS if token in text]
        if found and path.name not in normal_files:
            bad.append("%s has backpack tokens %s" % (path.name, found))
        if path.name in normal_files:
            for token in BACKPACK_BEHAVIOR_TOKENS:
                if token not in text:
                    missing.append("%s missing %s" % (path.name, token))
    if bad or missing:
        raise AssertionError("bad=%s missing=%s" % (bad, missing))
    return "backpack behavior is restricted to formal normal crabs"


def check_crab_backpack_item_tip():
    path = BP / "netease_items_beh" / "crab_backpack.json"
    data = _load_json(path)
    tips = data.get("minecraft:item", {}).get("components", {}).get("netease:customtips", {}).get("value", "")
    missing = []
    for token in ("潜行", "已驯服", "普通螃蟹", "27 格", "剪刀", "右键", "取下"):
        if token not in tips:
            missing.append(token)
    if missing:
        raise AssertionError("crab backpack tip missing tokens: %s" % missing)
    return "crab backpack item tip explains sneak-use, 27 slots, and shears right-click unequip"


def check_backpack_runtime_title_and_unequip_feedback():
    script_text = _read_text(BP / "fg_more_crabScripts" / "server" / "ServerMainSystem.py")
    required = [
        'NORMAL_CRAB_DEFAULT_NAMES = {',
        "CRAB_BACKPACK_NAME_DEBUG = False",
        'CRAB_BACKPACK_CONTAINER_TITLE = u"蟹壳背包"',
        'CRAB_BACKPACK_UNKNOWN_TITLE = u"未知"',
        "self._normal_crab_default_named = set()",
        "self._backpack_name_debug_seen = set()",
        "def _tick_normal_crab(self, entity_id, entity_type):",
        "def _ensure_tamed_normal_crab_default_name(self, entity_id, entity_type=None):",
        "self._ensure_tamed_normal_crab_default_name(entity_id, entity_type)",
        '"fg:is_tamed"',
        "default_name_set",
        "def _encode_name_for_set_name(self, name):",
        "encoded_type",
        "set_name_call",
        "def _debug_backpack_name(self, reason, entity_id, data=None, once_key=None):",
        '"minecraft:is_tamed"',
        "def _ensure_crab_backpack_container_title(self, entity_id):",
        "def _clear_crab_backpack_container_title(self, entity_id):",
        "CompFactory.CreateName(entity_id)",
        "setter(encoded_name)",
        "self._show_backpack_blocked_particle(entity_id)",
    ]
    missing = [token for token in required if token not in script_text]
    zh_text = _read_text(RP / "texts" / "zh_CN.lang")
    en_text = _read_text(RP / "texts" / "en_US.lang")
    if "action.interact.unequip_backpack=剪刀卸下空背包" not in zh_text:
        missing.append("zh_CN shears unequip interaction text")
    if "action.interact.unequip_backpack=Shears: Unequip Empty Backpack" not in en_text:
        missing.append("en_US shears unequip interaction text")
    if missing:
        raise AssertionError("backpack runtime title or unequip feedback missing: %s" % missing)
    return "tamed crab default naming, backpack title fallback, and shears unequip feedback are present"


def check_crab_backpack_container_title_l10n():
    required = {
        "zh_CN.lang": ("蟹壳背包",),
        "en_US.lang": ("Crab Shell Backpack",),
    }
    keys = (
        "container.fg:crab_backpack",
        "container.fg.crab_backpack",
        "container.crab_backpack",
        "container.crab_backpack.name",
    )
    bad = []
    for file_name, expected_values in required.items():
        path = RP / "texts" / file_name
        values = {}
        for line in _read_text(path).splitlines():
            if "=" not in line:
                continue
            key, value = line.split("=", 1)
            values[key] = value
        for key in keys:
            if values.get(key, None) not in expected_values:
                bad.append("%s missing %s" % (file_name, key))
    if bad:
        raise AssertionError("crab backpack container title localization incomplete: %s" % bad)
    return "crab backpack container title localization keys are present"


def check_normal_crab_entity_title_aliases():
    bad = []
    for file_name in NORMAL_CRAB_ENTITIES:
        entity_id = file_name[:-5].replace("fg_", "", 1)
        colon_key = "entity.fg:%s.name" % entity_id
        dot_key = "entity.fg.%s.name" % entity_id
        for lang_name in ("zh_CN.lang", "en_US.lang"):
            path = RP / "texts" / lang_name
            values = {}
            for line in _read_text(path).splitlines():
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                values[key] = value
            if not values.get(colon_key, ""):
                bad.append("%s missing %s" % (lang_name, colon_key))
            if values.get(dot_key, None) != values.get(colon_key, None):
                bad.append("%s %s does not mirror %s" % (lang_name, dot_key, colon_key))
    if bad:
        raise AssertionError("normal crab entity title localization aliases incomplete: %s" % bad)
    return "normal crab entity title localization includes colon and dot aliases"


def check_backpack_resource_bindings():
    bad = []
    expected_texture = "textures/entity/crab_backpack/crab_backpack"
    expected_geometry = "geometry.crab_backpack"
    expected_condition = "query.property('fg:has_backpack')"
    normal_resource_files = set(file_name.replace(".json", ".entity.json") for file_name in NORMAL_CRAB_ENTITIES)
    for file_name in NORMAL_CRAB_ENTITIES:
        path = RP / "entity" / file_name.replace(".json", ".entity.json")
        data = _load_json(path)
        desc = _client_entity_description(data)
        textures = desc.get("textures", {})
        geometry = desc.get("geometry", {})
        render_controllers = desc.get("render_controllers", [])
        if textures.get("crab_backpack", None) != expected_texture:
            bad.append("%s missing crab_backpack texture" % path.name)
        if geometry.get("crab_backpack", None) != expected_geometry:
            bad.append("%s missing crab_backpack geometry" % path.name)
        has_conditioned_controller = False
        for item in render_controllers:
            if isinstance(item, dict) and item.get("controller.render.crab_backpack", None) == expected_condition:
                has_conditioned_controller = True
        if not has_conditioned_controller:
            bad.append("%s missing conditioned crab_backpack render controller" % path.name)

    for path in sorted((RP / "entity").glob("*.entity.json")):
        if path.name in normal_resource_files:
            continue
        data = _load_json(path)
        desc = _client_entity_description(data)
        textures = desc.get("textures", {})
        geometry = desc.get("geometry", {})
        render_controllers = desc.get("render_controllers", [])
        if "crab_backpack" in textures:
            bad.append("%s should not bind crab_backpack texture" % path.name)
        if "crab_backpack" in geometry:
            bad.append("%s should not bind crab_backpack geometry" % path.name)
        for item in render_controllers:
            if item == "controller.render.crab_backpack":
                bad.append("%s should not use crab_backpack render controller" % path.name)
            if isinstance(item, dict) and "controller.render.crab_backpack" in item:
                bad.append("%s should not use crab_backpack render controller" % path.name)

    render_data = _load_json(RP / "render_controllers" / "mc_default.render.json")
    controllers = render_data.get("render_controllers", {})
    backpack_controller = controllers.get("controller.render.crab_backpack", {})
    backpack_visibility = json.dumps(backpack_controller.get("part_visibility", []), ensure_ascii=False)
    if expected_condition not in backpack_visibility:
        bad.append("controller.render.crab_backpack missing fg:has_backpack visibility guard")
    crab_controller = controllers.get("controller.render.fg_crab", {})
    crab_visibility = json.dumps(crab_controller.get("part_visibility", []), ensure_ascii=False)
    if '"crab_backpack": "0.0"' not in crab_visibility:
        bad.append("controller.render.fg_crab should hide embedded crab_backpack bone")

    if bad:
        raise AssertionError("backpack resource bindings incomplete: %s" % bad)
    return "normal crab backpack texture geometry and conditioned render controller are bound"


def check_boss_loot_and_chests():
    chest_core_refs = []
    missing_core = []
    for spec in BOSS_SPECS:
        chest_path = BP / "loot_tables" / "chests" / spec["chest"]
        chest_names = _collect_item_names(_load_json(chest_path))
        if spec["core"] in chest_names:
            chest_core_refs.append(spec["chest"])

        loot_path = BP / "loot_tables" / "entities" / spec["loot_file"]
        loot_names = _collect_item_names(_load_json(loot_path))
        if spec["core"] not in loot_names:
            missing_core.append(spec["loot_file"])
    if chest_core_refs or missing_core:
        raise AssertionError("chest_core_refs=%s missing_core=%s" % (chest_core_refs, missing_core))
    return "boss cores are direct boss drops, not structure chest drops"


def check_boss_weapon_entries():
    bad = []
    script_text = _read_text(BP / "fg_more_crabScripts" / "server" / "ServerMainSystem.py")
    if "BOSS_WEAPON_ACTIVE_COOLDOWN_TICKS = SERVER_TICKS_PER_SECOND * 12" not in script_text:
        bad.append("runtime cooldown is not 12 seconds at 30 ticks/sec")
    if "BOSS_LAIR_RESPAWN_INTERVAL_TICKS = SERVER_TICKS_PER_SECOND * 60 * 20 * 3" not in script_text:
        bad.append("boss lair respawn interval is not 3 minecraft days")
    for token in ("_boss_lair_anchor_by_bucket", "_boss_lair_next_respawn_tick", "bucket in self._boss_lair_buckets"):
        if token not in script_text:
            bad.append("boss lair one-time structure guard missing: %s" % token)
    for spec in BOSS_SPECS:
        path = BP / "netease_items_beh" / spec["weapon"]
        data = _load_json(path)
        item = data.get("minecraft:item", {})
        components = item.get("components", {})
        tips = components.get("netease:customtips", {}).get("value", "")
        if "右键" not in tips or "12 秒" not in tips:
            bad.append(spec["weapon"])
        if "minecraft:max_damage" not in components:
            bad.append(spec["weapon"] + " missing max damage")
    if bad:
        raise AssertionError("bad boss weapon entries: %s" % bad)
    return "boss weapons expose active skill tips and durability"


def check_crab_shell_shield_entry():
    path = BP / "netease_items_beh" / "crab_shell_shield.json"
    data = _load_json(path)
    item = data.get("minecraft:item", {})
    desc = item.get("description", {})
    components = item.get("components", {})
    bad = []
    if desc.get("custom_item_type") != "shield":
        bad.append("custom_item_type")
    if components.get("netease:allow_offhand", {}).get("value", None) is not True:
        bad.append("allow_offhand")
    if "minecraft:max_damage" not in components:
        bad.append("max_damage")
    script_text = _read_text(BP / "fg_more_crabScripts" / "server" / "ServerMainSystem.py")
    for token in ("OnPlayerActiveShieldServerEvent", "OnPlayerBlockedByShieldAfterServerEvent", "SetItemDefenceAngle", "GetIsBlocking"):
        if token not in script_text:
            bad.append(token)
    if bad:
        raise AssertionError("shield entry incomplete: %s" % bad)
    return "crab shell shield entry and script hooks present"


def check_boss_armor_runtime_effects():
    script_text = _read_text(BP / "fg_more_crabScripts" / "server" / "ServerMainSystem.py")
    required = [
        '"tidal"',
        '"push_aura": 0.24',
        'config.get("push_aura", 0)',
        "_push_entities_near_towards(player_pos, dimension_id, 4.0, player_pos",
    ]
    missing = [token for token in required if token not in script_text]
    if missing:
        raise AssertionError("boss armor runtime effect missing: %s" % missing)
    return "tidal boss armor has periodic push aura runtime hook"


def check_item_name_fallbacks():
    script_text = _read_text(BP / "fg_more_crabScripts" / "server" / "ServerMainSystem.py")
    required = [
        "def _get_item_name(self, item_dict):",
        "normalized_name = self._get_item_name(item_dict)",
        "item_name = self._get_item_name(weapon_slot[2])",
        "self._get_item_name(item_dict) == item_name",
        "armor_names.append(self._get_item_name(item_dict) if item_dict else \"\")",
    ]
    missing = [token for token in required if token not in script_text]
    if missing:
        raise AssertionError("item name fallback missing: %s" % missing)
    return "runtime item checks support itemName and newItemName"


def check_acceptance_docs():
    path = ROOT / "docs" / "TASK_01_15_acceptance_checklist.md"
    if not path.exists():
        raise AssertionError("missing docs/TASK_01_15_acceptance_checklist.md")
    text = _read_text(path)
    for token in ("TASK-01~15", "container", "不自动切", "实机"):
        if token not in text:
            raise AssertionError("acceptance checklist missing token: %s" % token)
    return "acceptance checklist documents current validation scope"


def check_expansion_task_roadmap():
    roadmap_path = ROOT / "docs" / "07_dev_roadmap.md"
    acceptance_path = ROOT / "docs" / "TASK_01_15_acceptance_checklist.md"
    roadmap = _read_text(roadmap_path)
    acceptance = _read_text(acceptance_path)

    for task_id in range(16, 24):
        token = "TASK-%s" % task_id
        if token not in roadmap:
            raise AssertionError("roadmap missing expansion task: %s" % token)
    for token in ("双线并行", "TASK-16~23"):
        if token not in roadmap:
            raise AssertionError("roadmap missing expansion policy: %s" % token)
    if "TASK-16~23" not in acceptance or "并行" not in acceptance:
        raise AssertionError("acceptance checklist must allow the parallel expansion task line")
    return "TASK-16 through TASK-23 are numbered and allowed to run in parallel"


CHECKS = [
    ("json", check_all_json),
    ("interact_filter_schema", check_interact_filter_schema),
    ("render_controller_molang", check_render_controller_molang_quotes),
    ("client_animation_references", check_client_animation_references),
    ("sound_definition_files", check_sound_definition_files),
    ("no_double_fg_namespace_prefix", check_no_double_fg_namespace_prefix),
    ("behavior_resource_id_links", check_behavior_resource_id_links),
    ("python_ast", check_python_ast),
    ("boss_structures", check_structures_exist),
    ("boss_spawn_rules", check_no_boss_spawn_rules),
    ("boss_spawn_flags", check_boss_entity_spawn_flags),
    ("crab_pot_spawn_flags", check_crab_pots_not_spawnable),
    ("crab_pot_health", check_crab_pot_health),
    ("crab_pot_ready_harvest", check_crab_pot_ready_harvest_is_not_empty),
    ("normal_crab_taming_owner_path", check_normal_crab_taming_uses_engine_owner),
    ("backpack_container_policy", check_backpack_container_policy),
    ("backpack_only_normal_crabs", check_backpack_only_normal_crabs),
    ("crab_backpack_item_tip", check_crab_backpack_item_tip),
    ("backpack_runtime_title_unequip_feedback", check_backpack_runtime_title_and_unequip_feedback),
    ("crab_backpack_container_title_l10n", check_crab_backpack_container_title_l10n),
    ("normal_crab_entity_title_aliases", check_normal_crab_entity_title_aliases),
    ("backpack_resource_bindings", check_backpack_resource_bindings),
    ("boss_loot", check_boss_loot_and_chests),
    ("boss_weapons", check_boss_weapon_entries),
    ("crab_shell_shield", check_crab_shell_shield_entry),
    ("boss_armor_effects", check_boss_armor_runtime_effects),
    ("item_name_fallbacks", check_item_name_fallbacks),
    ("acceptance_docs", check_acceptance_docs),
    ("expansion_task_roadmap", check_expansion_task_roadmap),
]


def main():
    failures = []
    for name, check in CHECKS:
        try:
            message = check()
            print("[PASS] %s: %s" % (name, message))
        except Exception as error:
            failures.append((name, error))
            print("[FAIL] %s: %s" % (name, error))
    if failures:
        print("")
        print("%s checks failed" % len(failures))
        return 1
    print("")
    print("all checks passed")
    return 0


if __name__ == "__main__":
    sys.exit(main())
