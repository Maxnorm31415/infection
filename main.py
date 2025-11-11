import pygame, random
import numpy as np

col_new_fish = (0, 128, 255)
col_young_fish = (15,82,186)
col_breeding_fish = (220,35,157)

col_new_bear = (150,75,0)
col_young_bear = (165,113,78)
col_breeding_bear = (150,75,0)
col_starving_bear = (75,75,75)

col_empty = (213, 196, 161)
col_grid = (30, 30, 60)

FRAMES_PER_SECOND = 60
SPEED = 15

ID = 0  # to identify each animal uniquely (for checking correctness)
def new_ID():
    global ID
    currentID = ID
    ID += 1
    return currentID

# Fish initial definition
fish_breed_age = 12     # 12
fish_overcrowd = 2   # 2
def new_fish():
    ID_fish = new_ID()
    fish = {'type': 'fish', 'id':ID_fish, 'col':col_new_fish, 'age': 0}
    return fish

# Bear initial definition
bear_breed_age = 8      # 8
bear_starvation = 10    # 10
def new_bear():
    ID_bear = new_ID()
    bear = {'type': 'bear', 'id':ID_bear, 'age': 0, 'col':col_new_bear, 'food': bear_starvation}
    return bear

def empty():
    return {'type': 'empty'}

def init(dimx, dimy, fish, bear):
    """Creates a starting grid, of dimension dimx * dimy and inserts {fish} new fishes and {bear} new bears.
       The rest of the cells in the grid are filled with empty dictionaries. """
    # create a list with fish fishes, bear bears and the rest (dimx*dimy-fish-bear) are empty  and shuffle them
    content_list = []
    for i in range(fish):
        content_list.append(new_fish())
    for i in range(bear):
        content_list.append(new_bear())
    for i in range((dimx * dimy - fish - bear)):
        content_list.append(empty())
    random.shuffle(content_list)
    # typecast the into a numpy array and reshape the 1 dimensional array to dimx * dimy
    cells_array = np.array(content_list)
    cells = np.reshape(cells_array, (dimy, dimx)) # the shape information is given in an  odd order
    return cells

# cur: the current array of cells,  r and c the row and column position which we are finding neighbours for.
def get_neighbors(cur, r, c):
    """Computes a list with the neighbouring cell positions of (r,c) in the grid {cur}"""
    r_min, c_min = 0 , 0
    r_max, c_max = cur.shape
    r_max, c_max = r_max -1 , c_max-1 # it's off by one
    # r-1,c-1 | r-1,c  | r-1,c+1
    # --------|--------|---------
    # r  ,c-1 | r  ,c  | r  ,c+1
    # --------|--------|---------
    # r+1,c-1 | r+1,c  | r+1,c+1
    neighbours = []
    # r-1:
    if r-1 >= r_min :
        if c-1 >= c_min: neighbours.append((r-1,c-1))
        neighbours.append((r-1,c))  # c is inside cur
        if c+1 <= c_max: neighbours.append((r - 1, c+1))
    # r:
    if c-1 >= c_min: neighbours.append((r,c-1))
    # skip center (r,c) since we are listing its neighbour positions
    if c + 1 <= c_max: neighbours.append((r,c+1))
    # r+1:
    if r + 1 <= r_max:
        if c - 1 >= c_min: neighbours.append((r+1,c-1))
        neighbours.append((r+1, c))  # c is inside cur
        if c + 1 <= c_max: neighbours.append((r+1,c+1))
    return neighbours

def neighbour_fish_empty_rest(cur,neighbours):
    """ Given a current grid and a set of neighbouring positions, it divides the neighbours into three lists of positions: """
    """ fish-neighbours, empty-neighbours cells and the rest"""
    # divide the neighbours into fish, empty cells and the rest
    fish_neighbours =[]
    empty_neighbours =[]
    rest_neighbours=[]
    for neighbour in neighbours:
        if cur[neighbour]['type'] == "fish":
            fish_neighbours.append(neighbour)
        elif cur[neighbour]['type'] == "bear":
            rest_neighbours.append(neighbour)
        else:
            empty_neighbours.append(neighbour)

    return fish_neighbours, empty_neighbours # we currently don't need:  rest_neighbours



def fish_rules(cur,r,c,neighbour_fish, neighbour_empty):
    """ Given the current grid {cur}, a position (r,c) which contains a fish, and a list of grid-positions for the
    fish-neighbours  and a list of grid-positions of empty neighbour cells. Update the grid according to the fish-rules"""
    # implement the fish rules
    # update age
    cur[r,c]['age'] += 1

    # it tries to breed if it has been alive for 12 states
    if cur[r,c]['age'] >= 12:
        cur[r,c]['col'] = col_breeding_fish # change/ensure that the color of fish is the breeding color
        if len(neighbour_empty)>0:  # if there exists an empty neighbour cell:
            r_empty, c_empty = random.choice(neighbour_empty)   # choose a random empty-neighbouring cell
            cur[r_empty, c_empty] = new_fish()                  # insert a new fish into that cell
            # since we have created a new fish in an empty neighbour cell the lists with fish-neighbours and empty neighbours are not up to date
            neighbour_fish.append((r_empty, c_empty))           # add the neighbour-cell position to the list containing the fish-filled neighbour-cells
            neighbour_empty.remove((r_empty, c_empty))          # remove the neighbour-cell position from the list containing the empty neighbour-cells

    # the fish dies of overcrowding if there are now 2 or more neighboring fish
    if len(neighbour_fish) >= fish_overcrowd:
        cur[r, c] = empty()

    # if the fish does not die try to move it to a neighboring empty cell
    if len(neighbour_empty) > 0:
        r_new, c_new = random.choice(neighbour_empty)
        cur[r_new,c_new] = cur[r,c]
        cur[r,c] = empty()

    return cur

def bear_rules(cur,r,c,neighbour_fish, neighbour_empty):
    """ Given the current grid {cur}, a position (r,c) which contains a bear, and a list of grid-positions for the
    fish-neighbours  and a list of grid-positions of empty neighbour cells. Update the grid according to the fish-rules"""
    # implement the bear rules

    # update age
    cur[r, c]['age'] += 1

    # update colors according to its state
    if cur[r, c]['age'] >= bear_breed_age:
        cur[r, c]['col'] = col_breeding_bear
    else:
        cur[r, c]['col'] = col_young_bear

    if cur[r, c]['food'] <= 1:
        cur[r, c]['col'] = col_starving_bear

    # if there is a fish eat it and reset food-counter, otherwise decrease food-counter
    if len(neighbour_fish) > 0:
        cur[r, c]['food'] = bear_starvation
        r_fish, c_fish = random.choice(neighbour_fish)
        neighbour_fish.remove((r_fish, c_fish))
        neighbour_empty.append((r_fish, c_fish))
        cur[r_fish, c_fish] = empty()
    else:
        # decrease food
        cur[r, c]['food'] -= 1

    # if the bear is starved it dies
    if cur[r, c]['food'] <= 0:
        cur[r, c] = empty()
    else:  # if the bear is not dead it, first, tries to breed
        if cur[r, c]['age'] >= bear_breed_age and len(neighbour_empty) > 0:
            # fish breeds to an empty cell
            r_new, c_new = random.choice(neighbour_empty)
            cur[r_new, c_new] = new_bear()
            neighbour_empty.remove((r_new, c_new))
        # it tries to move
        if len(neighbour_empty) > 0:
            r_new, c_new = random.choice(neighbour_empty)
            cur[r_new, c_new] = cur[r, c]
            cur[r, c] = empty()
    return cur

def update(surface, cur, sz):
    # for each cell
    for r, c in np.ndindex(cur.shape):
        # if there is a bear or a fish
        if cur[r, c]['type'] == "fish" or cur[r, c]['type'] == "bear":
            # calculate neighbours and find the empty and the fish neighbours (other bears are not important, currently)
            neighbours = get_neighbors(cur, r, c)
            neighbour_fish, neighbour_empty = neighbour_fish_empty_rest(cur, neighbours)
            # For checking the state of the animal (correctness)
            print(f"Pos: ({r},{c}), Animal: {cur[r, c]}")
            # if it is a fish
            if cur[r, c]['type'] == "fish":
                cur = fish_rules(cur, r, c, neighbour_fish, neighbour_empty)

            # if it is a bear
            elif cur[r, c]['type'] == "bear":
                cur = bear_rules(cur, r, c, neighbour_fish, neighbour_empty)
    return cur

def draw_grid(surface,cur,sz):
    """Given a grid {cur}, the size of the drawn cells, and a surface to draw on. Draw the """
    for r, c in np.ndindex(cur.shape):
        col = col_empty # if the cell is empty, the color should be that of "empty"
        if cur[r, c]['type'] != 'empty': # if the cell is not empty update the color according to its content
            col = cur[r, c]['col']
        pygame.draw.rect(surface, col, (c * sz, r * sz, sz - 1, sz - 1))

def main(dimx, dimy, cellsize,fish,bear):
    pygame.init()
    surface = pygame.display.set_mode((dimx * cellsize, dimy * cellsize))
    pygame.display.set_caption("Animal Kingdom")

    cells = init(dimx, dimy,fish,bear) # creates the grid representation

    clock = pygame.time.Clock()
    speed_count = 0
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return

        surface.fill(col_grid)
        if(speed_count % SPEED == 0):   # slows down the time step without slowing down the frame rate
            # update grid
            print(f"timestep: {speed_count // SPEED}")
            cells = update(surface, cells, cellsize)
        # draw the updated grid
        draw_grid(surface, cells, cellsize)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)
        speed_count = speed_count +1

if __name__ == "__main__":
    fish = 80
    bear = 1
    main(80, 20, 16,fish,bear)
