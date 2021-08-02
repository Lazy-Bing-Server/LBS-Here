import re
import os
import json
import time
import datetime

from typing import Any, Optional
from mcdreforged.api.all import *

PLUGIN_METADATA = {
	'id': 'here',
	'version': '2.0.0-alpha1',
	'name': 'Here',
	'author': [
		'Fallen_Breath',
		'nathan21hz',
		'Ra1ny_Yuki' # 做了一点微小的工作(指把它变臃肿了不少
   ],
	'link': 'https://github.com/TISUnion/Here'
}

# Editable content / 可编辑内容
CONFIG_FILE = 'config/here.json' # Configuration file path / 配置文件路径
VERBOSE = False # Set it to true to show debug logs / 设为true以显示调试日志
DEBUG_LOG_PATH = 'logs/here.log' # Log marked as DEBUG will be saved to here if VERBOSE is true / 被标记为DEBUG的调试日志在VERBOSE为true时会被保存到这里
# End editable content / 可编辑内容结束

# Here is ONLY default data of the config file
# 此处 仅为 配置默认数据
# DO NOT edit data here!!! If you need to change the config value, pls edit in config file
# 不要在这里改数据！！！要改配置去配置文件里改
# Access the link in plugin metadata to get config manual(current Chinese only)
# 请访问插件元数据中的链接以获取插件帮助手册(目前仅中文)
default_config = {
	'command_prefix':
	{
		'here': '!!here',
		'where': '!!where'
	},
	'permission_requirement':
	{
		'here': 0,
		'where': 1,
		'admin': 2
	},
	'highlight_time':
	{
		'here': 15,
		'where': 0
	},
	'display_waypoint':
	{
		'voxelmap': True,
		'xaeros_minimap': True
	},
	'console_here_text': '这有个鬼才运维试图广播服务端的坐标',
	'query_timeout': 3,
	'where_default_broadcast': False,
	'click_to_teleport': True,
	'where_protected_list': []
#  ,'disable_rcon': None, # Hided Debug Option
}

here_user = []

dimension_display = {
		'0': 'createWorld.customize.preset.overworld',
		'-1': 'advancements.nether.root.title',
		'1': 'advancements.end.root.title'
	}

dimension_color = {
		'0': RColor.dark_green,
		'-1': RColor.dark_red,
		'1': RColor.dark_purple
	}

help_message = '''
§7-----§r MCDR {2} v{3} §7-----§r
快速广播自己的坐标或查询别人的坐标
§d【格式说明】§r
§7{0}§r {4}
§7{0} help§r 显示此帮助信息
§7{0} reload§r 重载本插件
§7{1} §e<玩家名称>§a [<arg>]§r {5}
§d【参数说明】§r
§a<arg>§r处(仅§7{1}§r具有)可填入的可选参数有:
§a-a§r 无论默认行为如何, §6向所有人§r广播坐标信息
§a-s§r 无论默认行为如何, §6仅向自己§r显示坐标信息
'''.strip()


class Config:
	def __init__(self, file: str) -> None:
		self.file = file
		self.data = {}

	def __write_config(self, new_data = None):
		if isinstance(new_data, dict):
			self.data.update(new_data)
		with open(self.file, 'w', encoding='UTF-8') as f:
			json.dump(self.data, f, indent=4, ensure_ascii=False)

	def __get_config(self):
		with open(self.file, 'r', encoding='UTF-8') as f:
			self.data.update(json.load(f))

	def load(self, server: ServerInterface):
		if not os.path.isdir(os.path.dirname(self.file)):
			os.makedirs(os.path.dirname)
			server.logger.info('Config directory not found, created')
		if not os.path.isfile(self.file):
			self.__write_config(default_config)
			server.logger.info('Config file not found, using default')
		else:
			try:
				self.__get_config()
			except json.JSONDecodeError:
				self.__write_config(default_config)
				server.logger.info('Invalid config file, using default')

	def __getitem__(self, key: str) -> Any:
		ret = self.data.get(key)
		if ret is None and key in default_config.keys():
			ret = default_config[key]
			self.__write_config({key: ret})
		return ret

config = Config(CONFIG_FILE)


def show_help(server: ServerInterface, info: Info):
	help_msg_rtext = RTextList()
	for line in help_message.format(
		config['command_prefix']['here'],
		config['command_prefix']['where'],
		PLUGIN_METADATA['name'],
		PLUGIN_METADATA['version'],
		here_help, where_help
	).splitlines():
		for prefix in config['command_prefix'].values():
			result = re.search(r'(?<=§7){}[\S ]*?(?=§)'.format(prefix), line)
			if result is not None: break
		if result is not None:
			cmd = result.group() + ' '
			help_msg_rtext.append(RText(line).c(RAction.suggest_command, cmd).h('点击以填入 §7{}§r'.format(cmd)))
		else:
			help_msg_rtext.append(line)
		if line != help_message.splitlines()[-1]:
			help_msg_rtext.append('\n')
	server.reply(info, help_msg_rtext)


def debug_log(msg: str):
	if VERBOSE:
		msg = msg.replace('§r', '').replace('§d', '').replace('§c', '').replace('§6', '').replace('§e', '').replace('§a', '')
		with open(os.path.join(DEBUG_LOG_PATH), 'a+') as log:
			log.write(datetime.datetime.now().strftime("[%Y-%m-%d %H:%M:%S]") + msg + '\n')
		print("[MCDR] " + datetime.datetime.now().strftime("[%H:%M:%S]") + ' [{}/\033[1;36mDEBUG\033[0m] '.format(PLUGIN_METADATA['id']) + msg)


def process_coordinate(text: str) -> tuple:
	debug_log(text)
	data = text[1:-1].replace('d', '').split(', ')
	data = [(x + 'E0').split('E') for x in data]
	return tuple([float(e[0]) * 10 ** int(e[1]) for e in data])


def process_dimension(text: str) -> str:
	return text.replace(re.match(r'[\w ]+: ', text).group(), '', 1)


def coordinate_text(x: str, y: str, z: str, dimension: str, opposite=False):
	dimension_coordinate_color = {
		'0': RColor.green,
		'-1': RColor.red,
		'1': RColor.light_purple
	}
	dimension_name = {
		'0': 'minecraft:overworld',
		'1': 'minecraft:the_end',
		'-1': 'minecraft:the_nether'
	}

	if opposite:
		dimension = '-1' if dimension == '0' else '0'
		x, z = (x / 8, z / 8) if dimension == '-1' else (x * 8, z * 8)

	pattern = RText('[{}, {}, {}]'.format(int(x), int(y), int(z)), dimension_coordinate_color[dimension])
	dim_text = RTextTranslation(dimension_display[dimension], color=dimension_color[dimension])

	return pattern.h(dim_text) if not config['click_to_teleport'] else pattern.h(
		dim_text + ': 点击以传送到' + pattern.copy()
		).c(RAction.suggest_command, 
		'/execute in {} run tp {} {} {}'.format(dimension_name[dimension], int(x), int(y), int(z)))


def display(server: ServerInterface, name: str, position: str, dimension: str, mode: str, info: Optional[Info] = None):
	x, y, z = position
	dimension_convert = {
		'minecraft:overworld': '0',
		'"minecraft:overworld"': '0',
		'minecraft:the_nether': '-1',
		'"minecraft:the_nether"': '-1',
		'minecraft:the_end': '1',
		'"minecraft:the_end"': '1'
	}
	
	if dimension in dimension_convert:  # convert from 1.16 format to pre 1.16 format
		dimension = dimension_convert[dimension]

	# text base
	texts = RTextList(
		'§e{}§r'.format(name),
		' @ ',
		RTextTranslation(dimension_display[dimension], color=dimension_color[dimension]),
		' ',
		coordinate_text(x, y, z, dimension)
	)

	# click event to add waypoint
	if config['display_waypoint']['voxelmap']:
		texts.append( ' ',
			RText('[+V]', RColor.aqua).h('§bVoxelmap§r: 点此以高亮坐标点, 或者Ctrl点击添加路径点').c(
				RAction.run_command, '/newWaypoint [x:{}, y:{}, z:{}, dim:{}]'.format(
					int(x), int(y), int(z), dimension
				)))
	if config['display_waypoint']['xaeros_minimap']:
		texts.append( ' ',
			RText('[+X]', RColor.gold).h('§6Xaeros Minimap§r: 点击添加路径点').c(
				RAction.run_command, 'xaero_waypoint_add:{}:{}:{}:{}:{}:6:false:0:Internal_{}_waypoints'.format(
					name + "'s Location", name[0], int(x), int(y), int(z), dimension.replace('minecraft:', '').strip()
				)))

	# coordinate convertion between overworld and nether
	if dimension in ['0', '-1']:
		texts.append(
			' §7->§r ',
			coordinate_text(x, y, z, dimension, opposite=True)
			)
	if info is None:
		server.broadcast(texts)
	else:
		server.reply(info, texts)

	# highlight
	if config['highlight_time'][mode] > 0:
		server.execute('effect give {} minecraft:glowing {} 0 true'.format(name, config['highlight_time'][mode]))


def player_not_found(server: ServerInterface, info: Info):
	server.reply(info, RText('查询的玩家不在线或插件执行出错', color=RColor.red))


def run_rcon(server: ServerInterface, info: Info, name: str, mode: str, to_all = True):
	rcon_result = re.search(r'\[.*\]', server.rcon_query('data get entity {} Pos'.format(name)))
	debug_log(rcon_result.group())
	if rcon_result is None:
		player_not_found(server, info)
	position = process_coordinate(rcon_result.group())
	dimension = process_dimension(server.rcon_query('data get entity {} Dimension'.format(name)))
	info1 = None if to_all else info
	display(server, name, position, dimension, mode, info1)


@new_thread('Where - Wait for respond')
def wait_for_data(server: ServerInterface, info: Info, player_info: list, timeout: float = None):
	actual_timeout = config['query_timeout'] if timeout is None else timeout
	time.sleep(actual_timeout)
	debug_log('Player {} not fount'.format(player_info[0]))
	player_not_found(server, info)
	if len(here_user) > 1:
		here_user.remove(player_info)


def query_data(server: ServerInterface, info: Info, name = None, to_all = True):
	mode = 'where'
	if name is None:
		name = info.player
		mode = 'here'
	if mode == 'where' and name in config['where_protected_list'] and info.get_command_source().get_permission_level() < config['permission_requirement']['admin']:
		server.reply(info, RText('该玩家受到保护, 不可被查询到', color=RColor.red))
		return
	if hasattr(server, 'MCDR') and server.is_rcon_running() and not config['disable_rcon']:
		run_rcon(server, info, name, mode, to_all)
	else:
		player_info = [name, mode] if to_all else [name, mode, info]
		here_user.append(player_info)
		server.execute('data get entity ' + name)
		wait_for_data(server, info, player_info)


def on_info(server: ServerInterface, info: Info):
	def perm_requirement_not_met(perm: int):
		if perm <= 4:
			server.reply(info, RText('权限不足', RColor.red))
		else:
			info.should_send_to_server()

	def command_error():
		cmd = config['command_prefix']['here'] + ' help'
		server.reply(info, RText('指令出错! 点此获取指令帮助', RColor.red).c(
			RAction.run_command, cmd).h(
				'获取指令帮助(执行{})'.format(cmd)
			)
		)

	global here_user
	if info.is_user and info.content.strip().split(' ', 1)[0] in config['command_prefix'].values():
		info.cancel_send_to_server()
		args = info.content.strip().split(' ')
		clen = len(args)
		if args[0] == config['command_prefix']['here']:
			# !!here (from player)
			if clen == 1 and info.is_player:
				if info.get_command_source().get_permission_level() >= config['permission_requirement']['here']:
					query_data(server, info)
				else:
					perm_requirement_not_met(config['permission_requirement']['here'])
			# !!here (from cosole)
			elif clen == 1 and info.is_from_console:
				if isinstance(config['console_here_text'], str):
					server.broadcast(config['console_here_text'])
				else:
					info.should_send_to_server()
			# !!here help
			elif clen == 2 and args[1] == 'help':
				show_help(server, info)
			# !!here reload
			elif clen == 2 and args[1] == 'reload':
				if info.get_command_source().get_permission_level() >= config['permission_requirement']['admin']:
					server.reload_plugin(PLUGIN_METADATA['id'])
					server.reply(info, '插件重载§a完成§r')
				else:
					perm_requirement_not_met(config['permission_requirement']['where'])
			else:
				command_error()
		# !!where <player> [<arg>]
		elif args[0] == config['command_prefix']['where'] and clen in [2, 3]:
			# parse arguments
			to_all = config['where_default_broadcast']
			if '-s' in args:
				to_all = False
				args.remove('-s')
			if '-a' in args:
				to_all = True
				args.remove('-a')
			debug_log(str(args))
			if info.get_command_source().get_permission_level() >= config['permission_requirement']['where']:
				if len(args) == 2:
					query_data(server, info, args[1], to_all)
				else: 
					command_error()
			else:
				perm_requirement_not_met(config['command_prefix']['where'])
		else: 
			command_error()

	# wait for 'data get' output
	if not info.is_player and len(here_user) > 0 and re.match(r'\w+ has the following entity data: ', info.content) is not None:
		name = info.content.split(' ')[0]
		player_found = None
		for item in here_user:
			if item[0] == name:
				player_found = item
				break
		if player_found is not None:
			dimension = re.search(r'(?<= Dimension: )(.*?),', info.content).group().replace('"', '').replace(',', '')
			position_str = re.search(r'(?<=Pos: )\[.*?\]', info.content).group()
			position = process_coordinate(position_str)
			info1 = None if len(player_found) <= 2 else player_found[2]
			display(server, name, position, dimension, player_found[1], info1)
			here_user.remove(player_found)


def on_load(server: ServerInterface, old):
	global here_user, here_help, where_help
	config.load(server) # load config
	if old is not None:
		here_user = old.here_user # inherit data from old module
	# build and register help message
	here_help = '广播自己的坐标并高亮玩家' if config['highlight_time']['here'] > 0 else '广播自己的坐标'
	is_where_highlight = '并高亮玩家' if config['highlight_time']['where'] > 0 else ''
	is_where_broadcast = '、广播' if config['where_default_broadcast'] else ''
	where_help = f'查询{is_where_broadcast}别人的坐标{is_where_highlight}'
	if config['permission_requirement']['here'] <= 4:
		server.register_help_message(config['command_prefix']['here'], here_help)
	if config['permission_requirement']['where'] <= 4:
		server.register_help_message(config['command_prefix']['where'], where_help)