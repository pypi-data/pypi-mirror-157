from terraria_pc_player_api import TerrariaPCPlayer
from terraria_xbox360_player_api import TerrariaXbox360Player
from terraria_apis_objects import Item, Buff, SpawnPoint
from typing import Optional
from hashlib import sha256
from struct import pack, unpack, unpack_from
from base64 import b64encode, b64decode

from datetime import timedelta

_pet_to_buff = [41, 42, 45, 50, 51, 52, 53, 54, 55, 56, 61, 65, 66, 81, 82, 84, 85, 91, 92, 127, 136]
_buff_to_pet = {41: 6, 42: 7, 45: 8, 50: 9, 51: 10, 52: 11, 53: 12, 54: 13, 55: 14, 56: 15, 61: 16, 65: 17, 66: 18, 81: 19, 82: 20, 84: 21, 85: 22, 91: 23, 92: 24, 127: 25, 136: 26}


def try_read_index(array, index, default):
	try:
		return array[index]
	except IndexError:
		return default


def convert_xbox360_item_to_pc(item: Item) -> Item:
	if 0 <= item.id <= 2748:
		return Item(item.id, item.stack, item.prefix)
	return Item()


def convert_pc_item_to_xbox360(item: Item) -> Item:
	if 0 <= item.id <= 2748:
		return Item(item.id, item.stack, item.prefix)
	return Item()


def convert_xbox360_buff_to_pc(buff: Buff, pet: int) -> Buff:
	if buff.id == 156:
		if not (6 <= pet <= 26):
			return Buff()
		return Buff(_pet_to_buff[pet - 6], timedelta(minutes=5))

	if not (1 <= buff.id <= 139):
		return Buff()

	return buff


def convert_pc_buff_to_xbox360(buff: Buff) -> tuple[Buff, int]:  # returns buff and pet
	if not (1 <= buff.id <= 139):
		return Buff(), -1

	pet = _buff_to_pet.get(buff, -1)
	if pet != -1:
		return Buff(156, timedelta(minutes=5)), pet

	return buff, -1


def read_spawn_point_metadata(spawn_points: list, name: str) -> Optional[bytes]:
	return next((b64decode(x.world_name[len(name) + 11:]) for x in spawn_points
		  if x.x == 0 and x.y == 0 and x.world_id == -1 and x.world_name.startswith(f"_metadata_{name}_")),
		 None)


def remove_spawn_point_metadata(spawn_points: list):
	for x in range(len(spawn_points) - 1, -1, -1):
		spawn_point = spawn_points[x]
		if spawn_point.world_id == -1 and spawn_point.x == 0 and spawn_point.y == 0 and spawn_point.world_name.startswith("_metadata"):
			spawn_points.pop(x)


def add_spawn_point_metadata(spawn_points: list, name: str, data: bytes | bytearray = None):
	if data is not None:
		base64_encoded_data = f"_{b64encode(data).decode('utf-8')}"
		name = f"_{name}"
	else:
		base64_encoded_data = ""
		name = f" {name}"
	spawn_points.append(SpawnPoint(0, 0, -1, f"_metadata{name}{base64_encoded_data}"))


def convert_xbox360_to_pc(player: TerrariaXbox360Player) -> TerrariaPCPlayer:
	out_player = TerrariaPCPlayer()
	out_player.name = player.name
	out_player.difficulty = player.difficulty
	out_player.hair_style = player.hair_style
	out_player.hair_dye = player.hair_dye
	out_player.is_accessories_hidden = player.is_accessories_hidden
	out_player.is_male = player.is_male
	out_player.life = player.life
	out_player.max_life = player.max_life
	out_player.mana = player.mana
	out_player.max_mana = player.max_mana
	out_player.angler_quests_finished = player.angler_quests_finished
	out_player.quick_shortcuts = player.quick_shortcuts

	out_player.hair_color = player.hair_color
	out_player.skin_color = player.skin_color
	out_player.eye_color = player.eye_color
	out_player.shirt_color = player.under_shirt_color
	out_player.under_shirt_color = player.under_shirt_color
	out_player.pants_color = player.pants_color
	out_player.shoe_color = player.shoe_color

	for x in range(0, 8):
		out_player.armor_and_accessories.append(convert_xbox360_item_to_pc(try_read_index(player.armor_and_accessories, x, Item())))

	for x in range(0, 8):
		out_player.vanity_armor_and_accessories.append(convert_xbox360_item_to_pc(try_read_index(player.vanity_armor_and_accessories, x, Item())))

	for x in range(0, 8):
		out_player.dyes.append(convert_xbox360_item_to_pc(try_read_index(player.dyes, x, Item())))

	for x1 in range(0, 4):
		row = []
		for x2 in range(0, 10):
			row.append(convert_xbox360_item_to_pc(try_read_index(try_read_index(player.inventory, x1, []), x2, Item())))
		out_player.inventory.append(row)

	for x in range(0, 4):
		out_player.coins.append(convert_xbox360_item_to_pc(try_read_index(player.coins, x, Item())))

	for x in range(0, 4):
		out_player.ammo.append(convert_xbox360_item_to_pc(try_read_index(player.ammo, x, Item())))

	i = 0
	for _ in range(0, 4):
		row = []
		for _ in range(0, 10):
			row.append(convert_xbox360_item_to_pc(try_read_index(try_read_index(player.piggy_bank, int(i / 8), []), i % 8, Item())))
			i += 1
		out_player.piggy_bank.append(row)

	i = 0
	for _ in range(0, 4):
		row = []
		for _ in range(0, 10):
			row.append(convert_xbox360_item_to_pc(try_read_index(try_read_index(player.safe, int(i / 8), []), i % 8, Item())))
			i += 1
		out_player.safe.append(row)

	for buff in player.buffs:
		out_player.buffs.append(convert_xbox360_buff_to_pc(buff, player.pet))

	metadata_item_array = read_spawn_point_metadata(player.spawn_points, "pc_player_5th_item_row")
	if metadata_item_array is not None:
		row = []
		for x in range(0, 10):
			row.append(Item(
				unpack_from('i', metadata_item_array, x * 9)[0],
				unpack_from('i', metadata_item_array, x * 9 + 4)[0],
				unpack_from('b', metadata_item_array, x * 9 + 8)[0]
			))
		out_player.inventory.append(row)

	remove_spawn_point_metadata(player.spawn_points)

	add_spawn_point_metadata(out_player.spawn_points, "xbox360_player_id", pack('i', player.id))
	add_spawn_point_metadata(out_player.spawn_points, "player converted from xbox 360 with Filip K's converter")

	for spawn_point in player.spawn_points:
		out_player.spawn_points.append(spawn_point)

	return out_player


def convert_pc_to_xbox360(player: TerrariaPCPlayer):
	out_player = TerrariaXbox360Player()
	out_player.name = player.name
	out_player.difficulty = player.difficulty
	out_player.hair_style = player.hair_style
	out_player.hair_dye = player.hair_dye
	out_player.is_accessories_hidden = player.is_accessories_hidden
	out_player.is_male = player.is_male
	out_player.life = player.life
	out_player.max_life = player.max_life
	out_player.mana = player.mana
	out_player.max_mana = player.max_mana
	out_player.angler_quests_finished = player.angler_quests_finished
	out_player.quick_shortcuts = player.quick_shortcuts

	out_player.hair_color = player.hair_color
	out_player.skin_color = player.skin_color
	out_player.eye_color = player.eye_color
	out_player.shirt_color = player.under_shirt_color
	out_player.under_shirt_color = player.under_shirt_color
	out_player.pants_color = player.pants_color
	out_player.shoe_color = player.shoe_color

	for x in range(0, 8):
		out_player.armor_and_accessories.append(convert_pc_item_to_xbox360(try_read_index(player.armor_and_accessories, x, Item())))

	for x in range(0, 8):
		out_player.vanity_armor_and_accessories.append(convert_pc_item_to_xbox360(try_read_index(player.vanity_armor_and_accessories, x, Item())))

	for x in range(0, 8):
		out_player.dyes.append(convert_pc_item_to_xbox360(try_read_index(player.dyes, x, Item())))

	for x1 in range(0, 4):
		row = []
		for x2 in range(0, 10):
			row.append(convert_xbox360_item_to_pc(try_read_index(try_read_index(player.inventory, x1, []), x2, Item())))
		out_player.inventory.append(row)

	for x in range(0, 4):
		out_player.coins.append(convert_pc_item_to_xbox360(try_read_index(player.coins, x, Item())))

	for x in range(0, 4):
		out_player.ammo.append(convert_pc_item_to_xbox360(try_read_index(player.ammo, x, Item())))

	i = 0
	for x1 in range(0, 5):
		row = []
		for x2 in range(0, 8):
			row.append(convert_pc_item_to_xbox360(try_read_index(try_read_index(player.safe, int(i / 10), []), i % 10, Item())))
			i += 1
		out_player.safe.append(row)

	i = 0
	for x1 in range(0, 5):
		row = []
		for x2 in range(0, 8):
			row.append(convert_pc_item_to_xbox360(try_read_index(try_read_index(player.piggy_bank, int(i / 10), []), i % 10, Item())))
			i += 1
		out_player.piggy_bank.append(row)

	for buff in player.buffs:
		buff, pet = convert_pc_buff_to_xbox360(buff)
		if buff.id == 0 or (buff.id == 156 and buff == -1):
			continue
		if pet != -1:
			out_player.pet = pet
		out_player.buffs.append(buff)

	player_id = read_spawn_point_metadata(player.spawn_points, "xbox360_player_id")
	if player_id is None:
		player_id = sha256(player.name.encode('utf-8')).digest()[:4]
	out_player.id = unpack('i', player_id)[0]

	remove_spawn_point_metadata(player.spawn_points)

	is_empty = True
	metadata_item_array = bytearray()
	for x in range(0, 10):
		item = try_read_index(try_read_index(player.inventory, 4, []), x, Item())
		if item.id != 0:
			is_empty = False
		metadata_item_array += pack('i', item.id)
		metadata_item_array += pack('i', item.stack)
		metadata_item_array += pack('B', item.prefix)
	if not is_empty:
		add_spawn_point_metadata(out_player.spawn_points, "pc_player_5th_item_row", metadata_item_array)
	add_spawn_point_metadata(out_player.spawn_points, "player converted from pc with Filip K's converter")

	for spawn_point in player.spawn_points:
		out_player.spawn_points.append(spawn_point)

	return out_player
