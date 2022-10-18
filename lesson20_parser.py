import json
import pprint

import requests
from bs4 import BeautifulSoup


# Ссылки, которые мне были интересны:
# - Статья "Облегчаем себе жизнь с помощью BeautifulSoup4"
#   https://habr.com/ru/post/544828/
# - Документация Beautiful Soup
#   http://bs4ru.geekwriter.ru/bs4ru.html
# - Документация Beautiful Soup
#   https://www.crummy.com/software/BeautifulSoup/bs4/doc.ru/bs4ru.html


"""
Новости находятся в блоках:
<div class="item-container">...</div>

Каждый блок имеет структуру:
<div class="item-container">
 <div class="news-line-dates">
  <noindex>
   <span class="badge news-line-item-resource ru" title="Язык новости">
   </span>
  </noindex>
  <small>
   09.10.2022
   <i class="fa fa-long-arrow-right fa-lg">
   </i>
   <a class="section-link" href="/issue/459/">
    Выпуск 459
   </a>
   (03.10.2022 - 09.10.2022)
   <i class="fa fa-long-arrow-right fa-lg">
   </i>
   <a href="/feed/?section=6">
    Статьи
   </a>
  </small>
 </div>
 <noindex>
  <div class="news-line-item">
   <h4>
    <a href="https://habr.com/ru/post/691856/?utm_campaign=691856&amp;utm_source=habrahabr&amp;utm_medium=rss" onclick="trackUrl(60351, 'Статьи', 'Without tag');" rel="nofollow" target="_blank">
     Сократить объем кода при помощи библиотеки PyTorch-Ignite
    </a>
   </h4>
   <p>
   </p>
   <p>
    PyTorch — среда глубокого обучения, которая была принята такими технологическими гигантами, как Tesla, OpenAI и Microsoft для ключевых исследовательских и производственных рабочих нагрузок.
   </p>
   <p>
   </p>
  </div>
 </noindex>
</div>
"""

"""
Переход между страницами находится в списке:
<ul class="pagination pagination-sm"> ... </ul>

При поиске могут быть ситуации:
1. Результат поиска содержит две страницы и более.
2. Результат поиска содержит одну страницу.
3. Поиск вообще не дал результатов.

Во втором и третьем случае будет отсутствовать конструкция
<ul class="pagination pagination-sm"> ... </ul>
 
     'flask' - всего 19 страниц в результатах поиска
     'FastAPI' - всего 2 страницы в результатах поиска
     'FastAPI ' - одна страница в поиске
     'flask django' - результат не дал ни одного материала
    Запросы:
     - для строки поиска 'FastAPI': '?q=FastAPI'
       Результат: две страницы.
       Список страниц строится так:
         ← 1 2 →
     - для строки поиска 'flask': '?q=flask'
       Результат: девятнадцать страниц.
       Список страниц строится так:
         ← 1 2 3 4 5 6 7 8 9 10 ... 18 19 →
     - для строки поиска 'FastAPI ': '?q=FastAPI+'
       Результат: одна страница.
       Список страниц отсутствует.
     - для строки поиска 'flask django': '?q=flask+django'
       Результат: выдаётся сообщение 'Печально но факт! В этой ленте нет новостей.'
       Список страниц отсутствует.

Список страниц строится так:
← 1 2 3 ... 17 18 19 →
В зависимости от того, какая страница загружена - некоторые 
элементы могут меняться.
Если загружена страница N, то:
1. Символ "←" - связан со ссылкой на предыдущую страницу: 
   <a href="/feed/?q=flask&page=(N-1)">
2. Символ "→" - связан со ссылкой на следующую страницу: 
   <a href="/feed/?q=flask&page=(N+1)">
Если предыдущая /следующая страница отсутствует (когда 
находимся на первой/последней странице), то соответствующие 
ссылки отсутствуют, но символы рисуются.


Поэтому, чтобы получить ссылку на следующую страницу, делаем так:
1. Загружаем страницу. 
2. Ищем тэг: <ul class="pagination pagination-sm">
3. Ищем все тэги <li> внутри найденного списка 
   <ul class="pagination pagination-sm"> ... </ul>
4. Переходим на самый последний найденный тэг <li>.
5. В этом последнем тэге <li> получаем параметр href из тэга <a>
6. Если следующая страница существует, то получаем её адрес, например:
   /feed/?q=flask&page=10
   Если отсутствует (то есть, находимся на последней странице), 
   то получаем значение: None


Возможны три разных варианта построения списка:
1. Когда загружена самая первая страница.
2. Когда загружена страница с номерами от 2 до предпоследней 
   (включая границы).
3. Когда загружена самая последняя страница.

Разные варианты построения списка для страниц из 19 элементов – ниже.

Для активной страницы с номером 1 – самая первая страница 
(ссылка https://pythondigest.ru /feed/?q=flask):
    <ul class="pagination pagination-sm">
      <li class="disabled">
        <a>
          ←
        </a>
      </li>
      <li class="active">
        <a>
          1
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=2">
          2
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=3">
          3
        </a>
      </li>
    ........................тут удалён текст для уменьшения объёма........................
       <li>
        <a href="/feed/?q=flask&page=10">
          10
        </a>
      </li>
      <li>
      </li>
      <li class="disabled">
        <a>
          ...
        </a>
       </li>
       <li>
        <a href="/feed/?q=flask&page=18">
          18
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=19">
          19
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=2">
          →
        </a>
      </li>
    </ul>



Для активной страницы с номером 3 – страница где-то посередине 
списка (ссылка https://pythondigest.ru /feed/?q=flask&page=3):
    <ul class="pagination pagination-sm">
       <li>
          <a href="/feed/?q=flask&amp;page=2">
          ←
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&amp;page=1">
          1
        </a>
      </li>  <li>
        <a href="/feed/?q=flask&page=2">
          2
        </a>
      </li>
      <li class="active">
        <a>
          3
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=4">
          4
        </a>
      </li>
      <li>
     <li>
    ........................тут удалён текст для уменьшения объёма........................
       <li>
        <a href="/feed/?q=flask&page=10">
          10
        </a>
      </li>
      <li>
      </li>
       <li class="disabled">
        <a>
          ...
        </a>
      </li>
        <a href="/feed/?q=flask&page=18">
          18
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=19">
          19
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=4">
          →
        </a>
      </li>
    </ul>



Для активной страницы с номером 19 – самая последняя страница 
(ссылка https://pythondigest.ru /feed/?q=flask&page=19):
    <ul class="pagination pagination-sm">
      <li>
        <a href="/feed/?q=flask&page=18">
          ←
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=1">
          1
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=2">
          2
        </a>
      </li>
      <li>
      </li>
      <li class="disabled">
        <a>
          ...
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=10">
          10
        </a>
      </li>
      <li>
        <a href="/feed/?q=flask&page=11">
          11
        </a>
      </li>
    ........................тут удалён текст для уменьшения объёма........................
      <li>
        <a href="/feed/?q=flask&page=18">
          18
        </a>
      </li>
      <li class="active">
        <a>
          19
        </a>
      </li>
      <li class="disabled">
        <a>
          →
        </a>
      </li>
    </ul>


"""


def parser(max_news_num=5, query=None):
    DOMAIN = 'https://pythondigest.ru'
    # URL = f'{DOMAIN}/feed'

    page_url = '/feed'
    if query:
        page_url += '?q=' + query

    result_dict = {}  # итоговый словарь с собранной информацией
    references = []   # список заголовков и ссылок на статьи

    max_page_to_load = 3
    num_page_loaded = 0
    news_num = 0

    while (page_url and
           num_page_loaded < max_page_to_load and
           news_num < max_news_num):
        # Если page_url будет равно None, то цикл закроется

        result_lst = []  # Список с собранными новостями с загруженной страницы

        num_page_loaded += 1
        print('Загружаем страницу:', num_page_loaded)
        print('Адрес страницы:', DOMAIN + page_url)

        # Загружаем страницу по указанному адресу
        response = requests.get(DOMAIN + page_url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # Собираем новости в загруженной страницы
        news_item_div_lst = soup.find_all('div', class_='item-container')
        for news_item_div in news_item_div_lst:
            if news_num >= max_news_num:
                break

            news_num += 1

            result = {}  # Словарь с одной новостью.

            # Получили блок с одной новостью.
            # news_item_div = soup.find('div', class_='item-container')

            # печатаем всю структуру блока
            # print(news_item_div.prettify())
            # Ищем в блоке первый тэг span
            # Это:
            #    <span class="badge news-line-item-resource ru" title="Язык новости">
            #    </span>
            tmp_tag = news_item_div.find('span')
            # print(tmp_tag.prettify())
            # Получаем из него параметр title
            lang_title = tmp_tag.get('title')
            # Получаем список классов, чтобы определить язык. Варианты: ru, en
            lang = tmp_tag.get('class')[2]
            # print('title =', title)
            # print('lang =', lang)
            # Добавить несколько пар ключ-значение
            # Описание отсюда: https://rukovodstvo.net/posts/id_611/
            # Вариант первый:
            # new_key_values_itr = (('lang_title', lang_title), ('lang', lang))
            # result.update((('lang_title', lang_title), ('lang', lang)))
            # Вариант второй:
            # result.update(lang_title=lang_title, lang=lang)
            # Вариант третий:
            # new_key_values_dict = {'lang_title': lang_title, 'lang': lang}
            result.update({'lang_title': lang_title, 'lang': lang})
            # pprint.pprint(result)
            """
            Анализируем блок:
              <small>
                09.10.2022
                <i class="fa fa-long-arrow-right fa-lg">
                </i>
                <a class="section-link" href="/issue/459/">
                  Выпуск 459
                </a>
                (03.10.2022 - 09.10.2022)
                <i class="fa fa-long-arrow-right fa-lg">
                </i>
                <a href="/feed/?section=6">
                  Статьи
                </a>
              </small>
            """
            # Справка тут: http://bs4ru.geekwriter.ru/bs4ru.html#get-text
            # Смотреть про:
            #    [text for text in soup.stripped_strings]
            tmp_tag = news_item_div.find('small')
            # print(tmp_tag.prettify())
            tmp_text_lst = [text for text in tmp_tag.stripped_strings]
            # получили список:
            #    ['09.10.2022', 'Выпуск 459', '(03.10.2022 - 09.10.2022)', 'Статьи']
            # print(tmp_text_lst)
            result['article_details'] = {
                'article_date': tmp_text_lst[0],
                'journal_issue': tmp_text_lst[1],
                'journal_date': tmp_text_lst[2],
                'article_category': tmp_text_lst[3],
            }
            # pprint.pprint(result)

            """
            Анализируем блок:
              <h4>
                <a href="https://habr.com/ru/post/691856/?utm_campaign=691856&amp;utm_source=habrahabr&amp;utm_medium=rss" 
                   onclick="trackUrl(60351, 'Статьи', 'Without tag');" 
                   rel="nofollow" 
                   target="_blank">
                  Сократить объем кода при помощи библиотеки PyTorch-Ignite
                </a>
              </h4>
            """
            tmp_tag = news_item_div.find('h4')
            # print(tmp_tag.prettify())
            tmp_tag = tmp_tag.find('a')
            # print(tmp_tag.prettify())
            article_url = tmp_tag.get('href')
            article_title = tmp_tag.get_text()
            # print(article_url)
            # print(article_title)
            result['article_details'].update(article_url=article_url,
                                             article_title=article_title)
            references.append((article_title, article_url))
            # pprint.pprint(result)

            """
            Анализируем блок:
              <p>
              </p>
              <p>
                PyTorch — среда глубокого обучения, которая была принята такими технологическими гигантами, как Tesla, OpenAI и Microsoft для ключевых исследовательских и производственных рабочих нагрузок.
              </p>
              <p>
              </p>
            """
            tmp_tag = news_item_div.find_all('p')
            # print(tmp_tag)
            # Получили такой список:
            #    [<p></p>,
            #     <p>PyTorch — среда глубокого обучения, которая была принята такими технологическими гигантами, как Tesla, OpenAI и Microsoft для ключевых исследовательских и производственных рабочих нагрузок.</p>,
            #     <p></p>]
            # for num, item in enumerate(tmp_tag):
            #     article_title = item.get_text()
            #     print(f'num: {num} item_text: {article_title}')

            # Получаем текст из тегов <p></p>.
            # article_announcement_lst = [item.get_text() for item in tmp_tag]
            # print(article_announcement_lst)
            # Получили такой список:
            #    ['',
            #     'PyTorch\xa0— среда глубокого обучения, которая была принята такими технологическими гигантами, как Tesla, OpenAI и Microsoft для ключевых исследовательских и производственных рабочих нагрузок.',
            #     '']
            article_announcement = ''.join([item.get_text() for item in tmp_tag])
            # print(article_announcement)
            result['article_announcement'] = article_announcement
            pprint.pprint(result)
            # Запись в файл json
            # Статья:
            # - Запись кириллицы и других не ASCII символов в формате JSON
            #   https://pyneng.github.io/pyneng-3/json-module/
            # По умолчанию non-ASCII символы записываются как последовательность кодов юникод
            # Но, если этот файл нужно будет читать и человеку, то лучше чтобы все non-ASCII символы отображались нормально.
            # За это отвечает параметр ensure_ascii:
            #   ensure_ascii=False

            result_lst.append(result)

        result_dict.update({f'page_{num_page_loaded}_news_list': result_lst})
        pages_lst = soup.find('ul', class_='pagination pagination-sm')
        if pages_lst:
            page_last = pages_lst.find_all('li')[-1]
            # Из документации: http://bs4ru.geekwriter.ru/bs4ru.html#id17
            # Использование имени тега в качестве атрибута даст вам только
            # первый тег с таким именем:
            #      soup.a
            # Если вам нужно получить все теги <a> или что-нибудь более
            # сложное, чем первый тег с определенным именем, вам нужно
            # использовать один из методов, описанных в разделе
            # "Поиск по дереву", такой как find_all():
            # http://bs4ru.geekwriter.ru/bs4ru.html#id26
            #      soup.find_all('a')

            # Из документации: http://bs4ru.geekwriter.ru/bs4ru.html#tag
            # Раздел "Атрибуты".
            # У тега может быть любое количество атрибутов.
            # Тег <b id = "boldest"> имеет атрибут «id», значение которого
            # равно «boldest». Вы можете получить доступ к атрибутам тега,
            # обращаясь с тегом как со словарем:
            #        tag = BeautifulSoup('<b id="boldest">bold</b>', 'html.parser').b
            #        tag['id']
            #        # 'boldest'
            # Вы можете получить доступ к этому словарю напрямую как к .attrs:
            #        tag.attrs
            #        # {'id': 'boldest'}

            # Из работы со словарями в Python.
            # Чтобы получить доступ к элементам словаря, нужно передать
            # ключ в квадратных скобках [].

            # Методы словарей:
            # get() — отдаёт значение словаря по указанному ключу.
            # Если ключ не существует, а в качестве дополнительного
            # аргумента передано значение по умолчанию, то метод вернет его.
            # Если же значение по умолчанию опущено, метод вернет None.
            page_url = page_last.a.get('href')
    return result_dict, references


def parser_to_file(max_news_num=5, query=None):
    result_dict, _ = parser(query=query)
    file_name = 'data.json'

    # Открываем файл на запись - чтобы очистить
    # содержимое, если что-то в файле было.
    with open(file_name, 'w', encoding='utf-8') as outfile:
        pass

    with open(file_name, 'a', encoding='utf-8') as outfile:
        json.dump(result_dict, outfile, ensure_ascii=False)


if __name__ == '__main__':

    query = 'flask'
    parser_to_file(query=query)

    # Варианты значений (параметры), которые могут
    # указываться в URL после символа "?":
    # 1. q=  - указывается поисковая строка
    #    Примеры:
    #    q=flask+django - ищем слова: flask django
    #    q=flask - ищем слово: flask
    # 2. page=  - указывается номер загружаемой страницы
    #    Пример:
    #    page=3
    # Объединяем параметры:
    #      page_url = '/feed/?q=flask&page=3'
    #  'flask' - всего 19 страниц в результатах поиска
    #  'FastAPI' - всего 2 страницы в результатах поиска
    #  'FastAPI ' - одна страница в поиске
    # Запросы:
    #  - для строки поиска 'FastAPI': '?q=FastAPI'
    #    Результат: две страницы.
    #    Список страниц строится так:
    #      ← 1 2 →
    #  - для строки поиска 'FastAPI ': '?q=FastAPI+'
    #    Результат: одна страница.
    #    Список страниц отсутствует.
    #  - для строки поиска 'flask django': '?q=flask+django'
    #    Результат: отсутствует.
    #    Список страниц отсутствует.
