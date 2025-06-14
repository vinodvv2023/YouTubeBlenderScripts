import bpy
import sys

argv = sys.argv
argv = argv[argv.index("--") + 1:]
pos = argv[0].lower()

for strip in bpy.context.scene.sequence_editor.sequences_all:
    if strip.type == 'TEXT':
        if pos == "top":
            strip.location[1] = 0.9
        elif pos == "bottom":
            strip.location[1] = 0.1
        else:
            try:
                y = float(pos)
                strip.location[1] = y
            except:
                pass
bpy.ops.wm.save_mainfile()
