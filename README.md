## OBS-OSC-PythonScript 0.1
OBS Python scripts that allows to receive/send OSC messages from/to OBS and from/to another OSC sending capable software, like PureData, MobMuPlat, TouchOSC, etc.

OBS-OSC-PythonScript in **not yet approved** [OBS Python Resource](https://obsproject.com/forum/resources/obs-osc-pythonscript-0-1.1200/).

It is based on OBS script [OSC Sender for OBS](https://obsproject.com/forum/threads/osc-sender-for-obs.100618/), but this time, it can receive messages (original doesn't). It uses [python-osc](https://github.com/attwad/python-osc/ "Github attwad/python-osc") and it neither use [obs-websockets](https://github.com/Palakis/obs-websocket "Github Palakis/obs-websocket") nor [obs-websockets-py](https://github.com/Elektordi/obs-websocket-py "Github Elektordi/obs-websocket-py"). 

#### Requirements
- [python-osc](https://github.com/attwad/python-osc/)
- **IMPORTANT**: pythonosc server code needs Python 3.7 and OBS is originally done in 3.6. OBS has to be started with `LD_PRELOAD=/<path>/libpython3.8.so`. It is explained in this [Pull Request comment](https://github.com/obsproject/obs-studio/pull/3335#issuecomment-760255757)
- [PIL](https://pillow.readthedocs.io/en/stable/index.html) for image check (used by `/source_set_image_file`). It is not required, but you have to modify the code to take it off.

## Instructions
Load `obs_osc_pythonscript.py` in **Script**, in **Tools** menu.

#### Defaults
- Server Port: 10008 (\*)
- Client Port: 10000 (\*)
- Client IP: 127.0.0.1 (\*) 

*(\*) You can change these 3 in Configuration.*

### Examples of receiving OSC messages (Server)
The script opens a port in the computer and listen to incoming messages from another software. Messages are with 1 level address and some arguments, depend on the type of command. For example, to locate an item called "ball" in "main" scene, to x: 960 y: 540 (middle of FullHD), message is:

_/item_set_pos main ball 960 540_

Another example: to make the same ball "move" (interpolation included) from where it was to x: 960 y: 540, wait 500ms to start moving to get that location in 2000ms with an ease type of 'outQuad':

_/item_tween to_pos main ball 960 540 2000 500 outQuad_

### List of commands
#### Scenes: changing.
`/scene_change scene`
#### Items: position, scale, rotation, visibility, crop, alignment, delete, duplication, reference, etc.
```
# Change transform properties
/item_set_pos       scene item pos_x pos_y
/item_set_scl       scene item scl_x scl_y
/item_set_rot       scene item rotation
/item_set_transform scene item pos_x pos_y scl_x scl_y rotation
/item_set_alignment scene item alignment(int)
/item_set_crop      scene item left right top bottom
/item_set_visible   scene item visibility(bool)
# Remove item
/item_remove        scene item
# Duplicating/referencing items
/item_reference from_scene to_scene item
/item_duplicate from_scene to_scene item
```
#### Item tween
Item position, scale and rotation interpolated transformation, with duration, delay and ease type.
- To change item properties to a new position/scale/rotation, use `to_pos`, `to_scl`, `to_rot` and `to_transform`.
- If you want to set it from an specific position/scale/rotation to a new position/scale/rotation, use `from_to_pos`, `from_to_scl`, `from_to_rot` and `from_to_transform`.
- `duration` and `delay` are in miliseconds.
- Up to `duration` is required. `delay` and `ease_type` are optionals, but it has to be in that order and `ease_type` can't be alone: if you want to send `ease_type` value, you have to send `0` as delay.
- `ease_type` could be `linear` (default), `inQuad`, `outQuad`, `inOutQuad`, `inCubic`, `outCubic` or `inOutCubic`.
```
# Only target
/item_tween to_pos       scene item to_pos_x to_pos_y duration delay ease_type
/item_tween to_scl       scene item to_scl_x to_scl_y duration delay ease_type
/item_tween to_rot       scene item to_rot duration delay ease_type
/item_tween to_transform scene item to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration delay ease_type
# Origin and target
/item_tween from_to_pos       scene item from_pos_x from_pos_y to_pos_x to_pos_y duration delay ease_type
/item_tween from_to_scl       scene item from_scl_x from_scl_y to_scl_x to_scl_y duration delay ease_type
/item_tween from_to_rot       scene item from_rotation to_rotation duration delay ease_type
/item_tween from_to_transform scene item from_pos_x from_pos_y from_scl_x from_scl_y from_rotation to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration delay ease_type
```
#### Sources:
To change a source setting, you don't have to send the scene name, as a source will change in every scene where it is referenced.
```
# Files
/source_set_image_file     source filename(string)
/source_set_video_file     source filename(string)
# Text
/source_set_text           source text(string)
/source_set_text_size      source size(int)
# Image slide
/source_set_slide_time     source time_between_slides(int)
# Audio
/source_set_volume         source volume(float)
# Filters
/source_set_opacity        source opacity(int)
/source_filter_set_enabled source filter enabled(bool)
/source_filter_set_value   source filter setting(string) value(int)
/source_set_bri_sat_hue    source bri(int) sat(int) hue(int)
/source_set_hue            source hue(int)
/source_set_lut_file       source filter lut_filename(string)
```
### Examples of sending OSC messages (Client)
Not yet developed or documented. It only sends a message to `/init` with a `1` when script loads. Also, when a source that name starts with `/` is activated, it sends a message to `/name_of_item` with a `1` as message (as **OSC Sender for OBS** script does).
