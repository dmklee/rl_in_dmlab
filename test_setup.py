import os

errors = 0

try:
    import deepmind_lab
except ImportError:
    errors += 1
    print('ERROR: Deepmind Lab package not installed')

mypath = os.path.join(os.getcwd(), "level_scripts")
level_scripts = []
for f in os.listdir(mypath):
    if os.path.isfile(os.path.join(mypath, f)) and f.split('.')[1] == 'lua':
        level_scripts.append(f.split('.')[0])

for l in level_scripts:
    try:
        deepmind_lab.Lab(l,
                            [],
                            {})
    except RuntimeError:
        errors += 1
        print("ERROR: Level script: '%s.lua' not found." % l)

if errors == 0:
    print("SUCCESS: Deepmind lab package properly installed with necessary level scripts!")

