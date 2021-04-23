import requests
import datetime

country_codes = {}


# def parse_holidays(resp, date: datetime.date) -> list:
#     result = []
#     for holiday in resp:
#         if holiday["date"]["iso"] == date.isoformat():   # checkkkkkkkk before use iso
#             result.append(holiday)
#     return result


def format_holidays(list_of_jsons) -> list:
    result = []
    for holiday in list_of_jsons:
        print(holiday)
        my_holiday = [find_by_key('lang', 'en', holiday['holidayName'], "text"), holiday['countryFullName']]
        result.append(my_holiday)
    # перевести здесь
    if len(set([x[0] for x in result])) < len(result):
        print('cleaning')
        clear_from_repeating = dict()
        for holiday in result:
            clear_from_repeating[holiday[0]] = [x[1] for x in result if x[0] == holiday[0]]
            if len(clear_from_repeating[holiday[0]]) > 5:
                clear_from_repeating[holiday[0]] = []

        result = [[x, ', '.join(clear_from_repeating[x])] for x in clear_from_repeating.keys()]
    return result


def find_by_key(key, value, list_of_jsons, item_key):
    for json in list_of_jsons:
        for local_key in json.keys():
            if local_key == key and json[local_key] == value:
                return json[item_key]
    return 'не найдено :('


def make_readable(holidays, date):
    if holidays:
        if date.isoformat() == datetime.datetime.now().date().isoformat():
            # date = datetime.datetime.now().date().isoformat()
            date_str = "Сегодня"
        else:
            date_str = date.isoformat()

        result = [f"{date_str} праздники будут такие:"]
        for holiday in holidays:
            if holiday[1] != '':
                result.append(" - ".join(holiday))
            else:
                result.append(holiday[0])
        result = "\n".join(result)
    else:
        result = "Сегодня праздников нет :("
    return result


def get_holidays(date: datetime.date):
    final_result = []

    api_request = "https://kayaposoft.com/enrico/json/v2.0/"

    params = {
        "action": "whereIsPublicHoliday",
        "date": f"{date:%d-%m-%Y}"
    }
    response = requests.get(api_request, params=params).json()
    print(response)
    # response = parse_holidays(response, date)
    for item in response:
        final_result.append(item)

    # making final result from bunch of jsons to list of holidays
    final_result = format_holidays(final_result)

    # final_result = make_readable(final_result, date)
    print(final_result)
    return final_result


def get_list_of_countries(num=None):
    if country_codes == {}:
        api_request = "https://kayaposoft.com/enrico/json/v2.0"

        params = {
            "action": "getSupportedCountries"
        }
        response = requests.get(api_request, params=params).json()
        response = parse_countries(response)
        create_country_codes_dict(response)
    return make_countries_readable(country_codes, num)


def create_country_codes_dict(list_of_countries):
    for country in list_of_countries:
        regions = country[1]
        if not regions:
            regions = 'не поддерживаются'
        else:
            regions = ', '.join(regions)
        country_codes[country[0]] = regions


def parse_countries(list_of_jsons):
    result = []
    for country in list_of_jsons:
        result.append([country["fullName"], country["regions"]])
    return result


def make_countries_readable(countries_dict, num):
    result = []
    for country in countries_dict.keys():
        if countries_dict[country] != 'не поддерживаются':
            result.append('\n'.join([country, f"    Регионы: {countries_dict[country]}"]))
        else:
            result.append(country)
    if num is None or num > len(country_codes.keys()):
        num = len(country_codes.keys())
    result = result[:num]
    result = '\n'.join(result)
    return result
