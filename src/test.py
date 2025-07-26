
for level in range(1,50):
    kills = level*10
    damage = 50 + 4*level
    hp = (kills/2)*10
    print("level:", level,
          "damage:", damage,
          "hp:", hp)