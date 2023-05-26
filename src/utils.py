from configparser import ConfigParser
import psycopg2


def config(filename="database.ini", section="postgresql") -> dict:
    """
    Получить конфигурацию для подключения к базе данных
    :param filename: имя файла конфигурации
    :param section: имя секции в файле конфигурации
    :return: словарь с параметрами подключения
    """
    parser = ConfigParser()
    parser.read(filename)
    if parser.has_section(section):
        return dict(parser.items(section))
    else:
        raise Exception(
            f"Секция '{section}' не найдена в файле '{filename}'."
        )


def connection_to_db(connection_params: dict, query_db: str, fetch_all: bool = False, data=None):
    """
    Подключение к базе данных
    :param connection_params: конфигурация для подключения
    :param query_db: запрос к базе данных
    :param fetch_all: флаг, определяющий нужно ли получить все строки результата
    :param data: данные для записи в таблицу
    :return: результат выполнения запроса (зависит от fetch_all)
    """
    try:
        with psycopg2.connect(**connection_params) as connection:
            with connection.cursor() as cursor:
                if data:
                    cursor.executemany(query_db, data)
                else:
                    cursor.execute(query_db)
                connection.commit()
                if fetch_all:
                    return cursor.fetchall()
                else:
                    return None
    except (psycopg2.Error, psycopg2.OperationalError) as error:
        print(f"Ошибка при подключении к базе данных:\n{error}")


def load_connection_params(filename, section):
    """
    Загрузить параметры подключения из файла конфигурации
    """
    try:
        return config(filename, section)
    except Exception as e:
        print(f"Ошибка при загрузке параметров подключения: {e}")
        return {}


def print_vacancy(data):
    """
    Функция принимает список данных о вакансиях и выводит на экран информацию о каждой вакансии.
    Аргументы:
    data -- список словарей, каждый словарь содержит информацию о конкретной вакансии
    Вывод:
    Функция выводит на экран информацию о каждой вакансии, включая название вакансии, зарплату, ссылку на вакансию,
    требования и обязанности.
    """
    count = 0
    for vacancy in data:
        # Extracting information from the vacancy dictionary
        id_vacancy = vacancy.get('id', 'Не указано')
        company_name = vacancy.get('company_name', 'Не указано')
        vacancy_name = vacancy.get('vacancy_name', 'Не указано')
        salary_from = vacancy.get('salary_from', 'Не указано')
        salary_to = vacancy.get('salary_to', 'Не указано')
        url = vacancy.get('url', 'Не указано')

        # Formatting the salary information
        if salary_from is None and salary_to is None:
            salary = "Не указано"
        elif salary_from is None:
            salary = f"До {salary_to}"
        elif salary_to is None:
            salary = f"От {salary_from}"
        else:
            salary = f"{salary_from}-{salary_to}"

        # Printing the vacancy information
        print("=" * 50)
        print(f"ID: {id_vacancy}")
        print(f"Название компании: {company_name}")
        print(f"Название вакансии: {vacancy_name}")
        print(f"Зарплата: {salary}")
        print(f"Ссылка на вакансию: {url}")

        count += 1

    print(f"\nВсего {count} результатов")


def process_companies_and_vacancies(data):
    """
    Функция принимает список данных о компаниях и количестве вакансий и обрабатывает их аналогично функции print_vacancy.
    Аргументы:
    data -- список словарей, каждый словарь содержит информацию о компании и количестве вакансий
    """
    count = 0
    for item in data:
        employer_id = item.get('employer_id', 'Не указано')
        employer = item.get('employer', 'Не указано')
        vacancies_count = item.get('vacancies_count', 'Не указано')

        print("=" * 50)
        print(f"ID работодателя: {employer_id}")
        print(f"Название компании: {employer}")
        print(f"Количество вакансий: {vacancies_count}")

        count += 1

    print(f"\nВсего {count} результатов")


# User query menu
user_menu = {
    "1.Получить список всех компаний и количество вакансий.": "1",
    "2.Получить список всех вакансий с информацией о них.": "2",
    "3.Получить среднюю зарплату по вакансиям.": "3",
    "4.Получить список всех вакансий, у которых зарплата выше средней.": "4",
    "5.Получить список всех вакансий, в названии которых содержатся переданные слова.": "5",
    "6.Завершить обработку.": "6"
}
