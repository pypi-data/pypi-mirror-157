import os
import platform
import sys
from JS_py.Build.Buildtools import finalize, build
import shutil
pl = platform.system()
args = sys.argv
if args[1] == 'build':
    if os.path.splitext(__file__)[1] != '.bin' and pl == 'Linux':
        #print('\033[0;91mWarning: Use ./JS.py/m.bin for faster times.')
        pass

    if args[2].startswith('./'):
        t = os.getcwd()+args[2].replace('./','/')
    else:
        t = args[2]
    if not t.endswith('.pyjs'):
        print('Warning: Chosen file does not end with .pyjs')
    print('\033[0;37m')
    print('\rPrepraring for build...',flush=True, end="")
    p = os.path.dirname(t)+'/'+os.path.basename(t)+'.build/'
    os.mkdir(p)
    os.mkdir(os.path.dirname(t)+'/'+os.path.basename(t)+'.build/cache')
    with open(p+'parse.log', 'w'):
        pass
    with open(p+'build.log', 'w'):
        pass
    print('\rPrepraring for build... Done')
    print('\rBuilding:')
    build(t)
    print('\rFinalizing...',flush=True, end="")
    finalize(p, sys.argv, os.path.basename(t))
    print('\rFinalizing... Done')
    print('\rBuild complete')
    if '-b' in args[3:]:
        shutil.rmtree(p)
    else:
        print('Build dir kept.')
    print('JS built')
elif args[1] == "help":
    help = """
    * build <path> <any: -b -o>
    \tpath: the file path to the file you want to build.
    \tb: don't keep the build files.
    \to: build the debug file outside the build files.
    """
    print(help)
