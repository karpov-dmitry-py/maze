# -*- coding: utf-8 -*-

# Подземелье было выкопано ящеро-подобными монстрами рядом с аномальной рекой, постоянно выходящей из берегов.
# Из-за этого подземелье регулярно затапливается, монстры выживают, но не герои, рискнувшие спуститься к ним в поисках
# приключений.
# Почуяв безнаказанность, ящеры начали совершать набеги на ближайшие деревни. На защиту всех деревень не хватило
# солдат и вас, как известного в этих краях героя, наняли для их спасения.
#
# Карта подземелья представляет собой json-файл под названием rpg.json. Каждая локация в лабиринте описывается объектом,
# в котором находится единственный ключ с названием, соответствующем формату "Location_<N>_tm<T>",
# где N - это номер локации (целое число), а T (вещественное число) - это время,
# которое необходимо для перехода в эту локацию. Например, если игрок заходит в локацию "Location_8_tm30000",
# то он тратит на это 30000 секунд.
# По данному ключу находится список, который содержит в себе строки с описанием монстров а также другие локации.
# Описание монстра представляет собой строку в формате "Mob_exp<K>_tm<M>", где K (целое число) - это количество опыта,
# которое получает игрок, уничтожив данного монстра, а M (вещественное число) - это время,
# которое потратит игрок для уничтожения данного монстра.
# Например, уничтожив монстра "Boss_exp10_tm20", игрок потратит 20 секунд и получит 10 единиц опыта.
# Гарантируется, что в начале пути будет две локации и один монстр
# (то есть в коренном json-объекте содержится список, содержащий два json-объекта, одного монстра и ничего больше).
#
# На прохождение игры игроку дается 123456.0987654321 секунд.
# Цель игры: за отведенное время найти выход ("Hatch")
#
# По мере прохождения вглубь подземелья, оно начинает затапливаться, поэтому
# в каждую локацию можно попасть только один раз,
# и выйти из нее нельзя (то есть двигаться можно только вперед).
#
# Чтобы открыть люк ("Hatch") и выбраться через него на поверхность, нужно иметь не менее 280 очков опыта.
# Если до открытия люка время заканчивается - герой задыхается и умирает, воскрешаясь перед входом в подземелье,
# готовый к следующей попытке (игра начинается заново).
#
# Гарантируется, что искомый путь только один, и будьте аккуратны в расчетах!
# При неправильном использовании библиотеки decimal человек, играющий с вашим скриптом, рискует никогда не найти путь.
#
# Также, при каждом ходе игрока ваш скрипт должен запоминать следущую информацию:
# - текущую локацию
# - текущее количество опыта
# - текущие дату и время (для этого используйте библиотеку datetime)
# После успешного или неуспешного завершения игры вам необходимо записать
# всю собранную информацию в csv файл dungeon.csv.
# Названия столбцов для csv файла: current_location, current_experience, current_date
#
#
# Пример взаимодействия с игроком:
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло времени: 00:00
#
# Внутри вы видите:
# — Вход в локацию: Location_1_tm1040
# — Вход в локацию: Location_2_tm123456
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали переход в локацию Location_2_tm1234567890
#
# Вы находитесь в Location_2_tm1234567890
# У вас 0 опыта и осталось 0.0987654321 секунд до наводнения
# Прошло времени: 20:00
#
# Внутри вы видите:
# — Монстра Mob_exp10_tm10
# — Вход в локацию: Location_3_tm55500
# — Вход в локацию: Location_4_tm66600
# Выберите действие:
# 1.Атаковать монстра
# 2.Перейти в другую локацию
# 3.Сдаться и выйти из игры
#
# Вы выбрали сражаться с монстром
#
# Вы находитесь в Location_2_tm0
# У вас 10 опыта и осталось -9.9012345679 секунд до наводнения
#
# Вы не успели открыть люк!!! НАВОДНЕНИЕ!!! Алярм!
#
# У вас темнеет в глазах... прощай, принцесса...
# Но что это?! Вы воскресли у входа в пещеру... Не зря матушка дала вам оберег :)
# Ну, на этот-то раз у вас все получится! Трепещите, монстры!
# Вы осторожно входите в пещеру... (текст умирания/воскрешения можно придумать свой ;)
#
# Вы находитесь в Location_0_tm0
# У вас 0 опыта и осталось 123456.0987654321 секунд до наводнения
# Прошло уже 0:00:00
# Внутри вы видите:
#  ...
#  ...
#
# и так далее...


# remaining_time = '123456.0987654321'
# # если изначально не писать число в виде строки - теряется точность!
# field_names = ['current_location', 'current_experience', 'current_date']

import datetime
import logging
import json
import re
import csv
import os.path
from decimal import *
from collections import defaultdict


class Player:

    remaining_time_str = '123456.0987654321'
    exp_required_to_open_hatch = 280
    exp_re_pattern = re.compile(r'exp([0-9]+)_')
    time_re_pattern = re.compile(r'tm([0-9.]+)')

    @classmethod
    def _setup_logging(cls):
        cls.logger = logging.getLogger('maze_logger')
        cls.logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('{message}', style='{')

        stream_handler = logging.StreamHandler()
        stream_handler.setLevel(logging.DEBUG)
        stream_handler.setFormatter(formatter)

        cls.logger.addHandler(stream_handler)

    def log(self, message):
        Player.logger.info(message)

    def __init__(self, name='Lucky bastard'):
        self.name = name
        self.state = {'location': 'cave entrance', 'experience': 0}
        self.history = []
        self.remaining_time = Decimal(Player.remaining_time_str)
        self.killed_mobs = self._get_killed_mobs_new_dict()  # убитые в рамках одной конкретной локации мобы
        self._capture_current_state()
        self.log('***** --------------- НАЧИНАЕТСЯ НОВАЯ ИГРА --------------- *****\n\n')

    def __str__(self):
        return f'Игрок "{self.name}", тек. локация: {self.state["location"]}, опыт: {self.state["experience"]}, ' \
               f'осталось времени: {self.remaining_time} сек.'

    def _get_killed_mobs_new_dict(self):
        return defaultdict(int)

    def _format_time(self, time: datetime.datetime):
        time_format = '%d.%m.%Y %H:%M:%S'
        return time.strftime(time_format)

    def _deduct_time(self, object: str):

        match = re.search(Player.time_re_pattern, object)

        if not match:
            return

        time_spent_on_object = Decimal(match.group(1))
        if not int(time_spent_on_object):
            return

        self.remaining_time -= time_spent_on_object

    def _capture_current_state(self, location=None, experience=0):
        self.state['location'] = location if location else self.state['location']
        self.state['experience'] += experience
        self.state['time'] = datetime.datetime.now()

        current_state = {}
        current_state.update(self.state)
        self.history.append(current_state)

    def save_history(self):

        now = datetime.datetime.now().strftime('%d.%m.%Y_%H_%M_%S')
        out_filename = os.path.join(os.path.dirname(__file__), f'dungeon_{now}.csv')
        out_filename = os.path.normpath(out_filename)
        with open(out_filename, 'w', newline='') as out:
            writer = csv.DictWriter(out, fieldnames=self.history[0], delimiter=',')
            writer.writeheader()
            for state in self.history:
                state['time'] = self._format_time(state['time'])
                try:
                    writer.writerow(state)
                except ValueError as exc:
                    self.log(f'Возникла ошибка при записи истории игрока {self.name} в csv-файл: '
                             f'{exc.__class__.__name__}, {exc.args}')
            self.log(f'История игры игрока "{self.name}" сохранена в файл: {out_filename}')

    def _get_location_as_str(self, location: (dict, str)):
        result = tuple(location.keys())[0] if isinstance(location, dict) else location
        return result

    def _get_available_actions(self, location: dict):

        location_as_str = self._get_location_as_str(location)
        location_content = location.get(location_as_str)  # содержимое текущей локации по ключу-имени локации
        actions = []

        #  все мобы в этой локации
        mobs = defaultdict(int)
        for mob in location_content:
            if not isinstance(mob, str):
                continue
            mobs[mob] += 1

        # оставим только живых (еще не убитых) мобов в этой локации
        for mob, killed_count in self.killed_mobs.items():
            mobs[mob] -= killed_count

        for action in location_content:

            row = {}
            row['action'] = action

            if isinstance(action, dict):
                action_as_str = self._get_location_as_str(action)

                # люк
                if self._is_hatch(action_as_str):
                    row['info'] = f'!!! Выбраться через ЛЮК {action_as_str} на свободу !!!'
                    row['type'] = 'hatch'
                # локация
                else:
                    row['info'] = f'Шагнуть дальше в локацию {action_as_str}'
                    row['type'] = 'location'

            # проверка, сколько таких мобов игрок уже убил в этой локации
            elif isinstance(action, str):

                if mobs[action] <= 0:
                    continue
                mobs[action] -= 1

                row['info'] = f'Сразиться с монстром {action} и получить опыт'
                row['type'] = 'mob'

            actions.append(row)

        actions.append({'info': 'Завершить текущую игру.', 'type': 'quit'})
        return actions

    def _show_available_actions(self, actions):

        self.log('* --- Ваше текущее состояние --- *:')
        self.log(f'{self}\n')
        self.log('Введите номер нужного действия далее:')

        for i, action in enumerate(actions, start=1):
            self.log(f'<{i}>. {action["info"]}')

    def _dead_end_ahead(self, actions):
        return all(row['type'] == 'mob' for row in actions)

    def _get_user_choice(self, actions):

        bad_input = False
        while True:
            self.log('>>>> ')
            try:
                choice = int(input().strip())
                if not (1 <= choice <= len(actions)):
                    bad_input = True

            except (ValueError, TypeError):
                bad_input = True

            if bad_input:
                self.log('Неверный ввод. Попробуйте снова.')
                bad_input = False
                continue

            return actions[choice - 1]

    def _fight_mob(self, mob: str):

        # опыт
        experience_gained = 0
        match = re.search(Player.exp_re_pattern, mob)
        if match:
            experience_gained = int(match.group(1))
            self.state['experience'] += experience_gained

        # время
        self._deduct_time(mob)

        #  убитый моб
        self.killed_mobs[mob] += 1

        # информация
        success_message = f'Отлично! Вы победили монстра {mob} и получили {experience_gained} очков(-а) опыта!'
        self.log(success_message)

    def _is_hatch(self, location: str):
        return 'hatch' in location.lower()

    def _is_game_over(self):

        game_over = self.remaining_time <= 0
        if game_over:
            self.log('Вы не успели! Время закончилось! Игра завершена!\n')
            return True

        return False

    def handle_location(self, location: (dict, str), first_time_here=True):

        location_as_str = self._get_location_as_str(location)

        # игрок здесь первый раз (иначе же он 'вернулся' сюда после убийста моба или попытки открыть люк)
        if first_time_here:
            self.killed_mobs = self._get_killed_mobs_new_dict()
            self._deduct_time(location_as_str)

        # фиксация состояния
        self._capture_current_state(location=location_as_str)

        # проверка на остаток времени
        if self._is_game_over():
            return

        # проверка наличия люка
        if self._is_hatch(self.state['location']):
            self.log('Ура! Вот и люк! Вы выбрались! Игра успешно пройдена!')
            self._capture_current_state(location='cave exit')
            return

        # доступные действия
        actions = self._get_available_actions(location)

        if self._dead_end_ahead(actions):
            self.log('Впереди нет новых локаций! Некуда идти! Вы проиграли!')
            return

        self._show_available_actions(actions)

        # выбор следующего шага пользователем
        chosen_action = self._get_user_choice(actions)
        choice_as_str = f'Вы выбрали: {chosen_action["info"]}\n'
        self.log(choice_as_str)

        # обработка сделанного выбора
        if chosen_action['type'] == 'quit':
            return

        elif chosen_action['type'] == 'location':
            self.handle_location(chosen_action['action'])

        elif chosen_action['type'] == 'hatch':

            # проверка опыта
            exp_lack = Player.exp_required_to_open_hatch - self.state['experience']

            # возврат в меню текущей локации
            if exp_lack > 0:
                self.log(f'Не хватает опыта для открытия люка: {exp_lack}! Сразитесь с монстрами для увеличения опыта!')
                self.handle_location(location, first_time_here=False)

            self.handle_location(chosen_action['action'])

        elif chosen_action['type'] == 'mob':
            # схватка с мобом
            mob = chosen_action['action']
            self._fight_mob(mob)

            # возврат в меню текущей локации
            self.handle_location(location, first_time_here=False)


def new_game(maze):
    player = Player()
    player.handle_location(maze)
    player.save_history()

    # начать новую игру
    expected_yes = 'Y'
    player.log(f'Начать новую игру? (введите {expected_yes} для начала новой игры) >>>> ')
    play_again = input() == expected_yes

    if play_again:
        player = None
        new_game(maze)


def main():
    Player._setup_logging()

    with open('rpg.json') as source:
        maze = json.load(source)

    with localcontext() as ctx:
        ctx.prec = 50
        new_game(maze)


if __name__ == '__main__':
    main()
