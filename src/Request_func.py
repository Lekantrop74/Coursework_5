import requests
import time
from tqdm import tqdm


def get_employer_HH(company_name):
    """
    Получает вакансии для указанного работодателя с сайта HH.ru с использованием API.

    Аргументы:
    - company_name (str): ключевое слово компании для поиска работодателей

    Возвращает:
    - data (list): список словарей с информацией о каждой вакансии

    """
    url_company = "https://api.hh.ru/employers"
    url_vacancy = "https://api.hh.ru/vacancies"

    params_company = {
        "text": company_name,
        "only_with_vacancies": "true",
        "per_page": 10,
        "page": 0,
    }

    response_employers = requests.get(url_company, params=params_company)

    if response_employers.status_code == 200:
        employers = response_employers.json()["items"]
        data = []

        for employer in tqdm(employers, desc="Processing employers", ncols=80, ascii=True):
            employer_id = employer["id"]
            params_vacancy = {
                "employer_id": employer_id,
                "per_page": 100,
                "page": 0
            }
            response_vacancy = requests.get(url_vacancy, params=params_vacancy)
            if response_vacancy.status_code == 200:
                vacancies = response_vacancy.json()["items"]
                for vacancy in vacancies:
                    if vacancy["salary"] is None:
                        salary_from = None
                        salary_to = None
                    else:
                        if vacancy["salary"]["from"] is not None:
                            salary_from = int(vacancy["salary"]["from"])
                        else:
                            salary_from = None

                        if vacancy["salary"]["to"] is not None:
                            salary_to = int(vacancy["salary"]["to"])
                        else:
                            salary_to = None
                    vacancy_data = {
                        "id": vacancy["id"],
                        "employer_id": employer_id,
                        "name": vacancy["name"],
                        "url": vacancy["alternate_url"],
                        "employer": employer["name"],
                        "salary_from": salary_from,
                        "salary_to": salary_to,
                        "area": vacancy["area"]["name"],
                        # добавьте другие необходимые поля вакансии
                    }

                    # print(vacancy["id"])
                    data.append(vacancy_data)
                # print(f"{len(vacancies)} для {employer['name']}")

                # Добавляем задержку для эффекта прогресса
                time.sleep(0.01)
        print(f"Всего найдено {len(data)} вакансий в {len(employers)} кампаниях по ключевому слову {company_name}")

        return data

    else:
        print("Ошибка при выполнении запроса:", response_employers.status_code)
        return []