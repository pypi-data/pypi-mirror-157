# terraria pc xbox360 player converter

Library for converting between TerrariaPCPlayer and TerrariaXbox360Player.

## Examples

Convert xbox360 player file to pc
```python
>>> import terraria_xbox360_player_api
>>> import terraria_pc_xbox360_player_converter
>>> player = terraria_xbox360_player_api.TerrariaXbox360Player("PLAYER1.PLR")
>>> player = terraria_pc_xbox360_player_converter.convert_xbox360_to_pc(player)
>>> player.write_to_file("PLAYER1.plr")
```

Convert pc player file to xbox360
```python
>>> import terraria_pc_player_api
>>> import terraria_pc_xbox360_player_converter
>>> player = terraria_pc_player_api.TerrariaPCPlayer("PLAYER1.plr")
>>> player = terraria_pc_xbox360_player_converter.convert_pc_to_xbox360(player)
>>> player.write_to_file("PLAYER1.PLR")
```

## Dependencies

* [terraria-pc-player-api](https://gitlab.com/terraria-converters/terraria-pc-player-api)
* [terraria-xbox360-player-api](https://gitlab.com/terraria-converters/terraria-xbox360-player-api)

## Installation
```
pip install terraria-pc-xbox360-player-converter
```

## License

[GPL v3](LICENSE) © Filip K.
