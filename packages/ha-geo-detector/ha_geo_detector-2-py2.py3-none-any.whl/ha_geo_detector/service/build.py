import copy
import logging
import operator
import re

from workers.geo_detector.ha_geo_detector.service.additional import cleanup_and_tokenize


def build_countries_info(country_info, min_population=300000):
    countries = []
    for country_data in country_info:
        country_data = country_data.split('\t')
        country_data = [country_data[_] if _ < len(country_data) else '' for _ in range(19)]
        country = {
            'iso': country_data[0],
            'iso3': country_data[1],
            'iso_numeric': country_data[2],
            'fips': country_data[3],
            'country_name': country_data[4],
            'capital': country_data[5],
            'area': float(country_data[6]),
            'population': int(country_data[7]),
            'continent': country_data[8],
            'domain': country_data[9],
            'currency_code': country_data[10],
            'currency_name': country_data[11],
            'phone_code': country_data[12],
            'postal_code_format': country_data[13],
            'postal_code_regex': country_data[14],
            'languages': country_data[15],
            'geoname_id': int(country_data[16]),
            'neighbours': country_data[17],
            'equivalent_fips_code': country_data[18],
        }
        if country['population'] >= min_population:
            countries.append(country)
            if country['iso'] == 'GB':  # костыль для Англии как и в оригинале
                uk_fix = copy.deepcopy(country)
                uk_fix['iso'] = 'UK'
                uk_fix['country_name'] = 'England'
                countries.append(uk_fix)

    countries.sort(key=operator.itemgetter('population'), reverse=True)

    return countries


def build_cities_by_geonames(countries_info,
                             rg_cities,
                             black_list_names,
                             black_list_codes,
                             min_population=300000):
    countries = {}
    cities = {}

    for country in countries_info:
        countries[country['geoname_id']] = {
            'country_code': country['iso'],
            'population': country['population']
        }

    # regexp_codes = re.compile(r'[A-Z0-9]{2,4}')
    # regexp_upper_case = re.compile(r'[A-Z0-9]+$')
    regexp_shortname = re.compile(r'''(?:([a-z\-'"\s]{4,}|[^a-z]+))''', re.I)

    for city in rg_cities:
        city['city_id'] = int(city['city_id'])
        if city['state_id']:
            int(city['state_id'])
        else:
            city['state_id'] = 0
        city['country_id'] = int(city['country_id'])
        city['population'] = int(city['population'])

        if city['population'] >= min_population:
            if city['city_name'].lower() not in black_list_names:
                cities[' '.join(cleanup_and_tokenize(city['city_name']))] = {
                    'city_id': city['city_id'],
                    'state_id': city['state_id'],
                    'country_id': city['country_id'],
                    'country_code': countries[city['country_id']]['country_code'],
                    'population': countries[city['country_id']]['population'],
                    'city_population': city['population'],
                }

            if city['city_alternate_names']:
                for name in city['city_alternate_names'].split(','):
                    if name.isupper() and name.isalnum():
                        if name not in black_list_codes:
                            cities[name] = {
                                'city_id': city['city_id'],
                                'state_id': city['state_id'],
                                'country_id': city['country_id'],
                                'country_code': countries[city['country_id']]['country_code'],
                                'population': countries[city['country_id']]['population'],
                                'city_population': city['population'],
                            }
                    elif regexp_shortname.search(name):
                        if name.lower() not in black_list_names:
                            cities[' '.join(cleanup_and_tokenize(name))] = {
                                'city_id': city['city_id'],
                                'state_id': city['state_id'],
                                'country_id': city['country_id'],
                                'country_code': countries[city['country_id']]['country_code'],
                                'population': countries[city['country_id']]['population'],
                                'city_population': city['population'],
                            }
                    else:
                        logging.info('short city name skipped: {}\n'.format(name))
    return cities


def build_country_by_code(countries_info, black_list_codes):
    countries = {}
    for country in countries_info:
        if country['iso'] not in black_list_codes:
            countries[' '.join(cleanup_and_tokenize(country['iso']))] = {
                'city_id': 0,
                'state_id': 0,
                'country_id': country['geoname_id'],
                'country_code': country['iso'],
                'population': country['population'],
            }
        if country['iso3'] not in black_list_codes:
            countries[' '.join(cleanup_and_tokenize(country['iso3']))] = {
                'city_id': 0,
                'state_id': 0,
                'country_id': country['geoname_id'],
                'country_code': country['iso'],
                'population': country['population'],
            }

    return countries


def build_country_by_emoji(countries_info):
    result = {}
    for country in countries_info:
        result[country['iso']] = {
            'country_id': country['geoname_id'],
            'country_code': country['iso'],
            'population': country['population']
        }

    return result


def build_country_by_name(countries_info, black_list_names):
    result = {}
    for country in countries_info:
        if country['country_name'].lower() not in black_list_names:
            result[' '.join(cleanup_and_tokenize(country['country_name']))] = {
                'city_id': 0,
                'state_id': 0,
                'country_id': country['geoname_id'],
                'country_code': country['iso'],
                'population': country['population'],
            }
    return result


def build_country_by_nationality(country_info, nations):
    result = {}
    countries = {}
    for country in build_countries_info(country_info, 10000):
        countries[country['geoname_id']] = {
            'country_code': country['iso'],
            'population': country['population']
        }

    for line in nations:
        country_id, nation = line.split('\t')
        country_id = int(country_id)
        for name in nation.split(','):
            result[' '.join(cleanup_and_tokenize(name))] = {
                'city_id': 0,
                'state_id': 0,
                'country_id': country_id,
                'country_code': countries[country_id]['country_code'],
                'population': countries[country_id]['population']
            }

    return result


def build_country_by_state(countries_info, states):
    result = {}
    countries = {}
    for country in countries_info:
        countries[country['geoname_id']] = {
            'country_code': country['iso'],
            'population': country['population']
        }

    for line in states:
        state_id, state_name, country_id = line.split('\t')
        state_id = int(state_id)
        country_id = int(country_id)
        result[' '.join(cleanup_and_tokenize(state_name))] = {
            'city_id': 0,
            'state_id': state_id,
            'country_id': country_id,
            'country_code': countries[country_id]['country_code'],
            'population': countries[country_id]['population']
        }

    return result


def build_country_by_domain(countries_info):
    result = []
    regexp_punct = r'\s.,#!?;:<>©™®\|/\U0001F300-\U0001F5FF'
    regexp_start_domain = r'(?:[{}@]|\A)\s*'.format(regexp_punct)
    for country in countries_info:
        if country['domain']:
            result.append({
                'country_id': country['geoname_id'],
                'country_code': country['iso'],
                'rx': re.compile(r'(?i:{}([a-z0-9_\-]+(?:\.[a-z]{{2,3}})?{})(?:[^.a-z]|\s|\Z))'.format(
                    regexp_start_domain,
                    re.escape(country['domain']))),
                'population': country['population']
            })

    return result
