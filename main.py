import pygame, random, math
import numpy as np
from person import Human, Infected

BLACK = (0, 0, 0)

total_people = 1200 #min 120
steps = 3

continents = {}
list_humans = []
list_infected = []
FRAMES_PER_SECOND = 60
SPEED = 2

pygame.init()

screen_width, screen_height = 1600, 821

def on_the_land(x,y,mask1):
    if mask1.get_at((x,y)):
        return True
    else:
        return False

def make_continents():
    global continents, total_people
    total_people -= 120 #min 20 peoples on 1 continent
    # For the value max_people, we asked to calculate the percentage of people living on each continent relative to the total world population.
    # ChatGPT generated the following list with percentages:
    # Eurasia – 65.7%, Africa – 19.1%, North America – 8.9%, South America – 5.5%, Australia – 0.7%, Greenland – 0.1%.
    # bounds(x_min,y_min,x_max,y_max)
    continents = {
        "south_america":  {"bounds": (277,434,535,748), "max_people": 20 + int(total_people * 0.089), "infection_rang":9},
        "north_america":  {"bounds": (84,74,380,322), "max_people": 20 + int(total_people * 0.055), "infection_rang":6},
        "eurasia":        {"bounds": (586,39,1447,378), "max_people": 20 + int(total_people * 0.657), "infection_rang":7},
        "africa":         {"bounds": (636,272,988,710), "max_people": 20 + int(total_people * 0.191), "infection_rang":3},
        "australia":      {"bounds": (1370,587,1589,737), "max_people": 20 + int(total_people * 0.007), "infection_rang":9},
        "greenland":      {"bounds": (525,5,676,88), "max_people": 20 + int(total_people * 0.001), "infection_rang":6},
    }
    total_people = 0
    for continent in continents:
        total_people += continents[continent]["max_people"]

def check_spawn(x,y,num,board):
    if board.get_at((x,y)):
        if len(list_humans) > 0:
            for j in range((len(list_humans) - num), len(list_humans) - 1):
                if list_humans[j].pos_x == x and list_humans[j].pos_y == y:
                    return False
        return True
    else: return False


def check_movement(x,y,board,cont):
    if x > screen_width or x < 0 or y > screen_height or y < 0:
        return False
    if board.get_at((x,y)):
        min = 0
        max = continents["south_america"]["max_people"]
        for con in continents:
            if con == cont:
                max = min + continents[con]["max_people"]
            else:
                min += continents[con]["max_people"]
        for i in range(min,max):
            if x == list_humans[i].pos_x and y == list_humans[i].pos_y:
                return False
        return True
    else: return False


def make_humans(boards):
    global list_humans
    for cont in continents:
        for i in range(continents[cont]["max_people"]):
            finish = False
            while(not finish):
                x = random.randint(continents[cont]["bounds"][0],continents[cont]["bounds"][2])
                y = random.randint(continents[cont]["bounds"][1],continents[cont]["bounds"][3])
                if check_spawn(x,y,i,boards):
                    list_humans.append(Human(x,y,continents[cont]))
                    finish = True

def draw_humans(surface):
    for hum in list_humans:
        pygame.draw.circle(surface, hum.color, (hum.pos_x, hum.pos_y), 4)

def move_humans(boards):
    for hum in list_humans:
        finish = False
        while(not finish):
            angle = random.uniform(0, 2*math.pi)
            x = hum.pos_x + math.cos(angle)*steps
            y = hum.pos_y + math.sin(angle)*steps
            if check_movement(x,y,boards,hum.continent):
                hum.pos_x = x
                hum.pos_y = y
                finish = True

def main():
    screen = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption("Human Infection")
    mask = pygame.mask.from_surface(pygame.image.load('mask.png').convert_alpha())
    world = pygame.image.load('world.png').convert()
    clock = pygame.time.Clock()
    mouse_pos = pygame.mouse.get_pos()
    make_continents()
    make_humans(mask)
    count_speed = 0
    while True:
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == pygame.MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
        #print(on_the_land(mouse_pos[0], mouse_pos[1], mask))
        #print(mouse_pos)
        screen.fill(BLACK)
        screen.blit(world, (0, 0))
        draw_humans(screen)
        count_speed += 1
        if (count_speed % SPEED == 0):
            move_humans(mask)
            count_speed = 0
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)

if __name__ == "__main__":
    main()