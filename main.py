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
ticked = 1

continents = {}
list_humans = []
list_infected = []
FRAMES_PER_SECOND = 60
SPEED = 1
virus_stage_time = 3500
time_for_travel = 300

change_virus_stage = False
travel_ready = False
pause = False
stat_view = False
diagrams_view = False

#images
aircraft_left = pygame.image.load("images/airplane_left.png")
aircraft_right = pygame.image.load("images/airplane_right.png")
frame = pygame.image.load("images/frame.png")
accept = pygame.image.load("images/accept.png")

#For travel:
travel = False
passenger = Human(0,0,0,"none")
aircraft = aircraft_left
aircraft_pos = [0,0]
vector = [0,0]
continent_new = ""
counter = 0
flight_time = 0

#For diagrams:
main_graph = pygame.image.load("images/main_graph.png")
diagram = {
    'healthy':{"list":[], "color": (98, 12, 237)},
    'infected':{"list":[], "color": (255, 0, 0)},
    'deaths':{"list":[], "color": (0,0,0)},
    "infected_level_1": {"list":[], "color": (255, 255, 0),},
    "infected_level_2": {"list":[], "color": (255, 153, 0),},
    "infected_level_3": {"list":[], "color": (255, 0, 242),},
    "immunity_level_1": {"list":[], "color": (0, 72, 255),},
    "immunity_level_2": {"list":[], "color": (0, 195, 255),},
    "immunity_level_3": {"list":[], "color": (0, 255, 213),},
    "immunity_level_4": {"list":[], "color": (59, 184, 144),},
}
buttons = {}

screen_width, screen_height = 1600, 821

def check_on_mask(x,y,border, reverse=False):
    border_mask = [border[0],border[1],border[2],border[3]]
    y = screen_height-y
    if reverse:
        border_mask[2] = screen_height - border[3]
        border_mask[3] = screen_height - border[2]
    if x >= border_mask[0] and x <= border_mask[1] and y>=border_mask[2] and y <= border_mask[3]:
        return True
    else:
        return False

def get_ticks():
    global ticked
    tick = pygame.time.get_ticks()
    if tick/(100*ticked) >= 1:
        ticked += 1
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
        "greenland":      {"bounds": (525,5,676,88), "max_people": 20 + int(total_people * 0.001), "airport":(590,35),},
    }
    total_people = 0
    for continent in continents:
        total_people += continents[continent]["max_people"]

def refresh_stats():
    global diagram
    healthy = 0
    inf_lvl_1 = 0
    inf_lvl_2 = 0
    inf_lvl_3 = 0
    immun_lvl_1 = 0
    immun_lvl_2 = 0
    immun_lvl_3 = 0
    immun_lvl_4 = 0
    infected_people = 0
    deaths = 0
    for hum in list_humans:
        if not hum.alive:
            deaths += 1
        elif not hum.infection:
            healthy += 1
            if hum.immunity == 0:
                immun_lvl_1 += 1
            elif hum.immunity == 1:
                immun_lvl_2 += 1
            elif hum.immunity == 2:
                immun_lvl_3 += 1
            else:
                immun_lvl_4 += 1
        else:
            infected_people += 1
            if hum.virus_level == 1:
                inf_lvl_1 += 1
            elif hum.virus_level == 2:
                inf_lvl_2 += 1
            else:
                inf_lvl_3 += 1
    diagram['healthy']['list'].append(healthy)
    diagram['infected']['list'].append(infected_people)
    diagram['deaths']['list'].append(deaths)
    diagram["infected_level_1"]['list'].append(inf_lvl_1)
    diagram["infected_level_2"]['list'].append(inf_lvl_2)
    diagram["infected_level_3"]['list'].append(inf_lvl_3)
    diagram["immunity_level_1"]['list'].append(immun_lvl_1)
    diagram["immunity_level_2"]['list'].append(immun_lvl_2)
    diagram["immunity_level_3"]['list'].append(immun_lvl_3)
    diagram["immunity_level_4"]['list'].append(immun_lvl_4)

def make_live_graph(surface):
    global diagram
    diagram_img = pygame.image.load("images/diagram.png")
    start_point_x = 940
    start_point_y = 689
    surface.blit(diagram_img, (start_point_x, start_point_y))
    pygame.draw.line(surface, diagram["healthy"]['color'], (start_point_x + 10, start_point_y + 50),(start_point_x + 50, start_point_y + 50), 3)
    pygame.draw.line(surface, diagram["infected"]['color'], (start_point_x + 10, start_point_y + 82),(start_point_x + 50, start_point_y + 82), 3)
    pygame.draw.line(surface, diagram["deaths"]['color'], (start_point_x + 10, start_point_y + 114),(start_point_x + 50, start_point_y + 114), 3)
    font = pygame.font.Font("fonts/font_for_numbers.otf", 20)
    max_people = total_people
    start_text_x = start_point_x + 52
    start_text_y = start_point_y
    max_width_text = 31
    for i in range(6):
        text_num = font.render(str(max_people), True, BLACK)
        if text_num.get_width() < max_width_text:
            start_text_x += max_width_text - text_num.get_width()
        surface.blit(text_num, (start_text_x, start_text_y))
        start_text_x = start_point_x + 52
        start_text_y += 20
        if i == 4: max_people = 0
        else:
            max_people -= int(total_people/5)
    seconds = int(ticked/10)
    font_sec = pygame.font.Font("fonts/font_for_numbers.otf", 16)
    min = 0
    max = 0
    step = 19 / 10
    start_sec_x = start_point_x + 85
    start_sec_y = start_point_y + 108
    if seconds < 15:
        min = 0
    else:
        min = seconds - 15
    for sec in range(min,seconds + 1):
        text_sec = font_sec.render(str(sec), True, BLACK)
        surface.blit(text_sec, (start_sec_x, start_sec_y))
        start_sec_x += step * 10
    size = 103
    #if len(diagram[dia]) != 0:
    live_graph = ("healthy", "infected", "deaths")
    for dia in live_graph:
        start_line_x = start_point_x + 87.00
        end_line_x = start_line_x - step
        max = len(diagram[dia]['list'])
        if max < 160:
            min = 0
        else:
            min = max - 160
        start_line_y = start_point_y + 5 + size - (size * (diagram[dia]['list'][min] / total_people))
        end_line_y = start_line_y
        for num in range(min,max):
            end_line_x += step
            end_line_y = (start_point_y + 5+ size - (size * (diagram[dia]['list'][num]/total_people)))
            pygame.draw.line(surface,diagram[dia]['color'],(start_line_x, start_line_y),(end_line_x, end_line_y), 4)
            start_line_x = end_line_x
            start_line_y = end_line_y

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
    font = pygame.font.Font("fonts/font_for_game.ttf", 38)
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

def make_buttons():
    global buttons
    buttons = {
        "healthy": {"borders":[],"active": True},
        "infected": {"borders":[],"active": True},
        "deaths": {"borders":[],"active": True},
        "infected_level_1": {"borders":[],"active": False},
        "infected_level_2": {"borders":[],"active": False},
        "infected_level_3": {"borders":[],"active": False},
        "immunity_level_1": {"borders":[],"active": False},
        "immunity_level_2": {"borders":[],"active": False},
        "immunity_level_3": {"borders":[],"active": False},
        "immunity_level_4": {"borders":[],"active": False},
    }
    start_point_x = 300
    start_point_y = 60
    for butts in buttons:
        buttons[butts]["borders"] = [start_point_x,start_point_x + frame.get_width(), start_point_y, start_point_y + frame.get_height()]
        start_point_y += frame.get_height() + 10

def make_main_graph(surface):
    global buttons
    font_buttons = pygame.font.Font("fonts/font_for_button.otf", 35)
    start_text_x = buttons["healthy"]["borders"][1] + 20
    for butts in buttons:
        text = font_buttons.render(butts, True, diagram[butts]["color"])
        start_text_y = buttons[butts]["borders"][2] + frame.get_height() / 2 - text.get_height()/2
        surface.blit(frame, (buttons[butts]["borders"][0], buttons[butts]["borders"][2]))
        if buttons[butts]["active"]:
            surface.blit(accept, (buttons[butts]["borders"][0], buttons[butts]["borders"][2]))
        surface.blit(text, (start_text_x, start_text_y))
    start_graph_x = start_text_x + 280
    start_graph_y = buttons["healthy"]["borders"][2] + frame.get_height() / 2 + 20
    surface.blit(main_graph, (start_graph_x, start_graph_y))
    cells = 11
    cell_width = 55
    max_people = total_people
    start_num_x = start_graph_x - 40
    start_num_y = start_graph_y - 12
    font_nums = pygame.font.Font("fonts/font_for_button.otf", 24)
    for i in range(cells + 1):
        if i == cells:
            max_people = 0
        num = font_nums.render(str(max_people), True, WHITE)
        if num.get_width() < 44:
            start_num_x += 44 - num.get_width()
        surface.blit(num, (start_num_x, start_num_y))
        max_people -= int(total_people/cells)
        start_num_x = start_graph_x - 40
        start_num_y += cell_width
    point = int(ticked/100)
    min = 0
    max = point
    if point < 15:
        min = 0
    else:
        min = point - 15
    start_num_x = start_graph_x + 12
    start_num_y = start_graph_y + main_graph.get_height()
    for i in range(min,max+1):
        num = font_nums.render(str(i*10), True, WHITE)
        surface.blit(num, (start_num_x, start_num_y))
        start_num_x += cell_width
    graph_width = 608
    for dia in diagram:
        if not buttons[dia]["active"]:
            continue
        start_line_x = start_graph_x + 20
        end_line_x = start_line_x
        start_line_y = start_graph_y + (graph_width - (graph_width * diagram[dia]['list'][0]/total_people))
        if len(diagram[dia]['list']) < 100*15:
            min = 0
        else:
            min = len(diagram[dia]['list']) - 100*15
            start_line_y = start_graph_y + (graph_width - (graph_width * diagram[dia]['list'][min] / total_people))
        end_line_y = start_line_y
        for num in range(min, len(diagram[dia]['list'])):
            pygame.draw.line(surface, diagram[dia]['color'], (start_line_x, start_line_y), (end_line_x, end_line_y), 5)
            start_line_x = end_line_x
            start_line_y = end_line_y
            end_line_x += cell_width/100
            end_line_y = start_graph_y + (graph_width - (graph_width * diagram[dia]['list'][num]/total_people))

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
    global change_virus_stage,travel_ready
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
    if not travel:
        travel_ready = False
    if change_virus_stage:
        change_virus_stage = False

def speek(sound):
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
                    sound.play()

def main():
    global change_virus_stage,pause, aircraft_left, aircraft_right, travel_ready, stat_view, diagrams_view, buttons, frame, accept, main_graph
    #Main Window:
    pygame.init()
    screen = pygame.display.set_mode((screen_width,screen_height))
    pygame.display.set_caption("Human Infection")
    # =======================================================================================
    #Music and sounds:
    pygame.mixer.music.load("music/background.ogg")
    pygame.mixer.music.set_volume(0.1)
    sound_infected = pygame.mixer.Sound("music/sound_infected.mp3")
    sound_infected.set_volume(0.05)
    pygame.mixer.music.play(-1)
    # =======================================================================================
    #images:
    mask = pygame.mask.from_surface(pygame.image.load("images/mask.png").convert_alpha())
    world = pygame.image.load("images/world.png").convert()
    stat_icon = pygame.image.load("images/stat.png").convert_alpha()
    button_icon = pygame.image.load("images/button.png").convert_alpha()
    play = pygame.image.load("images/play.png").convert_alpha()
    stop = pygame.image.load("images/pause.png").convert_alpha()
    play_stop = stop
    aircraft_left = aircraft_right.convert_alpha()
    aircraft_right = aircraft_left.convert_alpha()
    frame = frame.convert_alpha()
    accept = accept.convert_alpha()
    main_graph = main_graph.convert_alpha()
    # =======================================================================================
    #Borders:
    stat_border = [10,110,10,110]
    diagram_border = [940, 1339, 12, 141]
    button_border = [0,0,0,0]
    play_stop_border = [10, 10 + play_stop.get_width(), 10, 10 + play_stop.get_height()]
    # =======================================================================================
    clock = pygame.time.Clock()
    mouse_pos = [0,0]
    make_continents()
    make_humans(mask)
    infected(random.choice(list_humans),1,0)
    count_speed = 1
    count_virus = 1
    count_travel = 0
    while True:
        ticks = pygame.time.get_ticks()
        # event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
            if event.type == MOUSEMOTION:
                mouse_pos = pygame.mouse.get_pos()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if not stat_view and not diagrams_view:
                    if check_on_mask(mouse_pos[0], mouse_pos[1], stat_border):
                        button_border = [screen_width / 2 - button_icon.get_width() - 10, screen_width / 2 - 10, 10,10 + button_icon.get_height()]
                        stat_view = True
                        play_stop_border = [screen_width - play_stop.get_width() - 10, screen_width - 10, 10,play_stop.get_height() + 10]
                    if check_on_mask(mouse_pos[0], mouse_pos[1], diagram_border):
                        diagrams_view = True
                        make_buttons()
                        button_border = [screen_width - button_icon.get_width()-10, screen_width-10, 10,10 + button_icon.get_height()]
                elif stat_view and check_on_mask(mouse_pos[0], mouse_pos[1], button_border, True):
                    stat_view = False
                    play_stop_border = [10, 10 + play_stop.get_width(), 10, 10 + play_stop.get_height()]
                elif diagrams_view and check_on_mask(mouse_pos[0], mouse_pos[1], button_border, True):
                    diagrams_view = False
                    buttons.clear()
                if check_on_mask(mouse_pos[0], mouse_pos[1], play_stop_border, True):
                    pause = not pause
                if len(buttons) != 0:
                    for butts in buttons:
                        if check_on_mask(mouse_pos[0], mouse_pos[1], buttons[butts]["borders"], True):
                            buttons[butts]["active"] = not buttons[butts]["active"]
        if pause:
            play_stop = stop
        else:
            play_stop = play
        #Draw some objects:
        screen.fill(BLACK)
        screen.blit(world, (0, 0))
        screen.blit(play_stop, (play_stop_border[0], play_stop_border[2]))
        screen.blit(stat_icon, (10, screen_height - stat_icon.get_height() - 10))
        draw_humans(screen)
        # =======================================================================================
        if get_ticks():
            refresh_stats()
        make_live_graph(screen)
        if not pause:
            if travel:
                flying(screen)
            if ticks/count_virus >= virus_stage_time:
                change_virus_stage = True
                count_virus += 1
            if not travel_ready:
                count_travel += 1
                if count_travel == time_for_travel:
                    travel_ready = True
                    count_travel = 0
            if ticks / count_speed >= SPEED:
                move_humans(mask)
                speek(sound_infected)
                count_speed += 1
        if stat_view:
            window_stat = (0,0,screen_width/2, screen_height)
            pygame.draw.rect(screen,GRAY,window_stat)
            screen.blit(button_icon, ((screen_width/2 - button_icon.get_width() - 10),10))
            make_stats(screen)
        if diagrams_view:
            copy_surf = pygame.Surface((screen_width,screen_height), pygame.SRCALPHA)
            window_diagrams = (0,0,screen_width,screen_height)
            pygame.draw.rect(copy_surf,GRAY,window_diagrams)
            copy_surf.set_alpha(245)
            screen.blit(copy_surf, (0,0))
            screen.blit(button_icon, (screen_width - button_icon.get_width() - 10, 10))
            screen.blit(play_stop, (10, 10))
            make_main_graph(screen)
        pygame.display.update()
        clock.tick(FRAMES_PER_SECOND)

if __name__ == "__main__":
    main()