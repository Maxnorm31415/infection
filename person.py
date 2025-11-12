import random

DARK_GREEN = (14, 112, 7)
RED = (176, 0, 0)

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
    color = (0,0,0)
    def __init__(self, id, x, y, cont,f_name = "None",l_name = "None",ag = 0,s_r = 0,t_r = 0, imun = 0):
        if f_name == "None":
            self.firstname = random.choice(["Alex", "Maya", "Leo", "Sophie", "Ethan", "Luna", "Oliver", "Isla", "Noah", "Aria"])
            self.lastname = random.choice(["Johnson", "Carter", "Bennett", "Miller", "Collins", "Smith", "Brown", "Davis", "Wilson", "Clark"])
            self.age = random.randint(15,80)
            self.social_rang = random.randint(1,10)
            self.travel_rang = random.randint(1,10)
            self.color = DARK_GREEN
        else:
            self.firstname = f_name
            self.lastname = l_name
            self.age = ag
            self.immunity = imun
            self.social_rang = s_r
            self.travel_rang = t_r
            self.color = RED
        self.id = id
        self.continent = cont
        self.pos_x = x
        self.pos_y = y

    def try_speek(self, human):
        chance = (0.1 * self.social_rang) * (0.1 * human.social_rang)
        return random.uniform(0, 1) <= chance

    def try_infection(self):
        return random.uniform(0, 1) <= 0.5

class Infected(Human):
    virus_live = 0
    virus_level = 1
    def __init__(self, human):
        super().__init__(human.id,human.pos_x, human.pos_y,human.continent,human.firstname, human.lastname, human.age, human.social_rang, human.travel_rang)
        self.infection = True
        self.virus_live = int(0.346*human.age + 2.308)

    def try_travel(self):
        chance = 0.015*self.travel_rang
        return random.uniform(0,1)<= chance

