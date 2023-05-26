from src.DBManager import DBManager
from src.utils import process_companies_and_vacancies, user_menu, print_vacancy


def process_user_query(data):
    writer = DBManager()
    writer.create_table()
    writer.clear_table("vacancies")
    writer.clear_table("company")
    writer.write_data(data)

    while True:
        print("\nМеню запросов:")
        for key in user_menu.keys():
            print(key)

        choice = input("Введите номер действия, которое вы хотите выполнить: ")

        if choice == "1":
            # Получить список всех компаний и количество вакансий
            process_companies_and_vacancies(writer.get_companies_and_vacancies_count())

        elif choice == "2":
            # Получить список всех вакансий с информацией о них
            companies_data = writer.get_vacancy_data()
            print_vacancy(companies_data)

        elif choice == "3":
            # Получить среднюю зарплату по вакансиям
            print(writer.get_avg_salary())

        elif choice == "4":
            # Получить список всех вакансий с зарплатой выше средней
            print_vacancy(writer.get_vacancies_with_higher_salary())

        elif choice == "5":
            # Получить список всех вакансий, в названии которых содержатся переданные слова
            search_keywords = input("Введите ключевые слова для поиска вакансий: ")
            print_vacancy(writer.get_vacancies_with_keyword(search_keywords))

        elif choice == "6":
            # Завершить обработку
            break

        else:
            print("Некорректный выбор. Пожалуйста, выберите номер из меню.")

        input("Нажмите Enter для продолжения")