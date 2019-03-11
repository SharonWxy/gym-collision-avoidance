import numpy as np
import imageio
import scipy.misc

class Map():
    def __init__(self, x_width, y_width, grid_cell_size, map_filename=None):
        # Set desired map parameters (regardless of actual image file dims)
        self.x_width = x_width
        self.y_width = y_width
        self.grid_cell_size = grid_cell_size

        # Load the image file corresponding to the static map, and resize according to desired specs
        dims = (int(self.x_width/self.grid_cell_size),int(self.y_width/self.grid_cell_size))
        if map_filename is None:
            self.static_map = np.zeros(dims, dtype=bool)
        else:
            self.static_map = imageio.imread(map_filename)
            if self.static_map.shape != dims:
                print("Resizing map from: {} to {}".format(self.static_map.shape, dims))
                self.static_map = scipy.misc.imresize(self.static_map, dims, interp='nearest')
            self.static_map = np.invert(self.static_map).astype(bool)

        self.origin_coords = np.array([(self.x_width/2.)/self.grid_cell_size, (self.y_width/2.)/self.grid_cell_size])
        self.map = None # This will store the current static+dynamic map at each timestep

    def world_coordinates_to_map_indices(self, pos):
        gx = int(np.floor(self.origin_coords[0]-pos[1]/self.grid_cell_size))
        gy = int(np.floor(self.origin_coords[1]+pos[0]/self.grid_cell_size))
        grid_coords = np.array([gx, gy])
        in_map = gx >= 0 and gy >= 0 and gx < self.map.shape[0] and gy < self.map.shape[1]
        return grid_coords, in_map

    def add_agents_to_map(self, agents):
        self.map = self.static_map.copy()
        for agent in agents:
            [gx, gy], in_map = self.world_coordinates_to_map_indices(agent.pos_global_frame)
            if in_map:
                mask = self.get_agent_map_indices([gx,gy], agent.radius)
                self.map[mask] = 255
                # self.map[gx, gy] = 255

    def get_agent_map_indices(self, pos, radius):
        x = np.arange(0, self.map.shape[1])
        y = np.arange(0, self.map.shape[0])
        mask = (x[np.newaxis,:]-pos[1])**2 + (y[:,np.newaxis]-pos[0])**2 < (radius/self.grid_cell_size)**2
        return mask