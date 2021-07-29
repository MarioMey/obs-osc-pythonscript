#!/usr/bin/env python3

# Otro: https://sites.google.com/site/xiangyangsite/home/technical-tips/software-development/python/python-readline-completions

from pythonosc import udp_client
import argparse, readline, copy

words = [
'true',
'True',
'false',
'False',
'camSettings',

'scene_change',
'system_',
'item_set_visible',        
'item_remove',             
'item_tween',              
'item_duplicate',          
'item_reference',          
'item_get_transform',      
'item_set_transform',      
'item_set_pos',            
'item_set_scl',            
'item_set_rot',            
'item_set_alignment',      
'item_set_visible',        
'item_set_crop',           
'item_get_order_index',    
'item_set_order_index',    
'item_swap_order_index',   
'item_set_private_setting',
'item_set_scl_filter',

'pos',
'scl',
'rot',
'transform',
'to_pos',
'to_scl',
'to_rot',
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
'source_filter_set_enabled',
'source_filter_set_value',  
'source_filter_get_settings',
'source_set_setting',       
'source_set_bri_sat_hue',   
'source_set_hue',           
'source_set_lut_file',      
'source_capture_window',    
'source_get_settings',
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
					# Y terminamos de 'saltearnos' resultados terminamos
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
				if e in ['False', 'false']:
					inpu_[num] = False
				elif e in ['True', 'true']:
					inpu_[num] = True
			# print(addr, [*inpu])
			client.send_message(addr, [*inpu_])


if __name__ == '__main__':
	parser = argparse.ArgumentParser()
	parser.add_argument('--ip', default='127.0.0.1', 	   help='The ip of the OSC server')
	parser.add_argument('--port', type=int, default=10008, help='The port the OSC server is listening on')
	args = parser.parse_args()
	client = udp_client.SimpleUDPClient(args.ip, args.port)
	
	main_loop()

