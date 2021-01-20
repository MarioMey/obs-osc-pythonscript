## OBS-OSC-PythonScript
OBS Python scripts that allows to receive/send OSC messages from/to OBS and from/to another OSC sending capable software, like PureData, MobMuPlat, TouchOSC, etc.

It is just Python and it doesn't use websockets.

### Examples:
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

/item_tween to_pos scene item to_pos_x to_pos_y duration
/item_tween to_scl scene item to_scl_x to_scl_y duration
/item_tween to_rot scene item to_rot duration
/item_tween to_tranform scene item to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration

/item_tween from_to_pos scene item from_pos_x from_pos_y to_pos_x to_pos_y duration
/item_tween from_to_scl scene item from_scl_x from_scl_y to_scl_x to_scl_y duration
/item_tween from_to_rot scene item from_rotation to_rotation duration
/item_tween fromto_tranform scene item from_pos_x from_pos_y from_scl_x from_scl_y from_rotation to_pos_x to_pos_y to_scl_x to_scl_y to_rot duration
```
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
