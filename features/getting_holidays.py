import os
import logging
from pprint import pprint
import requests
import datetime
from translator.translator import translate


def find_by_key(key, value, list_of_jsons, item_key):
    for json in list_of_jsons:
        for local_key in json.keys():
            if local_key == key and json[local_key] == value:
                return json[item_key]
    return 'не найдено :('


def format_holidays(list_of_jsons) -> list:
    try:
        result = []
        for holiday in list_of_jsons:
            print(holiday)
            eng_name = find_by_key('lang', 'en', holiday['holidayName'], "text")
            eng_country = holiday['countryFullName']
            my_holiday = [[translate(eng_name), translate(eng_country)],
                          [eng_name, eng_country]]
            result.append(my_holiday)
        clear_from_repeating = []
        for holiday in result:
            holiday_dict = dict()
            holiday_dict['name'] = holiday[0][0]
            countries_for_this_holiday = [[x[0][1], x[1][1]] for x in result if x[0][0] == holiday[0][0]]
            if len(countries_for_this_holiday) > 5:
                countries_for_this_holiday = []
            holiday_dict['countries'] = ', '.join([x[0] for x in countries_for_this_holiday])
            holiday_dict['en'] = f"{holiday[1][0]} in {', '.join([x[1] for x in countries_for_this_holiday]) if countries_for_this_holiday else 'the world'}"
            if not any(x['name'] == holiday_dict['name'] for x in clear_from_repeating):
                clear_from_repeating.append(holiday_dict)
        result = clear_from_repeating
        pprint(result)
        return result
    except BaseException as be:
        logging.fatal(be)


def make_readable(holidays, date):
    try:
        if holidays:
            if date.isoformat() == datetime.datetime.now().date().isoformat():
                # date = datetime.datetime.now().date().isoformat()
                date_str = "Сегодня"
            else:
                date_str = date.isoformat()

            result = [f"{date_str} праздники будут такие:"]
            for holiday in holidays:
                if holiday['countries'] != '':
                    result.append(" - ".join([holiday['name'], holiday['countries']]))
                else:
                    result.append(holiday['name'])
            result = "\n".join(result)
        else:
            result = "Сегодня праздников нет :("
        return result
    except BaseException as be:
        logging.fatal(be)


def get_holidays(date: datetime.date):
    try:
        final_result = []

        api_request = "https://kayaposoft.com/enrico/json/v2.0/"

        params = {
            "action": "whereIsPublicHoliday",
            "date": f"{date:%d-%m-%Y}"
        }
        response = requests.get(api_request, params=params).json()
        for item in response:
            final_result.append(item)
        final_result = format_holidays(final_result)
        return final_result
    except BaseException as be:
        logging.fatal(be)


def get_list_of_countries(num=None):
    try:
        data_folder = os.path.abspath(os.path.basename('data'))
        codes_filename = os.path.join(os.path.join(data_folder, 'country_codes'), 'countries_formatted.txt')
        with open(codes_filename, "r", encoding='utf-8') as file:
            data = file.readlines()
            data = data[:num]
        data = ''.join(data)
        return data
    except BaseException as be:
        logging.warning(be)


def update_countries():
    try:
        api_request = "https://kayaposoft.com/enrico/json/v2.0"

        params = {
            "action": "getSupportedCountries"
        }
        response = requests.get(api_request, params=params).json()
        response = parse_countries(response)
        # create_country_codes_dict(response)
        result = make_countries_readable(response, None)
        return result
    except BaseException as be:
        logging.warning(be)


def parse_countries(list_of_jsons):
    result = []
    for country in list_of_jsons:
        result.append([translate(country["fullName"]), country["regions"]])
    return result


def make_countries_readable(countries_list, num):
    try:
        result = []
        for country in countries_list:
            if countries_list[1]:
                result.append('\n'.join([country, f"    Регионы: {country[1]}"]))
            else:
                result.append(country)
        if num is None or num > len(countries_list):
            num = len(countries_list)
        result = result[:num]
        result = '\n'.join(result)
        data_folder = os.path.abspath(os.path.basename('data'))
        codes_filename = os.path.join(os.path.join(data_folder, 'country_codes'), 'countries_formatted.txt')
        with open(codes_filename, "w") as file:
            file.write(result)
        return result
    except BaseException as be:
        logging.warning(be)
