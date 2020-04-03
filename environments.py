import deepmind_lab
import numpy as np 

class DMLabBase():
    '''
    This implements simple functionality of DeepMindLab in a gym-like class
    where actions are move forward/backward and look left/right, observations
    are forward facing images (player pose is optionally provided), and episodes
    begin at random locations of user specified maps.
    '''
    def __init__(self, frame_skip=5, use_debug=True, obs_shape=(60,80)):
        self.level_script = "gridmap_spawnpoints"
        self.frame_skip = frame_skip

        self.H, self.W = obs_shape

        self.obs_specs = {'img' : 'RGB_INTERLEAVED'}
        if use_debug:
            # these will be added to observation
            # See link below on other possible debug observations
            # https://github.com/deepmind/lab/blob/master/game_scripts/decorators/debug_observations.lua
            self.obs_specs['position'] = 'DEBUG.POS.TRANS'
            self.obs_specs['rotation'] = 'DEBUG.POS.ROT'

        self.actions = [np.array((-20, 0, 0, 0, 0, 0, 0), dtype=np.intc),              # look left
                        np.array((20, 0, 0, 0, 0, 0, 0), dtype=np.intc),                # look right
                        np.array((0, 0, 0, 1, 0, 0, 0), dtype=np.intc),                 # forward
                        np.array((0, 0, 0, -1, 0, 0, 0), dtype=np.intc)                 # backward
                        ]       

        # call to load_map populates self.lab attribute
        self.lab = None 

    def load_map_from_grid(self, grid, use_variation=True, random_seed=1):
        '''
        Create level based on occupation grid (2D boolean array) where wall
        locations are True.  The boundary should be all True values.

        Example of single room as a grid:
        grid = np.array(((1,1,1,1,1,1),
                         (1,0,0,0,0,1),
                         (1,0,0,0,0,1),
                         (1,0,0,0,0,1),
                         (1,1,1,1,1,1)), dtype=bool)
        '''

        self.grid = grid.copy()

        # all configs values must be strings
        configs = {'fps'            : '30',
                   'width'          : str(self.W),
                   'height'         : str(self.H),
                   'text_map'       : self._create_text_map(grid),
                   'random_seed'    : str(random_seed),
                   'decalFrequency' : '0.1'
                   }
        if use_variation:
            configs['variation_map'] = self._create_room_variation_map(grid)
        
        self.lab = deepmind_lab.Lab(self.level_script,
                                        list(self.obs_specs.values()),
                                        configs)

        self.lab.reset()
        self.lab.step(np.zeros(7,dtype=np.intc), 10)

    def reset(self, start_pose, goal_position=(0,0)):
        '''
        Resets location of player in the loaded map.
        '''
        assert self.lab is not None, "No map has been loaded yet!"

        # set new spawn pose
        self.lab.write_property('params.spawn_pose.x', str(start_pose[0]))
        self.lab.write_property('params.spawn_pose.y', str(start_pose[1]))
        self.lab.write_property('params.spawn_pose.theta', str(start_pose[2]))

        # default goal_position places it off the map
        self.lab.write_property('params.goal_position.x', str(goal_position[0]))
        self.lab.write_property('params.goal_position.y', str(goal_position[1]))
        

        # reset level, spawning agent at specified location
        self.lab.reset()

        # perform no action for a few time steps
        # this prevents an error caused by custom respawning
        self.lab.step(np.zeros(7,dtype=np.intc), 10)

        return self._get_obs()

    def step(self, a):
        '''
        Take action in environment. 
        '''
        assert 0 <= a < len(self.actions)

        lab_reward = 0
        lab_reward += self.lab.step(self.actions[a], num_steps=self.frame_skip)

        obs = self._get_obs()
        reward = self._get_reward(lab_reward)
        done = False
        info = {}
        
        return obs, reward, done, info

    def _get_obs(self):
        '''
        Returns dictionary of observations specified in 
        self.obs_specs
        '''
        lab_obs = self.lab.observations()
        obs = {}
        for k,v in self.obs_specs.items():
            obs[k] = lab_obs[v]
        
        return obs

    def _get_reward(self, lab_reward):
        '''
        The lab reward is what is provided by DMlab based on collecting tokens.
        Additional rewards could be implemented here by looking at state of the 
        player (e.g. reward based on euclidean distance to a specified position)
        '''
        return lab_reward

    def random_pose(self):
        '''
        Produce (x,y,theta) that is valid for current map.  
        Used by reset method to choose respawn location.

        As written, a random tile location in self.grid is chosen
        as the position, and theta is uniformly distributed in [0, 2pi)
        '''

        free_tiles = np.argwhere(self.grid==False)
        chosen_tile = free_tiles[np.random.randint(len(free_tiles))]

        # place agent in middle of grid tile
        grid_location = chosen_tile + 0.5

        # convert to position in deepmind lab level
        x,y = self._grid_location_to_position(grid_location)

        theta = np.random.uniform(0, 2*np.pi)

        return x, y, theta

    def _grid_location_to_position(self, grid_location):
        '''
        Converts from location in grid to position in deepmind lab map.
        For all text-generated maps, each cell in the grid corresponds to 
        100 units.  DMLab uses bottom left as origin so we flip one axis
        '''
        return 100.*np.array((grid_location[1], self.grid.shape[0]-grid_location[0]))

    def _position_to_grid_location(self, position):
        '''
        Converts from position in level to corresponding location in grid space
        '''
        return np.array((self.grid.shape[0]-position[1]/100., position[0]/100.))

    def _create_text_map(self, grid):
        '''
        Convert a 2D boolean occupancy grid into a string 
        where '*' indicates a wall and ' ' indicates free space.
        A single 'P' is added to serve as the spawn point of the 
        agent.  A spawn point is needed to reset the environment 
        properly.  The actual location of the spawning can be 
        changed after the DMlab level has been created.
        '''
        mapping = {True: "*", False: " "}
        string_map = ''
        M,N = grid.shape
        for i in range(M):
            for j in range(N):
                char = mapping[grid[i,j]]
                string_map = string_map + char
            string_map = string_map + "\n"

        # add spawn and goal 
        string_map = string_map.replace(' ', 'P', 1)
        string_map = string_map.replace(' ', 'A', 1)
        return string_map

    def _create_room_variation_map(self, grid):
        '''
        This creates a variation layer such that each
        room on the map has a different variation code.

        As an example:

        ********      
        *   *  *      AAA BB 
        * P    *  ->  AAA BB 
        *   *  *      AAA BB 
        ********   

        See this link for more info:
        https://github.com/deepmind/lab/blob/7b851dcbf6171fa184bf8a25bf2c87fe6d3f5380/docs/developers/creating_levels/text_level.md   
        '''
        dm = np.array((0,1,0,-1),dtype=int)
        dn = np.array((1,0,-1,0),dtype=int)

        def is_doorway(m,n, grid):
            if (grid[m+1,n] and grid[m-1,n]) or \
                (grid[m,n+1] and grid[m,n-1]):
                return True
            return False

        def get_room(m,n, grid, seen):
            if seen[m,n]: 
                yield []
            else:
                seen[m,n] = True
                if is_doorway(m,n, grid):
                    yield []
                else:
                    yield (m,n)
                    for i,j in zip((m+dm), n+dn):
                        for a in get_room(i,j, grid, seen):
                            if len(a) != 0:
                                yield a

        seen = np.copy(grid).astype(bool)
        M,N = np.meshgrid(np.arange(grid.shape[0]), np.arange(grid.shape[1]))

        variation_map = [[' ' for _ in range(grid.shape[1])] for _ in range(grid.shape[0])]

        characters = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
        room_num = 0
        for m,n in zip(M.flatten(),N.flatten()):
            if seen[m,n]: continue
            room_indices = list(get_room(m, n, grid, seen))
            if len(room_indices) <= 1: continue
            for i,j in room_indices:
                variation_map[i][j] = characters[room_num]
            room_num += 1
        
        variation_map = '\n'.join([''.join(row) for row in variation_map])
        return variation_map   

if __name__ == "__main__":
    grid = np.ones((5,5),dtype=bool)
    grid[1:-1,1:-1] = 0

    env = DMLabBase()
    env.load_map_from_grid(grid, random_seed=2)

    import matplotlib.pyplot as plt 

    obs = env.reset((150,150,0))
    plt.figure()
    plt.imshow(obs['img'])
    plt.savefig('here')