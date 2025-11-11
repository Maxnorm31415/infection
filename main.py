import pygame, random
import numpy as np
from person import Human, Infected

h1 = Human(0,0)
h2 = Human(0,0)
i1 = Infected(h1)
num = 0
for i in range(100):
    b = i1.try_speek(h2)
    print(b)
    if b: num += 1
print(num)
print(i1.social_rang)
print(h2.social_rang)