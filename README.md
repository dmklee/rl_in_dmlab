## Environments for Reinforcement Learning with DeepMind Lab
The purpose of this repo is to provide gym-like environments for training RL agents for navigation in DeepMind Lab levels. 

## How to use

We provide several lua scripts designed to generate DMLab levels from text maps, and provide specific access to players state or cu stom observations in the levels.  These lua scripts must be added to the deepmind_lab repo and before building the DMLab Python module, so they can be accessed without bazel. Follow the steps below to ensure these scripts are included in the pip package.

1. Clone deepmind_lab repo: 
    $git clone https://github.com/deepmind/lab.git

2. Clone this repo:
    $git clone 

3. Add provided lua scripts to deepmind_lab :
    $cp rl_in_dmlab/level_scripts/*.lua lab/game_scripts/levels

4. Build and install DeepMind Lab Python package follwing instructions at https://github.com/deepmind/lab/tree/9c1e1b9eb0ee241d07066a81edf3de8d33e4a621/python/pip_package 

To test that the python package was properly installed with the necessary level scripts run $python test.py
