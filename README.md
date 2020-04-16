## Environments for Reinforcement Learning with DeepMind Lab
The purpose of this repo is to provide a gym-like environment for training RL agents for navigation in DeepMind Lab levels. Specifically, functionality is provided for:
- loading new grid-like environments (for domain randomization during training)
- resetting player spawn location and goal location (for goal-conditioned q-learning)
- accessing custom observations of the maps (for learning latent encodings, or providing additional information to agents during training)

## How to use

We provide a lua script designed to generate DeepMind Lab levels from text maps or bsp files, and provide specific access to players state or custom observations in the levels.  The lua script (and any compiled maps) must be added to the deepmind_lab repo before building the DMLab Python module, so they can be accessed without bazel. Follow the steps below to ensure these scripts are included in the pip package.

1. Clone deepmind_lab repo: 
    $git clone https://github.com/deepmind/lab.git

2. Clone this repo:
    $git clone https://github.com/dmklee/rl_in_dmlab.git

3. Add provided lua scripts to deepmind_lab :
    $cp rl_in_dmlab/level_scripts/*.lua lab/game_scripts/levels

4. [OPTIONAL] Add any compiled bsp files to deepmind_lab :
    $cp rl_in_dmlab/precompile_maps/bsp_files/*.bsp lab/assets/maps/built

5. Build and install DeepMind Lab Python package follwing instructions at https://github.com/deepmind/lab/tree/9c1e1b9eb0ee241d07066a81edf3de8d33e4a621/python/pip_package 

To test that the python package was properly installed with the necessary level scripts run "$python test_setup.py"

## How to Precompile Maps from Text Files
Generate text files that follow the formatting in "/precompile_maps/to_be_compiled/example.txt".  Add all such text files to the to_be_compiled folder.  Remember to keep track of the underlying grid used to create each map, as this information will be needed to determine where spawn and goal locations are created. Run "$python -m precompile_maps.compile_maps" to populate the bsp_files folder with compiled bsp files. 

## Features

- [x] Create maps from occupation grids
- [x] Create maps from bsp files
- [x] Convert txt file to bsp
- [x] Change respawn position of loaded map
- [x] Change goal position of loaded map
- [x] Add custom view observation
- [ ] Add debugging visualization
- [ ] Add velocity based actions