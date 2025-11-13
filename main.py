from itertools import count
from warnings import catch_warnings

import pygame, random, math
import numpy as np
from pygame import MOUSEMOTION

from person import Human, Infected

WHITE = (225, 225, 225)
BLACK = (0, 0, 0)
GRAY = (39, 41, 37)

total_people = 600 #min 120
steps = 3
radius_speek = 4

continents = {}
list_humans = []
list_infected = []
FRAMES_PER_SECOND = 60
SPEED = 1
virus_stage = 200
time_for_travel = 200

change_virus_stage = False
travel_ready = False
pause = False

aircraft_left = pygame.image.load('airplane_left.png')
aircraft_right = pygame.image.load('airplane_right.png')

#For travel:
travel = False
passenger = Human(0,0,0,"none")
aircraft = aircraft_left
aircraft_pos = [0,0]
vector = [0,0]
continent_new = ""
counter = 0
flight_time = 0

screen_width, screen_height = 1600, 821

def check_on_mask(x,y,x_min,x_max,y_min,y_max):
    y = screen_height-y
    if x >= x_min and x <= x_max and y>=y_min and y <= y_max:
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
        "south_america":  {"bounds": (277,434,535,748), "max_people": 20 + int(total_people * 0.089),"airport":(440,552)},
        "north_america":  {"bounds": (84,74,380,322), "max_people": 20 + int(total_people * 0.055),"airport":(260,155)},
        "eurasia":        {"bounds": (785,39,1447,268), "max_people": 20 + int(total_people * 0.657),"airport":(1034,235)},
        "africa":         {"bounds": (636,306,988,710), "max_people": 20 + int(total_people * 0.191),"airport":(722,330)},
        "australia":      {"bounds": (1370,587,1589,737), "max_people": 20 + int(total_people * 0.007),"airport":(1450,660)},
        "greenland":      {"bounds": (525,5,676,88), "max_people": 20 + int(total_people * 0.001), "airport":(620,35),},
    }
    total_people = 0
    for continent in continents:
        total_people += continents[continent]["max_people"]

def make_stats(surface):
    healthy = 0
    infected_people = 0
    deaths = 0
    virus_level_1 = 0
    virus_level_2 = 0
    virus_level_3 = 0
    index = 0
    continents_infected = {
        "south_america": 0,
        "north_america": 0,
        "eurasia": 0,
        "africa": 0,
        "australia": 0,
        "greenland": 0,
    }
    for con in continents:
        for i in range(index, index + continents[con]["max_people"]):
            hum = list_humans[i]
            if not hum.alive:
                deaths += 1
            elif not hum.infection:
                healthy += 1
            else:
                infected_people += 1
                continents_infected[con] += 1
                if hum.virus_level == 1:
                    virus_level_1 += 1
                elif hum.virus_level == 2:
                    virus_level_2 += 1
                else:
                    virus_level_3 += 1
        index += continents[con]["max_people"]
    sentence = {
        "Total People:": total_people,
        "Healthy people:": healthy,
        "Infected people:": infected_people,
        "Dead people:": deaths,
        "People infected with the first stage:": virus_level_1,
        "People infected with the second stage:": virus_level_2,
        "People infected with the third stage:": virus_level_3,
        "Number of flights": flight_time,
        "Number of people in South America:": continents["south_america"]["max_people"],
        "Number of people in North America:": continents["north_america"]["max_people"],
        "Number of people in Eurasia:": continents["eurasia"]["max_people"],
        "Number of people in Africa:": continents["africa"]["max_people"],
        "Number of people in Australia:": continents["australia"]["max_people"],
        "Number of people in Greenland:": continents["greenland"]["max_people"],
        "Infected people in South America:": continents_infected["south_america"],
        "Infected people in North America:": continents_infected["north_america"],
        "Infected people in Eurasia:": continents_infected["eurasia"],
        "Infected people in Africa:": continents_infected["africa"],
        "Infected people in Australia:": continents_infected["australia"],
        "Infected people in Greenland:": continents_infected["greenland"],
    }
    font = pygame.font.Font("font_for_game.ttf", 38)
    start_point_x = 100
    start_point_y = 35
    count = 1
    for sent in sentence:
        text = font.render(sent + " " + str(sentence[sent]), True, WHITE)
        surface.blit(text, (start_point_x, start_point_y))
        start_point_y += text.get_height() + 5
        if count == 8 or count == 14:
            start_point_y += 15
        count += 1
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
        return True
    else: return False

def infected(hum,v_lvl,immun):
    global list_infected, list_humans
    index = hum.id
    list_infected.append(index)
    list_humans[index] = Infected(hum,v_lvl,immun)

def flying(surface):
    global aircraft_pos, flight_time,counter, travel, list_humans,list_infected, travel_ready
    if counter != 100:
        surface.blit(aircraft, (aircraft_pos[0] + 36, aircraft_pos[1] - 25))
        aircraft_pos[0] += vector[0]/100
        aircraft_pos[1] += vector[1]/100
        counter += 1
    else:
        min = 0
        max = 0
        for con in continents:
            if con == continent_new:
                max = min + continents[con]["max_people"]
                break
            else:
                min += continents[con]["max_people"]
        #print(max-1, continent_new)
        passenger.pos_x = continents[continent_new]["airport"][0]
        passenger.pos_y = continents[continent_new]["airport"][1]
        passenger.continent = continent_new
        passenger.id = max-1
        list_infected.append(passenger.id)
        list_humans.insert(max, passenger)
        for i in range(max,len(list_humans)):
            if list_humans[i].infection:
                list_infected.remove(list_humans[i].id)
                list_infected.append(list_humans[i].id+1)
            list_humans[i].id += 1
        continents[continent_new]["max_people"] += 1
        #for hu in list_humans:
            #print(hu.id, hu.continent)
        counter = 0
        flight_time += 1
        travel = False
        travel_ready = False

def found_neighbors(x,y,cont):
    list_neighbors = []
    min = 0
    max = continents["south_america"]["max_people"]
    for con in continents:
        if con == cont:
            max = min + continents[con]["max_people"]
            break
        else:
            min += continents[con]["max_people"]
    for i in range(min, max):
        if list_humans[i].infection:
            continue
        elif (((list_humans[i].pos_x) - x)**2) + (((list_humans[i].pos_y) - y)**2) <= radius_speek**2:
            list_neighbors.append(i)
    return list_neighbors

def make_humans(boards):
    global list_humans
    index = 0
    for cont in continents:
        for i in range(continents[cont]["max_people"]):
            finish = False
            while(not finish):
                x = random.randint(continents[cont]["bounds"][0],continents[cont]["bounds"][2])
                y = random.randint(continents[cont]["bounds"][1],continents[cont]["bounds"][3])
                if check_spawn(x,y,i,boards):
                    list_humans.append(Human(index,x,y,cont))
                    finish = True
            index += 1

def draw_humans(surface):
    for hum in list_humans:
        pygame.draw.circle(surface, hum.color, (hum.pos_x, hum.pos_y), 4)

#def infection_die(hum):

def make_travel(hum):
    global passenger, vector, travel,aircraft, continent_new, aircraft_pos
    if hum.try_travel():
        travel = True
        passenger = hum
        continent_new = hum.continent
        start = [continents[hum.continent]["airport"][0],continents[hum.continent]["airport"][1]]
        continents[hum.continent]["max_people"]-= 1
        end = (0, 0)
        finish = False
        list_airports = []
        for con in continents:
            list_airports.append(con)
        while not finish:
            continent_new = random.choice(list_airports)
            end = continents[continent_new]["airport"]
            if end[0] == start[0] and end[1] == start[1]:
                continue
            else:
                finish = True
        aircraft_pos = start
        vector = ((end[0] - start[0]), (end[1]) - start[1])
        angle = math.degrees(math.atan2(vector[1], vector[0]))
        angle = -angle
        if abs(angle) < 90:
            aircraft = pygame.transform.rotate(aircraft_right, angle)
        else:
            #angle = 180 - abs(angle)
            aircraft = pygame.transform.rotate(aircraft_left, angle)
        list_humans.remove(hum)
        list_infected.remove(hum.id)
        for i in range(hum.id, len(list_humans)):
            if list_humans[i].infection:
                list_infected.remove(list_humans[i].id)
                list_infected.append(list_humans[i].id - 1)
            list_humans[i].id -= 1



def move_humans(boards):
    global change_virus_stage
    for hum in list_humans:
        if not hum.alive:
            continue
        finish = False
        while(not finish):
            angle = random.uniform(0, 2*math.pi)
            x = hum.pos_x + math.cos(angle)*steps
            y = hum.pos_y + math.sin(angle)*steps
            if check_movement(x,y,boards,hum.continent):
                hum.pos_x = x
                hum.pos_y = y
                finish = True
        if hum.infection and change_virus_stage:
            hum.virus_live -= 1
            hum.update()
            if hum.virus_live == 0:
                list_humans[hum.id] = Human(hum.id,hum.pos_x, hum.pos_y,hum.continent, False,hum.firstname,
                                            hum.lastname, hum.age, hum.social_rang, hum.travel_rang,(hum.immunity + 1))
                list_infected.remove(hum.id)
        if hum.infection and not travel and travel_ready:
            make_travel(hum)

    if change_virus_stage:
        change_virus_stage = False

def speek():
    global list_infected
    for i in list_infected:
        if not list_humans[i].alive:
            continue
        hum = list_humans[i]
        neighbors = found_neighbors(hum.pos_x, hum.pos_y, hum.continent)
        if len(neighbors) > 0:
            index = random.choice(neighbors)
            neighbor = list_humans[index]
            if hum.try_speek(neighbor):
                if neighbor.try_infection():
                    #print(neighbor.lastname, neighbor.firstname, "infected")
                    infected(neighbor, hum.virus_level, hum.immunity)

def main():
    global change_virus_stage,pause, aircraft_left, aircraft_right, travel_ready
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption("Human Infection")
    mask = pygame.mask.from_surface(pygame.image.load('mask.png').convert_alpha())
    world = pygame.image.load('world.png').convert()
    aircraft_left = aircraft_right.convert_alpha()
    aircraft_right = aircraft_left.convert_alpha()
    stat_icon = pygame.image.load('stat.png').convert_alpha()
    button_icon = pygame.image.load('button.png').convert_alpha()
    clock = pygame.time.Clock()
    make_continents()
    make_humans(mask)
    infected(random.choice(list_humans),1,0)
    count_speed = 0
    count_virus = 0
    count_travel = 0
    while True:
        if len(list_infected) + len(list_humans) > total_people*2:
            print("HAHAHAHAH",len(list_infected),len(list_humans))
            pygame.quit()
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not pause and check_on_mask(mouse_pos[0], mouse_pos[1], 10, 110, 10, 110):
                    pause = True
                if pause and check_on_mask(mouse_pos[0], mouse_pos[1], screen_width/2-button_icon.get_width()-10, screen_width/2-10,
                                        screen_height- (10 + button_icon.get_height()), screen_height - 10):
                    pause = False
        screen.fill(BLACK)
        screen.blit(world, (0, 0))
        draw_humans(screen)
        if not pause:
            screen.blit(stat_icon, (10,screen_height-stat_icon.get_height() - 10))
            if travel:
                flying(screen)
            count_speed += 1
            if count_virus == virus_stage:
                change_virus_stage = True
                count_virus = 0
            else:
                count_virus += 1
            if not travel_ready:
                count_travel += 1
                if count_travel == time_for_travel:
                    travel_ready = True
                    count_travel = 0
            if (count_speed % SPEED == 0):
               # print(len(list_infected))
                move_humans(mask)
                speek()
                count_speed = 0
        else:
            window_stat = (0,0,screen_width/2, screen_height)
            pygame.draw.rect(screen,GRAY,window_stat)
            screen.blit(button_icon, ((screen_width/2 - button_icon.get_width() - 10),10))
            make_stats(screen)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)

if __name__ == "__main__":
    main()