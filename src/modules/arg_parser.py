import sys

arg_debug = False
arg_cam = False

for arg in sys.argv[1:]:
  if arg == "--debug":
    arg_debug = True 
  elif arg == "--cam":
    arg_cam = True
