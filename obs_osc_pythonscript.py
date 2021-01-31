import time, threading
import obspython as obs

from obs_osc_api import (
	scene_change, 
	consola, 
	consola_hslider, 
	c1, c2, c3, 
	c, 
	client,
	th
)

from obs_osc_api import (
	item_set_visible,
	item_remove, 
	item_tween, 
	item_duplicate,
	item_reference,
	item_get_transform,
	item_set_transform,
	item_set_pos,
	item_set_scl,
	item_set_rot,
	item_set_alignment,
	item_set_visible,
	item_set_crop
)

from obs_osc_api import (
	source_set_image_file, 
	source_set_video_file, 
	source_set_slide_time,
	source_set_text,
	source_set_text_size,
	source_set_volume, 
	source_set_opacity,
	source_set_bri_sat_hue, 
	source_set_hue, 
	source_set_lut_file,
	source_filter_set_value, 
	source_filter_set_enabled, 
	source_set_text,
	source_get_settings
)

from pythonosc import osc_message_builder
from pythonosc import dispatcher
from pythonosc import osc_server

serverPort = 10008
server = None

def handleOSC(address, args, data):
	print(f'{address}, {args}, {data}')

def tween(*args):

	if args[1] in ['to_pos', 'pos']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_pos_x=args[4],
			to_pos_y=args[5],
			duration=args[6],
			delay=args[7] if len(args) > 7 else 0,
			ease_type=args[8] if len(args) > 8 else 'linear')

	elif args[1] == 'from_to_pos':
		item_tween(None, 
			scene_name=args[2],
			item_name=args[3],
			from_pos_x=args[4],
			from_pos_y=args[5], 
			to_pos_x=args[6],
			to_pos_y=args[7],
			duration=args[8],
			delay=args[9] if len(args) > 9 else 0,
			ease_type=args[10] if len(args) > 10 else 'linear')
	
	elif args[1] in ['to_scl', 'scl']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_scl_x=args[4],
			to_scl_y=args[5],
			duration=args[6],
			delay=args[7] if len(args) > 7 else 0,
			ease_type=args[8] if len(args) > 8 else 'linear')

	elif args[1] == 'from_to_scl':
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			from_scl_x=args[4],
			from_scl_y=args[5], 
			to_scl_x=args[6],
			to_scl_y=args[7],
			duration=args[8],
			delay=args[9] if len(args) > 9 else 0,
			ease_type=args[10] if len(args) > 10 else 'linear')

	elif args[1] in ['to_rot', 'rot']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_rot=args[4],
			duration=args[5],
			delay=args[6] if len(args) > 6 else 0,
			ease_type=args[7] if len(args) > 7 else 'linear')

	elif args[1] == 'from_to_rot':
		item_tween(None, 
			scene_name=args[2],
			item_name=args[3],
			from_rot=args[4],
			to_rot=args[5],
			duration=args[6],
			delay=args[7] if len(args) > 7 else 0,
			ease_type=args[8] if len(args) > 8 else 'linear')

	elif args[1] in ['to_transform', 'transform']:
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			to_pos_x=args[4],
			to_pos_y=args[5],
			to_scl_x=args[6],
			to_scl_y=args[7],
			to_rot=args[8], 
			duration=args[9],
			delay=args[10] if len(args) > 10 else 0,
			ease_type=args[11] if len(args) > 11 else 'linear')

	elif args[1] == 'from_to_transform':
		item_tween(None,
			scene_name=args[2],
			item_name=args[3],
			from_pos_x=args[4],
			from_pos_y=args[5],
			from_scl_x=args[6],
			from_scl_y=args[7],
			from_rot=args[8],
			to_pos_x=args[9],
			to_pos_y=args[10],
			to_scl_x=args[11],
			to_scl_y=args[12],
			to_rot=args[13],
			duration=args[14], 
			delay=args[15] if len(args) > 15 else 0,
			ease_type=args[16] if len(args) > 16 else 'linear')

# defines script description 
def script_description():
	return '''obs-osc-pythonscript
	OBS Python scripts that allows to receive/send OSC messages from/to OBS and from/to another OSC sending capable software, like PureData, MobMuPlat, TouchOSC, etc.'''

# defines user properties
def script_properties():
	#global props 
	props = obs.obs_properties_create()
	# obs.obs_properties_add_text(props, "host", "Host IP", obs.OBS_TEXT_DEFAULT)
	# obs.obs_properties_add_int(props, "port", "Host port", 1, 400000, 1)
	# obs.obs_properties_add_bool(props, "logOscOutput", "Log OSC output")
	obs.obs_properties_add_int(props, "serverPort", "Listen port", 1, 400000, 1)
	return props

def script_defaults(settings):
	# obs.obs_data_set_default_string(settings, "host", targetIp)
	# obs.obs_data_set_default_int(settings, "port", targetPort)
	obs.obs_data_set_default_int(settings, "serverPort", serverPort)


def script_load(settings):
	
	# sh = obs.obs_get_signal_handler()
	# obs.signal_handler_connect(sh, "source_activate", source_activated)
	# obs.signal_handler_connect(sh, "source_deactivate", source_deactivated)

	global despachante
	despachante = dispatcher.Dispatcher()

	despachante.map("/scene_change", scene_change)

	despachante.map("/item_set_visible",   item_set_visible)
	despachante.map("/item_remove",        item_remove)
	despachante.map("/item_tween",         tween)
	despachante.map("/item_duplicate",     item_duplicate)
	despachante.map("/item_reference",     item_reference)
	despachante.map("/item_set_transform", item_set_transform)
	despachante.map("/item_get_transform", item_get_transform)
	despachante.map("/item_set_pos",       item_set_pos)
	despachante.map("/item_set_scl",       item_set_scl)
	despachante.map("/item_set_rot",       item_set_rot)
	despachante.map("/item_set_alignment", item_set_alignment)
	despachante.map("/item_set_visible",   item_set_visible)
	despachante.map("/item_set_crop",      item_set_crop)

	despachante.map("/source_set_image_file",     source_set_image_file)
	despachante.map("/source_set_video_file",     source_set_video_file)
	despachante.map("/source_set_slide_time",     source_set_slide_time)
	despachante.map("/source_set_text",           source_set_text)
	despachante.map("/source_set_text_size",      source_set_text_size)
	despachante.map("/source_set_volume",         source_set_volume)
	despachante.map("/source_set_opacity",        source_set_opacity)
	despachante.map("/source_filter_set_enabled", source_filter_set_enabled)
	despachante.map("/source_filter_set_value",   source_filter_set_value)
	despachante.map("/source_set_bri_sat_hue",    source_set_bri_sat_hue)
	despachante.map("/source_set_hue",            source_set_hue)
	despachante.map("/source_set_lut_file",       source_set_lut_file)
	despachante.map("/source_get_settings",       source_get_settings)
	# despachante.map("/*", handleOSC)


def script_unload():
	print(f'Script_unload')
	global server
	server.server_close()
	time.sleep(1)

def script_update(settings):
	global host
	global port
	# global client
	global server
	global pleaseLog

	pleaseLog    = obs.obs_data_get_bool(settings, "logOscOutput")
	host         = obs.obs_data_get_string(settings, "host")
	port         = obs.obs_data_get_int(settings, "port")

	# Client
	# client = udp_client.SimpleUDPClient(host, port)
	# print("target set to "+host+":"+str(port)+"")

	# Server
	serverPort = obs.obs_data_get_int(settings, "serverPort")
	try:
		server.server_close()
	except:
		print('*Server not created yet')
		# raise
	server = osc_server.BlockingOSCUDPServer(("127.0.0.1", serverPort), despachante)
	th(server_th, [settings])

	# Loop cada 1000ms
	# obs.timer_remove(funcion_loop)
	# if and source_name != "":
		# obs.timer_add(funcion_loop, 1000)

def server_th(settings):
	print(f'Serving on {server.server_address}')
	server.serve_forever()  # Blocks forever
	print(f'CORRECTLY CLOSED SERVER {server.server_address}')