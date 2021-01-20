## OBS-OSC-PythonScript
OBS Python scripts that allows to receive/send OSC messages from/to OBS and from/to another OSC sending capable software, like PureData, MobMuPlat, TouchOSC, etc.

It is based on OBS script [OSC Sender for OBS](https://obsproject.com/forum/threads/osc-sender-for-obs.100618/), but this time, it can receive messages (original doesn't). It uses [python-osc](https://github.com/attwad/python-osc/ "Github attwad/python-osc") and it neither use [obs-websockets](https://github.com/Palakis/obs-websocket "Github Palakis/obs-websocket") nor [obs-websockets-py](https://github.com/Elektordi/obs-websocket-py "Github Elektordi/obs-websocket-py"). 

**IMPORTANT**: pythonosc server code needs Python 3.7 and OBS is originally done in 3.6. OBS has to be started with `LD_PRELOAD=/<path>/libpython3.8.so`. It is explained in this [Pull Request comment](https://github.com/obsproject/obs-studio/pull/3335#issuecomment-760255757)

### Examples of receiving OSC messages (Server)
The script opens a port in the computer and listen to incoming messages from another software. Messages are with 1 level address and some arguments, depend on the type of command. For example, to locate a source called "ball" in "main" scene, to x: 960 x: 540 (middle of FullHD), message is:

_/item_set_pos main ball 960 540_

Another example: to make the same ball move to that point, from where it was, with a tween of 2 seconds and an ease type of 'outQuad':

_/item_tween to_pos main ball 960 540 2000 outQuad_

### List of commands
#### Scenes: changing.
`/scene_change scene`
#### Items: position, scale, rotation, visibility, crop, alignment, delete, duplication, reference, etc.
```
/item_set_pos scene item pos_x pos_y
/item_set_scl scene item scl_x scl_y
/item_set_rot scene item rotation
/item_set_transform scene item pos_x pos_y scl_x scl_y rotation

/item_set_visible scene item visibility(bool)
/item_delete scene item
/item_reference from_scene to_scene item
/item_duplicate from_scene to_scene item
/item_set_alignment scene item alignment(int)
/item_set_crop scene item left right top bottom

/item_tween to_pos scene item to_pos_x to_pos_y duration ease_type
/item_tween to_scl scene item to_scl_x to_scl_y duration ease_type
/item_tween to_rot scene item to_rot duration ease_type
/item_tween to_tranform scene item to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration ease_type

/item_tween from_to_pos scene item from_pos_x from_pos_y to_pos_x to_pos_y duration ease_type
/item_tween from_to_scl scene item from_scl_x from_scl_y to_scl_x to_scl_y duration ease_type
/item_tween from_to_rot scene item from_rotation to_rotation duration ease_type
/item_tween fromto_tranform scene item from_pos_x from_pos_y from_scl_x from_scl_y from_rotation to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration ease_type
```
`ease_type` argument is optional. It could be `linear` (default), `inQuad`, `outQuad`, `inOutQuad`, `inCubic`, `outCubic`, `inOutCubic`.

#### Sources:
```
/source_set_image_file source filename(string)
/source_set_volume  source volume(float)
/source_set_opacity source opacity(int)
/source_filter_set_enabled source filter enabled(bool)
/source_filter_set_value source filter slider value(int)
/source_set_bri_sat_hue source bri(int) sat(int) hue(int)
/source_set_hue_shift source hue_shift(int)
/source_set_text source text(string)
```

### Examples of sending OSC messages (Client)
Not yet developed or documented. The only part that it is done is what OSC Sender for OBS script has.
