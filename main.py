from src.choice_func import process_user_query
from src.Request_func import get_employer_HH


def main():
    list_employers = ["Мясо", "Yandex", "Грибы", "Water", "Gem"]
    hh_employer = []

    for i in list_employers:
        hh_employer.extend(get_employer_HH(i))

    process_user_query(hh_employer)


if __name__ == '__main__':
    main()
