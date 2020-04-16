#!/bin/bash
cd ~/lab
cp ~/rl_in_dmlab/lua_level_scripts/*.lua ~/lab/game_scripts/levels
cp ~/rl_in_dmlab/precompile_maps/bsp_files/*.bsp ~/lab/assets/maps/built
yes | pip uninstall deepmind_lab
bazel build -c opt --python_version=PY3 //python/pip_package:build_pip_package
./bazel-bin/python/pip_package/build_pip_package /tmp/dmlab_pkg
pip install /tmp/dmlab_pkg/deepmind_lab-1.0-py3-none-any.whl
cd -