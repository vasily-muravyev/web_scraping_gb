"""
Вариант 1
Необходимо собрать информацию о вакансиях на вводимую должность
(используем input или через аргументы) с сайта HH.
Приложение должно анализировать несколько страниц сайта (также вводим через input или аргументы).

Получившийся список должен содержать в себе минимум:

Наименование вакансии.
Предлагаемую зарплату (отдельно минимальную и максимальную).
Ссылку на саму вакансию.
Сайт, откуда собрана вакансия.

По желанию можно добавить ещё параметры вакансии (например, работодателя и расположение).
Результат можно вывести с помощью dataFrame через pandas. Сохраните в json либо csv.
"""

import time
import requests
import re
import pandas as pd
from bs4 import BeautifulSoup as bs
from collections import defaultdict
# from urllib.parse import urljoin


def get(url, headers, params, proxies):
    r = requests.get(url, headers=headers, params=params, proxies=proxies)
    return r


def parse_min_max_salary(salary):
    if salary is None:
        return "-", "-"
    salary = salary.strip()
    if salary == "":
        return "-", "-"

    if salary.startswith("от "):
        return salary[3:], "-"
    elif salary.startswith("до "):
        return "-", salary[3:]
    else:
        min_max_salary_pattern = re.compile(r"([\d\s]+) – ([\d\s]+) (.*)")
        match = min_max_salary_pattern.match(salary)
        return match.group(1) + " " + match.group(3), \
               match.group(2) + " " + match.group(3)


def parse_one_page(vacancy_name, page):
    vacancy_url = "https://hh.ru/search/vacancy/"

    params = {
        "text": vacancy_name,
        "page": page
    }

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko)"
                      " Chrome/89.0.4389.114 Safari/537.36"
    }

    proxies = {}

    r = get(vacancy_url, headers, params, proxies)
    print(f"\n{r.status_code} {r.url}\n")
    if r.status_code != 200:
        return {}

    soup = bs(r.text, "html.parser")

    vacancy_items = soup.find_all(attrs={"class": "vacancy-serp-item"})

    data = defaultdict(list)

    for index, item in enumerate(vacancy_items, 50 * page + 1):
        job_title_item = item.find(attrs={"data-qa": "vacancy-serp__vacancy-title"})
        job_salary_item = item.find(attrs={"data-qa": "vacancy-serp__vacancy-compensation"})
        job_employer_item = item.find(attrs={"data-qa": "vacancy-serp__vacancy-employer"})
        job_link = job_title_item.attrs["href"]
        job_source_site = "https://hh.ru"

        print(index, job_title_item.text)
        data['title'].append(job_title_item.text)
        print(job_employer_item.text)
        data['employer'].append(job_employer_item.text)
        print(f"source: {job_source_site}")
        data['source'].append(job_source_site)
        print(f"link: {job_link}")
        data['link'].append(job_link)
        print(f"salary: {job_salary_item.text if job_salary_item else '-'}")
        min_salary, max_salary = parse_min_max_salary(job_salary_item.text if job_salary_item else None)
        print(f"min salary: {min_salary}")
        print(f"max salary: {max_salary}")
        data['min_salary'].append(min_salary)
        data['max_salary'].append(max_salary)
        print()

    return data


vacancy = input("Enter vacancy name >>> ")
max_num_pages_to_parse = input("Enter max num of pages >>> ")

try:
    max_num_pages_to_parse = int(max_num_pages_to_parse)
except:
    print(f'Incorrect number of pages: {max_num_pages_to_parse}. Changing to 10')
    max_num_pages_to_parse = 10

pages = []
for page in range(max_num_pages_to_parse):
    page_data = parse_one_page(vacancy, page)
    if not page_data:
        break
    pages.append(page_data)
    time.sleep(2)

merged_data = defaultdict(list)
for page_data in pages:
    for key, value in page_data.items():
        merged_data[key].extend(value)

column_order = ['title', 'employer', 'min_salary', 'max_salary', 'source', 'link']
pd.DataFrame.from_records(merged_data)[column_order].to_csv("vacancies.csv", encoding="utf-8", index=False)


# можно было также сделать переход не по индексам, а следующим образом:
# next_page_item = soup.find(attrs={"data-qa": "pager-next"})
# next_page_url = urljoin("https://hh.ru", next_page_item.attrs['href'])
# print(next_page_url)
