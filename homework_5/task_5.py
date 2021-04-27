"""
Написать программу, которая собирает посты из группы https://vk.com/tokyofashion
Будьте внимательны к сайту!
Делайте задержки, не делайте частых запросов!

1) В программе должен быть ввод, который передается в поисковую строку по постам группы

2) Соберите данные постов:
- Дата поста
- Текст поста
- Ссылка на пост(полная)
- Ссылки на изображения(если они есть)
- Количество лайков, "поделиться" и просмотров поста

3) Сохраните собранные данные в MongoDB

4) Скролльте страницу, чтобы получить больше постов(хотя бы 2-3 раза)

5) (Дополнительно, необязательно) Придумайте как можно скроллить "до конца" до тех пор пока посты не перестанут добавляться

Чем пользоваться?
Selenium, можно пользоваться lxml, BeautifulSoup

Советы
Пример изменения Selenium через Options:

Советы по дз:
1) Окно, которое мешает сбору данных появляется не сразу - напишите отдельную функцию для его поиска
Ну и подумайте как можно спровоцировать его появление и поймите что нужно нажать, чтобы продолжить работу с сайтом
2) Можете подумать как собрать все посты(скроллить "до упора"), но это необязательно, достаточно сделать 2-5 скроллов
3) Сделайте отдельную функцию, чтобы посылать запрос в поисковую строку по постам

Посмотрите комментарий по задаче - https://gb.ru/lessons/124838#!#comment-723755

"""

import time
from pprint import pprint

from pymongo import MongoClient

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.action_chains import ActionChains

from lxml import html

# 1. Вводим строку для поиска
search_string = input("Введите поисковую строку >>> ")

url = "https://vk.com/tokyofashion"

options = Options()
options.add_argument("start-maximized")

DRIVER_PATH = "./chromedriver.exe"
driver = webdriver.Chrome(DRIVER_PATH, options=options)

# 2. Открываем изначальную страницу и делаем несколько скроллов для того чтобы показалось окно регистрации
driver.get(url)

for i in range(3):
    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
    time.sleep(2)

not_now_link = driver.find_element_by_class_name("JoinForm__notNow")
not_now_link.click()

for i in range(2):
    ActionChains(driver).key_down(Keys.PAGE_UP).key_up(Keys.PAGE_UP).perform()
    time.sleep(2)

# 3. Вводим поисковые запрос
search_element = driver.find_element_by_class_name("ui_tab_search")
search_element.click()

search_input = driver.find_element_by_class_name("ui_search_field")
search_input.send_keys(search_string)
search_input.send_keys(Keys.ENTER)

time.sleep(2)

# 4. Делаем несколько скроллов вниз чтобы получить больше статей. Далее находим все посты

for i in range(20):
    ActionChains(driver).key_down(Keys.PAGE_DOWN).key_up(Keys.PAGE_DOWN).perform()
    time.sleep(2)

search_posts = driver.find_element_by_xpath("//div[@id = 'page_search_posts']")
time.sleep(2)
posts = search_posts.find_elements_by_class_name('post')

# 5. Собираем все данные по постам
posts_info = []

for index, post in enumerate(posts, 1):
    # print('\n' * 5)
    # print(index, post.text)

    ActionChains(driver).move_to_element(post)

    one_post_info = {}
    one_post_info['date'] = post.find_element_by_class_name('rel_date').text
    one_post_info['text'] = post.find_element_by_class_name('wall_post_text').text
    one_post_info['link'] = post.find_element_by_class_name('post_link').get_attribute('href')

    one_post_info['likes_count'] = post.find_element_by_class_name('_like').get_attribute('data-count')
    one_post_info['shares_count'] = post.find_element_by_class_name('_share').get_attribute('data-count')

    # показы получилось достать только для первых постов, дальше сбор перестает работать
    # пока не получилось разобраться почему именно
    like_views_element = post.find_element_by_class_name('like_views')
    if like_views_element.is_displayed():
        ActionChains(driver).move_to_element(like_views_element).perform()
        one_post_info['views_count'] = post.find_element_by_class_name('like_views').text

    # ссылки на картинки и видео можно достать из тега ниже, но они нетривиально спрятаны внутри js кода
    # у меня не получилось за адекватное время их достать, а больше заниматься этим сейчас не было времени

    # TODO: либо исполнять JS, либо делать клики по каждой картинке, либо доставать ссылки через regex
    # media = post.find_element_by_class_name("page_post_sized_thumbs").find_elements_by_tag_name('a')

    time.sleep(1)
    posts_info.append(one_post_info)

MONGO_URI = "127.0.0.1:27017"
MONGO_DB = "fashion"


def write_fashion_to_db(search, posts):
    with MongoClient(MONGO_URI) as client:
        db = client[MONGO_DB]
        collection = db[search]
        for post in posts:
            id = post["link"]
            collection.update_one(
                {"_id": id},
                {
                    "$set": {"date": post["date"],
                             "text": post["text"],
                             "likes_count": post["likes_count"],
                             "shares_count": post["shares_count"],
                             "views_count": post["views_count"] if "views_count" in post else None}
                },
                upsert=True
            )


# pprint(posts_info)
write_fashion_to_db(search_string, posts_info)