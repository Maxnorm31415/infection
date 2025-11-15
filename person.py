import random

DARK_GREEN = (14, 112, 7)
RED = (176, 0, 0)
PINK = (255,0,127)
ORANGE = (255, 183, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
PURPLE = (166, 0, 255)
LIGHTBLUE = (0, 255, 213)

class Human:
    id = 0
    firstname = ""
    lastname = ""
    age = 0
    immunity = 0
    social_rang = 0
    travel_rang = 0
    pos_x = 0
    pos_y = 0
    continent = ""
    infection = False
    alive = True
    virus_level = 1
    die_chance = 0.00
    color = (0,0,0)
    def __init__(self, id, x, y, cont,inf = False,f_name = "None",l_name = "None",ag = 0,s_r = 0,t_r = 0, imun = 0):
        if f_name == "None":
            self.firstname = random.choice(["Alex", "Maya", "Leo", "Sophie", "Ethan", "Luna", "Oliver", "Isla", "Noah", "Aria"])
            self.lastname = random.choice(["Johnson", "Carter", "Bennett", "Miller", "Collins", "Smith", "Brown", "Davis", "Wilson", "Clark"])
            self.age = random.randint(15,80)
            self.social_rang = random.randint(1,10)
            self.travel_rang = random.randint(1,10)
            self.immunity= 0
        else:
            self.firstname = f_name
            self.lastname = l_name
            self.age = ag
            self.immunity = imun
            self.social_rang = s_r
            self.travel_rang = t_r
        if not inf:
            self.infection = False
            if self.immunity == 0:
                self.color = DARK_GREEN
            elif self.immunity == 1:
                self.color = BLUE
            elif self.immunity == 2:
                self.color = LIGHTBLUE
            else:
                self.color = PURPLE

        self.id = id
        self.continent = cont
        self.pos_x = x
        self.pos_y = y


    def try_infection(self):
        return random.uniform(0, 1) <= 0.5

class Infected(Human):
    virus_live = 0
    streak = 0
    def __init__(self, human, v_lvl, immun):
        super().__init__(human.id,human.pos_x, human.pos_y,human.continent, True,human.firstname, human.lastname,
                         human.age, human.social_rang, human.travel_rang, immun)
        self.infection = True
        self.virus_live = int(0.346*human.age + 2.308)
        self.virus_level = v_lvl
        if self.virus_level == 1:
            self.color = RED
        elif self.virus_level == 2:
            self.color = PINK
        else:
            self.color = ORANGE
        self.die_chance = (self.virus_live - 1) * 0.0015

    def try_travel(self):
        chance = 0.005*self.travel_rang
        return random.uniform(0,1)<= chance

    def try_speek(self, human):
        if human.immunity < self.virus_level:
            chance = (0.1 * self.social_rang) * (0.1 * human.social_rang)
            return random.uniform(0, 1) <= chance
        else: return False

    def update(self):
        if self.alive:
            self.streak += 1
            if self.virus_level > 1:
                if random.uniform(0,1) < self.die_chance:
                    self.alive = False
                    self.color = BLACK
            if self.streak == 17 and self.virus_level < 3:
                self.virus_level += 1
                self.die_chance = (self.virus_level - 1) * 0.0015
                self.virus_live += random.randint(5,20)
                self.immunity += 1
                self.streak = 0
                if self.virus_level == 2:
                    self.color = PINK
                else:
                    self.color = ORANGE
