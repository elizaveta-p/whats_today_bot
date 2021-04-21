import requests
import datetime
from api_key import API_KEY


country_codes = {}


def parse_holidays(resp, date: datetime.date) -> list:
    result = []
    for holiday in resp:
        if holiday["date"]["iso"] == date.isoformat():   # checkkkkkkkk before use iso
            result.append(holiday)
    return result


def format_holidays(list_of_jsons) -> list:
    result = []
    for holiday in list_of_jsons:
        my_holiday = [holiday["name"], holiday["country"]["name"]]
        result.append(my_holiday)

    return result


def make_readable(holidays, date):
    if date.isoformat() == datetime.datetime.now().date().isoformat():
        # date = datetime.datetime.now().date().isoformat()
        date_str = "Сегодня"
    else:
        date_str = date.isoformat()

    result = [f"{date_str} праздники такие:"]
    for holiday in holidays:
        result.append(" - ".join(holiday))

    result = "\n".join(result)
    return result


def get_holidays(date: datetime.date, countries="RU"):
    final_result = []

    api_server = 'https://calendarific.com/api/v2/holidays'

    year = date.year
    month = date.month
    day = date.day

    if countries != "RU":
        for country in countries:

            params = {
                "api_key": API_KEY,
                "year": year,
                "month": month,
                "day": day,
                "country": country
            }
            response = requests.get(api_server, params=params).json()["response"]["holidays"]
            # response = parse_holidays(response, date)
            for item in response:
                final_result.append(item)

    else:
        params = {
            "api_key": API_KEY,
            "year": year,
            "month": month,
            "day": day,
            "country": countries
        }

        response = requests.get(api_server, params=params).json()["response"]["holidays"]
        # response = parse_holidays(response, date)
        final_result = response

    # making final result from bunch of jsons to list of holidays
    final_result = format_holidays(final_result)

    # final_result = make_readable(final_result, date)

    return final_result


def get_list_of_countries(num=None):
    if country_codes == {}:
        api_server = "https://calendarific.com/api/v2/countries"

        params = {
            "api_key": API_KEY
        }

        response = requests.get(api_server, params=params).json()["response"]["countries"]

        create_country_codes_dict(response)

    return make_countries_readable(country_codes, num)


def create_country_codes_dict(list_of_jsons):
    for country in list_of_jsons:
        country_codes[country["country_name"]] = country["iso-3166"]


def make_countries_readable(countries_dict, num):
    result = []
    for country in countries_dict.keys():
        result.append([country, countries_dict[country]])

    if num is None or num > len(country_codes.keys()):
        num = len(country_codes.keys())

    result = '\n'.join(['\t'.join(x) for x in result][:num])
    return result
