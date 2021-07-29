#!/usr/bin/env python3

import obspython as obs
import random, time, string, json, math
from contextlib import contextmanager

from easing_functions import (
    LinearInOut,
    QuadEaseInOut,
    QuadEaseIn,
    QuadEaseOut,
    CubicEaseInOut,
    CubicEaseIn,
    CubicEaseOut,
    QuarticEaseInOut,
    QuarticEaseIn,
    QuarticEaseOut,
    QuinticEaseInOut,
    QuinticEaseIn,
    QuinticEaseOut,
    SineEaseInOut,
    SineEaseIn,
    SineEaseOut,
    CircularEaseIn,
    CircularEaseInOut,
    CircularEaseOut,
    ExponentialEaseInOut,
    ExponentialEaseIn,
    ExponentialEaseOut,
    ElasticEaseIn,
    ElasticEaseInOut,
    ElasticEaseOut,
    BackEaseIn,
    BackEaseInOut,
    BackEaseOut,
    BounceEaseIn,
    BounceEaseInOut,
    BounceEaseOut,
)

# Try to load my personal file that it is not in this repository
try:
	from obs_api import (
		th, c1, c2, c3, c4, c, 
		consola, thread, globalDict, 
		tobool, toint, tolist, tofloat
		)
except:
	from obs_osc_api import(
		th, c1, c2, c3, c4, c,
		consola, thread, globalDict,
		tobool, toint, tolist, tofloat
		)

from contextlib import contextmanager, ExitStack

def get_scene_context(scene_name):
	scenes_list = obs.obs_frontend_get_scenes()
	return_scene = None
	for scene in scenes_list:
		name = obs.obs_source_get_name(scene)
		if name == scene_name:
			return_scene = obs.obs_scene_from_source(scene)
	return return_scene, scenes_list

@contextmanager
def source_list_auto_release(source_list):
	try:
		yield source_list
	finally:
		obs.source_list_release(source_list)

@contextmanager
def source_auto_release(source_name):
	source = obs.obs_get_source_by_name(source_name)
	try:
		yield source
	finally:
		obs.obs_source_release(source)

@contextmanager
def get_filter(source, filter_name):
	filter_ = obs.obs_source_get_filter_by_name(source, filter_name)
	try:
		yield filter_
	finally:
		obs.obs_source_release(filter_)

@contextmanager
def new_settings():
	newSettings = obs.obs_data_create()
	try:
		yield newSettings
	finally:
		obs.obs_data_release(newSettings)

def source_tween(unused_addr,
	source_name,
	filter_name=None,      setting=None,
	from_value=None,       to_value=None,
	duration=1000,         delay=0,
	ease_type='outQuad',   fps=30,
	extra=None,            eval_=None,
	private=False):

	c2(f'source_tween(source_name="{source_name}",')
	c2(f'   filter_name={filter_name}, setting={setting},')
	c2(f'   from_value={from_value}, to_value={to_value},')
	c2(f'	duration={duration}, delay={delay}, ease_type={ease_type},')
	c2(f'	fps={fps}, extra={extra}), eval_={eval_})')

	duration     = toint(duration)
	delay        = toint(delay)
	fps          = toint(fps)
	from_value   = tofloat(from_value)
	to_value     = tofloat(to_value)
	value        = float()

	with ExitStack() as stack:
		if not private: source = stack.enter_context(source_auto_release(source_name))
		else:           source = globals()[source_name]
		
		if source:
			filter_ = stack.enter_context(get_filter(source, filter_name))
			if filter_:
				sourceSettings = obs.obs_source_get_settings(filter_)
				json_from_filter = obs.obs_data_get_json(sourceSettings)
				settings_from_filter = json.loads(json_from_filter)
				
				if setting not in settings_from_filter:
					print(f'Setting {setting} no está seteada aún')
					return
				
				if from_value == None:
					from_value = settings_from_filter[setting]
				
				value = settings_from_filter[setting]

				# Código único para que se ejecute un tween a la vez
				code = ''.join(random.choice(string.ascii_letters) for i in range(10))

				# Momento en que comienza el tween.
				init_time = time.time()*1000
				
				# Crea elemento en diccionario. Queda forever.
				globalDict.tween_sources[source_name] = {
					'source_name': source_name,
					'filter_name': filter_name,
					'setting':     setting,
					'value':       value,
					'code':        code,
					'init_time':   init_time,
					'extra':       extra,
					'eval_':       eval_,
				}
				# TIENE QUE IR TH()
				th_source_tween(
					source_name,
					filter_name, setting,
					from_value, to_value,
					init_time, duration, delay, ease_type,
					code, fps, extra, eval_, private)

			else: print(f'Filter no existe: {filter_name}')
		else: print(f'Source no existe: {source_name}')

def th_source_tween(
	source_name,
	filter_name, setting,
	from_value, to_value,
	init_time, duration, delay, ease_type,
	code, fps, extra, eval_, private):

	# Delay
	if delay > 0:
		time.sleep(delay/1000)
		init_time += delay

	with ExitStack() as stack:

		if not private: source = stack.enter_context(source_auto_release(source_name))
		else:           source = globals()[source_name]
		if source:
			filter_ = stack.enter_context(get_filter(source, filter_name))
			if filter_:

				# Loop
				while init_time + duration > time.time()*1000:
					
					# Si no está en la lista de tweens, muere tween.
					if source_name not in globalDict.tween_sources:
						return
					
					# Si el código no es el mismo que el registrado, muere tween.
					if code != globalDict.tween_sources[source_name]['code']:
						return
					
					elapsed_time = time.time()*1000 - init_time
					value_change = None if to_value == None else to_value - from_value

					# time, beginning position, change inposition, and duration
					value = None if to_value == None else tween_eq(ease_type, elapsed_time, from_value, value_change, duration)

					c4(f'TWEEN TRANSFORM - SOURCE')
					c4(f'   source_name="{source_name}", filter_name={filter_name},')
					c4(f'   setting={setting}, value={value}')

					# Si hay modificaciones, las hace y guarda info del objeto
					if value != None:
				
						newSettings = stack.enter_context(new_settings())
						obs.obs_data_set_double(newSettings, setting, value)
						obs.obs_source_update(filter_, newSettings)
						globalDict.tween_sources[source_name]['value'] = value

				if eval_ != None:
					eval(eval_)

				if extra != None:
					pass

				time_sleep = 1 / fps
				time.sleep(time_sleep)

				# Si hay modificaciones, las hace y guarda info del objeto
				if 'value' in locals() and value != None:
					newSettings = stack.enter_context(new_settings())
					obs.obs_data_set_double(newSettings, setting, to_value)
					obs.obs_source_update(filter_, newSettings)
					globalDict.tween_sources[source_name]['value'] = to_value

				c4(f'TWEEN SOURCE TRANSFORM - FINISH')
				c4(f'   source_name="{source_name}", filter_name={filter_name}')
				c4(f'   setting={setting}, value={to_value}')

				# Ningunea elementos propios del tween que termina
				globalDict.tween_sources[source_name]['init_time'] = None
				globalDict.tween_sources[source_name]['code']      = None
				globalDict.tween_sources[source_name]['extra']     = None
				globalDict.tween_sources[source_name]['eval_']     = None
				
				# Para ejecutar algo al final
				# TO DO
				if eval_ != None:
					eval(eval_)

				c3(f'Terminó source_tween "{source_name}"')

			else: print(f'Filter no existe: {filter_name}')
		else: print(f'Source no existe: {source_name}')


def item_tween(unused_addr,
	scene_name,            item_name,
	from_pos_y=None,       to_pos_x=None,
	from_pos_x=None,       to_pos_y=None,
	from_scl_x=None,       to_scl_x=None,
	from_scl_y=None,       to_scl_y=None,
	from_rot=None,         to_rot=None,
	alignment=None,        visible=True,
	duration=1000,         delay=0,
	ease_type='outQuad',   fps=30,
	extra=None,            eval_=None): 

	c2(f'item_tween(scene_name="{scene_name}", item_name="{item_name}",')
	c2(f'	duration={duration}, delay={delay}, ease_type={ease_type},')
	c2(f'	from_pos_x={from_pos_x}, from_pos_y={from_pos_y},')
	c2(f'	from_scl_x={from_scl_x}, from_scl_y={from_scl_y},')
	c2(f'	from_rot={from_rot},')
	c2(f'	to_pos_x={to_pos_x}, to_pos_y={to_pos_y},')
	c2(f'	to_scl_x={to_scl_x}, to_scl_y={to_scl_y},')
	c2(f'	to_rot={to_rot},')
	c2(f'	alignment={alignment}, visible={visible},')
	c2(f'	fps={fps}, extra={extra}), eval_={eval_})')

	duration   = toint(duration)
	delay      = toint(delay)
	from_pos_x = toint(from_pos_x)
	from_pos_y = toint(from_pos_y)
	from_scl_x = tofloat(from_scl_x)
	from_scl_y = tofloat(from_scl_y)
	from_rot   = toint(from_rot)
	to_pos_x   = toint(to_pos_x)
	to_pos_y   = toint(to_pos_y)
	to_scl_x   = tofloat(to_scl_x)
	to_scl_y   = tofloat(to_scl_y)
	to_rot     = tofloat(to_rot)
	alignment  = toint(alignment)
	visible    = tobool(visible)
	fps        = toint(fps)

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		return

	with source_list_auto_release(scenes_list):
		
		if item_name.startswith('id:'):
			scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
			if scene_item: item_id = int(item_name[3:])
		else:
			scene_item = obs.obs_scene_find_source(scene, item_name)
			if scene_item: item_id = obs.obs_sceneitem_get_id(scene_item)


		if scene_item:
			item_info = obs.obs_transform_info()
			obs.obs_sceneitem_get_info(scene_item, item_info)

			if from_pos_x == None: from_pos_x = item_info.pos.x 
			if from_pos_y == None: from_pos_y = item_info.pos.y 
			if from_scl_x == None: from_scl_x = item_info.scale.x
			if from_scl_y == None: from_scl_y = item_info.scale.y
			if from_rot   == None: from_rot   = item_info.rot

			# Código único para que se ejecute un tween a la vez
			code = ''.join(random.choice(string.ascii_letters) for i in range(10))

			# Momento en que comienza el tween.
			init_time = time.time()*1000
			
			# Crea elemento en diccionario. Queda forever.
			globalDict.tween_sceneitems[item_id] = {
				'scene_name': scene_name,
				'item_name':  item_name,
				'code':       code,
				'init_time':  init_time,
				'pos_x':      from_pos_x,
				'pos_y':      from_pos_y,
				'scl_x':      from_scl_x,
				'scl_y':      from_scl_y,
				'rot':        from_rot,
				'alignment':  alignment,
				'visible':    visible,
				'extra':      extra,
				'eval_':      eval_,
			}

			# Función en Thread
			th(th_item_tween, [scene_name, item_name, scene_item,
				item_info, item_id, code,
				init_time, duration, delay, ease_type,
				from_pos_x, from_pos_y, from_scl_x, from_scl_y, from_rot,
				to_pos_x, to_pos_y, to_scl_x, to_scl_y, to_rot,
				alignment, visible, fps, extra, eval_])
		else:
			print(f'item_tween() Item no existe: "{item_name}"')

def th_item_tween(scene_name, item_name, scene_item,
	item_info, item_id, code,
	init_time, duration, delay, ease_type,
	from_pos_x, from_pos_y, from_scl_x, from_scl_y, from_rot,
	to_pos_x, to_pos_y, to_scl_x, to_scl_y, to_rot,
	alignment, visible, fps, extra, eval_):
	# Delay
	if delay > 0:
		time.sleep(delay/1000)
		init_time += delay

	# Lo hace visible al comienzo o no
	obs.obs_sceneitem_set_visible(scene_item, bool(visible))
	
	# Loop
	while init_time + duration > time.time()*1000:

		# Si no está en la lista de tweens, muere tween.
		if item_id not in globalDict.tween_sceneitems:
			return
		
		# Si el código no es el mismo que el registrado, muere tween.
		if code != globalDict.tween_sceneitems[item_id]['code']:
			return
		
		elapsed_time = time.time()*1000 - init_time
		# pos_change_x = None if to_pos_x == None else to_pos_x - from_pos_x
		# pos_change_y = None if to_pos_y == None else to_pos_y - from_pos_y
		# scl_change_x = None if to_scl_x == None else to_scl_x - from_scl_x
		# scl_change_y = None if to_scl_y == None else to_scl_y - from_scl_y
		# rot_change   = None if to_rot   == None else to_rot   - from_rot
		
		# time, beginning position, change inposition, and duration
		pos_x = None if to_pos_x == None else tween_eq(ease_type, elapsed_time, from_pos_x, to_pos_x, duration)
		pos_y = None if to_pos_y == None else tween_eq(ease_type, elapsed_time, from_pos_y, to_pos_y, duration)
		scl_x = None if to_scl_x == None else tween_eq(ease_type, elapsed_time, from_scl_x, to_scl_x, duration)
		scl_y = None if to_scl_y == None else tween_eq(ease_type, elapsed_time, from_scl_y, to_scl_y, duration)
		rot   = None if to_rot   == None else tween_eq(ease_type, elapsed_time, from_rot  , to_rot  , duration)

		# pos_change_x = None if to_pos_x == None else to_pos_x - from_pos_x
		# pos_change_y = None if to_pos_y == None else to_pos_y - from_pos_y
		# scl_change_x = None if to_scl_x == None else to_scl_x - from_scl_x
		# scl_change_y = None if to_scl_y == None else to_scl_y - from_scl_y
		# rot_change   = None if to_rot   == None else to_rot   - from_rot
		
		# # time, beginning position, change inposition, and duration
		# pos_x = None if to_pos_x == None else tween_eq(ease_type, elapsed_time, from_pos_x, pos_change_x, duration)
		# pos_y = None if to_pos_y == None else tween_eq(ease_type, elapsed_time, from_pos_y, pos_change_y, duration)
		# scl_x = None if to_scl_x == None else tween_eq(ease_type, elapsed_time, from_scl_x, scl_change_x, duration)
		# scl_y = None if to_scl_y == None else tween_eq(ease_type, elapsed_time, from_scl_y, scl_change_y, duration)
		# rot   = None if to_rot   == None else tween_eq(ease_type, elapsed_time, from_rot  , rot_change  , duration)

		c4(f'TWEEN SCENEITEM TRANSFORM')
		c4(f'   scene_name="{scene_name}", item_name="{item_name}",')
		c4(f'   pos_x={pos_x}, pos_y={pos_y}, scl_x={scl_x}, scl_y={scl_y},')
		c4(f'   rot={rot}, alignment={alignment}, visible={visible})')

		# Si hay modificaciones, las hace y guarda info del objeto
		if pos_x     != None:
			item_info.pos.x                               = int(pos_x)
			globalDict.tween_sceneitems[item_id]['pos_x'] = int(pos_x)
		if pos_y     != None:
			item_info.pos.y                               = int(pos_y)
			globalDict.tween_sceneitems[item_id]['pos_y'] = int(pos_y)
		if scl_x     != None:
			item_info.scale.x                             = scl_x
			globalDict.tween_sceneitems[item_id]['scl_x'] = scl_x
		if scl_y     != None:
			item_info.scale.y                             = scl_y
			globalDict.tween_sceneitems[item_id]['scl_y'] = scl_y
		if rot       != None:
			item_info.rot                                 = rot
			globalDict.tween_sceneitems[item_id]['rot']   = rot
		if alignment != None:
			item_info.alignment                               = alignment
			globalDict.tween_sceneitems[item_id]['alignment'] = alignment
		obs.obs_sceneitem_set_info(scene_item, item_info)


		if eval_ != None:
			eval(eval_)

		if extra != None:
			pass

		time_sleep = 1 / fps
		time.sleep(time_sleep)
	
	# Si hay modificaciones, las hace y guarda info del objeto
	if 'pos_x' in locals() and pos_x != None:
		item_info.pos.x                               = int(to_pos_x)
		globalDict.tween_sceneitems[item_id]['pos_x'] = int(to_pos_x)
	if 'pos_y' in locals() and pos_y != None:
		item_info.pos.y                               = int(to_pos_y)
		globalDict.tween_sceneitems[item_id]['pos_y'] = int(to_pos_y)
	if 'scl_x' in locals() and scl_x != None:
		item_info.scale.x                             = to_scl_x
		globalDict.tween_sceneitems[item_id]['scl_x'] = to_scl_x
	if 'scl_y' in locals() and scl_y != None:
		item_info.scale.y                             = to_scl_y
		globalDict.tween_sceneitems[item_id]['scl_y'] = to_scl_y
	if 'rot'   in locals() and rot   != None:
		item_info.rot                                 = to_rot
		globalDict.tween_sceneitems[item_id]['rot']   = to_rot
	if 'alignment' in locals() and alignment != None:
		item_info.alignment                               = alignment
		globalDict.tween_sceneitems[item_id]['alignment'] = alignment
	obs.obs_sceneitem_set_info(scene_item, item_info)

	c4(f'TWEEN ITEM TRANSFORM - FINISH')
	c4(f'   scene_name="{scene_name}", item_name="{item_name}",')
	c4(f'   pos_x={int(to_pos_x)}, pos_y={int(to_pos_y)}, scl_x={to_scl_x}, scl_y={to_scl_y},')
	c4(f'   rot={to_rot}, alignment={alignment}, visible={visible})')

	# Ningunea elementos propios del tween que termina
	globalDict.tween_sceneitems[item_id]['init_time'] = None
	globalDict.tween_sceneitems[item_id]['code']      = None
	globalDict.tween_sceneitems[item_id]['extra']     = None
	globalDict.tween_sceneitems[item_id]['eval_']     = None
	
	# Para ejecutar algo al final
	# TO DO
	if eval_ != None:
		eval(eval_)

	c3(f'Terminó item tween "{scene_name}" "{item_name}"')

# TWEEN - Ecuaciones from https://github.com/semitable/easing-functions
def tween_eq(ease_type, t, b, c, d):
	#~ if t >= 0:
	if ease_type in ['linear', 'LinearInOut']:
		a = LinearInOut(b, c, d)
		return a(t)
	elif ease_type in ['inQuad', 'QuadEaseIn']:
		a = QuadEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outQuad', 'QuadEaseOut']:
		a = QuadEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutQuad', 'QuadEaseInOut']:
		a = QuadEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inCubic', 'CubicEaseIn']:
		a = CubicEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outCubic', 'CubicEaseOut']:
		a = CubicEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutCubic', 'CubicEaseInOut']:
		a = CubicEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inQuartic', 'QuarticEaseIn']:
		a = QuarticEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outQuartic', 'QuarticEaseOut']:
		a = QuarticEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutQuartic', 'QuarticEaseInOut']:
		a = QuarticEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inQuintic', 'QuinticEaseIn']:
		a = QuinticEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outQuintic', 'QuinticEaseOut']:
		a = QuinticEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutQuintic', 'QuinticEaseInOut']:
		a = QuinticEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inSine', 'SineEaseIn']:
		a = SineEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outSine', 'SineEaseOut']:
		a = SineEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutSine', 'SineEaseInOut']:
		a = SineEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inCircular', 'CircularEaseIn']:
		a = CircularEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outCircular', 'CircularEaseOut']:
		a = CircularEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutCircular', 'CircularEaseInOut']:
		a = CircularEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inExponential', 'ExponentialEaseIn']:
		a = ExponentialEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outExponential', 'ExponentialEaseOut']:
		a = ExponentialEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutExponential', 'ExponentialEaseInOut']:
		a = ExponentialEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inElastic', 'ElasticEaseIn']:
		a = ElasticEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outElastic', 'ElasticEaseOut']:
		a = ElasticEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutElastic', 'ElasticEaseInOut']:
		a = ElasticEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inBack', 'BackEaseIn']:
		a = BackEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outBack', 'BackEaseOut']:
		a = BackEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutBack', 'BackEaseInOut']:
		a = BackEaseInOut(b, c, d)
		return a(t)
	elif ease_type in ['inBounce', 'BounceEaseIn']:
		a = BounceEaseIn(b, c, d)
		return a(t)
	elif ease_type in ['outBounce', 'BounceEaseOut']:
		a = BounceEaseOut(b, c, d)
		return a(t)
	elif ease_type in ['inOutBounce', 'BounceEaseInOut']:
		a = BounceEaseInOut(b, c, d)
		return a(t)

def write_tween_sceneitems():
	while True:
		with open("/home/mario/meytv/obs-scripts/tween_items_sources.watch", "w") as outfile:
			new_dict = {
				'sceneitems': globalDict.tween_sceneitems, 
				'sources':    globalDict.tween_sources,
				}
			json.dump(
				new_dict,
				outfile,
				default=str,
				sort_keys=True,
				indent=2,
				ensure_ascii=False
				)
		time.sleep(1)        # 1fps
thread(write_tween_sceneitems)
