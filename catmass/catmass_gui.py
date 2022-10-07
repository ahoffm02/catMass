


import sys
import subprocess
import pkg_resources

required  = {'xraydb'} 
installed = {pkg.key for pkg in pkg_resources.working_set}
missing   = required - installed

if missing:
    # implement pip as a subprocess:
    subprocess.check_call([sys.executable, 'pip', 'install', *missing])
    print(" has been imported")
    
from src.__main__ import main

if __name__ == '__main__':
    main()