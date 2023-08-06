from distutils.core import setup

VERSION = '1.0.3'
PACKAGE_NAME = 'terraria-pc-xbox360-player-converter'
AUTHOR = 'Filip K'
AUTHOR_EMAIL = 'fkwilczek@gmail.com'
URL = 'https://gitlab.com/terraria-converters/terraria-pc-xbox360-player-converter'

LICENSE = 'GNU General Public License v3 (GPLv3)'
DESCRIPTION = 'Library for converting between TerrariaPCPlayer and TerrariaXbox360Player'
LONG_DESCRIPTION = open('README.md', encoding='utf-8').read()
LONG_DESC_TYPE = "text/markdown"

PYTHON_REQUIRES = '>=3.10'
INSTALL_REQUIRES = [
	'terraria-pc-player-api',
	'terraria-xbox360-player-api'
]

setup(
	name=PACKAGE_NAME,
	version=VERSION,
	author=AUTHOR,
	author_email=AUTHOR_EMAIL,
	description=DESCRIPTION,
	long_description=LONG_DESCRIPTION,
	long_description_content_type=LONG_DESC_TYPE,
	url=URL,
	license=LICENSE,
	python_requires=PYTHON_REQUIRES,
	install_requires=INSTALL_REQUIRES,
	classifiers=[
		'Programming Language :: Python :: 3.10',
		'Operating System :: OS Independent',
		'License :: OSI Approved :: GNU General Public License v3 (GPLv3)'
	],
	packages=['terraria_pc_xbox360_player_converter'],
)
