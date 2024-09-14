from matplotlib import pyplot as plt
from matplotlib import colors
import numpy as np

#Reference to gridmap
#https://stackoverflow.com/questions/56614725/generate-grid-cells-occupancy-grid-color-cells-and-remove-xlabels

class grid_unit:
    def __init__(self, id, row, column, probability, bound):
        self.id = id
        self.row = row
        self.column = column
        self.probability = probability
        self.bound = bound
        self.occupancy = True

class map:
    def __init__(self, rows, cols):
        #self.grids = dict()
        self.rows = rows
        self.cols = cols
        self.data = np.zeros(self.rows * self.cols).reshape(self.rows, self.cols)
        self.raster = np.zeros(self.rows * self.cols).reshape(self.rows, self.cols)
        self.mcl_matrix = np.zeros(self.rows * self.cols).reshape(self.rows, self.cols)
        self.grids = []

        self.labels = {
            "EMPTY_CELL" : 0,
            "OBSTACLE_CELL" : 1,
            "START_CELL" : 2,
            "GOAL_CELL" : 3,
            "MOVE_CELL" : 4
            }
        
    def find_grid(self, id):
        for grid in self.grids:
            if grid.id == id:
                return grid
        return False
    
    def create_grid(self, grid_x: int, grid_y: int, bound: int, prob: float) -> None:
        id = "G"+str(grid_x)+","+str(grid_y)
        grid = grid_unit(id, grid_x, grid_y, prob, bound)
        self.grids.append(grid)
        return grid
    
    def nearest_neighbour(self, xzt, yzt):
        dist = np.inf
        if len(self.grids) > 0:
            for grid in self.grids:
                 if grid.occupancy == True:
                      dist_calc = np.sqrt(np.power(xzt - grid.row, 2) + np.power(yzt - grid.column, 2))
                      if dist_calc < dist:
                           dist = dist_calc
        else:
            dist = 0

        #print(f'xzt: {xzt} yzt: {yzt} ')
        return dist
    
    def print_grids_info(self):
        file_name = "./results/grids.txt"
        #file_conn = open(file_name, "w", encoding="utf-8")
        for grid in self.grids:
            print(f'{grid.id}\t{grid.row}\t{grid.column}\t{grid.probability}')
        #    if file_conn != None:
        #        file_conn.write(f'{grid.id}\t{grid.row}\t{grid.column}\t{grid.probability}\n')
        #file_conn.close()

    def save_raster(self):
        '''
        R Code to plot raster of probabilities
        data = as.matrix(read.table("raster.txt", header = FALSE))
        image(data, useRaster=TRUE, axes=FALSE, col = grey(seq(0,1,length=256)))
        '''
        file_name = "./results/raster.txt"
        file_conn = open(file_name, 'w', encoding="utf-8")
        #print(sum(self.raster))
        for x in range(self.rows):
            for y in range(self.cols):
                if file_conn != None:
                    file_conn.write(f'{self.raster[x,y]} ')
            file_conn.write("\n")
        file_conn.close()

    def set_cell(self, grid_data, bound):
        self.data[int(self.rows/2)-grid_data[1], grid_data[0]+int(self.cols/2)] = bound
        #self.create_grid(grid_data[0], grid_data[1], bound)

    def set_raster_cell(self, grid_data, probability):
        self.raster[int(self.rows/2)+grid_data[0], grid_data[1]+int(self.cols/2)] = probability

    def set_mcl_cell(self, sample_x, sample_y, probability):
        self.mcl_matrix[int(self.rows/2)+sample_x, sample_y+int(self.cols/2)] = probability

    def get_grid(self, x, y):
        grid_x = int(np.trunc(x))
        grid_y = int(np.trunc(y))
        return [grid_x, grid_y, "G"+str(grid_x)+","+str(grid_y)]
    
    # Function to define the position given the current map.
    # TO DO: Take into account the dimensions of the vehicle. 
    def probability_position_map(self, grid_x, grid_y):
        if self.data[int(self.rows/2)-grid_x, grid_y+int(self.cols/2)] == self.labels["MOVE_CELL"]:
            return self.labels["MOVE_CELL"]
        else:
            return self.labels["OBSTACLE_CELL"]

    def plot_grid(self):
        EMPTY_CELL = 0
        OBSTACLE_CELL = 1
        START_CELL = 2
        GOAL_CELL = 3
        MOVE_CELL = 4
        bounds = [EMPTY_CELL, OBSTACLE_CELL, START_CELL, GOAL_CELL, MOVE_CELL ,MOVE_CELL + 1]
        cmap = colors.ListedColormap(['white', 'black', 'green', 'red', 'blue'])

        norm = colors.BoundaryNorm(bounds, cmap.N)

        fig, ax = plt.subplots()
        ax.imshow(self.data, cmap=cmap, norm=norm)
        #print(self.data)
        # draw gridlines
        ax.grid(which='major', axis='both', linestyle='-', color='k', linewidth=1)

        ax.set_xticks(np.arange(0.5, self.rows, 1));
        ax.set_yticks(np.arange(0.5, self.cols, 1));
        plt.tick_params(axis='both', which='both', bottom=False,   
                    left=False, labelbottom=False, labelleft=False) 
        #fig.set_size_inches((8.5, 11), forward=False)
        fig.set_size_inches((100, 100), forward=False)
        
        #plt.show()
