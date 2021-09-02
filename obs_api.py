#!/usr/bin/env python3
""" obs_api

Some funtions to use with OBS

This program is free software: you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation, either version 3 of the License, or (at your option) any later
version.
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.
You should have received a copy of the GNU General Public License along with
this program. If not, see <http://www.gnu.org/licenses/>.
"""

__author__ = "Mario Mey"
__contact__ = "mariomey@gmail.com"
__credits__ = []
__date__ = "2021/08/13"
__deprecated__ = False
__license__ = "GPLv3"
__maintainer__ = "developer"
__status__ = "Production"
__version__ = "0.1"

from contextlib import contextmanager, ExitStack
import random, time, datetime, threading, ast

import obspython as obs

from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor(max_workers=100)

from os import listdir
from os.path import join, isdir, isfile

import requests
from io import BytesIO

from pythonosc import udp_client
targetIp = "127.0.0.1"
targetPort = 10000
client = udp_client.SimpleUDPClient(targetIp, targetPort)

from PIL import Image

import globalDict

client.send_message("/init", 1)
bolita_image   = '/home/mario/videoconfestejo/juegos/ark/bola.png'

sd = obs.obs_video_info()
obs.obs_get_video_info(sd)


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
	if globalDict.gd['verbose'][0]:
		texto = str(texto)
		print(color_texto, texto, c.reset)

def c2(texto, color_texto=c.azul):
	if globalDict.gd['verbose'][1]:
		texto = str(texto)
		print(color_texto, texto, c.reset)

def c3(texto, color_texto=c.cian):
	if globalDict.gd['verbose'][2]:
		texto = str(texto)
		print(color_texto, texto, c.reset)

def c4(texto, color_texto=c.rosa):
	if globalDict.gd['verbose'][3]:
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
		if i == lugar1:                              print('*', end='')
		elif num2 != None and i == lugar2:           print('$', end='')
		elif num2 != None and i == lugar1 == lugar2: print('&', end='')
		else:
			if start < 0 < end and i == int((-start / (end - start)) * largo): print('0', end='')
			else:                                                              print('.', end='')
	print(end, num1, '\r', c.reset, end='')

# Conversión lineal de x0-x1 -> y0-y1.
def lin_eq_conv(x, x0, x1, y0, y1):
	a = (y0 - y1) / (x0 - x1)
	b = -(a * x0) + y0
	return a * x + b

# Threading
def thread(function, args=[]):
	t = threading.Thread(
		target=function,
		args=(args),
		name=f'{function}({args})',
		daemon=True)
	t.start()

# Threading POOL
def th(function, args=[]):
	executor.submit(function, *args)

# Retrasa una función, tantos milisegundos
def delay_func(funcion, delay_ms, args=[]):
	c4(f'delay_func(funcion={funcion}, delay_ms={delay_ms}, args={args}')
	start_time = time.time()
	seg = int(delay_ms/1000)
	while int(delay_ms/1000) > (time.time()- start_time) :
		c4(f'delay_func(funcion) Faltan {seg} segundos...')
		seg -= 1
		time.sleep(1)
	c4(f'delay_func(funcion) Faltan {delay_ms % 1000}ms...')
	time.sleep(delay_ms % 1000 / 1000)
	c4(f'delay_func(funcion) Se ejecuta {funcion}')
	funcion(*args)

# Convierte una línea de texto, cortando las palabras
def text2paragraph(text, chars=0, new_line='\n'):
	if chars == 0:
		print('Especificar una cantidad mínimia (negativo)')
		print('o máxima (positivo) de caracteres en el párrafo.')
		return
	palabras, lineas = text.split(' '), []
	palabra_count, linea_count = 0, 0
	while palabra_count < len(palabras):
		lineas.append('')
		lineas[linea_count] += palabras[palabra_count] + ' '
		palabra_count += 1
		if chars < 0:
			chars = - chars
			while palabra_count < len(palabras) and len(lineas[linea_count]) < chars:
				lineas[linea_count] += palabras[palabra_count] + ' '
				palabra_count += 1
		else:
			while palabra_count < len(palabras) and len(lineas[linea_count] + palabras[palabra_count]) < chars:
				lineas[linea_count] += palabras[palabra_count] + ' '
				palabra_count += 1
		linea_count += 1
	return str(new_line).join([str(linea) for linea in lineas])

# Convierte [r,g,b,a] (0-1) a decimal
def rgba2decimal(rgba_):
	# return (rgba[3] << 24) + (rgba[2] << 16) + (rgba[1] << 8) + rgba[0]
	rgba = [int(rgba_[0] * 255), int(rgba_[1] * 255), int(rgba_[2] * 255), int(rgba_[3] * 255)]
	return (256**3)*rgba[3] + (256**2)*rgba[2] + 256*rgba[1] + rgba[0]

# Convierte decimal a [r,g,b,a] (0-1)
def decimal2rgba(decimal):
	# a = decimal >> 24
	# b = (decimal >> 16) % 256
	# g = (decimal >> 8) % 256
	# r = decimal % 256
	# return [round(r / 255, 3), round(g / 255, 3), round(b / 255, 3), round(a / 255, 3)]
	a     = decimal / (256**3)
	amod  = decimal % (256**3)
	b     = amod    / (256**2)
	bmod  = amod    % (256**2)
	g     = bmod    / 256
	gmod  = bmod    % 256
	r     = gmod
	return [round(r/255, 3), round(min(g/255, 1.0), 3), round(min(b/255, 1.0), 3), round(min(a/255, 1.0), 3)]

@contextmanager
def scene_from_source(source):
	scene = obs.obs_scene_from_source(source)
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
def item_auto_release(scene_item):
	try:
		yield scene_item
	finally:
		obs.obs_sceneitem_release(scene_item)

@contextmanager
def item_from_name(scene, item_name):
	scene_item = obs.obs_scene_find_source(scene, item_name)
	try:
		yield scene_item
	finally:
		obs.obs_sceneitem_release(scene_item)

@contextmanager
def item_from_id(scene, id_num):
	scene_item = obs.obs_scene_find_sceneitem_by_id(scene, id_num)
	try:
		yield scene_item
	finally:
		obs.obs_sceneitem_release(scene_item)

@contextmanager
def source_creation(source_type, source_name, newSettings):
	source = obs.obs_source_create(source_type, source_name, newSettings, None)
	try:
		yield source
	finally:
		obs.obs_source_release(source)

@contextmanager
def private_source_creation(source_type, source_name, newSettings):
	source = obs.obs_source_create_private(source_type, source_name, newSettings)
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
def items_list_auto_release(items_list):
	try:
		yield items_list
	finally:
		obs.source_list_release(items_list)

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
	return_scene = None
	for scene in scenes_list:
		name = obs.obs_source_get_name(scene)
		# consola(name, c.debug)
		if name == scene_name:
			# consola(f'encontrada {name}', c.violeta)
			return_scene = obs.obs_scene_from_source(scene)

	return return_scene, scenes_list

def tobool(que):
	if type(que) == bool:
		return que
	elif type(que) == float or type(que) == int:
		return bool(int(que))
	elif type(que) == str:
		if que in ['True', 'true', '1', '1.0']:
			return True
		elif que in ['False', 'false', '0', '0.0']:
			return False
		elif que in ['None', 'none', 'Null', 'null']:
			return None
	elif type(que) == None:
		return None
	
def tolist(que):
	if type(que) == list:
		return que
	elif type(que) == str and que.startswith('[') and que.endswith(']'):
		lista =  que[1:-1].split(',')
		isdig = []
		for i in lista:
			if i.translate({ord(c): None for c in '-.'}).isdigit():
				isdig.append(True)
		if all(isdig):
			return [float(i) for i in lista]
		else:
			return lista
	else:
		consola('tolist() - No recibió bien la lista', c.error)

def toint(que):
	if type(que) == int:
		return que
	elif type(que) == float:
		return int(que)
	elif type(que) == str:
		if que in ['None', 'none', 'Null', 'null']:
			return None
		if que.translate({ord(c): None for c in '-.'}).isdigit():
			return int(que)
	elif type(que) == None:	
		return None

def tofloat(que):
	if type(que) == float:
		return que
	elif type(que) == int:
		return float(que)
	elif type(que) == str:
		if que in ['None', 'none', 'Null', 'null']:
			return None
		if que.translate({ord(c): None for c in '-.'}).isdigit():
			return float(que)
	elif type(que) == None:	
		return None

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


def source_filter_set_value(unused_addr, source_name, filter_name, setting, value, private=False):
	c2(f'source_filter_set_value(source_name="{source_name}",')
	c2(f'	filter_name="{filter_name}", setting={setting}, value={value})')

	with ExitStack() as stack:
		# if not private: source = stack.enter_context(source_auto_release(source_name))
		# else:           source = globals()[source_name]
		source = stack.enter_context(source_auto_release(source_name))
		if source:
			filter_ = stack.enter_context(get_filter(source, filter_name))
			if filter_:
				newSettings = stack.enter_context(new_settings())
				# if filter_name in ['opacity', 'hue_shift']:
				# 	obs.obs_data_set_int(newSettings, setting, value)
				# else:
				if type(value) == str:
					obs.obs_data_set_string(newSettings, setting, value)
				elif type(value) == int:
					obs.obs_data_set_int(newSettings, setting, value)
				elif type(value) == float:
					obs.obs_data_set_double(newSettings, setting, value)
				obs.obs_source_update(filter_, newSettings)
			else: print(f'source_filter_set_value() Filter no existe: {filter_name}')
		else: print(f'source_filter_set_value() Source no existe: {source_name}')

def source_filter_get_settings(unused_addr, source_name, filter_name, private=False, print=False):
	c2(f'source_filter_set_value(source_name="{source_name}", filter_name="{filter_name}")')
	with ExitStack() as stack:
		if not private: source = stack.enter_context(source_auto_release(source_name))
		else:           source = globals()[source_name]
		if source:
			filter_ = stack.enter_context(get_filter(source, filter_name))
			if filter_:
				sourceSettings = obs.obs_source_get_settings(filter_)
				json_from_filter = obs.obs_data_get_json(sourceSettings)
				if print: consola(json_from_filter)
				return json_from_filter
			else: print(f'Filter no existe: {filter_name}')
		else: print(f'Source no existe: {source_name}')

def source_set_opacity(unused_addr, source_name, opacity, private=False):
	source_filter_set_value(None, source_name, 'Color Correction', 'opacity', tofloat(opacity), private=private)

def source_set_hue(unused_addr, source_name, hue, private=False):
	source_filter_set_value(None, source_name, 'Color Correction', 'hue_shift', int(hue), private=private)

def source_set_bri_sat_hue(unused_addr, source_name, valores, private=False):
	source_filter_set_value(None, source_name, 'Color Correction', 'brightness', float(valores[0]), private=private)
	source_filter_set_value(None, source_name, 'Color Correction', 'saturation', float(valores[1]), private=private)
	source_filter_set_value(None, source_name, 'Color Correction', 'hue_shift',    int(valores[2]), private=private)

def source_set_con_bri_sat_hue(unused_addr, source_name, valores, private=False):
	source_filter_set_value(None, source_name, 'Color Correction', 'contrast',   float(valores[0]), private=private)
	source_filter_set_value(None, source_name, 'Color Correction', 'brightness', float(valores[1]), private=private)
	source_filter_set_value(None, source_name, 'Color Correction', 'saturation', float(valores[2]), private=private)
	source_filter_set_value(None, source_name, 'Color Correction', 'hue_shift',    int(valores[3]), private=private)

def source_set_lut_file(unused_addr, source_name, filter_name, lut_file, enabled=None, private=False):
	source_filter_set_value(None, source_name, 'lut', 'image_path', lut_file, private)
	if enabled != None:
		source_filter_set_enabled(None, source_name, filter_name, enabled, private)

def source_filter_set_enabled(unused_addr, source_name, filter_name, boolean, private=False):
	c2(f'source_filter_set_enabled(source_name="{source_name}", {filter_name}, {boolean}, {private})')
	with ExitStack() as stack:
		if not private: source = stack.enter_context(source_auto_release(source_name))
		else:           source = globals()[source_name]
		if source:
			filter_ = stack.enter_context(get_filter(source, filter_name))
			if filter_:
				obs.obs_source_set_enabled(filter_, bool(boolean))
			else: print(f'Filter no existe: {filter_name}')
		else: print(f'Source no existe: {source_name}')

def source_set_image_file(unused_addr, source_name, image_file, from_web=False, private=False):
	c2(f'source_set_image_file(source_name="{source_name}", image_file="{image_file}", from_web={from_web})')
	
	size_   = list()
	mode_   = str()
	format_ = str()

	# Chequear archivo
	if from_web:
		newSettings = requests.get(image_file)
		try:
			with Image.open(BytesIO(newSettings.content)) as im:
				size_   = list(im.size)
				mode_   = list(im.mode)
				format_ = list(im.format)
		except FileNotFoundError:
			print(f'Image_file (from_web) no existe: {image_file}')
			return
	else:
		try:
			with Image.open(image_file) as im:
				size_   = list(im.size)
				mode_   = list(im.mode)
				format_ = list(im.format)
		except FileNotFoundError:
			print(f'Image_file no existe: {image_file}')
			return
	
	source_set_setting(None, source_name=source_name, setting='file', value=image_file, private=private)
	return {'size': size_, 'mode': mode_, 'format':format_}

def source_set_setting(unused_addr, source_name, setting, value, private=False):
	c2(f'source_set_setting(source_name="{source_name}", setting="{setting}", value="{value}", private={private})')
	with ExitStack() as stack:

		if not private:
			source = stack.enter_context(source_auto_release(source_name))
		else:
			source = globals()[source_name]
		
		if source:
			newSettings = stack.enter_context(new_settings())
			if   type(value) == bool:
				obs.obs_data_set_bool(newSettings, setting, value)
			
			elif type(value) == str and (value == 'true' or value == 'True'):
				obs.obs_data_set_bool(newSettings, setting, True)
			
			elif type(value) == str and (value == 'false' or value == 'False'):
				obs.obs_data_set_bool(newSettings, setting, False)
			
			elif type(value) == str:
				obs.obs_data_set_string(newSettings, setting, value)
			
			elif type(value) == int:
				obs.obs_data_set_int(newSettings, setting, value)
			
			elif type(value) == float:
				obs.obs_data_set_double(newSettings, setting, value)
			
			elif type(value) == list:
				value = rgba2decimal(value)
				obs.obs_data_set_int(newSettings, setting, value)
			
			obs.obs_source_update(source, newSettings)
		else: print(f'Source no existe: {source_name}')

def source_set_video_file(unused_addr, source_name, video_file):
	c2(f'source_set_video_file(source_name="{source_name}", video_file="{video_file}")')
	source_set_setting(None, source_name=source_name, setting='local_file', value=video_file)

def source_set_slide_time(unused_addr, source_name, slide_time):
	c2(f'source_set_slide_time(source_name="{source_name}", slide_time={slide_time})')
	source_set_setting(None, source_name=source_name, setting='slide_time', value=slide_time)

def source_set_text(unused_addr, source_name, text_string, private=False):
	text_string = text_string.replace('_', ' ')
	c2(f'source_set_text(source_name="{source_name}", text_string="{text_string}")')
	source_set_setting(None, source_name=source_name, setting='text', value=text_string, private=private)

def source_set_text_size(unused_addr, source_name, size):
	c2(f'source_set_text_size(source_name="{source_name}", size="{size}")')
	source_set_setting(None, source_name=source_name, setting='size', value=size)

def source_get_settings(unused_addr, source_name, print_=False):
	c2(f'source_get_settings(source_name="{source_name}")')
	source = obs.obs_get_source_by_name(source_name)
	sourceSettings = obs.obs_source_get_settings(source)

	with ExitStack() as stack:
		newSettings = stack.enter_context(new_settings())
		# newSettings = obs.obs_data_create()
		
		obs.obs_data_set_string(newSettings, "sourceName", obs.obs_source_get_name(source))
		obs.obs_data_set_string(newSettings, "sourceId", obs.obs_source_get_id(source))
		obs.obs_data_set_double(newSettings, "sourceType", obs.obs_source_get_type(source))
		obs.obs_data_set_obj(newSettings, "sourceSettings", sourceSettings)
		obs.obs_source_release(source)
		retorno = obs.obs_data_get_json(newSettings)
		
		if bool(print_):
			consola(retorno)
		return retorno

# Asigna un filtro a un source.
def source_assign_filter(unused_addr, source_name, filter_type='color_filter', filter_name="Color Correction", private=False):
	c3(f'source_assign_filter(source_name="{source_name}", filter_type="{filter_type}", filter_name="{filter_name}")')

	with ExitStack() as stack:
		if not private:
			source = stack.enter_context(source_auto_release(source_name))
		else:
			source = globals()[source_name]
		
		if source:
			# Aplica filtro color_source para opacidad
			newSettings = stack.enter_context(new_settings())
			source_color = obs.obs_source_create_private(filter_type, filter_name, newSettings)
			obs.obs_source_filter_add(source, source_color)
		else:
			print(f'source_assign_filter() Source no existe: "{source_name}"')

def source_set_name(unused_addr, source_name, new_name, private=False):
	c3(f'source_set_name(source_name="{source_name}", new_name={new_name}, private={private})')

	with ExitStack() as stack:
		if not private:
			source = stack.enter_context(source_auto_release(source_name))
			if source:
				obs.obs_source_set_name(source, new_name)
			else:
				print(f'source_set_name() Source no existe: "{source_name}"')
		else:
			source = globals()[source_name]
			if source:
				obs.obs_source_set_name(source, new_name)
				globals()[new_name] = source
				del globals()[source_name]
			else:
				print(f'source_set_name() Source no existe: "{source_name}"')


# ITEMS
# ITEMS
# ITEMS
def item_get_props(unused_addr, scene_name, item_name):
	c2(f'item_get_props(scene_name="{scene_name}", item_name="{item_name}")')
	scene_item = obs.obs_scene_find_source(get_scene_context(scene_name), item_name)
	source = obs.obs_sceneitem_get_source(scene_item)
	
	itemInfo = obs.obs_transform_info()
	obs.obs_sceneitem_get_info(scene_item, itemInfo)

	with ExitStack() as stack:
		newSettings = stack.enter_context(new_settings())
		# newSettings = obs.obs_data_create()
		obs.obs_data_set_int(newSettings, "itemId", obs.obs_sceneitem_get_id(scene_item))
		obs.obs_data_set_string(newSettings, "sourceName", obs.obs_source_get_name(source))
		# TODO
		# obs.obs_data_set_array(newSettings, "itemInfo", obs.obs_data_get_json(itemInfo))

		return obs.obs_data_get_json(newSettings)

def item_get_transform(unused_addr, scene_name, item_name, print_=False):
	c2(f'item_get_transform(scene_name="{scene_name}", item_name="{item_name}")')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)
			
		if scene_item:
			source = obs.obs_sceneitem_get_source(scene_item)
			itemInfo = obs.obs_transform_info()
			crop = obs.obs_sceneitem_crop()

			obs.obs_sceneitem_get_info(scene_item, itemInfo)
			obs.obs_sceneitem_get_crop(scene_item, crop)
			todaladata = {
				'bounds': {'alignment': itemInfo.bounds_alignment, 'type': itemInfo.bounds_type,
				'x': itemInfo.bounds.x, 'y': itemInfo.bounds.y},
				# 'width': obs.obs_source_get_height(source) * itemInfo.scale.x,
				# 'height': obs.obs_source_get_width(source) * itemInfo.scale.y,
				'width':  (obs.obs_source_get_width(source)  - crop.left - crop.right)  * itemInfo.scale.x,
				'height': (obs.obs_source_get_height(source) - crop.top -  crop.bottom) * itemInfo.scale.y,
				'crop': {'bottom': crop.bottom, 'left': crop.left, 'right': crop.right, 'top': crop.top},
				'itemId': obs.obs_sceneitem_get_id(scene_item), 'locked': obs.obs_sceneitem_locked(scene_item), 'name': item_name,
				'position': {'alignment': itemInfo.alignment, 'x': itemInfo.pos.x, 'y': itemInfo.pos.y},
				'rotation': itemInfo.rot, 'scale': {'x': itemInfo.scale.x, 'y': itemInfo.scale.x},
				'sourceHeight': obs.obs_source_get_height(source), 'sourceWidth': obs.obs_source_get_width(source),
				'visible': obs.obs_sceneitem_visible(scene_item)}
	
			if bool(print_):
				consola(todaladata)
	
			return todaladata
		else:
			print(f'item_get_transform() Item no existe: "{item_name}"')
			return None


def item_set_pos(unused_addr, scene_name, item_name, pos_x=None, pos_y=None, add_x=0, add_y=0):
	c4(f'item_set_pos(scene_name="{scene_name}", item_name="{item_name}", pos_x={pos_x}, pos_y={pos_y}, add_x={add_x}, add_y={add_y})')

	scene, scenes_list = get_scene_context(scene_name)
	if scene:
		with source_list_auto_release(scenes_list):
			if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
			else: scene_item = obs.obs_scene_find_source(scene, item_name)
			if scene_item:
				old_pos = obs.vec2()
				obs.obs_sceneitem_get_pos(scene_item, old_pos)
				new_pos = obs.vec2()
				new_pos.x = int(pos_x) if pos_x not in [None, 'none', 'None'] else old_pos.x + add_x
				new_pos.y = int(pos_y) if pos_y not in [None, 'none', 'None'] else old_pos.y + add_y
				obs.obs_sceneitem_set_pos(scene_item, new_pos)
			else:
				print(f'item_set_pos() Item no existe: "{item_name}"')
	else:
		obs.source_list_release(scenes_list)
		print(f'item_set_pos() Scene no existe: "{scene_name}"')
		return

def item_set_scl(unused_addr, scene_name, item_name, scl_x=None, scl_y=None):
	c4(f'item_set_scl(scene_name="{scene_name}", item_name="{item_name}", scl_x={scl_x}, scl_y={scl_y})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_scl() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			old_scl = obs.vec2()
			obs.obs_sceneitem_get_scale(scene_item, old_scl)
			new_scl = obs.vec2()
			new_scl.x = float(scl_x) if scl_x not in [None, 'none', 'None'] else old_scl.x
			new_scl.y = float(scl_y) if scl_y not in [None, 'none', 'None'] else old_scl.y
			obs.obs_sceneitem_set_scale(scene_item, new_scl)

		else:
			print(f'item_set_scl() Item no existe: "{item_name}"')

def item_set_size(unused_addr,
	scene_name,
	item_name,
	width=None,
	height=None,
	private=False):
	c4(f'item_set_size(scene_name="{scene_name}", item_name="{item_name}", width={width}, height={height}, private={private})')

	width   = toint(width)
	height  = toint(height)
	private = tobool(private)

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_size() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'):
			scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else:
			scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			with ExitStack() as stack:
				try:
					if item_name.startswith('id:'):
						if not private:
							source = stack.enter_context(get_source(scene_item))
						else:
							source_aux = stack.enter_context(get_source(scene_item))
							sceneitem_name = obs.obs_source_get_name(source_aux)
							source = globals()[sceneitem_name]
							consola(f'OJO: item_set_size() sceneitem como "{item_name}" y "private=True" en modo BETA', c.error)
							return
					else:
						if not private:
							source = stack.enter_context(source_auto_release(item_name))
						else:
							source = globals()[item_name]

					item_info = obs.obs_transform_info()
					crop = obs.obs_sceneitem_crop()
					obs.obs_sceneitem_get_info(scene_item, item_info)
					obs.obs_sceneitem_get_crop(scene_item, crop)

					old_scl = obs.vec2()
					obs.obs_sceneitem_get_scale(scene_item, old_scl)
					old_width  = (obs.obs_source_get_width(source)  - crop.left - crop.right)  * item_info.scale.x
					old_height = (obs.obs_source_get_height(source) - crop.top -  crop.bottom) * item_info.scale.y

					new_scl = obs.vec2()
					new_scl.x = old_scl.x * (width  / old_width)  if width  not in [None, 'none', 'None'] else old_scl.x
					new_scl.y = old_scl.y * (height / old_height) if height not in [None, 'none', 'None'] else old_scl.y

					obs.obs_sceneitem_set_scale(scene_item, new_scl)
				
				except:
					print(f'item_set_size() Item "{item_name}" mal definido valor de "private"')

		else:
			print(f'item_set_size() Item no existe: "{item_name}"')

def item_set_scl_filter(unused_addr, scene_name, item_name, scl_filter):
	c4(f'item_set_scl_filter(scene_name="{scene_name}", item_name="{item_name}", scl_filter={scl_filter})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_scl() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			obs.obs_sceneitem_set_scale_filter(scene_item, int(scl_filter))
		else:
			print(f'item_set_scl() Item no existe: "{item_name}"')
		
		# OBS_SCALE_DISABLE  # OBS_SCALE_POINT     # OBS_SCALE_BICUBIC
		# OBS_SCALE_BILINEAR # OBS_SCALE_LANCZOS

def item_set_rot(unused_addr, scene_name, item_name, rot=None):
	c4(f'item_set_rot(scene_name="{scene_name}", item_name="{item_name}", rot={rot})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_rot() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			obs.obs_sceneitem_set_rot(scene_item, float(rot))
		else:
			print(f'item_set_rot() Item no existe: "{item_name}"')

def item_set_alignment(unused_addr, scene_name, item_name, alignment):
	"""
	# 0: centro
	# 5: top-left
	"""
	c4(f'item_set_alignment(scene_name="{scene_name}", item_name="{item_name}", {alignment})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_alignment() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			obs.obs_sceneitem_set_alignment(scene_item, alignment)
		else:
			print(f'item_set_alignment() Item no existe: "{item_name}"')

def item_set_visible(unused_addr, scene_name, item_name, visible):
	c4(f'item_set_visible(scene_name="{scene_name}", item_name="{item_name}", {bool(visible)})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_visible() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			obs.obs_sceneitem_set_visible(scene_item, bool(int(visible)))
		else:
			print(f'item_set_visible() Item no existe: "{item_name}"')

# Visible dentro de un grupo
def item_set_visible2(unused_addr, scene_name, group_name, item_name, visible):
	c4(f'item_set_visible(scene_name="{scene_name}", item_name="{item_name}", {bool(visible)})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_visible() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if group_name.startswith('id:'): group_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else:                            group_item = obs.obs_scene_find_source(scene, group_name)
		group_scene = obs.obs_sceneitem_group_get_scene(group_item)
		if group_scene:
			if item_name.startswith('id:'):  scene_item = obs.obs_scene_find_sceneitem_by_id(group_scene, int(item_name[3:]))
			else:                            scene_item = obs.obs_scene_find_source(group_scene, item_name)
		else:
			print(f'item_set_visible() Group no existe: "{group_name}"')
			return

		if scene_item:
			obs.obs_sceneitem_set_visible(scene_item, bool(visible))
		else:
			print(f'item_set_visible() Item no existe: "{item_name}"')

def item_set_transform(unused_addr, 
	scene_name, 
	item_name, 
	pos_x=None, pos_y=None,
	scl_x=None, scl_y=None, 
	width=None, height=None, 
	rot=None, 
	alignment=None, 
	visible=None):
	c4(f'item_set_transform(scene_name="{scene_name}", item_name="{item_name}", pos_x={pos_x}, pos_y={pos_y},')
	c4(f'	scl_x={scl_x}, scl_y={scl_y}, rot={rot}, alignment={alignment}, visible={bool(visible)})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_transform() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)
		
		if scene_item:
			info = obs.obs_transform_info()
			obs.obs_sceneitem_get_info(scene_item, info)
			if pos_x     not in [None, 'none', 'None']: info.pos.x     = int(float(pos_x))
			if pos_y     not in [None, 'none', 'None']: info.pos.y     = int(float(pos_y))
			if scl_x     not in [None, 'none', 'None']: info.scale.x   = float(scl_x)
			if scl_y     not in [None, 'none', 'None']: info.scale.y   = float(scl_y)
			if rot       not in [None, 'none', 'None']: info.rot       = float(rot)
			if alignment not in [None, 'none', 'None']: info.alignment = int(alignment)

			# Para usar Width y Height. Sobrescribe info.scale.x/y
			if width not in [None, 'none', 'None'] or height not in [None, 'none', 'None']:
				crop = obs.obs_sceneitem_crop()
				obs.obs_sceneitem_get_crop(scene_item, crop)
				source = obs.obs_sceneitem_get_source(scene_item)
	
				if width  not in [None, 'none', 'None']:
					info.scale.x = int(width)  / obs.obs_source_get_width(source)  - int(crop.left) - int(crop.right)
				if height not in [None, 'none', 'None']:
					info.scale.y = int(height) / obs.obs_source_get_height(source) - int(crop.top)  - int(crop.bottom)

			obs.obs_sceneitem_set_info(scene_item, info)
		
			if visible != None:
				obs.obs_sceneitem_set_visible(scene_item, bool(visible))
		else:
			print(f'item_set_transform() Item no existe: "{item_name}"')

def item_remove(unused_addr, scene_name, item_name):
	c3(f'item_remove(scene_name="{scene_name}", item_name="{item_name}")')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_remove() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			obs.obs_sceneitem_remove(scene_item)
			c3(f'ITEM REMOVED item_remove(scene_name="{scene_name}", item_name="{item_name}")')
		else:
			print(f'item_remove() Item no existe: "{item_name}"')

def global_source_release(source_name):
	if source_name in globals():
		obs.obs_source_release(globals()[source_name])
		del globals()[source_name]
	else: print(f'No se encuentra: globals()["{source_name}"')

def item_set_private_setting(unused_addr, scene_name, item_name, setting, value):
	c4(f'item_set_private_setting(scene_name="{scene_name}", item_name="{item_name}", setting="{setting}", value={value})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_remove() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			data = obs.obs_sceneitem_get_private_settings(scene_item)
			# obs.obs_data_release(data)
			if   type(value) == bool:  obs.obs_data_set_bool(data, setting, value)
			elif type(value) == str:   obs.obs_data_set_string(data, setting, value)
			elif type(value) == int:   obs.obs_data_set_int(data, setting, value)
			elif type(value) == float: obs.obs_data_set_double(data, setting, value)
		else:
			print(f'item_set_private_setting() Item no existe: "{item_name}"')


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
		print(f'item_set_crop() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)
		
		if scene_item:
			crop = obs.obs_sceneitem_crop()
			obs.obs_sceneitem_get_crop(scene_item, crop)
			if left != None:   crop.left   = int(left)
			if right != None:  crop.right  = int(right)
			if top != None:    crop.top    = int(top)
			if bottom != None: crop.bottom = int(bottom)
			obs.obs_sceneitem_set_crop(scene_item, crop)
		else:
			print(f'item_set_crop() Item no existe: "{item_name}"')

# Cropea un item dentro de un grupo en una escena
def item_set_crop2(unused_addr, 
	scene_name, 
	group_name, 
	item_name, 
	left=None, 
	right=None, 
	top=None, 
	bottom=None):
	
	c3(f'item_set_crop2(scene_name="{scene_name}", group_name="{group_name}", item_name="{item_name}",')
	c3(f'	left={left}, right={right}, top={top}, bottom={bottom})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_crop() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):

		group_item   = obs.obs_scene_get_group(scene, group_name)
		group_scene  = obs.obs_sceneitem_group_get_scene(group_item)
		scene_item   = obs.obs_scene_find_source(group_scene, item_name)
		
		if scene_item:
			crop = obs.obs_sceneitem_crop()
			obs.obs_sceneitem_get_crop(scene_item, crop)
			if left != None:   crop.left   = int(left)
			if right != None:  crop.right  = int(right)
			if top != None:    crop.top    = int(top)
			if bottom != None: crop.bottom = int(bottom)
			obs.obs_sceneitem_set_crop(scene_item, crop)
		else:
			print(f'item_set_crop2() Item no existe: "{item_name}"')
	
	# obs.obs_source_release(scene_source)
	# obs.obs_source_release(group_scene)

	
def sprite_covid(unused_addr, scene_name, item_name, pos_x):
	c4(f'sprite_covid({scene_name}, {item_name}, {pos_x})')
	d = [256,256]
	q = [16, 1]
	left =   pos_x * d[0]
	right = (q[0] - 1 - pos_x) * d[0]
	item_set_crop(None, scene_name, item_name, left, right, None, None)

# Cambia de sprite de un item
def item_set_sprite(unused_addr, scene_name='', item_name='', img_size=[], grid=[], pos=[]):
	c4(f'sprite_(scene_name="{scene_name}", item_name="{item_name}", img_size={img_size}, grid={grid}, pos={pos})')
	sprite_size = [img_size[0] / grid[0], img_size[1] / grid[1]]
	
	left   = pos[0] * sprite_size[0]
	top    = pos[1] * sprite_size[1]
	right  = (grid[0] - 1 - pos[0]) * sprite_size[0]
	bottom = (grid[1] - 1 - pos[1]) * sprite_size[1]
	item_set_crop(None, scene_name, item_name, left, right, top, bottom)

# Cambia de sprite de un item dentro de un grupo (en una escena)
def item_set_sprite2(unused_addr, scene_name='', group_name='', item_name='', img_size=[], grid=[], pos=[]):
	c4(f'sprite_(scene_name="{scene_name}", item_name="{item_name}", img_size={img_size}, grid={grid}, pos={pos})')
	sprite_size = [img_size[0] / grid[0], img_size[1] / grid[1]]
	
	left   = pos[0] * sprite_size[0]
	top    = pos[1] * sprite_size[1]
	right  = (grid[0] - 1 - pos[0]) * sprite_size[0]
	bottom = (grid[1] - 1 - pos[1]) * sprite_size[1]
	item_set_crop2(None, scene_name, group_name, item_name, left, right, top, bottom)

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
	reference=False,
	private=False):
	
	c2(f'item_duplicate(fromScene_name="{fromScene_name}", toScene_name="{toScene_name}",')
	c2(f'	item_name="{item_name}", new_item_name="{new_item_name}",')
	c2(f'	copy_info_crop={copy_info_crop}, visible={visible}, reference={reference})')

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

	with source_list_auto_release(scenes_list1):
		with ExitStack() as stack:

			if item_name.startswith('id:'):
				scene_item = obs.obs_scene_find_sceneitem_by_id(fromScene, int(item_name[3:]))
			else:
				scene_item = obs.obs_scene_find_source(fromScene, item_name)
		
			if scene_item:

				if tobool(copy_info_crop):
					info = obs.obs_transform_info()
					crop = obs.obs_sceneitem_crop()
					obs.obs_sceneitem_get_info(scene_item, info)
					obs.obs_sceneitem_get_crop(scene_item, crop)

				# Lo elije como source
				source = obs.obs_sceneitem_get_source(scene_item)

				if tobool(reference):
					# Crea item tomando como referencia el source
					new_item = obs.obs_scene_add(toScene, source)
				else:

					# Duplica
					if not private:
						duplicated = obs.obs_source_duplicate(source, new_item_name, False)
						new_item = obs.obs_scene_add(toScene, duplicated)
						obs.obs_source_release(duplicated)
					else:
						# globals()[item_name] = obs.obs_source_duplicate(source, new_item_name, True)
						# new_item = obs.obs_scene_add(toScene, globals()[item_name])
						duplicated = obs.obs_source_duplicate(source, new_item_name, True)
						new_item = obs.obs_scene_add(toScene, duplicated)
						obs.obs_source_release(duplicated)

				if tobool(copy_info_crop):
					obs.obs_sceneitem_set_info(new_item, info)
					obs.obs_sceneitem_set_crop(new_item, crop)

				if tobool(visible) != None:
					obs.obs_sceneitem_set_visible(new_item, tobool(visible))

				obs.obs_scene_release(fromScene)
				obs.obs_scene_release(toScene)

				item_id = obs.obs_sceneitem_get_id(new_item)
				return item_id
			else:
				print(f'item_duplicate() Item no existe: "{item_name}"')

def item_create_group(unused_addr, scene_name, group_name, items=[], visible=True):
	c2(f'item_create_group(scene_name="{scene_name}", group_name="{group_name}", items="{items}", visible={visible})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_create_group() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		# TO DO
		# scene_items = []
		# new_group = obs.obs_scene_insert_group(scene, group_name, scene_items, len(scene_items))
		new_group = obs.obs_scene_insert_group(scene, group_name, None, 0)

		for item_name in items:
			if item_name.startswith('id:'): 
				scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
				# with item_auto_release(scene_item):
				obs.obs_sceneitem_group_add_item(new_group, scene_item)
			else:
				scene_item = obs.obs_scene_find_source(scene, item_name)
				# with item_auto_release(scene_item):
				obs.obs_sceneitem_group_add_item(new_group, scene_item)

		group_id = obs.obs_sceneitem_get_id(new_group)
		return group_id

def item_create_image(unused_addr, 
	scene_name, 
	item_name, 
	image_file, 
	crop_lrtb=[], 
	pos_xy=[], 
	scl_xy=[], 
	alignment=None, 
	visible=None, 
	locked=None,
	private=False):
	
	c2(f'item_create_image(scene_name="{scene_name}", item_name="{item_name}", image_file="{image_file}",')
	c2(f'    crop_lrtb={crop_lrtb}, pos_xy={pos_xy}, scl_xy={scl_xy}, alignment={alignment}, visible={visible}, private={private})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_create_image() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		with ExitStack() as stack:
			newSettings = stack.enter_context(new_settings())
			obs.obs_data_set_string(newSettings, "file", image_file)
			
			if not private:
				source = stack.enter_context(source_creation("image_source", item_name, newSettings))
				new_item = obs.obs_scene_add(scene, source)
			else:
				globals()[item_name] = obs.obs_source_create_private("image_source", item_name, newSettings)
				new_item = obs.obs_scene_add(scene, globals()[item_name])
			
			obs.obs_sceneitem_set_visible(new_item, False)
			if len(crop_lrtb) == 4:
				crop = obs.obs_sceneitem_crop()
				obs.obs_sceneitem_get_crop(new_item, crop)
				crop.left, crop.right  = int(crop_lrtb[0]), int(crop_lrtb[1])
				crop.top,  crop.bottom = int(crop_lrtb[2]), int(crop_lrtb[3])
				obs.obs_sceneitem_set_crop(new_item, crop)
			if len(pos_xy) == 2:
				new_pos = obs.vec2()
				new_pos.x, new_pos.y = int(pos_xy[0]), int(pos_xy[1])
				obs.obs_sceneitem_set_pos(new_item, new_pos)
			if len(scl_xy) == 2:
				new_scale = obs.vec2()	
				new_scale.x, new_scale.y = scl_xy[0], scl_xy[1]
				obs.obs_sceneitem_set_scale(new_item, new_scale)
			if alignment != None:
				obs.obs_sceneitem_set_alignment(new_item, alignment)
			if visible in [None, True]:
				obs.obs_sceneitem_set_visible(new_item, True)
			if locked != None:
				obs.obs_sceneitem_set_locked(new_item, bool(locked))
			
			item_id = obs.obs_sceneitem_get_id(new_item)
			c4(item_id)
			return item_id

def item_create_video(unused_addr, 
	scene_name, 
	item_name, 
	video_file,
	linear_alpha=True, 
	crop_lrtb=[], 
	pos_xy=[], 
	scl_xy=[], 
	alignment=None, 
	visible=None, 
	locked=None,
	private=False):
	
	c2(f'item_create_image(scene_name="{scene_name}", item_name="{item_name}", video_file="{video_file}",')
	c2(f'    crop_lrtb={crop_lrtb}, pos_xy={pos_xy}, scl_xy={scl_xy}, alignment={alignment}, visible={visible}, private={private})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_create_image() Scene no existe: "{scene_name}"')
		return
	
	linear_alpha = tobool(linear_alpha)
	crop_lrtb =    tolist(crop_lrtb)
	pos_xy =       tolist(pos_xy)
	scl_xy =       tolist(scl_xy)
	alignment =    tobool(alignment)
	visible =      tobool(visible)
	locked =       tobool(locked)
	private =      tobool(private)

	with source_list_auto_release(scenes_list):
		with ExitStack() as stack:
			newSettings = stack.enter_context(new_settings())
			obs.obs_data_set_string(newSettings, "local_file",        video_file)
			obs.obs_data_set_bool(newSettings, "linear_alpha",        linear_alpha)
			obs.obs_data_set_bool(newSettings, "is_local_file",       True)
			obs.obs_data_set_bool(newSettings, "clear_on_media_end",  True)
			obs.obs_data_set_bool(newSettings, "looping",             True)
			obs.obs_data_set_bool(newSettings, "restart_on_activate", True)
			obs.obs_data_set_int(newSettings, "speed_percent",        100)
			obs.obs_data_set_int(newSettings, "buffering_mb",         2)
			obs.obs_data_set_int(newSettings, "reconnect_delay_sec",  10)
			
			if not private:
				source = stack.enter_context(source_creation("ffmpeg_source", item_name, newSettings))
				new_item = obs.obs_scene_add(scene, source)
			else:
				globals()[item_name] = obs.obs_source_create_private("ffmpeg_source", item_name, newSettings)
				new_item = obs.obs_scene_add(scene, globals()[item_name])
			
			obs.obs_sceneitem_set_visible(new_item, False)
			if len(crop_lrtb) == 4:
				crop = obs.obs_sceneitem_crop()
				obs.obs_sceneitem_get_crop(new_item, crop)
				crop.left, crop.right  = int(crop_lrtb[0]), int(crop_lrtb[1])
				crop.top,  crop.bottom = int(crop_lrtb[2]), int(crop_lrtb[3])
				obs.obs_sceneitem_set_crop(new_item, crop)
			if len(pos_xy) == 2:
				new_pos = obs.vec2()
				new_pos.x, new_pos.y = int(pos_xy[0]), int(pos_xy[1])
				obs.obs_sceneitem_set_pos(new_item, new_pos)
			if len(scl_xy) == 2:
				new_scale = obs.vec2()	
				new_scale.x, new_scale.y = scl_xy[0], scl_xy[1]
				obs.obs_sceneitem_set_scale(new_item, new_scale)
			if alignment != None:
				obs.obs_sceneitem_set_alignment(new_item, alignment)
			if visible in [None, True]:
				obs.obs_sceneitem_set_visible(new_item, True)
			if locked != None:
				obs.obs_sceneitem_set_locked(new_item, bool(locked))
			
			item_id = obs.obs_sceneitem_get_id(new_item)
			c4(item_id)
			return item_id

def item_create_text(unused_addr, 
	scene_name, 
	item_name, 
	text='', 
	face='Sans Serif', 
	size=28, 
	color1=None, 
	color2=None,
	outline=None,
	drop_shadow=None,
	pos_xy=[], 
	scl_xy=[], 
	visible=None,
	locked=None,
	private=False):
	
	c2(f'item_create_text(scene_name="{scene_name}", item_name="{item_name}", text="{text}, face="{face}", size="{size}", ')
	c2(f'   color1="{color1}", color2="{color2}, outline="{outline}", drop_shadow="{drop_shadow}",')
	c2(f'   pos_xy={pos_xy}, scl_xy={scl_xy}, visible={visible}, locked={locked}, private={private})')


	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_create_text() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):

		with ExitStack() as stack:

			newSettings = stack.enter_context(new_settings())
			obs.obs_data_set_string(newSettings, 'text', text)
			
			if color1 != None: 	    obs.obs_data_set_int(newSettings,  'color1', rgba2decimal(color1))
			if color2 != None:	    obs.obs_data_set_int(newSettings,  'color2', rgba2decimal(color2))
			if drop_shadow != None:	obs.obs_data_set_bool(newSettings, 'drop_shadow', bool(drop_shadow))
			if outline != None:     obs.obs_data_set_bool(newSettings, 'outline',     bool(outline))

			item = stack.enter_context(new_settings())
			obs.obs_data_set_string(item, "face", face)
			obs.obs_data_set_int   (item, "flags", 0)
			obs.obs_data_set_double(item, "size", size)
			obs.obs_data_set_string(item, "style", '')
			obs.obs_data_set_obj(newSettings, 'font', item)

			if not private:
				source = stack.enter_context(source_creation("text_ft2_source", item_name, newSettings))
				new_item = obs.obs_scene_add(scene, source)
			else:
				globals()[item_name] = obs.obs_source_create_private("text_ft2_source", item_name, newSettings)
				new_item = obs.obs_scene_add(scene, globals()[item_name])

			if len(pos_xy) == 2:
				new_pos = obs.vec2()
				new_pos.x, new_pos.y = int(pos_xy[0]), int(pos_xy[1])
				obs.obs_sceneitem_set_pos(new_item, new_pos)
			if len(scl_xy) == 2:
				new_scale = obs.vec2()	
				new_scale.x, new_scale.y = scl_xy[0], scl_xy[1]
				obs.obs_sceneitem_set_scale(new_item, new_scale)
			if visible != None:
				obs.obs_sceneitem_set_visible(new_item, bool(visible))
			if locked != None:
				obs.obs_sceneitem_set_locked(new_item, bool(locked))

			item_id = obs.obs_sceneitem_get_id(new_item)
			c4(item_id)
			return item_id

def item_create_box(unused_addr, 
	scene_name,
	item_name, 
	pos_x=0,
	pos_y=0, 
	width=100,
	height=100, 
	rgb=[1,1,1],
	opacity=1,
	alignment=0,
	private=True,
	):
	
	c2(f'item_create_box(scene_name="{scene_name}", item_name="{item_name}", rgb={rgb}, opacity={opacity}, alignment={alignment})')

	rgb = tolist(rgb)
	color_decimal = rgba2decimal([rgb[0], rgb[1], rgb[2], 1])

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_create_debug_box() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):

		with ExitStack() as stack:

			sourceSettings = stack.enter_context(new_settings())
			obs.obs_data_set_int(sourceSettings, "color", color_decimal)
			obs.obs_data_set_int(sourceSettings, "width", int(width))
			obs.obs_data_set_int(sourceSettings, "height", int(height))

			# Aplica filtro color_source para opacidad
			filterSettings = stack.enter_context(new_settings())
			obs.obs_data_set_double(filterSettings, "opacity", opacity)
			source_color = obs.obs_source_create_private("color_filter_v2", "Color Correction", filterSettings)

			if not private:
				source = stack.enter_context(source_creation("color_source", item_name, sourceSettings))
				new_item = obs.obs_scene_add(scene, source)
				obs.obs_source_filter_add(source, source_color)
			else:
				globals()[item_name] = obs.obs_source_create_private("color_source", item_name, sourceSettings)
				new_item = obs.obs_scene_add(scene, globals()[item_name])
				obs.obs_source_filter_add(globals()[item_name], source_color)

		# scene_item = obs.obs_scene_find_source(scene, item_name)
		new_pos = obs.vec2()
		new_pos.x, new_pos.y = pos_x, pos_y
		obs.obs_sceneitem_set_pos(new_item, new_pos)
		obs.obs_sceneitem_set_alignment(new_item, alignment)

		item_id = obs.obs_sceneitem_get_id(new_item)
		return item_id

def item_dupli_set_prop(unused_addr, 
	fromScene_name, 
	toScene_name, 
	item_name, 
	new_item_name=None, 
	reference=False,
	pos_x=None, pos_y=None, 
	scl_x=None, scl_y=None, 
	rot=None, alignment=None, visible=None):

	item_id = item_duplicate(None, 
		fromScene_name=fromScene_name, 
		toScene_name=toScene_name,
		item_name=item_name, 
		new_item_name=new_item_name, 
		visible=False, 
		reference=reference)
	
	item_set_transform(None, 
		scene_name=toScene_name, 
		item_name=new_item_name,
		pos_x=pos_x, pos_y=pos_y, 
		scl_x=scl_x, scl_y=scl_y,
		rot=rot, alignment=alignment, 
		visible=visible)
	
	return item_id	

def item_create_image_set_prop(unused_addr, 
	scene_name, 
	item_name, 
	image_file, 
	pos_x=None, pos_y=None, 
	scl_x=None, scl_y=None, 
	rot=None, alignment=None, visible=None):

	item_id = item_create_image(None, scene_name=scene_name,
		item_name=item_name, 
		image_file=image_file,
		visible=False)
	
	item_set_transform(None, scene_name=scene_name, 
		item_name={'id': item_id},
		pos_x=pos_x, pos_y=pos_y, 
		scl_x=scl_x, scl_y=scl_y,
		rot=rot, alignment=alignment, visible=visible)
	
	return item_id	

# devuelve una lista con dicts con 'index', 'name', 'scene_item'(Swig Object) e 'id' c/u
def get_order(scene_items=None):
	order = list()
	for i, s in enumerate(scene_items):
		source  = obs.obs_sceneitem_get_source(s)
		name    = obs.obs_source_get_name(source)
		item_id = obs.obs_sceneitem_get_id(s)
		order.append({"index": i, "name": name, "scene_item": s, 'id': item_id})
	return order

def item_swap_order_index(unused_addr,scene_name, item_name1, item_name2):
	c2(f'item_swap_order_index(scene_name={scene_name}, item_name1={item_name1}, item_name2={item_name2})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_swap_order_index() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		with scene_enum(scene) as scene_items:

			# order es una lista con {"index": i, "name": name, "scene_item": s, 'id': item_id}
			order = get_order(scene_items)
			for dic in order:
				if   (item_name1.startswith('id:') and int(item_name1[3:]) == dic['id']) or item_name1 == dic['name']:
					item_pos1 = dic['index']
				elif (item_name2.startswith('id:') and int(item_name2[3:]) == dic['id']) or item_name2 == dic['name']:
					item_pos2 = dic['index']
			
			if 'item_pos1' not in locals() or 'item_pos2' not in locals():
				consola(f'No existe {item_name1} o {item_name2}.')
				return
			
			# consola(order, c.debug)
			# for i in sorted(order, key=lambda item: item['index'], reverse=True):
			# 	consola(f"{i['index']}: {i['name']}", c.violeta)
			
			# print([item_pos1, order[item_pos1]["name"]])
			# print([item_pos2, order[item_pos2]["name"]])
			
			obs.obs_sceneitem_set_order_position(order[item_pos1]["scene_item"], item_pos2)
			obs.obs_sceneitem_set_order_position(order[item_pos2]["scene_item"], item_pos1)

			
			# order[item_pos1]["index"], order[item_pos2]["index"] = order[item_pos2]["index"], order[item_pos1]["index"]
			# for s in sorted(order, key=lambda i: i["index"]):
			# 	obs.obs_sceneitem_set_order_position(s["scene_item"], s["index"])

# Devuelve el orden de items en la escena.
def items_get_order(unused_addr, scene_name):
	c2(f'items_get_order(scene_name={scene_name})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_get_order_index() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		with scene_enum(scene) as scene_items:
			order = get_order(scene_items)
			return order

# Devuelve la posición de orden en la lista de items en la escena.
def item_get_order_index(unused_addr, scene_name, item_name):
	c2(f'item_get_order_index(scene_name={scene_name}, item_name={item_name})')

	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_get_order_index() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		with scene_enum(scene) as scene_items:
			order = get_order(scene_items)
			for i, dic in enumerate(order):

				if type(item_name) == str or (type(item_name) == dict and 'id' in item_name):
					if dic['name'] == item_name:
						return i
				elif type(item_name) == dict and 'id' in item_name:
					if dic['id'] == item_name['id']:
						return i
			
			print(f'item_get_order_index() Item no existe: "{item_name}"')

# Mueve de lugar. 0 y positivos de abajo hacia arriba. Negativos, de arriba hacia abajo.
def item_set_order_index(unused_addr, scene_name, item_name, index=None):
	c2(f'item_set_order_index(scene_name="{scene_name}", item_name="{item_name}")')
		
	scene, scenes_list = get_scene_context(scene_name)
	if not scene:
		obs.source_list_release(scenes_list)
		print(f'item_set_order_index() Scene no existe: "{scene_name}"')
		return

	with source_list_auto_release(scenes_list):
		if item_name.startswith('id:'): scene_item = obs.obs_scene_find_sceneitem_by_id(scene, int(item_name[3:]))
		else: scene_item = obs.obs_scene_find_source(scene, item_name)

		if scene_item:
			if index >= 0:
				obs.obs_sceneitem_set_order_position(scene_item, int(index))
			elif index < 0:
				with scene_enum(scene) as scene_items:
					order = len(get_order(scene_items))
					obs.obs_sceneitem_set_order_position(scene_item, int(order + 1 + index))
		else:
			print(f'item_set_order_index() Item no existe: "{item_name}"')

zoom_window = ''
def source_capture_window(unused_addr, source_name, que, restore_name=None):
	global zoom_window

	source = obs.obs_get_source_by_name(source_name)
	source_name = obs.obs_source_get_name(source)
	consola(f'source_name: {source_name}', c.debug)

	if source:

		if que == 'backup':

			oldSettings = obs.obs_source_get_settings(source)
			zoom_window = obs.obs_data_get_string(oldSettings, 'capture_window')
			print(zoom_window)
			# client.send_message("/source_capture_window", zoom_window)
			obs.obs_data_release(oldSettings)

		elif que == 'restore':
			with ExitStack() as stack:
				newSettings = stack.enter_context(new_settings())
				# newSettings = obs.obs_data_create()
				obs.obs_data_set_string(newSettings, "capture_window", restore_name)
				obs.obs_source_update(source, newSettings)
				# obs.obs_data_release(newSettings)

		else:
			print('Solo recibe backup o restore.')
		
		obs.obs_source_release(source)

# TODO
def monitorFix():
	pass
# 	lista = ws.call(requests.GetSourcesList())
# 	for i in lista.getSources():
# 		o = i['name']
# 		actual = ws.call(requests.GetAudioMonitorType(o)).getMonitorType()
# 		print(o, actual)
# 		if actual == 'monitorAndOutput':
# 			ws.call(requests.SetAudioMonitorType(o, 'none'))
# 			ws.call(requests.SetAudioMonitorType(o, 'monitorAndOutput'))

def pre_cuanto_falta(momento):
	t1 = datetime.datetime.now().replace(hour=int(momento.split(':')[0]), minute=int(momento.split(':')[1]), second=0, microsecond=0)
	t2 = datetime.datetime.now()
	_time = str(t1 - t2)
	c3(_time)
	if not _time.startswith('-1 day'):
		try:
			h, m, s, _ = _time.replace('.', ':').split(':')
			if h == m == '0':
				if s == '1':                new_time = 'Falta '  + str(int(s)) + ' segundo'
				else:                       new_time = 'Faltan ' + str(int(s)) + ' segundos'
			elif h == '0' and m != '0':
				if m == '1':                new_time = 'Faltan ' + str(int(m)) + ' minuto y '
				else:                       new_time = 'Faltan ' + str(int(m)) + ' minutos y '
				if s == '1':                new_time = new_time  + str(int(s)) + ' segundo'
				else:                       new_time = new_time  + str(int(s)) + ' segundos'	
			elif h != '0':                  new_time = '>1hora'
				
			if new_time == '>1hora':        _time = 'Falta mas de una hora para que empiece.'
			elif new_time != '':            _time = new_time + ' para que empiece...'

		except:
			print('Revisa bien el horario de comienzo...')
			return
	else:                                   _time = '¡Ya comenzamos!'
	_time =  ' ' * int((51 - len(_time)) / 1.5) + _time
	source_set_text(None, 'pre-countdown', _time)

def crea_grilla(scene, mitad, lienzo, elem_width, elem_height, verbose):
	grilla = list()
	if not mitad:
		casilleros_x = int((sd.base_width   * lienzo) / elem_width)
		casilleros_y = int((sd.base_height  * lienzo) / elem_height)
		espacio_pre_x = (sd.base_width  - (casilleros_x * elem_width))  / 2
		espacio_pre_y = (sd.base_height - (casilleros_y * elem_height)) / 2
	
	else:
		casilleros_x = int((sd.base_height * lienzo) / elem_width)
		casilleros_y = int((sd.base_height * lienzo) / elem_height)
		espacio_pre_x  = (sd.base_width - sd.base_height) / 2
		espacio_pre_x += (sd.base_height - (casilleros_x * elem_width))  / 2
		espacio_pre_y  = (sd.base_height - (casilleros_y * elem_height)) / 2

	c2(f'casilleros_x: {casilleros_x}, casilleros_y: {casilleros_y}')

	# Crea grilla
	grilla_size = {'width': casilleros_x * elem_width, 'height': casilleros_y * elem_height}
	c2(f'grilla_size: {grilla_size}')
	for i in range(casilleros_y):
		grilla.append([])
		for o in range(casilleros_x):
			pos_x = o * elem_width  + (sd.base_width - grilla_size['width'])/2   + elem_width/2
			pos_y = i * elem_height + (sd.base_height - grilla_size['height'])/2 + elem_height/2
			if verbose[3]:
				bolita_id = item_create_image(None, 
					scene_name=scene,
					image_file=bolita_image,
					item_name='bolita',
					visible=True,
					pos_xy=[pos_x, pos_y],
					private=True)
				grilla[i].append({'x': pos_x, 'y': pos_y, 'id': bolita_id})
				time.sleep(.05)
			else:
				grilla[i].append({'x': pos_x, 'y': pos_y})
	
	return [grilla, casilleros_x, casilleros_y]

def files_in_path(path, extension, devuelve='lista'):
	if devuelve.startswith('l'):   return sorted([f for f in listdir(path) if isfile(join(path, f)) and f.split('.')[-1] == extension])
	elif devuelve.startswith('d'): return sorted([{'extension': f.split('.')[-1], 'file': f, 'path': f'{path}/{f}'} for f in listdir(path) if isfile(f'{path}/{f}') and f.split('.')[-1] == extension], key=lambda k: k['file'])

def images_in_path(path, *extensions):
	return sorted([{'extension': f.split('.')[-1], 'file': f, 'path': f'{path}/{f}', 'size': list(Image.open(f'{path}/{f}').size)} for f in listdir(path) if isfile(f'{path}/{f}') and f.split('.')[-1] in list(extensions)], key=lambda k: k['file']) 

def dirs_in_path(path, devuelve='lista'):
	if devuelve.startswith('l'):   return sorted([f for f in listdir(path) if isdir(f'{path}/{f}')])
	elif devuelve.startswith('d'): return sorted([{'dir': f, 'cantidad': len(listdir(f'{path}/{f}'))} for f in listdir(path) if isdir(f'{path}/{f}')], key=lambda k: k['dir']) 

def testdebug():
	consola(f'Active threads: {threading.active_count()}', c.violeta)
	for i in threading.enumerate():
		consola(i.name)
	# print(globals())
	# with open('/home/mario/globals.txt', 'w') as file:
	# 	file.write(str(globals()))
