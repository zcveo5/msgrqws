import os
import subprocess
import sys

os.environ['__LOW_LAUNCHER'] = 'launcher.pyw'
subprocess.run([sys.executable, 'loader.py'] + sys.argv[1::])
print('ex')