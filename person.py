import random
# in this file, the Human class and its subclass Infected with new functions

#colors:
DARK_GREEN = (14, 112, 7)
RED = (176, 0, 0)
PINK = (255,0,127)
ORANGE = (255, 183, 0)
BLACK = (0, 0, 0)
BLUE = (0, 0, 255)
LIGHTBLUE = (0, 255, 213)
DARK_BLUE = (48, 18, 196)
GRAY_BLUE = (81, 126, 173)
PURPLE = (166, 0, 255)

class Human:
    id = 0
    firstname = ""
    lastname = ""
    age = 0
    immunity = 0  # immunity level against a virus of the same or lower stage
    social_rang = 0 # communication level (from 0 to 10)
    travel_rang = 0 # travel level (from 0 to 10)
    # location on the map:
    pos_x = 0
    pos_y = 0
    continent = ""
    infection = False # checks whether the person is infected
    alive = True # checks whether the person is alive
    virus_level = 1
    die_chance = 0.00
    color = (0,0,0)
    # creating a person;
    # since there is a subclass and Python has no overloading, if-else is used
    def __init__(self, id, x, y, cont,inf = False,f_name = "None",l_name = "None",ag = 0,s_r = 0,t_r = 0, imun = 0):
        if f_name == "None":
            # when creating a person, a random name, surname, age, communication level, and travel level are used
            # names are not used in the game since this is a future part of the gameplay
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
        # if the person is not infected, assigns a color based on their immunity level:
        if not inf:
            self.infection = False
            if self.immunity == 0:
                self.color = DARK_GREEN
            elif self.immunity == 1:
                self.color = BLUE
            elif self.immunity == 2:
                self.color = LIGHTBLUE
            elif self.immunity == 3:
                self.color = DARK_BLUE
            else:
                self.color = GRAY_BLUE

        self.id = id
        self.continent = cont
        self.pos_x = x
        self.pos_y = y

    # if a person talks to an infected one, they have a 50% chance of getting infected:
    def try_infection(self):
        return random.uniform(0, 1) <= 0.5

class Infected(Human):
    # virus life is determined based on the human age
    # in the future, new variables may be added that will affect life and infection:
    virus_live = 0
    streak = 0 # counter for how long the virus has lived
    def __init__(self, human, v_lvl, immun):
        super().__init__(human.id,human.pos_x, human.pos_y,human.continent, True,human.firstname, human.lastname,
                         human.age, human.social_rang, human.travel_rang, immun)
        self.infection = True
        self.virus_live = int(0.346*human.age + 2.308)
        self.virus_level = v_lvl
        # assigns a color depending on the virus stage:
        if self.virus_level == 1:
            self.color = RED
        elif self.virus_level == 2:
            self.color = PINK
        elif self.virus_level == 3:
            self.color = ORANGE
        else:
            self.color = PURPLE
        # starting from the second virus stage, the person has a chance to die:
        self.die_chance = (self.virus_live - 1) * 0.0015

    # only infected have a chance to travel, based on their travel level:
    def try_travel(self):
        chance = 0.005*self.travel_rang
        return random.uniform(0,1)<= chance

    # only infected have a chance to talk to a healthy person, depending on their communication level:
    def try_speek(self, human):
        if human.immunity < self.virus_level:
            chance = (0.1 * self.social_rang) * (0.1 * human.social_rang)
            return random.uniform(0, 1) <= chance
        else: return False

    # updates information about the infected
    def update(self):
        if self.alive:
            self.streak += 1
            if self.virus_level > 1:
                if random.uniform(0,1) < self.die_chance:
                    self.alive = False
                    self.color = BLACK
            # if the virus lives for 17 stages, it advances to the next level up to level 4
            # at level 4 a new mechanic appears — heal
            if self.streak == 17 and self.virus_level < 4:
                self.virus_level += 1
                if self.virus_level != 4:
                    # the chance to die increases with each new level (from 0.15% to 0.30%)
                    self.die_chance = (self.virus_level - 1) * 0.0015
                    # adds virus life when advancing to the next level (from 5 to 20):
                    self.virus_live += random.randint(5,20)
                else:
                    # at the final level, the virus has only 10 lives and a 5% chance to die:
                    self.die_chance = 0.05
                    self.virus_live = 10
                self.immunity += 1
                self.streak = 0
                if self.virus_level == 2:
                    self.color = PINK
                elif self.virus_level == 3:
                    self.color = ORANGE
                else:
                    self.color = PURPLE

    # attempts to heal the person based on their age (more parameters may be added in the future);
    # if successful, the virus loses one life
    def try_heal(self):
        chance = -0.004*self.age + 0.36
        if random.uniform(0,1) < chance:
            self.virus_live -= 1