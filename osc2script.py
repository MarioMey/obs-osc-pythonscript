#!/usr/bin/env python3
"""
Envía mensajes OSC (https://github.com/MarioMey/obs-osc-pythonscript)

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
__version__ = "0.3"

from pythonosc import udp_client
import argparse, readline, copy, ast


words = [
'true',
'True',
'false',
'False',
'camSettings',

'overlay',
'main',

'amor',
'brillos',
'circulos',
'cositas',
'energia',
'explosiones',
'firulete',
'flares',
'hipnosis',
'lindos',
'plasma',

'cam-C920',
'C920',
'main',

'scene_change', 

'item_tween',
'item_set_visible',
'item_remove', 
'item_duplicate',
'item_reference',
'item_set_transform',
'item_get_transform',
'item_set_pos',
'item_set_scl',
'item_set_rot',
'item_set_alignment',
'item_set_visible',
'item_set_crop',
'item_set_size',
'item_set_scl_filter',
'item_get_order_index',
'item_set_order_index',
'item_swap_order_index',
'item_set_private_setting',
'item_create_group',
'item_create_text',
'item_create_image',
'item_create_video',
'item_create_box',

'width',
'height',
'pos',
'scl',
'rot',
'size',
'transform',
'to_pos',
'to_scl',
'to_rot',
'to_size',
'to_transform',
'to_value',
'from_to_pos',
'from_to_scl',
'from_to_rot',
'from_to_transform',
'from_value',

'source_tween',
'source_set_image_file',
'source_set_video_file',
'source_set_slide_time',
'source_set_text',
'source_set_text_size',
'source_set_volume',
'source_set_opacity',
'source_set_bri_sat_hue',
'source_set_hue',
'source_set_lut_file',
'source_set_setting',
'source_filter_set_value',
'source_filter_set_enabled',
'source_filter_get_settings',
'source_set_text',
'source_capture_window',
'source_get_settings',

'LinearInOut',
'QuadEaseInOut',
'QuadEaseIn',
'QuadEaseOut',
'CubicEaseInOut',
'CubicEaseIn',
'CubicEaseOut',
'QuarticEaseInOut',
'QuarticEaseIn',
'QuarticEaseOut',
'QuinticEaseInOut',
'QuinticEaseIn',
'QuinticEaseOut',
'SineEaseInOut',
'SineEaseIn',
'SineEaseOut',
'CircularEaseIn',
'CircularEaseInOut',
'CircularEaseOut',
'ExponentialEaseInOut',
'ExponentialEaseIn',
'ExponentialEaseOut',
'ElasticEaseIn',
'ElasticEaseInOut',
'ElasticEaseOut',
'BackEaseIn',
'BackEaseInOut',
'BackEaseOut',
'BounceEaseIn',
'BounceEaseInOut',
'BounceEaseOut',
]

def completer_for(wordlist):
	wordlist = sorted(wordlist)

	def completer(text, result_idx):
		text_len = len(text)
		# Búsqueda lineal, seguro se puede hacer mejor!
		for word in wordlist:
			if text == word[:text_len]:
				# Si matcheamos el prefijo
				if result_idx > 0:
					# Y tenemos que saltearlos lo salteamos
					result_idx -= 1
				else:
					# Y terminamos de 'saltearnos' resultados termi	namos
					return word
			elif text < word:
				# Si nos pasamos de mambo podemos terminar antes
				return None

	return completer

def init_readline():
	readline.set_completer(completer_for(words))
	readline.parse_and_bind('tab: complete')

def main_loop():
	init_readline()

	print('Envío OSC a script de OBS. ^D para salir. Ej:')
	print('/item_set_pos main C920 100 100\n')

	while True:
		while True:
			inpu = input('> ').split(' ')
			addr = inpu[0]
			inpu.pop(0)
			inpu_ = copy.deepcopy(inpu)
			for num, e in enumerate(inpu):
				# False
				if e in ['False', 'false']:
					inpu_[num] = False
				# True
				elif e in ['True', 'true']:
					inpu_[num] = True
				# Float
				elif e.translate({ord(c): None for c in '-.'}).isdigit() and '.' in e:
					inpu_[num] = float(e)
				# Int
				elif e.translate({ord(c): None for c in '-.'}).isdigit() and '.' not in e:
					inpu_[num] = int(e)
				# List
				elif type(e) == str and e.startswith('[') and e.endswith(']'):
					lista =  e[1:-1].split(',')
					isdig = []
					for i in lista:
						if i.translate({ord(c): None for c in '-.'}).isdigit():
							isdig.append(True)
					if all(isdig):
						inpu_[num] = [float(i) for i in lista]
					else:
						inpu_[num] = lista
				
			# print(addr, [*inpu])
			client.send_message(addr, [*inpu_])


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--ip', default='127.0.0.1', 	     help='The ip of the OSC server')
	parser.add_argument('--port', type=int, default=10008, help='The port the OSC server is listening on')
	args = parser.parse_args()
	client = udp_client.SimpleUDPClient(args.ip, args.port)
	
	main_loop()

