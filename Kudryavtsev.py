# -*- coding: utf-8 -*-

from astrobox.core import Drone
from robogame_engine.geometry import Point
from robogame_engine.geometry import Vector
from robogame_engine.theme import theme


class KudryavtsevDrone(Drone):
    my_team = []  # Список команды
    statistics = {'call-console': 0, 'empty': 0, 'half-full': 0, 'full': 0}  # Сбор информации по полёту

    def __init__(self, **kwargs):
        """
        Иницилизация.
        """
        super().__init__(**kwargs)
        self.drone_number = 0
        self.near_asteroids = None
        self.enemies = []
        self.enemies_ships = []
        self.dead_drones = []
        self.is_busy = False
        self.dead_ship = []
        self.distance_2000 = 2000
        self.distance_700 = 700
        self.health_drone = 90
        self.circle = 150
        self.distance_150 = 150
        self.distance_300 = 300
        self.count_elerium = 700

    def on_born(self):
        """
        Метод возраждения и первый полёт до ближайшей точки
        """
        self.drone_number = len(self.my_team)  # Вычисляем кол-во дронов
        self.my_team.append(self.drone_number)  # Добавляем номера дронов в команду
        self.collect_resource()

    def on_stop_at_asteroid(self, asteroid):
        """
        Метод остановки на астероиде
        """
        if self.is_empty:  # Если дрон пустой, то повернись к союзному кораблю и загрузи элериум с астероида.
            self.is_busy = False
            self.turn_to(self.mothership)
            self.load_from(asteroid)
        elif not self.is_full and not self.is_empty:  # Если дрон не полный и не пустой, то повернись к след. астероиду
            # и загружай элериаум.
            self.turn_to(self.next_asteroid())
            self.load_from(asteroid)

    def on_load_complete(self):
        """
        Метод завершения загрузки элериума
        """
        if self.is_empty:  # Если дрон пустой, то внеси дистанцию в статистику и отправь дрона к след. астероиду
            self.is_busy = False
            self.statistics['empty'] += int(self.distance_to(self.next_asteroid()))
            self.move_at(self.next_asteroid())
        elif not self.is_full and not self.is_empty:  # Если дрон не полный и не пустой, то внеси дистанцию
            # в статистику и отправь дрона к след. астероиду
            self.statistics['half-full'] += int(self.distance_to(self.next_asteroid()))
            self.move_at(self.next_asteroid())
        elif self.is_full:  # Если дрон полный, то внеси дистанцию в статистику и отправь дрона на базу
            self.is_busy = True
            self.statistics['full'] += int(self.distance_to(self.mothership))
            self.move_at(self.mothership)

    def on_stop_at_mothership(self, mothership):
        """
        Метод остановки на союзной базе
        """
        if all(not asteroid.is_empty for asteroid in self.asteroids):
            self.collect_resource()
        self.is_busy = True
        self.turn_to(self.next_asteroid())  # Повернись к след астероиду и разгрузи элериум на базу
        if self.team == mothership.team:
            self.unload_to(mothership)
        else:
            self.load_from(mothership)
            self.is_busy = True

    def on_unload_complete(self):
        """
        Метод завершения разгрузки элериума
        """
        self.is_busy = False
        if self.is_empty:  # Если дрон пустой, то запиши в статистику и лети на след. астероид
            if len(self.dead_drones) >= 15 and len(self.dead_ship) == 3:
                self.move_at(self.dead_ship[0])
            self.statistics['empty'] += int(self.distance_to(self.next_asteroid()))
            self.near_asteroids = [asteroid for asteroid in self.asteroids if
                                   self.distance_to(asteroid) < self.distance_2000 and asteroid.counter]
            if self.near_asteroids:  # Берем ближайший астероид
                self.near_asteroids.sort(key=lambda x: self.distance_to(x))  # Сортируем астероиды
                if len(self.near_asteroids) < 5:  # Если кол-во астероидов меньше 5, то летим к ближайшему оставш.!
                    self.move_at(self.near_asteroids[0])
                else:  # Иначе летим к ближайшим всей командой.
                    self.move_at(self.near_asteroids[self.drone_number])

    def stat_in_console(self):
        """
        Метод вывода статистики на консоль
        """
        total_distance = sum(self.statistics.values())  # Создаём общую дистанцию
        if self.statistics['call-console'] == 0:  # Проверяем - вызывалось ли статистика хоть раз, если нет, то вызовем
            print(f'В общем дроны пролетели с пустым трюмом {int((self.statistics["empty"] / total_distance) * 100)}%, '
                  f'с полу-полным трюмом пролетели {int((self.statistics["half-full"] / total_distance) * 100)}% '
                  f'и с полным трюмом пролетели {int((self.statistics["full"] / total_distance) * 100)}%.\n'
                  f'Общее пройденное расстояние в космосе {total_distance} метр(ов).')
            self.statistics['call-console'] = 1
        else:
            pass

    def next_asteroid(self):
        """
        Метод на проверку ближайшего астероида
        """
        nearest_point = self.mothership
        distance_to_the_nearest_point = self.distance_2000
        for asteroid in self.asteroids:  # Проходим циклом for по астероидам.
            if asteroid.counter and self.distance_to(asteroid) < distance_to_the_nearest_point:  # Проверяем кол-во
                # элериума на астероиде. И если дистанция до астер. меньше 2к, то летим до него
                nearest_point = asteroid
                distance_to_the_nearest_point = self.distance_to(asteroid)
        return nearest_point  # Возвращаем точку

    def enemy_information(self):
        """
        Метод для сбора информации о вражеском дроне
        """
        for drone in self.scene.drones:  # Проходимся по дронам
            if drone.team != self.team:  # Проверям вражеский дрон или нет
                if drone.is_alive:  # Живой ли вражеский дрон
                    self.enemies = [[enemy, self.distance_to(enemy)]
                                    for enemy in self.scene.drones
                                    if enemy.team != self.team
                                    and enemy.is_alive and enemy not in self.enemies]  # Нашёл врага
                    self.enemies.sort(key=lambda x: x[1])  # Отсортировал врагов.
                    nearest_enemy = self.enemies[0][0]  # Получаем ближайшего врага
                    self.destroy_enemies(drone, nearest_enemy)  # Уничтожаем вражеский дрон
                else:
                    if drone in self.dead_drones:  # Если дрон мертв, то продолжаем проверять
                        continue
                    else:
                        self.dead_drones.append(drone)  # Добавлем вражеского мертвого дрона в список
            else:
                self.collect_all_resource()  # Идём собирать все ресурсы

    def destroy_enemies(self, drone, nearest_enemy):
        """
        Метод для атаки вражеских дронов
        :param drone: Вражеский дрон
        :param nearest_enemy: Ближайший враг
        """
        list_defend_point = self.defender_point()
        list_attack_point = self.attack_point()
        if len(self.enemies) == 1:  # Если врагов меньше или равно двум
            if self.coord.x == list_attack_point[self.drone_number].x and \
                    self.coord.y == list_attack_point[self.drone_number].y:  # Если координата равна указаной
                # координате, то поворачиваемся к ближайшему врагу и расстреливаем
                self.turn_to(nearest_enemy)
                self.gun.shot(nearest_enemy)
            else:  # Иначе же летим к указанным координатам
                self.move_at(
                    Point(list_attack_point[self.drone_number].x, list_attack_point[self.drone_number].y))
        else:  # Если же дронов больше двух
            if self.distance_to(drone) <= 650:  # Проверяем дистанцию
                try:
                    if self.coord.x == list_defend_point[self.drone_number].x and \
                            self.coord.y == list_defend_point[self.drone_number].y:
                        self.turn_to(nearest_enemy)  # Поворачиваемся к ближайшему врагу
                        self.gun.shot(nearest_enemy)  # Стреляем в ближайшего врага
                    else:  # Иначе же летим к указанным координатам
                        self.point_stop()
                except IndexError:
                    return

    def point_stop(self):
        """
        Координаты для остановки дронов
        """
        list_defend_point = self.defender_point()
        if self.mothership.coord.x == self.mothership.coord.x and \
                self.mothership.coord.y == self.mothership.coord.y:
            self.move_at(list_defend_point[self.drone_number])  # Координаты при старте

    def collect_all_resource(self):
        """
        Метод для сбора всех ресурсов
        """
        self.near_asteroids = [asteroid for asteroid in self.asteroids if self.distance_to(asteroid) < self.distance_700
                               and not self.near(asteroid)
                               and not asteroid.is_empty]  # Находим ближайший и не пустой астероид
        if len(self.dead_drones) == len(self.scene.drones) - len(self.my_team) and self.near_asteroids:  # проверяем,
            # что все дроны мертвы, кроме союзных и есть ли ближайший астероид
            self.near_asteroids.sort(key=lambda x: self.distance_to(x))  # Сортируем астероиды
            if self.is_full:  # Если дрон полный, то внеси дистанцию в статистику и отправь дрона на базу
                self.statistics['full'] += int(self.distance_to(self.mothership))
                self.move_at(self.mothership)
            else:  # Если же дрон пустой, то внеси дистанцию в статистику и отправь дрона на базу
                next_asteroid = self.next_asteroid()
                self.statistics['empty'] += int(self.distance_to(next_asteroid))
                self.move_at(next_asteroid)

    def information_about_enemy_ship(self):
        """
        Метод для сбора информации о вражеском корабле
        """
        if all(asteroid.is_empty for asteroid in self.asteroids):  # Проверяем на пустоту всех астероидов
            for ship in self.scene.motherships:  # проходимся по кораблям
                if ship.team != self.team and ship.is_alive:  # Если корабль не союзный и живой
                    self.destroy_an_enemy_ship(ship)  # Уничтожить вражеский корабль
                elif not ship.is_alive:
                    if ship in self.dead_ship:  # Если дрон мертв, то продолжаем проверять
                        continue
                    else:
                        self.dead_ship.append(ship)  # Добавлем вражеского мертвого дрона в список
        else:  # Иначе же собираем весь ресурс
            self.collect_all_resource()

    def destroy_an_enemy_ship(self, ship):
        """
        Метод для атаки вражеских кораблей
        :param ship: Вражеский корабль
        """
        list_attack_point = self.attack_point()
        if self.distance_to(ship) < self.distance_2000:  # Проверяем дистанцию до корабля
            self.enemies_ships = [[enemy_ship, self.distance_to(enemy_ship)] for enemy_ship in
                                  self.scene.motherships if enemy_ship.team != self.team and
                                  enemy_ship.is_alive and enemy_ship not in self.enemies_ships]  # Находим вражеский
            # корабль
            self.enemies_ships.sort(key=lambda x: x[1])  # Отсортировал вражеские корабли.
            nearest_enemy_ship = self.enemies_ships[0][0]  # Получаем ближайший вражеский корабль
            if self.coord.x == list_attack_point[self.drone_number].x and \
                    self.coord.y == list_attack_point[self.drone_number].y:  # Если координата совпала
                # с указанной координатой, то поворачиваемся и стреляем в ближайшего врага
                self.turn_to(nearest_enemy_ship)
                self.gun.shot(nearest_enemy_ship)
            else:  # Иначе же лети к указанной координате
                self.move_at(
                    Point(list_attack_point[self.drone_number].x, list_attack_point[self.drone_number].y))

    def defender_point(self):
        """
        Метод для выставления дронов в защиту
        """
        center_field = Point(theme.FIELD_WIDTH // 2, theme.FIELD_HEIGHT // 2)
        vec_for_drones = Vector.from_points(self.mothership.coord, center_field, self.circle)
        vec_for_drone_first = vec_for_drones.copy()
        vec_for_drone_first.rotate(-45)
        vec_for_drone_third = vec_for_drones.copy()
        vec_for_drone_fifth = vec_for_drones.copy()
        vec_for_drone_fifth.rotate(45)
        list_defend_point = [
            Point(self.mothership.coord.x + vec_for_drone_third.x, self.mothership.coord.y + vec_for_drone_third.y),
            Point(self.mothership.coord.x + vec_for_drone_first.x, self.mothership.coord.y + vec_for_drone_first.y),
            Point(self.mothership.coord.x + vec_for_drone_fifth.x, self.mothership.coord.y + vec_for_drone_fifth.y),
        ]
        return list_defend_point

    def detachment_or_collection(self):
        """
        Метод для атаки или сбора ресурсов
        """
        if self.drone_number == 3 or self.drone_number == 4:
            if self.is_full and self.health >= self.health_drone:
                self.is_busy = True
                self.move_at(self.mothership)
            elif self.is_full and self.health <= self.health_drone:
                self.is_busy = True
                self.move_at(self.mothership)
            elif self.is_empty and self.health >= self.health_drone:
                self.is_busy = False
                self.move_at(self.next_asteroid())
            elif self.is_empty and self.health <= self.health_drone:
                self.is_busy = False
                self.move_at(self.mothership)
            elif not self.is_empty and not self.is_full and self.health >= self.health_drone:
                self.is_busy = True
                self.move_at(self.mothership)
            elif not self.is_empty and not self.is_full and self.health <= self.health_drone:
                self.is_busy = True
                self.move_at(self.mothership)

    def collect_the_remaining_resource(self):
        """
        Метод для сбора оставшегося ресурса
        """
        if len(self.dead_drones) >= len(self.scene.drones) - len(self.my_team):
            if self.dead_ship is False:
                self.move_at(self.my_mothership)
            if not self.dead_ship[0].is_empty:
                self.move_at(self.dead_ship[0])
                if self.is_full:
                    self.is_busy = True
                    self.move_at(self.mothership)
            elif self.dead_ship[0].is_empty:
                self.dead_ship.pop(0)

    def attack_point(self):
        """
        Метод для выставления дронов в атаку
        """
        center_field = Point(theme.FIELD_WIDTH // 2, theme.FIELD_HEIGHT // 2)
        vec_for_drones = Vector.from_points(self.mothership.coord, center_field)
        vec_for_drone_first = vec_for_drones.copy()
        vec_for_drone_first.y -= self.distance_300
        vec_for_drone_second = vec_for_drones.copy()
        vec_for_drone_second.y += self.distance_300
        vec_for_drone_third = vec_for_drones.copy()
        vec_for_drone_fourth = vec_for_drones.copy()
        vec_for_drone_fourth.y += self.distance_150
        vec_for_drone_fifth = vec_for_drones.copy()
        vec_for_drone_fifth.y -= self.distance_150
        list_attack_point = [
            Point(self.mothership.coord.x + vec_for_drone_third.x, self.mothership.coord.y + vec_for_drone_third.y),
            Point(self.mothership.coord.x + vec_for_drone_first.x, self.mothership.coord.y + vec_for_drone_first.y),
            Point(self.mothership.coord.x + vec_for_drone_second.x, self.mothership.coord.y + vec_for_drone_second.y),
            Point(self.mothership.coord.x + vec_for_drone_fourth.x, self.mothership.coord.y + vec_for_drone_fourth.y),
            Point(self.mothership.coord.x + vec_for_drone_fifth.x, self.mothership.coord.y + vec_for_drone_fifth.y),
        ]
        return list_attack_point

    def collect_resource(self):
        """
        Метод для сбора всех ресурсов
        """
        self.near_asteroids = [asteroid for asteroid in self.asteroids if self.distance_to(asteroid) < self.distance_700
                               and not asteroid.is_empty]  # Находим ближайший и не пустой астероид
        self.near_asteroids.sort(key=lambda x: self.distance_to(x))  # Сортируем астероиды
        if self.is_full:  # Если дрон полный, то внеси дистанцию в статистику и отправь дрона на базу
            self.is_busy = True
            self.statistics['full'] += int(self.distance_to(self.mothership))
            self.move_at(self.mothership)
        else:  # Если же дрон пустой, то внеси дистанцию в статистику и отправь дрона на базу
            self.is_busy = True
            self.statistics['empty'] += int(self.distance_to(self.near_asteroids[self.drone_number]))
            self.move_at(self.near_asteroids[self.drone_number])

    def on_heartbeat(self):
        # Переключатель для полной разгрузки.
        if self.is_empty:
            self.is_busy = False
        if self.is_busy:
            return
        # Проверка уничтоженных дронов и кораблей
        if len(self.dead_drones) >= len(self.scene.drones) - len(self.my_team):
            # Летим к первому по списку уничтоженных кораблей
            if not self.is_moving and self.coord.x == self.mothership.coord.x and \
                                      self.coord.y == self.mothership.coord.y:
                self.move_at(self.dead_ship[0])
        # Если на корабле 700 или более элериума, то встаём в защиту, а двух других дронов отпраляем на сбор ресурсов
        if self.mothership.payload >= self.count_elerium:
            self.detachment_or_collection()
            self.collect_the_remaining_resource()
            self.enemy_information()  # Собираем информацию о враге и уничтожаем
            if len(self.dead_drones) == len(self.scene.drones) - len(self.my_team):
                self.information_about_enemy_ship()  # Собираем информацию о вражеском корабле и уничтожаем
        elif self.mothership.payload >= self.distance_700 and all(asteroid.is_empty for asteroid in self.asteroids):
            self.detachment_or_collection()
            self.collect_the_remaining_resource()
            self.enemy_information()  # Собираем информацию о враге и уничтожаем
            if len(self.dead_drones) == len(self.scene.drones) - len(self.my_team):
                self.information_about_enemy_ship()  # Собираем информацию о вражеском корабле и уничтожаем
        elif self.mothership.payload <= self.distance_700 and all(asteroid.is_empty for asteroid in self.asteroids):
            if not self.is_empty:
                self.move_at(self.mothership)
            else:
                self.detachment_or_collection()
                self.collect_the_remaining_resource()
                self.enemy_information()  # Собираем информацию о враге и уничтожаем
                if len(self.dead_drones) == len(self.scene.drones) - len(self.my_team):
                    self.information_about_enemy_ship()  # Собираем информацию о вражеском корабле и уничтожаем


drone_class = KudryavtsevDrone
