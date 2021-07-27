# -*- coding: utf-8 -*-

from astrobox.space_field import SpaceField
from devastator import DevastatorDrone
from Kudryavtsev import KudryavtsevDrone

NUMBER_OF_DRONES = 5

if __name__ == '__main__':
    scene = SpaceField(
        field=(1200, 900),
        speed=10,
        asteroids_count=27,
        can_fight=True,
    )

    team_1 = [KudryavtsevDrone() for _ in range(NUMBER_OF_DRONES)]
    team_2 = [DevastatorDrone() for _ in range(NUMBER_OF_DRONES)]
    scene.go()
