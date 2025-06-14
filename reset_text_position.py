import bpy

for strip in bpy.context.scene.sequence_editor.sequences_all:
    if strip.type == 'TEXT':
        strip.location[1] = 0.9  # Default to top
bpy.ops.wm.save_mainfile()
