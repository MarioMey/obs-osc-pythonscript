![oscobs-logo](https://user-images.githubusercontent.com/4954109/127521780-a654f51c-ec5f-450a-93af-c0c0de1ad81c.png)

# OBS-OSC-PythonScript 0.3
[OBS-OSC-PythonScript in OBS Python Resource](https://obsproject.com/forum/resources/obs-osc-pythonscript-0-1.1200/).

OBS Python scripts that allows to receive/send OSC messages from/to OBS and from/to another OSC sending capable software, like PureData, MobMuPlat, TouchOSC, etc. It uses ready-to-use functions to _do some stuff_ like manipulate sources, scenes and sceneitems. Check `obs_api.py` and `obs_tween.py`. 

It is based on [OSC Sender for OBS](https://obsproject.com/forum/threads/osc-sender-for-obs.100618/) script, but this time, it can receive messages (original one doesn't). It uses [python-osc](https://github.com/attwad/python-osc/ "Github attwad/python-osc") with no need to use `obs-websockets` nor `obs-websockets-py`.

Ease equations taken from https://github.com/semitable/easing-functions.

## Requirements
- [python-osc](https://github.com/attwad/python-osc/)
- **IMPORTANT**: pythonosc server code needs Python 3.7 and OBS is originally done in 3.6. OBS has to be started with `LD_PRELOAD=/<path>/libpython3.7.so`. It is explained in this [Pull Request comment](https://github.com/obsproject/obs-studio/pull/3335#issuecomment-760255757)
- [PIL](https://pillow.readthedocs.io/en/stable/index.html) for image check (used by `/source_set_image_file`). It is not required, but you have to modify the code to take it off.

## Instructions
Load `obs_osc_pythonscript.py` in **Script**, in **Tools** menu.

### Defaults
- Server Port: 10008 (\*)
- Client Port: 10000 (\*)
- Client IP: 127.0.0.1 (\*) 

*(\*) You can change these 3 in Configuration.*

### Examples of receiving OSC messages (Server)
The script opens a port in the computer and listen to incoming messages from another software. Messages are with 1 level address and some arguments, depend on the type of command. For example, to locate an item called "ball" in "main" scene, to x: 960 y: 540 (middle of FullHD), message is:

```
/item_set_pos main ball 960 540
```

Another example: to make the same ball "move" (interpolation included) from where it was to x: 960 y: 540, wait 500ms to start moving to get that location in 2000ms with an ease type of 'outQuad':

```
/item_tween to_pos main ball 960 540 2000 500 outQuad
```

Fade in (opacity) a source with already "Color Correction V2" filter applied. Also, the setting that will be modified **has** to be changed by hand at least once. This is the way that OBS writes setting to JSON file. Then, you can change it with /source_tween. This example takes opacity from the value it was to 0.3 in 1000ms.

```
/source_tween to_value main ball colorcorrection opacity 0.3 1000
```

### List of commands
#### Scenes: changing.
```
/scene_change scene_name
```
#### SceneItems: position, scale, size, rotation, visibility, crop, alignment, delete, duplication, reference, etc.
```
# Change transform properties
/item_set_pos       scene_name item_name pos_x pos_y
/item_set_scl       scene_name item_name scl_x scl_y
/item_set_rot       scene_name item_name rotation
/item_set_size      scene_name item_name width height
/item_set_transform scene_name item_name pos_x pos_y scl_x scl_y rotation
/item_set_alignment scene_name item_name alignment(int)
/item_set_crop      scene_name item_name left right top bottom
/item_set_visible   scene_name item_name visibility(bool)

# Remove item
/item_remove        scene sceneitem

# Duplicating/referencing SceneItems
/item_reference from_scene_name to_scene_name item_name
/item_duplicate from_scene_name to_scene_name item_name

# Not yet documented
/item_get_transform
/item_set_scl_filter
/item_get_order_index
/item_set_order_index
/item_swap_order_index
/item_set_private_setting
/item_create_group
/item_create_text
/item_create_image
/item_create_video
/item_create_box
```
## SceneItems tween
Item position, scale, size and rotation interpolated transformation, with duration, delay and ease type.
- To change SceneItem properties to a new position/scale/size/rotation, use `to_pos`, `to_scl`, `to_size`, `to_rot` and `to_transform`.
- If you want to set it from an specific position/scale/size/rotation to a new position/scale/size/rotation, use `from_to_pos`, `from_to_scl`, `from_to_size`, `from_to_rot` and `from_to_transform`.
- To change position and size at the same time, use `to_pos_size` or `from_to_pos_size`.
- `duration` and `delay` are in miliseconds.
- Values up to `duration` are required. `delay` and `ease_type` are optionals, but it has to be in that order and `ease_type` can't be alone: if you want to send `ease_type` value, you have to send `0` as delay.
- `ease_type` could be `LinearInOut` (default), `QuadEaseInOut`, `QuadEaseIn`, `QuadEaseOut`, `CubicEaseInOut`, `CubicEaseIn`, `CubicEaseOut`, `QuarticEaseInOut`, `QuarticEaseIn`, `QuarticEaseOut`, `QuinticEaseInOut`, `QuinticEaseIn`, `QuinticEaseOut`, `SineEaseInOut`, `SineEaseIn`, `SineEaseOut`, `CircularEaseIn`, `CircularEaseInOut`, `CircularEaseOut`, `ExponentialEaseInOut`, `ExponentialEaseIn`, `ExponentialEaseOut`, `ElasticEaseIn`, `ElasticEaseInOut`, `ElasticEaseOut`, `BackEaseIn`, `BackEaseInOut`, `BackEaseOut`, `BounceEaseIn`, `BounceEaseInOut` or `BounceEaseOut`.
```
# Only target
/item_tween to_pos       scene_name item_name to_pos_x to_pos_y duration delay ease_type
/item_tween to_scl       scene_name item_name to_scl_x to_scl_y duration delay ease_type
/item_tween to_size      scene_name item_name to_width to_height duration delay ease_type
/item_tween to_pos_size  scene_name item_name to_pos_x to_pos_y to_width to_height duration delay ease_type
/item_tween to_rot       scene_name item_name to_rot duration delay ease_type
/item_tween to_transform scene_name item_name to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration delay ease_type
# Origin and target
/item_tween from_to_pos       scene_name item_name from_pos_x from_pos_y to_pos_x to_pos_y duration delay ease_type
/item_tween from_to_scl       scene_name item_name from_scl_x from_scl_y to_scl_x to_scl_y duration delay ease_type
/item_tween from_to_size      scene_name item_name from_width from_height to_width to_height duration delay ease_type
/item_tween from_to_pos_size  scene_name item_name from_pos_x from_pos_y from_width from_height to_pos_x to_pos_y to_width to_height duration delay ease_type
/item_tween from_to_rot       scene_name item_name from_rotation to_rotation duration delay ease_type
/item_tween from_to_transform scene_name item_name from_pos_x from_pos_y from_scl_x from_scl_y from_rotation to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration delay ease_type
```
## Sources:
To change a source setting, you don't have to send the scene name, as a source will change in every scene where it is referenced.
```
# Files
/source_set_image_file     source_name filename(string)
/source_set_video_file     source_name filename(string)
# Text
/source_set_text           source_name text(string)
/source_set_text_size      source_name size(int)
# Image slide
/source_set_slide_time     source_name time_between_slides(int)
# Audio
/source_set_volume         source_name volume(float)
# Filters
/source_set_opacity        source_name opacity(int)
/source_filter_set_enabled source_name filter enabled(bool)
/source_filter_set_value   source_name filter setting(string) value(int)
/source_set_bri_sat_hue    source_name bri(int) sat(int) hue(int)
/source_set_hue            source_name hue(int)
/source_set_lut_file       source_name filter lut_filename(string)

# Not yet docummented
/source_get_settings
/source_set_setting
/source_filter_set_value
/source_filter_set_enabled
/source_filter_get_settings
/source_capture_window
```
## Sources tween:
For the moment, it can change a value of a setting of a filter of a source. For example: opacity.
```
/source_tween to_value source_name filter_name setting to_value duration delay ease_type
/source_tween from_to_value source_name filter_name setting from_value to_value duration delay ease_type
```

## Examples of sending OSC messages (Client)
Not yet developed or documented. It only sends a message to `/init` with a `1` when script loads. Also, when a source that name starts with `/` is activated, it sends a message to `/name_of_item` with a `1` as message (as **OSC Sender for OBS** script does).

# TEST
You can use osc2script.py to send OSC messages to the script. It has a list of preset words to use Tab key to autocomplete. Just write something like: 
```
mario@debian:~$ python3.7 osc2script.py
Envío OSC a script de OBS. ^D para salir. Ej:
/item_set_pos main C920 100 100

> /source_tween value image_source color_correction opacity 1 1000
```
