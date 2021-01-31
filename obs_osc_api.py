from contextlib import contextmanager, ExitStack
import random, time, threading, logging
import obspython as obs

import requests
from io import BytesIO
from PIL import Image

class gD:
	def __init__(self):
		self.verbose = 1
globalDict = gD()

class Color:
	def __init__(self):
		self.reset = '\x1b[0m'
		self.blanco = '\x1b[97m'
		self.negro = '\x1b[90m'
		self.rojo = '\x1b[91m'
		self.verde = '\x1b[92m'
		self.azul = '\x1b[94m'
		self.amarillo = '\x1b[93m'
		self.magenta = '\x1b[95m'
		self.magenta_bold = '\x1b[95;1m'
		self.azul_bold = '\x1b[94;1m'
		self.cian = '\x1b[96m'
		self.naranja = '\x1b[38;5;202m'
		self.violeta = '\x1b[38;5;129m'
		self.rosa = '\x1b[38;5;213m'
		self.ocre = '\x1b[38;5;172m'
		self.marron = '\x1b[38;5;52m'
		self.musgo = '\x1b[38;5;58m'
		self.error = '\x1b[93;41m'
		self.remoto = '\x1b[93;42m'
		self.debug = '\x1b[93;44m'
		self.lista_attrs = []
		self.attrs = self.__dict__
		
		for k, v in self.attrs.items():
			if k not in ['lista_attrs', 'attrs', 'random']:
				self.lista_attrs.append(v)
	
		self.random = random.choice(self.lista_attrs)
c = Color()

def c1(texto, color_texto=c.azul_bold):
	if globalDict.verbose > 0:
		texto = str(texto)
		print(color_texto, texto, c.reset)

def c2(texto, color_texto=c.azul):
	if globalDict.verbose > 1:
		texto = str(texto)
		print(color_texto, texto, c.reset)

def c3(texto, color_texto=c.cian):
	if globalDict.verbose > 2:
		texto = str(texto)
		print(color_texto, texto, c.reset)

def c4(texto, color_texto=c.rosa):
	if globalDict.verbose > 3:
		texto = str(texto)
		print(color_texto, texto, c.reset)

def consola(texto, color_texto=c.verde):
	texto = str(texto)
	print(color_texto, texto, c.reset)

def consola_hslider(num1, start=0, end=1, largo=10, num2=None):
	print(start, c.amarillo, end='')
	
	for i in range(largo):
		lugar1 = int(((num1  - start) / (end - start)) * largo)
		lugar2 = int(((num2  - start) / (end - start)) * largo)
		if i == lugar1:
			print('*', end='')
		elif num2 != None and i == lugar2:
			print('$', end='')
		elif num2 != None and i == lugar1 == lugar2:
			print('&', end='')
		else:
			if start < 0 < end and i == int((-start / (end - start)) * largo):
				print('0', end='')
			else:
				print('.', end='')
	print(end, num1, '\r', c.reset, end='')

def lin_eq_conv(x, x0, x1, y0, y1):
	a = (y0 - y1) / (x0 - x1)
	b = -(a * x0) + y0
	return a * x + b

# Threading
# threads = list()
def th(function, args=[]):
	t = threading.Thread(
		target=function,
		args=(args),
		name=f'{function}({args})',
		daemon=True)
	t.start()

@contextmanager
def scene_ar(scene):
	scene = obs.obs_scene_from_source(scene)
	try:
		yield scene
	finally:
		obs.obs_scene_release(scene)

@contextmanager
def scene_enum(items):
	items = obs.obs_scene_enum_items(items)
	try:
		yield items
	finally:
		obs.sceneitem_list_release(items)

@contextmanager
def source_auto_release(source_name):
	source = obs.obs_get_source_by_name(source_name)
	try:
		yield source
	finally:
		obs.obs_source_release(source)

@contextmanager
def source_list_auto_release(source_list):
    try:
        yield source_list
    finally:
        obs.source_list_release(source_list)

@contextmanager
def new_settings():
	newSettings = obs.obs_data_create()
	try:
		yield newSettings
	finally:
		obs.obs_data_release(newSettings)

# contextmanagers MIOS???
@contextmanager
def get_source(item):
	source = obs.obs_sceneitem_get_source(item)
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


def get_selected_scene(scene_name):
	scenes = obs.obs_frontend_get_scenes()
	found = False
	for scene in scenes:
		name = obs.obs_source_get_name(scene)
		if name == scene_name:
			found = True
	obs.source_list_release(scenes)
	return found

def get_scene_context(scene_name):
	scenes_list = obs.obs_frontend_get_scenes()
	for scene in scenes_list:
		name = obs.obs_source_get_name(scene)
		# consola(name, c.debug)
		if name == scene_name:
			# consola(f'encontrada {name}', c.violeta)
			return_scene = obs.obs_scene_from_source(scene)
			return return_scene, scenes_list

def scene_change(unused_addr, scene_name, trans='Fade', duration=500):
	consola(f'Cambiando a escena "{scene_name}"')
	scenes = obs.obs_frontend_get_scenes()
	for scene in scenes:
		name = obs.obs_source_get_name(scene)
		if name == scene_name:
			obs.obs_frontend_set_current_scene(scene)
	obs.source_list_release(scenes)

def source_set_volume(unused_addr, source_name, volume):
	c2(f'source_set_volume(source_name="{source_name}", volume={volume})')
	with ExitStack() as stack:
		source = stack.enter_context(source_auto_release(source_name))
		if source:
			obs.obs_source_set_volume(source, volume)
		else: print(f'Source no existe: {source_name}')


def source_filter_set_value(unused_addr, source_name, filter_name, setting, value):
	c2(f'source_filter_set_value(source_name="{source_name}",')
	c2(f'	filter_name="{filter_name}", setting={setting}, value={value})')

	with ExitStack() as stack:
		source = stack.enter_context(source_auto_release(source_name))
		if source:
			filter_ = stack.enter_context(get_filter(source, filter_name))
			if filter_:
				newSettings = stack.enter_context(new_settings())
				if filter_name in ['opacity', 'hue_shift']:
					obs.obs_data_set_int(newSettings, setting, int(value))
				else:
					if type(value) == str:
						obs.obs_data_set_string(newSettings, setting, value)
					elif type(value) == int:
						obs.obs_data_set_int(newSettings, setting, value)
					elif type(value) == float:
						obs.obs_data_set_double(newSettings, setting, value)
				obs.obs_source_update(filter_, newSettings)
			else: print(f'Filter no existe: {filter_name}')
		else: print(f'Source no existe: {source_name}')

def source_set_opacity(unused_addr, source_name, opacity):
	source_filter_set_value(None, source_name, 'Color Correction', 'opacity', int(opacity))

def source_set_hue(unused_addr, source_name, hue):
	source_filter_set_value(None, source_name, 'Color Correction', 'hue_shift', int(hue))

def source_set_bri_sat_hue(unused_addr, source_name, valores):
	source_filter_set_value(None, source_name, 'Color Correction', 'brightness', int(valores[0]))
	source_filter_set_value(None, source_name, 'Color Correction', 'saturation', int(valores[1]))
	source_filter_set_value(None, source_name, 'Color Correction', 'hue_shift', int(valores[2]))

def source_filter_set_enabled(unused_addr, source_name, filter_name, boolean):
	c2(f'source_filter_set_enabled(source_name="{source_name}", {filter_name}, {boolean})')
	with ExitStack() as stack:
		source = stack.enter_context(source_auto_release(source_name))
		if source:
			filter_ = stack.enter_context(get_filter(source, filter_name))
			if filter_:
				obs.obs_source_set_enabled(filter_, bool(boolean))
			else: print(f'Filter no existe: {filter_name}')
		else: print(f'Source no existe: {source_name}')

def source_set_lut_file(unused_addr, source_name, filter_name, lut_file):
	source_filter_set_value(None, source_name=source_name,
		filter_name='lut', setting='image_path', value=lut_file)

def source_set_image_file(unused_addr, source_name, image_file, from_web=False):
	c2(f'source_set_image_file(source_name="{source_name}", image_file="{image_file}", from_web={from_web})')
	
	# Chequear archivo
	if from_web:
		response = requests.get(image_file)
		try:
			im = Image.open(BytesIO(response.content))
			im.close()
		except FileNotFoundError:
			print(f'Image_file (from_web) no existe: {image_file}')
			return
	else:
		try:
			im = Image.open(image_file)
			im.close()
		except FileNotFoundError:
			print(f'Image_file no existe: {image_file}')
			return
	
	source_set_setting(None, source_name=source_name, setting='file', value=image_file)

def source_set_setting(unused_addr, source_name, setting, value):
	c4(f'source_set_video_file(source_name="{source_name}", setting="{setting}", value={value})')
	with ExitStack() as stack:	
		source = stack.enter_context(source_auto_release(source_name))
		if source:
			newSettings = stack.enter_context(new_settings())
			if type(value) == str:
				obs.obs_data_set_string(newSettings, setting, value)
			elif type(value) == int:
				obs.obs_data_set_int(newSettings, setting, value)
			elif type(value) == float:
				obs.obs_data_set_double(newSettings, setting, value)
			obs.obs_source_update(source, newSettings)
		else: print(f'Source no existe: {source_name}')

def source_set_video_file(unused_addr, source_name, video_file):
	c2(f'source_set_video_file(source_name="{source_name}", video_file="{video_file}")')
	source_set_setting(None, source_name=source_name, setting='local_file', value=video_file)

def source_set_slide_time(unused_addr, source_name, slide_time):
	c2(f'source_set_slide_time(source_name="{source_name}", slide_time={slide_time})')
	source_set_setting(None, source_name=source_name, setting='slide_time', value=slide_time)

def source_set_text(unused_addr, source_name, text_string):
	c2(f'source_set_text(source_name="{source_name}", text_string="{text_string}")')
	source_set_setting(None, source_name=source_name, setting='text', value=text_string)

def source_set_text_size(unused_addr, source_name, size):
	c2(f'source_set_text_size(source_name="{source_name}", size="{size}")')
	source_set_setting(None, source_name=source_name, setting='size', value=size)

def source_get_settings(unused_addr, source_name):
	c2(f'source_get_settings(source_name="{source_name}")')
	source = obs.obs_get_source_by_name(source_name)
	sourceSettings = obs.obs_source_get_settings(source)

	response = obs.obs_data_create()
	
	obs.obs_data_set_string(response, "sourceName", obs.obs_source_get_name(source))
	obs.obs_data_set_string(response, "sourceId", obs.obs_source_get_id(source))
	obs.obs_data_set_string(response, "sourceType", obs.obs_source_get_type(source))
	obs.obs_data_set_obj(response, "sourceSettings", sourceSettings)
	obs.obs_source_release(source)
	retorno = obs.obs_data_get_json(response)
	return retorno
	
def item_get_transform(unused_addr, scene_name, item_name):
	c2(f'item_get_transform(scene_name="{scene_name}", item_name="{item_name}")')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

			
		if scene_item:
			source = obs.obs_sceneitem_get_source(scene_item)
			itemInfo = obs.obs_transform_info()
			crop = obs.obs_sceneitem_crop()
			obs.obs_sceneitem_get_info(scene_item, itemInfo)
			obs.obs_sceneitem_get_crop(scene_item, crop)
			retorno = {
				'bounds': {'alignment': itemInfo.bounds_alignment, 'type': itemInfo.bounds_type,
				'x': itemInfo.bounds.x, 'y': itemInfo.bounds.y},
				'width': obs.obs_source_get_height(source) * itemInfo.scale.x,
				'height': obs.obs_source_get_width(source) * itemInfo.scale.y,
				'crop': {'bottom': crop.bottom, 'left': crop.left, 'right': crop.right, 'top': crop.top},
				'itemId': obs.obs_sceneitem_get_id(scene_item), 'locked': obs.obs_sceneitem_locked(scene_item), 'name': item_name,
				'position': {'alignment': itemInfo.alignment, 'x': itemInfo.pos.x, 'y': itemInfo.pos.y},
				'rotation': itemInfo.rot, 'scale': {'x': itemInfo.scale.x, 'y': itemInfo.scale.x},
				'sourceHeight': obs.obs_source_get_height(source), 'sourceWidth': obs.obs_source_get_width(source),
				'visible': obs.obs_sceneitem_visible(scene_item)}
			
			print(retorno)
			return retorno
		else:
			print(f'item_get_transform() Item no existe: {item_name}')


def item_set_pos(unused_addr, scene_name, item_name, pos_x=None, pos_y=None):
	c4(f'item_set_pos(scene_name="{scene_name}", item_name="{item_name}", {pos_x}, {pos_y})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_pos() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:
			new_pos = obs.vec2()
			if pos_x != None : new_pos.x = pos_x
			if pos_y != None : new_pos.y = pos_y
			obs.obs_sceneitem_set_pos(scene_item, new_pos)
			
		else:
			print(f'item_set_pos() Item no existe: {item_name}')

def item_set_scl(unused_addr, scene_name, item_name, scl_x=None, scl_y=None):
	c4(f'item_set_scl(scene_name="{scene_name}", item_name="{item_name}", scl_x={scl_x}, scl_y={scl_y})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_scl() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:
			new_scale = obs.vec2()
			if scl_x != None: new_scale.x = scl_x
			if scl_y != None: new_scale.y = scl_y
			obs.obs_sceneitem_set_scale(scene_item, new_scale)
		else:
			print(f'item_set_scl() Item no existe: {item_name}')

def item_set_rot(unused_addr, scene_name, item_name, rot=None):
	c4(f'item_set_rot(scene_name="{scene_name}", item_name="{item_name}", rot={rot})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_rot() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:
			obs.obs_sceneitem_set_rot(scene_item, rot)
		else:
			print(f'item_set_rot() Item no existe: {item_name}')

def item_set_alignment(unused_addr, scene_name, item_name, alignment):
	c4(f'item_set_alignment(scene_name="{scene_name}", item_name="{item_name}", {alignment})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_alignment() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:
			obs.obs_sceneitem_set_alignment(scene_item, alignment)
		else:
			print(f'item_set_alignment() Item no existe: {item_name}')

def item_set_visible(unused_addr, scene_name, item_name, visible):
	c4(f'item_set_visible(scene_name="{scene_name}", item_name="{item_name}", {bool(visible)})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_visible() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:
			obs.obs_sceneitem_set_visible(scene_item, bool(visible))
		else:
			print(f'item_set_visible() Item no existe: {item_name}')

def item_set_transform(unused_addr, 
	scene_name, 
	item_name, 
	pos_x=None, pos_y=None,
	scl_x=None, scl_y=None, 
	rot=None, 
	alignment=None, 
	visible=None):

	c4(f'item_set_transform(scene_name="{scene_name}", item_name="{item_name}", pos_x={pos_x}, pos_y={pos_y},')
	c4(f'	scl_x={scl_x}, scl_y={scl_y}, rot={rot}, alignment={alignment}, visible={bool(visible)})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_transform() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:
			info = obs.obs_transform_info()
			obs.obs_sceneitem_get_info(scene_item, info)
			if pos_x     != None: info.pos.x     = pos_x
			if pos_y     != None: info.pos.y     = pos_y
			if scl_x     != None: info.scale.x   = scl_x
			if scl_y     != None: info.scale.y   = scl_y
			if rot       != None: info.rot       = rot
			if alignment != None: info.alignment = alignment
			obs.obs_sceneitem_set_info(scene_item, info)
		
			if visible != None:
				obs.obs_sceneitem_set_visible(scene_item, bool(visible))
		else:
			print(f'item_set_transform() Item no existe: {item_name}')

def item_remove(unused_addr, scene_name, item_name):
	c3(f'item_remove(scene_name="{scene_name}", item_name="{item_name}")')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_remove() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source(scene, item_name['name'])

		if scene_item:
			obs.obs_sceneitem_remove(scene_item)
			c3(f'ITEM REMOVED item_remove(scene_name="{scene_name}", item_name="{item_name}")')
		else:
			print(f'item_remove() Item no existe: {item_name}')

def item_set_crop(unused_addr, 
	scene_name, 
	item_name, 
	left=None, 
	right=None, 
	top=None, 
	bottom=None):
	
	c3(f'item_set_crop(scene_name="{scene_name}", item_name="{item_name}",')
	c3(f'	left={left}, right={right}, top={top}, bottom={bottom})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_crop() Scene no existe: {scene_name}')
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:
			crop = obs.obs_sceneitem_crop()
			obs.obs_sceneitem_get_crop(scene_item, crop)
			if left != None:   crop.left   = int(left)
			if right != None:  crop.right  = int(right)
			if top != None:    crop.top    = int(top)
			if bottom != None: crop.bottom = int(bottom)
			obs.obs_sceneitem_set_crop(scene_item, crop)
		else:
			print(f'item_set_crop() Item no existe: {item_name}')

def item_reference(unused_addr, 
	fromScene_name, 
	toScene_name, 
	item_name, 
	new_item_name):
	
	item_duplicate(None, 
		fromScene_name=fromScene_name, 
		toScene_name=toScene_name,
		item_name=item_name, 
		new_item_name=new_item_name, 
		reference=True)

def item_duplicate(unused_addr, 
	fromScene_name, 
	toScene_name,
	item_name, 
	new_item_name=None, 
	copy_info_crop=True, 
	visible=None, 
	reference=False):
	
	c3(f'item_duplicate(fromScene_name="{fromScene_name}", toScene_name="{toScene_name}",')
	c3(f'	item_name="{item_name}", new_item_name="{new_item_name}",')
	c3(f'	copy_info_crop={copy_info_crop}, visible={visible})')

	fromScene, scenes_list1 = get_scene_context(fromScene_name)
	if not fromScene:
		obs.source_list_release(scenes_list1)
		print(f'item_duplicate() fromScene no existe: {fromScene_name}')
		return
	
	toScene, scenes_list2 = get_scene_context(toScene_name)
	if not toScene:
		obs.source_list_release(scenes_list2)
		print(f'item_duplicate() toScene no existe: {toScene_name}')
		return

	consola(fromScene, c.naranja)
	consola(toScene, c.naranja)

	with source_list_auto_release(scenes_list1):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(fromScene, item_name)
			consola(item_name, c.error)
			consola(fromScene, c.error)
			consola(scene_item, c.error)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(fromScene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(fromScene, item_name['name'])
	
		if scene_item:

			if copy_info_crop:
				info = obs.obs_transform_info()
				crop = obs.obs_sceneitem_crop()
				obs.obs_sceneitem_get_info(scene_item, info)
				obs.obs_sceneitem_get_crop(scene_item, crop)

			# Lo elije como source
			source = obs.obs_sceneitem_get_source(scene_item)

			if reference:
				# Crea item tomando como referencia el source
				scene_item2 = obs.obs_scene_add(toScene, source)
			else:
				# Duplica
				duplicated = obs.obs_source_duplicate(source, new_item_name, False)
				# Crea item con 
				scene_item2 = obs.obs_scene_add(toScene, duplicated)
				obs.obs_source_release(duplicated)

			if copy_info_crop:
				obs.obs_sceneitem_set_info(scene_item2, info)
				obs.obs_sceneitem_set_crop(scene_item2, crop)

			obs.obs_scene_release(fromScene)
			obs.obs_scene_release(toScene)

			item_id = obs.obs_sceneitem_get_id(scene_item2)
			return item_id
		else:
			print(f'item_duplicate() Item no existe: {item_name}')

def item_tween(unused_addr,
	scene_name, 
	item_name, 
	from_pos_x=None, 
	from_pos_y=None, 
	from_scl_x=None, 
	from_scl_y=None, 
	from_rot=None,
	to_pos_x=None, 
	to_pos_y=None, 
	to_scl_x=None, 
	to_scl_y=None, 
	to_rot=None,
	alignment=None, 
	visible=True, 
	duration=1000, 
	delay=0, 
	ease_type='outQuad',
	fps=30):

	c2(f'item_tween(scene_name="{scene_name}", item_name="{item_name}",')
	c2(f'	duration={duration}, delay={delay}, ease_type={ease_type},')
	c2(f'	from_pos_x={from_pos_x}, from_pos_y={from_pos_y},')
	c2(f'	from_scl_x={from_scl_x}, from_scl_y={from_scl_y},')
	c2(f'	from_rot={from_rot}, to_pos_x={to_pos_x}, to_pos_y={to_pos_y},')
	c2(f'	to_scl_x={to_scl_x}, to_scl_y={to_scl_y}, to_scl_rot={to_rot},')
	c2(f'	alignment={alignment}, visible={visible}, fps={fps})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		return

	with source_list_auto_release(scenes_list):
		if type(item_name) == str:
			scene_item = obs.obs_scene_find_source_recursive(scene, item_name)
		elif type(item_name) == dict:
			if 'id' in item_name:
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, item_name['id'])
			elif 'name' in item_name:
				scene_item = obs.obs_scene_find_source_recursive(scene, item_name['name'])

		if scene_item:

			item_info = obs.obs_transform_info()
			obs.obs_sceneitem_get_info(scene_item, item_info)

			if from_pos_x == None: from_pos_x = item_info.pos.x 
			if from_pos_y == None: from_pos_y = item_info.pos.y 
			if from_scl_x == None: from_scl_x = item_info.scale.x
			if from_scl_y == None: from_scl_y = item_info.scale.y
			if from_rot   == None: from_rot   = item_info.rot

			init_time = time.time()*1000

			# Función en Thread
			th(th_tween, [scene_name, item_name, scene_item, item_info,
				init_time, duration, delay, ease_type,
				from_pos_x, from_pos_y, from_scl_x, from_scl_y, from_rot,
				to_pos_x, to_pos_y, to_scl_x, to_scl_y, to_rot,
				alignment, visible, fps])

def th_tween(scene_name, item_name, scene_item, item_info,
	init_time, duration, delay, ease_type,
	from_pos_x, from_pos_y, from_scl_x, from_scl_y, from_rot,
	to_pos_x, to_pos_y, to_scl_x, to_scl_y, to_rot,
	alignment, visible, fps):
		# Delay
		if delay > 0:
			time.sleep(delay/1000)
			init_time += delay

		# Visible
		obs.obs_sceneitem_set_visible(scene_item, bool(visible))
		
		# Loop
		while init_time + duration > time.time()*1000:	
			# if not scene_item:
			# 	return
			
			elapsed_time = time.time()*1000 - init_time
			pos_change_x = None if to_pos_x == None else to_pos_x - from_pos_x
			pos_change_y = None if to_pos_y == None else to_pos_y - from_pos_y
			scl_change_x = None if to_scl_x == None else to_scl_x - from_scl_x
			scl_change_y = None if to_scl_y == None else to_scl_y - from_scl_y
			rot_change   = None if to_rot   == None else to_rot   - from_rot
			
			# time, beginning position, change inposition, and duration
			pos_x = None if to_pos_x == None else tween_eq(ease_type, elapsed_time, from_pos_x, pos_change_x, duration)
			pos_y = None if to_pos_y == None else tween_eq(ease_type, elapsed_time, from_pos_y, pos_change_y, duration)
			scl_x = None if to_scl_x == None else tween_eq(ease_type, elapsed_time, from_scl_x, scl_change_x, duration)
			scl_y = None if to_scl_y == None else tween_eq(ease_type, elapsed_time, from_scl_y, scl_change_y, duration)
			rot   = None if to_rot   == None else tween_eq(ease_type, elapsed_time, from_rot  , rot_change  , duration)

			c4(f'item_set_transform(scene_name="{scene_name}", item_name="{item_name}",')
			c4(f'	pos_x={pos_x}, pos_y={pos_y}, scl_x={scl_x}, scl_y={scl_y},')
			c4(f'	rot={rot}, alignment={alignment}, visible={visible})')

			if pos_x     != None: item_info.pos.x     = int(pos_x)
			if pos_y     != None: item_info.pos.y     = int(pos_y)
			if scl_x     != None: item_info.scale.x   = scl_x
			if scl_y     != None: item_info.scale.y   = scl_y
			if rot       != None: item_info.rot       = rot
			if alignment != None: item_info.alignment = alignment
			obs.obs_sceneitem_set_info(scene_item, item_info)

			time_sleep = 1 / fps
			time.sleep(time_sleep)
		
		if to_pos_x  != None: item_info.pos.x     = int(to_pos_x)
		if to_pos_y  != None: item_info.pos.y     = int(to_pos_y)
		if to_scl_x  != None: item_info.scale.x   = to_scl_x
		if to_scl_y  != None: item_info.scale.y   = to_scl_y
		if to_rot    != None: item_info.rot       = to_rot
		if alignment != None: item_info.alignment = alignment
		obs.obs_sceneitem_set_info(scene_item, item_info)

		c3(f'Terminó tween "{scene_name}" "{item_name}"')

# TWEEN - Ecuaciones
def tween_eq(ease_type, t, b, c, d):
	#~ if t >= 0:
	if ease_type == 'linear':
		return c * t / d + b
	elif ease_type == 'inQuad':
		t /= d
		return c * t * t + b
	elif ease_type == 'outQuad':
		t /= d
		return - c * t * (t - 2) + b
	elif ease_type == 'inOutQuad':
		t /= d / 2
		if (t < 1):
			return c / 2 * t * t + b
		t -= 1
		return -c / 2 * ((t) * (t - 2) - 1) + b
	elif ease_type == 'inCubic':
		t /= d
		return c * t * t * t + b
	elif ease_type == 'outCubic':
		t /= d
		t -= 1
		return c * (t * t * t + 1) + b
	elif ease_type == 'inOutCubic':
		t /= d / 2
		if (t < 1):
			return c / 2 * t * t * t + b
		t -= 2
		return c / 2 * (t * t * t + 2) + b
