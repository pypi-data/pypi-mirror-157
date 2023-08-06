import datetime
import logging

from pymongo import UpdateOne
from pymongo.errors import BulkWriteError
import csv

from base.db import get_raw_db, get_data_science_db, get_social_data_db
from base.utils.measurer import track
from workers.geo_detector.service.build import build_cities_by_geonames, build_countries_info, \
    build_country_by_nationality, build_country_by_state, build_country_by_code, build_country_by_emoji, \
    build_country_by_name, build_country_by_domain
from workers.geo_detector.service.detect import detect_country_by_name, detect_country_by_phone, \
    detect_cities_by_geonames, detect_country_by_code, detect_country_by_emoji, detect_country_by_nationality, \
    detect_country_by_state, detect_country_by_domain


def parse_txt_file(filepath):
    with open(filepath, 'rt') as file:
        for line in file.read().splitlines():
            if not line.startswith('#'):
                yield line


def parse_csv_file(filepath):
    with open(filepath, 'r') as file:
        reader = csv.DictReader(file, delimiter='\t')
        for line in reader:
            yield line


def init_locations_dictionary():
    black_list_codes = {code: True for code in parse_txt_file('workers/geo_detector/ha_geo_detector/data/blacklisted_codes.txt')}
    black_list_names = [name for name in parse_txt_file('workers/geo_detector/ha_geo_detector/data/blacklisted_names.txt')]
    countries_info = [name for name in parse_txt_file('workers/geo_detector/ha_geo_detector/data/countryInfo.txt')]
    rg_cities = [name for name in parse_csv_file('workers/geo_detector/data/rg_cities1000_copy.csv')]
    nations_base = [name for name in parse_txt_file('workers/geo_detector/data/nations.tsv')]
    states_base = [name for name in parse_txt_file('workers/geo_detector/data/states.tsv')]

    countries = build_countries_info(countries_info)
    cities = build_cities_by_geonames(countries, rg_cities, black_list_names, black_list_codes)
    locations_dictionary = {
        'countries': countries,
        'cities': cities,
        'cities_by_ids': {item['city_id']: {
            'city_name': city_name,
            'city_population': item['city_population'],
            'population': item['population'],
            'state_id': item['state_id'],
            'country_id': item['country_id'],
            'country_code': item['country_code'],
        } for city_name, item in cities.items()},
        'nations': build_country_by_nationality(countries_info, nations_base),
        'states': build_country_by_state(countries, states_base),
        'emoji': build_country_by_emoji(countries),
        'code': build_country_by_code(countries, black_list_codes),
        'name': build_country_by_name(countries, black_list_names),
        'domain': build_country_by_domain(countries),
    }
    cities_by_first_letter = {}
    for key, value in cities.items():
        if key[0] not in cities_by_first_letter:
            cities_by_first_letter[key[0]] = {}
        cities_by_first_letter[key[0]][key] = value

    locations_dictionary['cities_by_first_letter'] = cities_by_first_letter

    return locations_dictionary


def get_account_descriptions(user_ids, social_network):
    descriptions = {}
    if social_network == 'ig':
        if user_ids:
            cursor = get_raw_db()['instagram_users'].find({'_id': {'$in': user_ids}}, {'_id': 1, 'data.biography': 1})
        else:
            cursor = get_raw_db()['instagram_users'].find({}, {'_id': 1, 'data.biography': 1}).limit(100)

        for item in cursor:
            descriptions[item['_id']] = item['data']['biography']
    elif social_network == 'tt':
        if user_ids:
            # cursor = get_social_data_db()['tiktok_user'].find({'_id': {'$in': user_ids}}, {'_id': 1,
            #                                                                                'data.signature': 1,
            #                                                                                'data.nickName': 1})
            cursor = get_social_data_db()['tiktok_user_min'].find({'_id': {'$in': user_ids}}, {'_id': 1,
                                                                                               'data.b': 1})
        else:
            cursor = get_social_data_db()['tiktok_user_min'].find({}, {'_id': 1, 'data.b': 1}).limit(100)

        for item in cursor:
            descriptions[item['_id']] = item['data']['b']
            # descriptions[item['_id']] = item['data']['signature']
            # descriptions[item['_id']] = item['data']['nickName'] + ' ' + item['data']['signature']

    for user_id in user_ids:
        if user_id not in descriptions:
            descriptions[user_id] = ''

    return descriptions


def detect_named_entities(ner_model, account_descriptions):
    result = {}
    for _id, text in account_descriptions.items():
        detects = ner_model(text)
        result[_id] = detects

    return result


# def get_locations_from_named_entities(named_entities):
#     result = {}
#     for _id, detects in named_entities.items():
#         started = False
#         locations = []
#         location = ''
#         for item in detects:
#             entity = item['entity']
#             # score = item['score']
#             word = item['word']
#             # location = ''
#             if entity == 'B-LOC':
#                 if started and location:
#                     locations.append(location)
#                 started = True
#                 location = word
#             elif entity == 'I-LOC':
#                 location = location + word.replace('#', '')
#             else:
#                 pass
#         if location:
#             locations.append(location)
#
#         result[_id] = locations
#
#     return result


@track('mongo')
def m_set_geo_data(filtered_locations, social_network):
    if filtered_locations is None:
        return
    now = datetime.datetime.utcnow()
    requests = []
    for user_id, item in filtered_locations.items():
        requests.append(UpdateOne(
            {'_id': user_id},
            {
                '$set': {
                    **item,
                    'time_updated': now,
                },
                '$setOnInsert': {
                    'time_added': now,
                }
            },
            upsert=True
        ))
    if social_network == 'tt':
        collection = 'tt_cache_detected_geo'
    else:
        return
    try:
        result = get_data_science_db()[collection].bulk_write(requests, ordered=False)
    except BulkWriteError as bwe:
        panic = list(filter(lambda x: x['code'] != 11000, bwe.details['writeErrors']))
        if len(panic) > 0:
            logging.error('Error while m_set_tt_cache_detected_geo')
            logging.error(bwe.details)
            raise
        else:
            logging.error('Error while m_set_tt_cache_detected_geo 1100')


def detect_entities_from_text(account_descriptions, geo_locations_dictionary):
    full_detects = {}
    for _id, text in account_descriptions.items():
        full_detects[_id] = []
        full_detects[_id] += detect_country_by_phone(text, geo_locations_dictionary['countries'])
        full_detects[_id] += detect_cities_by_geonames(text, geo_locations_dictionary['cities_by_first_letter'])
        full_detects[_id] += detect_country_by_code(text, geo_locations_dictionary['code'])
        full_detects[_id] += detect_country_by_emoji(text, geo_locations_dictionary['emoji'])
        full_detects[_id] += detect_country_by_name(text, geo_locations_dictionary['name'])
        full_detects[_id] += detect_country_by_nationality(text, geo_locations_dictionary['nations'])
        full_detects[_id] += detect_country_by_state(text, geo_locations_dictionary['states'])
        full_detects[_id] += detect_country_by_domain(text, geo_locations_dictionary['domain'])

    return full_detects


def detect_country_from_items(items):
    countries_dict = {}
    salvador = False
    salvador_br = False
    for item in items:
        if item['country_code'] not in countries_dict:
            countries_dict[item['country_code']] = {
                'count': 0,
                'population': item['population'],
            }
            if item['country_code'] == 'SV':
                salvador = True
            if item['match'] == 'salvador' and item['feature'] == 'city':
                salvador_br = True
        countries_dict[item['country_code']]['count'] += 1

    countries_dict = sorted(countries_dict.items(),
                            key=lambda x: (x[1]['count'], x[1]['population']),
                            reverse=True)

    if countries_dict[0][0] == 'BR' and salvador_br and salvador:
        return 'SV'
    return countries_dict[0][0]


def detect_city_from_items(items, country, cities):
    cities_dict = {}
    for item in items:
        if item['city_id'] > 0 and item['city_id'] not in cities_dict and item['country_code'] == country:
            cities_dict[item['city_id']] = {
                'count': 0,
                'state_id': item['state_id'],
                'city_population': cities[item['city_id']]['city_population'],
            }
        if item['city_id'] > 0 and item['country_code'] == country:
            cities_dict[item['city_id']]['count'] += 1

    cities_dict = sorted(cities_dict.items(),
                         key=lambda x: (x[1]['count'], x[1]['city_population']),
                         reverse=True)

    if cities_dict:
        return cities_dict[0][0], cities_dict[0][1]['state_id']
    else:
        return None, None


def get_most_probable_location(text_entities, geo_data):
    results = {}
    for _id, items in text_entities.items():
        if items:
            country = detect_country_from_items(items)
            city, state = detect_city_from_items(items, country, geo_data['cities_by_ids'])
            results[_id] = {
                'country': country,
                'city': city,
                'state': state,
            }
        else:
            results[_id] = {
                'country': None,
                'city': None,
                'state': None,
            }

    return results


def detect_geo(user_ids,
               geo_locations_dictionary,
               social_network):
    # get data
    account_descriptions = get_account_descriptions(user_ids, social_network)

    # get geo from text
    text_entities = detect_entities_from_text(account_descriptions,
                                              geo_locations_dictionary)

    probable_locations = get_most_probable_location(text_entities, geo_locations_dictionary)

    # save results
    m_set_geo_data(probable_locations, social_network)
