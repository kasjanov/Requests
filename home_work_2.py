import requests
import pandas as pd

from bs4 import BeautifulSoup
from forex_python.converter import CurrencyCodes


def parser_vacancies_on_hh(vacancy_name):
    url = 'https://hh.ru'

    params = {'area': [1, 2],
              'search_field': ['company_name', 'description'],
              'clusters': 'true',
              'ored_clusters': 'true',
              'enable_snippets': 'true',
              'text': vacancy_name,
              'items_on_page': 20,
              'page': 0}

    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                             'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.45 Safari/537.36'}

    response = requests.get(url + '/search/vacancy', params=params, headers=headers)

    if response.ok:
        dom = BeautifulSoup(response.text, 'html.parser')

        pages = dom.find_all('span', {'class', 'pager-item-not-in-short-range'})
        last_page = int(pages[len(pages)-1].text)
        if last_page != 0:
            print(last_page)
        else:
            print('По вашему запросу нет вакансий')

        vacancies_list = []
        for page in range(0, last_page):
            params['page'] = page

            response = requests.get(url + '/search/vacancy', params=params, headers=headers)

            dom = BeautifulSoup(response.text, 'html.parser')
            vacancies = dom.find_all('div', {'class', 'vacancy-serp-item'})

            for vacancy in vacancies:
                vacancies_list.append(parser_vacancies_on_page(vacancy, url))

        return vacancies_list
    else:
        print('Неудачная попытка get запроса')


def parser_vacancies_on_page(vacancy, url):
    vacancy_data = {}
    name = vacancy.find('span', {'class': 'g-user-content'})
    link = name.contents[0].attrs.get('href')
    try:
        company_name = vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).text
    except AttributeError:
        company_name = None
    try:
        company_url = url + vacancy.find('a', {'data-qa': 'vacancy-serp__vacancy-employer'}).attrs.get('href')
    except AttributeError:
        company_url = None
    try:
        vacancy_address = str(vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy-address'}).contents[0])
    except AttributeError:
        vacancy_address = None
    try:
        vacancy_metro_point = vacancy.find('span', {'class', 'metro-station'}).text
    except AttributeError:
        vacancy_metro_point = None
    try:
        vacancy_responsibility = \
            vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy_snippet_responsibility'}).text
    except AttributeError:
        vacancy_responsibility = None
    try:
        vacancy_requirement = \
            vacancy.find('div', {'data-qa': 'vacancy-serp__vacancy_snippet_requirement'}).text
    except AttributeError:
        vacancy_requirement = None

    salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
    if salary is not None:
        if len(salary.contents) > 3:
            if str(salary.contents[0]).split()[0] == 'от':
                salary_min = \
                    int(str(salary.contents[2].encode('ascii', 'ignore')).split(' ')[0].split('\'')[1])
                salary_max = None
                salary_currency = str(salary.contents[6])
                if (salary_currency == 'руб.') | (salary_currency == 'руб'):
                    salary_currency = salary_currency_converter('RUB')
                else:
                    salary_currency = salary_currency_converter(salary_currency)
            else:
                salary_max = \
                    int(str(salary.contents[2].encode('ascii', 'ignore')).split(' ')[0].split('\'')[1])
                salary_min = None
                salary_currency = str(salary.contents[6])
                if (salary_currency == 'руб.') | (salary_currency == 'руб'):
                    salary_currency = salary_currency_converter('RUB')
                else:
                    salary_currency = salary_currency_converter(salary_currency)
        else:
            salary_min = \
                int(str(salary.contents[0].encode('ascii', 'ignore')).split(' ')[0].split('\'')[1])
            salary_max = \
                int(str(salary.contents[0].encode('ascii', 'ignore')).split(' ')[2])
            salary_currency = str(salary.contents[2])
            if (salary_currency == 'руб.') | (salary_currency == 'руб'):
                salary_currency = salary_currency_converter('RUB')
            else:
                salary_currency = salary_currency_converter(salary_currency)
    else:
        salary_min = None
        salary_max = None
        salary_currency = None

    name = name.text

    vacancy_data['name'] = name
    vacancy_data['link'] = link
    vacancy_data['company_name'] = company_name
    vacancy_data['company_url'] = company_url
    vacancy_data['vacancy_url'] = url
    vacancy_data['salary_min'] = salary_min
    vacancy_data['salary_max'] = salary_max
    vacancy_data['salary_currency'] = salary_currency
    vacancy_data['vacancy_address'] = vacancy_address
    vacancy_data['vacancy_metro_point'] = vacancy_metro_point
    vacancy_data['vacancy_responsibility'] = vacancy_responsibility
    vacancy_data['vacancy_requirement'] = vacancy_requirement

    return vacancy_data


def salary_currency_converter(salary_currency):
    c = CurrencyCodes()
    salary_currency = c.get_symbol(salary_currency)
    return salary_currency


vacancy_name_ = input('\nВведите название специальности: ')
result = parser_vacancies_on_hh(vacancy_name_)
df = pd.DataFrame(result)

# noinspection PyTypeChecker
df.to_csv('Home_work_2.csv', index=None)
df.to_json('Home_work_2.json')
