"""
Задание 1.
Посмотреть документацию к API GitHub, разобраться как вывести список репозиториев
для конкретного пользователя, сохранить JSON-вывод в файле *.json;
написать функцию, возвращающую список репозиториев.
"""

import requests
import json
import os
from pprint import pprint
from pathlib import Path

data_path = Path("repositories-data")

headers = {
    "Accept": "application/vnd.github.v3+json"
}


def get_user_repositories(user_name):
    """возвращает json с данными о репозиториях user_name"""
    url = "https://api.github.com/users/" + user_name + "/repos"
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None


def print_repositories_names(user_name, repositories):
    print(f"Repositories for user: {user_name}")
    pprint([repo['name'] for repo in repositories])
    print()


def save_user_repositories(user_name, repositories):
    filename = data_path / (user_name + ".json")
    data_path.mkdir(exist_ok=True)
    with open(filename, 'w') as f:
        json.dump(repositories, f)


def load_user_repositories(user_name):
    filename = data_path / (user_name + ".json")
    with open(filename) as f:
        return json.load(f)


user_names = ["vasily-muravyev", "eugeneyan", "Dyakonov"]
users_repos = list(map(get_user_repositories, user_names))

for user, repos in zip(user_names, users_repos):
    print_repositories_names(user, repos)
    save_user_repositories(user, repos)

my_repos = load_user_repositories(user_names[0])
print_repositories_names(user_names[0], my_repos)