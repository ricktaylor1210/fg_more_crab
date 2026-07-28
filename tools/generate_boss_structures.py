from __future__ import print_function

import math
import struct
from pathlib import Path


TAG_END = 0
TAG_BYTE = 1
TAG_SHORT = 2
TAG_INT = 3
TAG_LONG = 4
TAG_FLOAT = 5
TAG_DOUBLE = 6
TAG_BYTE_ARRAY = 7
TAG_STRING = 8
TAG_LIST = 9
TAG_COMPOUND = 10
TAG_INT_ARRAY = 11
TAG_LONG_ARRAY = 12

BLOCK_VERSION = 18163713
STRUCTURE_VOID = "minecraft:structure_void"
AIR = "minecraft:air"


def _write_string(buf, value):
    data = value.encode("utf-8")
    buf.extend(struct.pack("<H", len(data)))
    buf.extend(data)


def _write_payload(buf, tag_type, value):
    if tag_type == TAG_BYTE:
        buf.extend(struct.pack("<b", value))
    elif tag_type == TAG_SHORT:
        buf.extend(struct.pack("<h", value))
    elif tag_type == TAG_INT:
        buf.extend(struct.pack("<i", value))
    elif tag_type == TAG_LONG:
        buf.extend(struct.pack("<q", value))
    elif tag_type == TAG_FLOAT:
        buf.extend(struct.pack("<f", value))
    elif tag_type == TAG_DOUBLE:
        buf.extend(struct.pack("<d", value))
    elif tag_type == TAG_STRING:
        _write_string(buf, value)
    elif tag_type == TAG_LIST:
        child_type, values = value
        buf.extend(struct.pack("<bi", child_type, len(values)))
        for item in values:
            _write_payload(buf, child_type, item)
    elif tag_type == TAG_COMPOUND:
        for name, child_type, child_value in value:
            buf.extend(struct.pack("<b", child_type))
            _write_string(buf, name)
            _write_payload(buf, child_type, child_value)
        buf.extend(struct.pack("<b", TAG_END))
    else:
        raise ValueError("Unsupported NBT tag type: %s" % tag_type)


def _write_root_compound(fields):
    buf = bytearray()
    buf.extend(struct.pack("<b", TAG_COMPOUND))
    _write_string(buf, "")
    _write_payload(buf, TAG_COMPOUND, fields)
    return bytes(buf)


def _block_entry(block_name):
    return [
        ("name", TAG_STRING, block_name),
        ("states", TAG_COMPOUND, []),
        ("version", TAG_INT, BLOCK_VERSION),
    ]


def _index(size, x, y, z):
    return y * size[2] * size[0] + z * size[0] + x


class Structure(object):
    def __init__(self, size):
        self.size = size
        self.blocks = {}
        self.cx = size[0] // 2
        self.cz = size[2] // 2

    def set_block(self, x, y, z, block_name):
        if x < 0 or y < 0 or z < 0:
            return
        if x >= self.size[0] or y >= self.size[1] or z >= self.size[2]:
            return
        self.blocks[(x, y, z)] = block_name

    def fill_air_cylinder(self, radius, height):
        for y in range(1, min(height + 1, self.size[1])):
            for x in range(self.size[0]):
                for z in range(self.size[2]):
                    if self._dist_sq(x, z) <= radius * radius:
                        self.set_block(x, y, z, AIR)

    def floor_disc(self, radius, floor_block, border_block, trim_block=None):
        for x in range(self.size[0]):
            for z in range(self.size[2]):
                dist = math.sqrt(self._dist_sq(x, z))
                if dist > radius:
                    continue
                block_name = floor_block
                if dist >= radius - 1.5:
                    block_name = border_block
                elif trim_block and int(dist) % 6 == 0:
                    block_name = trim_block
                self.set_block(x, 0, z, block_name)

    def ring(self, radius, block_name, y=0, width=1):
        for x in range(self.size[0]):
            for z in range(self.size[2]):
                dist = math.sqrt(self._dist_sq(x, z))
                if radius - width <= dist <= radius:
                    self.set_block(x, y, z, block_name)

    def cross_path(self, block_name, half_len, width=1):
        for i in range(-half_len, half_len + 1):
            for w in range(-width, width + 1):
                self.set_block(self.cx + i, 0, self.cz + w, block_name)
                self.set_block(self.cx + w, 0, self.cz + i, block_name)

    def diagonal_path(self, block_name, half_len):
        for i in range(-half_len, half_len + 1):
            for w in (-1, 0, 1):
                self.set_block(self.cx + i, 0, self.cz + i + w, block_name)
                self.set_block(self.cx + i, 0, self.cz - i + w, block_name)

    def altar(self, base_block, marker_block, accent_block=None):
        for dx in range(-2, 3):
            for dz in range(-2, 3):
                if abs(dx) == 2 and abs(dz) == 2:
                    continue
                self.set_block(self.cx + dx, 1, self.cz + dz, base_block)
        for dx in range(-1, 2):
            for dz in range(-1, 2):
                self.set_block(self.cx + dx, 2, self.cz + dz, base_block)
        self.set_block(self.cx, 3, self.cz, marker_block)
        if accent_block:
            self.set_block(self.cx - 3, 1, self.cz, accent_block)
            self.set_block(self.cx + 3, 1, self.cz, accent_block)
            self.set_block(self.cx, 1, self.cz - 3, accent_block)
            self.set_block(self.cx, 1, self.cz + 3, accent_block)

    def pillars(self, block_name, cap_block, height, radius):
        for dx, dz in ((radius, radius), (-radius, radius), (radius, -radius), (-radius, -radius)):
            self.column(self.cx + dx, self.cz + dz, 1, height, block_name, cap_block)

    def column(self, x, z, start_y, height, block_name, cap_block=None):
        for y in range(start_y, min(start_y + height, self.size[1])):
            self.set_block(x, y, z, block_name)
        if cap_block:
            top_y = min(start_y + height, self.size[1] - 1)
            self.set_block(x, top_y, z, cap_block)

    def scatter_ring(self, block_name, radius, y=1, step=30):
        for angle in range(0, 360, step):
            rad = math.radians(angle)
            x = int(round(self.cx + math.cos(rad) * radius))
            z = int(round(self.cz + math.sin(rad) * radius))
            self.set_block(x, y, z, block_name)

    def hazard_pool(self, block_name, radius, y=0, count=4):
        for angle in range(45, 360, max(1, 360 // count)):
            rad = math.radians(angle)
            px = int(round(self.cx + math.cos(rad) * radius))
            pz = int(round(self.cz + math.sin(rad) * radius))
            for dx in range(-2, 3):
                for dz in range(-2, 3):
                    if dx * dx + dz * dz <= 4:
                        self.set_block(px + dx, y, pz + dz, block_name)

    def gates(self, block_name, cap_block, radius, height):
        for x, z in (
                (self.cx, self.cz - radius),
                (self.cx, self.cz + radius),
                (self.cx - radius, self.cz),
                (self.cx + radius, self.cz)):
            self.column(x - 1, z, 1, height, block_name, cap_block)
            self.column(x + 1, z, 1, height, block_name, cap_block)
            self.set_block(x, height, z, cap_block)

    def chest_points(self, base_block):
        for dx, dz in ((-6, -8), (6, -8), (0, 9)):
            self.set_block(self.cx + dx, 0, self.cz + dz, base_block)
            self.set_block(self.cx + dx, 1, self.cz + dz, "minecraft:chest")

    def _dist_sq(self, x, z):
        return (x - self.cx) * (x - self.cx) + (z - self.cz) * (z - self.cz)

    def to_mcstructure(self):
        palette = [STRUCTURE_VOID, AIR]
        for block_name in sorted(set(self.blocks.values())):
            if block_name not in palette:
                palette.append(block_name)
        palette_index = dict((name, index) for index, name in enumerate(palette))

        total = self.size[0] * self.size[1] * self.size[2]
        primary = [0] * total
        secondary = [-1] * total
        for (x, y, z), block_name in self.blocks.items():
            primary[_index(self.size, x, y, z)] = palette_index[block_name]

        block_palette = [_block_entry(block_name) for block_name in palette]
        fields = [
            ("format_version", TAG_INT, 1),
            ("size", TAG_LIST, (TAG_INT, list(self.size))),
            ("structure", TAG_COMPOUND, [
                ("block_indices", TAG_LIST, (TAG_LIST, [
                    (TAG_INT, primary),
                    (TAG_INT, secondary),
                ])),
                ("entities", TAG_LIST, (TAG_COMPOUND, [])),
                ("palette", TAG_COMPOUND, [
                    ("default", TAG_COMPOUND, [
                        ("block_palette", TAG_LIST, (TAG_COMPOUND, block_palette)),
                        ("block_position_data", TAG_COMPOUND, []),
                    ]),
                ]),
            ]),
            ("structure_world_origin", TAG_LIST, (TAG_INT, [0, 0, 0])),
        ]
        return _write_root_compound(fields)


def _make_lava():
    s = Structure((33, 14, 33))
    s.fill_air_cylinder(14, 9)
    s.floor_disc(15, "minecraft:blackstone", "minecraft:magma", "minecraft:basalt")
    s.cross_path("minecraft:polished_blackstone", 13, 1)
    s.diagonal_path("minecraft:basalt", 10)
    s.ring(11, "minecraft:magma", 0, 1)
    s.hazard_pool("minecraft:lava", 8, 0, 5)
    s.pillars("minecraft:basalt", "minecraft:magma", 7, 11)
    s.gates("minecraft:blackstone", "minecraft:magma", 14, 5)
    s.altar("minecraft:blackstone", "minecraft:magma", "minecraft:fire")
    s.scatter_ring("minecraft:fire", 6, 1, 30)
    s.chest_points("minecraft:blackstone")
    return s


def _make_ice():
    s = Structure((33, 14, 33))
    s.fill_air_cylinder(14, 9)
    s.floor_disc(15, "minecraft:packed_ice", "minecraft:snow", "minecraft:blue_ice")
    s.cross_path("minecraft:blue_ice", 13, 1)
    s.diagonal_path("minecraft:ice", 10)
    s.ring(11, "minecraft:snow", 0, 1)
    s.hazard_pool("minecraft:powder_snow", 8, 0, 5)
    s.pillars("minecraft:packed_ice", "minecraft:blue_ice", 7, 11)
    s.gates("minecraft:ice", "minecraft:blue_ice", 14, 5)
    s.altar("minecraft:packed_ice", "minecraft:blue_ice", "minecraft:snow_layer")
    s.scatter_ring("minecraft:snow_layer", 6, 1, 30)
    s.chest_points("minecraft:packed_ice")
    return s


def _make_swamp():
    s = Structure((33, 12, 33))
    s.fill_air_cylinder(14, 7)
    s.floor_disc(15, "minecraft:mud", "minecraft:moss_block", "minecraft:clay")
    s.cross_path("minecraft:mangrove_planks", 13, 1)
    s.diagonal_path("minecraft:clay", 10)
    s.ring(11, "minecraft:moss_block", 0, 1)
    s.hazard_pool("minecraft:slime_block", 8, 0, 6)
    s.pillars("minecraft:mangrove_log", "minecraft:moss_block", 5, 11)
    s.gates("minecraft:mangrove_log", "minecraft:moss_block", 14, 4)
    s.altar("minecraft:moss_block", "minecraft:slime_block", "minecraft:brown_mushroom")
    s.scatter_ring("minecraft:slime_block", 6, 1, 45)
    s.chest_points("minecraft:moss_block")
    return s


def _make_tidal():
    s = Structure((35, 12, 35))
    s.fill_air_cylinder(15, 7)
    s.floor_disc(16, "minecraft:prismarine", "minecraft:dark_prismarine", "minecraft:sea_lantern")
    s.cross_path("minecraft:sea_lantern", 14, 1)
    s.diagonal_path("minecraft:prismarine_bricks", 11)
    s.ring(12, "minecraft:water", 0, 1)
    s.hazard_pool("minecraft:flowing_water", 9, 0, 6)
    s.pillars("minecraft:dark_prismarine", "minecraft:sea_lantern", 5, 12)
    s.gates("minecraft:prismarine_bricks", "minecraft:sea_lantern", 15, 4)
    s.altar("minecraft:prismarine", "minecraft:sea_lantern", "minecraft:water")
    s.scatter_ring("minecraft:sea_lantern", 7, 1, 30)
    s.chest_points("minecraft:prismarine")
    return s


def _make_echo():
    s = Structure((39, 16, 39))
    s.fill_air_cylinder(17, 11)
    s.floor_disc(18, "minecraft:deepslate", "minecraft:calcite", "minecraft:amethyst_block")
    s.cross_path("minecraft:amethyst_block", 16, 1)
    s.diagonal_path("minecraft:tuff", 13)
    s.ring(13, "minecraft:calcite", 0, 1)
    s.hazard_pool("minecraft:amethyst_block", 9, 0, 6)
    s.pillars("minecraft:deepslate", "minecraft:amethyst_block", 9, 14)
    s.gates("minecraft:deepslate", "minecraft:amethyst_block", 17, 6)
    s.altar("minecraft:calcite", "minecraft:amethyst_block", "minecraft:sculk")
    s.scatter_ring("minecraft:amethyst_block", 8, 2, 30)
    s.chest_points("minecraft:deepslate")
    return s


STRUCTURES = {
    "boss_lair_lava.mcstructure": _make_lava,
    "boss_lair_ice.mcstructure": _make_ice,
    "boss_lair_poisonous_swamp.mcstructure": _make_swamp,
    "boss_lair_tidal.mcstructure": _make_tidal,
    "boss_temple_sound_guard.mcstructure": _make_echo,
}


def main():
    out_dir = Path("fg_more_crabBehaviorPack") / "structures" / "fg_more_crab"
    out_dir.mkdir(parents=True, exist_ok=True)
    for file_name, factory in sorted(STRUCTURES.items()):
        structure = factory()
        path = out_dir / file_name
        path.write_bytes(structure.to_mcstructure())
        print("%s %s bytes" % (path, path.stat().st_size))


if __name__ == "__main__":
    main()
