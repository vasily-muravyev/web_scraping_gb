"""
1. Развернуть у себя на компьютере/виртуальной машине/хостинге MongoDB
 и реализовать функцию, записывающую собранные вакансии в созданную БД.

2. Написать функцию, которая производит поиск и выводит на экран вакансии
 с заработной платой больше введённой суммы, а также использование одновременно
 мин/макс зарплаты. Необязательно - возможность выбрать вакансии без указанных зарплат

3. Написать функцию, которая будет добавлять в вашу базу данных только новые вакансии с сайта.


Будем исходить из того, что предыдущая задача (сбор данных с hh и сохранение в csv)
уже решена и данные по вакансиям сохранены в csv файлы

Если необходимо собрать новые вакансии - необходимо запустить предыдущий процесс
по сбору вакансий

Для примера будем работать с двумя вакансиями - 1) Python, 2) Data Engineer
Данные по вакансиями хранятся в папке data в одноименных файлах

Для хранения данных о вакансиях в рамках Mongo создадим новую базу данных vacancies
Данные по каждой вакансии будем хранить в рамках отдельной одноименной коллекции

Дубли по вакансиям не добавляются, т.к. ключом является имя компании + имя вакансии
Удаление старых вакансий не предусмотрено
"""

from pprint import pprint
from pymongo import MongoClient
from pathlib import Path
import pandas as pd
import re

MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "vacancies"


def vacancy_id(vacancy, employer):
    return vacancy + " / " + employer


def parse_salary_currency(salary):
    salary = salary if salary != "-" else None
    currency = None
    salary_currency_pattern = re.compile(r"([\d\s]+)(.*)")

    if salary is not None:
        match = salary_currency_pattern.match(salary)
        salary, currency = match.group(1), match.group(2)
        salary = int("".join(salary.split()))

    if currency is not None:
        currency = currency[:-1] if currency[-1] == '.' else currency
        currency = currency.lower()
    return salary, currency


def write_one_vacancy(collection, row):
    id = vacancy_id(row['title'], row['employer'])
    min_salary, currency_min = parse_salary_currency(row["min_salary"])
    max_salary, currency_max = parse_salary_currency(row["max_salary"])
    currency = currency_min if currency_min is not None else currency_max
    collection.update_one(
        {"_id": id},
        {
            "$set": {"title": row["title"],
                     "employer": row["employer"],
                     "min_salary": min_salary,
                     "max_salary": max_salary,
                     "currency": currency},
        },
        upsert=True
    )


def write_vacancies_to_db(vacancy):
    filename = Path("data") / ("vacancies_" + vacancy + ".csv")
    with MongoClient(MONGO_URI) as client:
        db = client[MONGO_DB]
        collection = db[vacancy]
        vacancy_df = pd.read_csv(filename, encoding="utf-8")
        for index, row in vacancy_df.iterrows():
            write_one_vacancy(collection, row)

# vacancies = ['python', 'data_engineer']
# for vacancy_ in vacancies:
#     write_vacancies_to_db(vacancy_)


def search_vacancies(vacancy, currency, min_salary, max_salary=None):
    print("-" * 80)
    print(f"Vacancies {vacancy}")
    print("-" * 80)
    with MongoClient(MONGO_URI) as client:
        db = client[MONGO_DB]
        collection = db[vacancy]
        if max_salary is None:
            result = collection.find({
                "currency": currency,
                "min_salary": {"$gte": min_salary}
            })
        else:
            result = collection.find({
                "currency": currency,
                "min_salary": {"$gte": min_salary},
                "max_salary": {"$lte": max_salary}
            })
        for item in result:
            pprint(item)
            print()


search_vacancies("data_engineer", "usd", 3000)
search_vacancies("python", "руб", 50000, 200000)