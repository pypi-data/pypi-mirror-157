#!/usr/bin/python3
# Author: https://vk.com/id181265169
# https://github.com/fgRuslan/vk-spammer
import argparse
import vk_api
import random
import time
from python3_anticaptcha import ImageToTextTask

import threading
import sys
import os
import platform
import json

HOME_PATH = os.path.expanduser("~")
SPAMMER_PATH = os.path.join(HOME_PATH + "/" + ".vk-spammer/")
MESSAGES_PATH: str = os.path.join(SPAMMER_PATH, "messages.txt")
AUTH_PATH: str = os.path.join(SPAMMER_PATH, "auth.dat")

spamming_online_users = False
spamming_friends = False
use_token = False

# Данные из Kate mobile
API_ID = "2685278"
API_SECRET = "hHbJug59sKJie78wjrH8"

ANTICAPTCHA_KEY = ''

username = None
password = None

# Если директории с настройками спамера нет, создать её
if not os.path.exists(SPAMMER_PATH):
    os.mkdir(SPAMMER_PATH)

API_VERSION = 5.131

DEFAULT_DELAY = 4  # Количество секунд задержки

auth_data = {}

vk_session = None

# -------------------------------------------
# Сообщения, которые будет отправлять спаммер
messages = []

if os.path.exists(MESSAGES_PATH):
    with open(MESSAGES_PATH, 'r', encoding="utf-8") as f:
        for line in f:
            messages.append(line)
else:
    messages = [
        "hi",
        "2",
        "3",
        "fuck",
        "5"
    ]
    # Создаём файл messages.txt и записываем стандартные сообщения для примера
    with open(MESSAGES_PATH, "w", encoding="utf-8") as f:
        f.writelines(f"{x}\n" for x in messages)

# -------------------------------------------
# Сохраняем введённые данные авторизации в файл auth.dat


def do_save_auth_data():
    with open(AUTH_PATH, "w+", encoding="utf-8") as f:
        json.dump(auth_data, f)

# Загружаем данные авторизации из файла auth.dat


def load_auth_data():
    global auth_data
    if os.path.exists(AUTH_PATH):
        with open(AUTH_PATH, 'r', encoding="utf-8") as f:
            obj = json.load(f)
        auth_data = obj
        return True
    return False


def remove_auth_data():
    print("Удаляю текущие данные авторизации...")
    os.remove(AUTH_PATH)
# -------------------------------------------


class MainThread(threading.Thread):
    def run(self):
        if(len(messages) == 0):
            print("Список сообщений пуст. Запустите спамер с параметром -e (vk-spammer -e) чтобы ввести список сообщений.")
            sys.exit(0)
        print("-" * 4)
        print("Задержка: ", args.delay)
        print("-" * 4)
        print("Нажмите Ctrl+C чтобы остановить")

        delay = args.delay
        if spamming_online_users:
            friend_list = vk_session.method('friends.search', {"is_closed": "false",
                                                               "can_access_closed": "true", 'can_write_private_message': 1, 'count': 1000,
                                                               'fields': 'online'})['items']
            while(True):
                try:
                    msg = random.choice(messages)
                    for friend in friend_list:
                        if friend['online'] == 0:
                            continue
                        victim_id = int(friend['id'])
                        vk.messages.send(
                            user_id=victim_id, message=msg, v=API_VERSION, random_id=random.randint(0, 10000))
                        print("Отправлено: ", msg, " получателю: ", victim_id)
                    time.sleep(delay)
                except vk_api.exceptions.ApiError as e:
                    print("ОШИБКА!")
                    print(e)
                except Exception as e:
                    print(e)
        elif spamming_friends:
            friend_list = vk_session.method('friends.search', {"is_closed": "false",
                                                               "can_access_closed": "true", 'can_write_private_message': 1, 'count': 1000,
                                                               'fields': 'online'})['items']
            while(True):
                try:
                    msg = random.choice(messages)
                    for friend in friend_list:
                        victim_id = int(friend['id'])
                        if(hasattr(friend, 'deactivated')):
                            continue
                        vk.messages.send(
                            user_id=victim_id, message=msg, v=API_VERSION, random_id=random.randint(0, 10000))
                        print("Отправлено: ", msg, " получателю: ", victim_id)
                    time.sleep(delay)
                except vk_api.exceptions.ApiError as e:
                    print("ОШИБКА!")
                    print(e)
                except Exception as e:
                    print(e)
        else:
            while(True):
                try:
                    msg = random.choice(messages)
                    print(victim)
                    vk.messages.send(
                        peer_id=victim, message=msg, v=API_VERSION, random_id=random.randint(0, 10000))
                    print("Отправлено: ", msg)
                    time.sleep(delay)
                except vk_api.exceptions.ApiError as e:
                    print("ОШИБКА!")
                    print(e)
                except Exception as e:
                    print(e)


def main():
    try:
        thread = MainThread()
        thread.daemon = True
        thread.start()

        while thread.is_alive():
            thread.join(1)
    except KeyboardInterrupt:
        print("Нажали Ctrl+C, выходим...")
        sys.exit(1)


# -------------------------------------------
# Парсер аргументов
parser = argparse.ArgumentParser(description='Spam settings:')
parser.add_argument(
    '-d',
    '--delay',
    type=int,
    default=DEFAULT_DELAY,
    help='Delay (default: 4)'
)
parser.add_argument('-e', '--editmessages', action='store_true',
                    help='Use this argument to edit the message list')
parser.add_argument('-r', '--removedata', action='store_true',
                    help='Use this argument to delete auth data (login, password)')
args = parser.parse_args()
# -------------------------------------------

if(args.editmessages):
    if platform.system() == "Windows":
        os.system("notepad.exe " + SPAMMER_PATH + "messages.txt")
    if platform.system() == "Linux":
        os.system("nano " + SPAMMER_PATH + "messages.txt")
    print("Перезапустите спамер, чтобы обновить список сообщений")
    exit(0)

if(args.removedata):
    remove_auth_data()


# Пытаемся загрузить данные авторизации из файла
# Если не удалось, просим их ввести
load_result = load_auth_data()
if(load_result == False):
    username = input("Login (или токен): ")
    if len(username) == 85:
        use_token = True
    if not use_token:
        password = input("Пароль: ")
    else:
        password = ''
    save_auth_data = input("Сохранить эти данные авторизации? (Y/n): ")

    if(save_auth_data == "Y" or save_auth_data == "y" or save_auth_data == ""):
        auth_data['username'] = username
        auth_data['password'] = password
        do_save_auth_data()
else:
    print("Данные авторизации получены из настроек")
    username = auth_data['username']
    password = auth_data['password']
    if len(username) == 85:
        use_token = True


def captcha_handler(captcha):
    if ANTICAPTCHA_KEY == '':
        solution = input("Решите капчу ({0}): ".format(captcha.get_url()))
        return captcha.try_again(solution)
    key = ImageToTextTask.ImageToTextTask(
        anticaptcha_key=ANTICAPTCHA_KEY, save_format='const').captcha_handler(captcha_link=captcha.get_url())
    return captcha.try_again(key['solution']['text'])


def auth_handler():
    key = input("Введите код подтверждения: ")
    remember_device = True
    return key, remember_device


# -------------------------------------------
# Логинимся и получаем токен
anticaptcha_api_key = input(
    "API ключ от anti-captcha.com (оставьте пустым если он не нужен): ")
if anticaptcha_api_key == '':
    if use_token:
        vk_session = vk_api.VkApi(
            token=username, auth_handler=auth_handler, app_id=API_ID, client_secret=API_SECRET)
    else:
        vk_session = vk_api.VkApi(
            username, password, auth_handler=auth_handler, app_id=API_ID, client_secret=API_SECRET)
else:
    ANTICAPTCHA_KEY = anticaptcha_api_key
    if use_token:
        vk_session = vk_api.VkApi(token=username, captcha_handler=captcha_handler,
                                  auth_handler=auth_handler, app_id=API_ID, client_secret=API_SECRET)
    else:
        vk_session = vk_api.VkApi(username, password, captcha_handler=captcha_handler,
                                  auth_handler=auth_handler, app_id=API_ID, client_secret=API_SECRET)

try:
    vk_session.auth(token_only=True)
except vk_api.AuthError as error_msg:
    print(error_msg)

vk = vk_session.get_api()


# -------------------------------------------
# Преобразовываем введённый id пользователя в цифровой формат

print()
print("Укажите id жертвы.")
print("Чтобы спамить своим друзьям, укажите #friends.")
print("Чтобы спамить друзьям, которые сейчас в сети, укажите #online.")
print("Чтобы спамить в беседу, укажите её id как в примере: #c375")
print("375 - это id беседы")
print()
victim = input("id жертвы: ")

if victim == "#online":
    spamming_online_users = True
elif victim == "#friends":
    spamming_friends = True
elif victim.startswith("#c"):
    victim = victim.replace("#c", "")
    victim = int(victim) + 2000000000
else:

    victim = victim.split("/")
    victim = victim[len(victim) - 1]

    if victim.isdigit():
        victim = victim
    else:
        print("Распознаём id...")
        r = vk.utils.resolveScreenName(screen_name=victim, v=API_VERSION)
        victim = r["object_id"]
        print("id: " + str(victim))

    r = vk.users.get(user_id=victim, fields="id", v=API_VERSION)
    r = r[0]["id"]

    victim = r
# -------------------------------------------
# Запускатор главного потока
main()
