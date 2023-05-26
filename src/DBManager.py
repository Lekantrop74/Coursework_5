import psycopg2

from src.utils import connection_to_db, load_connection_params


class DBManager:
    def __init__(self, filename="database.ini", section="postgresql"):
        self.connection_params = load_connection_params(filename, section)

    def create_table(self):
        """
        Создать таблицы vacancies и company
        """
        query = """
        CREATE TABLE IF NOT EXISTS company (
            employer_id VARCHAR(255) PRIMARY KEY,
            employer VARCHAR(255)
        );

        CREATE TABLE IF NOT EXISTS vacancies (
            id SERIAL PRIMARY KEY,
            employer_id VARCHAR(255) REFERENCES company (employer_id),
            name VARCHAR(255),
            url VARCHAR(255),
            salary_from INTEGER,
            salary_to INTEGER,
            area VARCHAR(255)
        );
        """

        connection_to_db(self.connection_params, query)
        print("Таблицы vacancies и company успешно созданы.")

    def clear_table(self, table_name):
        """
        Очищает указанную таблицу в базе данных.
        :param connection_params: параметры подключения к базе данных
        :param table_name: имя таблицы для очистки
        :return:
        """
        query = f"DELETE FROM {table_name}"

        connection_to_db(self.connection_params, query)

        # print(f"Таблица {table_name} успешно очищена.")

    def write_data(self, data):
        """
        Записывает данные в таблицы в базе данных.
        :param data: список словарей с данными для записи
        :return:
        """
        company_query = """
        INSERT INTO company (employer_id, employer)
        VALUES (%(employer_id)s, %(employer)s)
        ON CONFLICT (employer_id) DO NOTHING
        """

        vacancy_query = """
        INSERT INTO vacancies (id, employer_id, name, url, salary_from, salary_to, area)
        VALUES (%(id)s, %(employer_id)s, %(name)s, %(url)s, %(salary_from)s, %(salary_to)s, %(area)s)
        ON CONFLICT (id) DO NOTHING
        """

        connection_to_db(self.connection_params, company_query, False, data)
        connection_to_db(self.connection_params, vacancy_query, False, data)

        print("Данные успешно записаны в базу данных.")

    def get_companies_and_vacancies_count(self):
        """
        Получает список всех компаний и количество вакансий у каждой компании.
        :return: список словарей с информацией о каждой компании и количестве вакансий
        """
        query = """
        SELECT c.employer_id, c.employer, COUNT(v.id) AS vacancies_count
        FROM company c
        LEFT JOIN vacancies v ON c.employer_id = v.employer_id
        GROUP BY c.employer_id, c.employer
        """

        result = connection_to_db(self.connection_params, query, fetch_all=True)

        companies_and_vacancies = []
        for row in result:
            company_data = {
                "employer_id": row[0],
                "employer": row[1],
                "vacancies_count": row[2]
            }
            companies_and_vacancies.append(company_data)

        return companies_and_vacancies

    def get_all_vacancies(self):
        """
        Получает список всех вакансий с указанием названия компании, названия вакансии,
        зарплаты и ссылки на вакансию.
        :return: список словарей с информацией о каждой вакансии
        """
        query = """
        SELECT v.id, c.employer AS company_name, v.name AS vacancy_name,
               v.salary_from, v.salary_to, v.url
        FROM vacancies v
        JOIN company c ON v.employer_id = c.employer_id
        """

        result = connection_to_db(self.connection_params, query, fetch_all=True)

        vacancies = []
        for row in result:
            vacancy_data = {
                "id": row[0],
                "company_name": row[1],
                "vacancy_name": row[2],
                "salary_from": row[3],
                "salary_to": row[4],
                "url": row[5]
            }
            vacancies.append(vacancy_data)

        return vacancies

    def get_avg_salary(self):
        """
        Получает среднюю зарплату по вакансиям.
        :return: средняя зарплата
        """
        query = """
        SELECT AVG(salary_from) AS avg_salary
        FROM vacancies
        WHERE salary_from IS NOT NULL
        """

        result = connection_to_db(self.connection_params, query, fetch_all=True)

        if result:
            avg_salary = result[0][0]
            return f"Средняя зарплата по вакансиям: {int(avg_salary)}"
        else:
            return None

    def get_vacancies_with_higher_salary(self):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям.
        :return: список словарей с информацией о каждой вакансии
        """
        query = """
        SELECT v.id, v.name, v.url, v.salary_from, v.salary_to, c.employer
        FROM vacancies AS v
        JOIN company AS c ON v.employer_id = c.employer_id
        WHERE v.salary_from > (
            SELECT AVG(salary_from)
            FROM vacancies
        )
        """

        result = connection_to_db(self.connection_params, query, fetch_all=True)

        vacancies = []
        if result:
            for row in result:
                vacancy_data = {
                    "id": row[0],
                    "vacancy_name": row[1],
                    "url": row[2],
                    "salary_from": row[3],
                    "salary_to": row[4],
                    "company_name": row[5],
                }
                vacancies.append(vacancy_data)

        return vacancies

    def get_vacancies_with_keyword(self, keyword):
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова.
        :param keyword: ключевое слово для поиска в названии вакансии
        :return: список словарей с информацией о каждой вакансии
        """
        query = """
        SELECT v.id, v.name, v.url, v.salary_from, v.salary_to, c.employer
        FROM vacancies AS v
        JOIN company AS c ON v.employer_id = c.employer_id
        WHERE v.name ILIKE %s
        """

        connection_params = load_connection_params("database.ini", "postgresql")

        try:
            with psycopg2.connect(**self.connection_params) as connection:
                with connection.cursor() as cursor:
                    cursor.execute(query, (f"%{keyword}%",))
                    result = cursor.fetchall()

            vacancies = []
            for row in result:
                vacancy_data = {
                    "id": row[0],
                    "vacancy_name": row[1],
                    "url": row[2],
                    "salary_from": row[3],
                    "salary_to": row[4],
                    "company_name": row[5],
                }
                vacancies.append(vacancy_data)

            return vacancies

        except (psycopg2.Error, psycopg2.OperationalError) as error:
            print(f"Ошибка при подключении к базе данных:\n{error}")
            return []

    def get_vacancy_data(self):
        query = """
        SELECT v.id, v.employer_id, v.name, v.url, c.employer, v.salary_from, v.salary_to, v.area
        FROM vacancies AS v
        JOIN company AS c ON v.employer_id = c.employer_id
        """
        result = connection_to_db(self.connection_params, query, fetch_all=True)

        vacancies = []
        for row in result:
            vacancy_data = {
                "id": row[0],
                "employer_id": row[1],
                "vacancy_name": row[2],
                "url": row[3],
                "company_name": row[4],
                "salary_from": row[5],
                "salary_to": row[6],
                "area": row[7],
            }
            vacancies.append(vacancy_data)

        return vacancies










