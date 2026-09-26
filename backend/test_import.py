import sys
import traceback

sys.path.insert(0, '.')

try:
    import main
    print('OK')
except Exception as e:
    traceback.print_exc()
    sys.exit(1)
