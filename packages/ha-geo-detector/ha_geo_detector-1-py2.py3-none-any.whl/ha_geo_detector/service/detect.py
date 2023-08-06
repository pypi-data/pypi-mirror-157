import logging
import re

import phonenumbers
from Levenshtein import ratio

from workers.geo_detector.ha_geo_detector.service.additional import cleanup_and_tokenize


def detect_country_by_phone(text, countries_info):
    result = []
    country_code2_geoname_id = {}
    for country in countries_info:
        country_code2_geoname_id[country['iso']] = {
            'country_id': country['geoname_id'],
            'country_code': country['iso'],
            'population': country['population'],
        }

    for phone in phonenumbers.PhoneNumberMatcher(text, None):
        try:
            if phonenumbers.is_valid_number(phone.number):
                country_code = phonenumbers.region_code_for_number(phone.number)
                if country_code in country_code2_geoname_id:
                    result.append({
                        'feature': 'country_phone',
                        'match': phone.raw_string,
                        'city_id': 0,
                        'state_id': 0,
                        'country_id': country_code2_geoname_id[country_code]['country_id'],
                        'country_code': country_code2_geoname_id[country_code]['country_code'],
                        'population': country_code2_geoname_id[country_code]['population'],
                    })
        except phonenumbers.phonenumberutil.NumberParseException:
            logging.error("Phone number couldn't be parsed for some reason. Bad input?")

    return result


def detect_cities_by_geonames(text, cities_by_first_letter) -> list:
    matched = {}
    ngrams = []
    words = cleanup_and_tokenize(text)

    for i, word in enumerate(words):
        ngrams.append(word)
        if i < len(words) - 1:
            ngrams.append(' '.join(words[i:i + 2]))
        if i < len(words) - 2:
            ngrams.append(' '.join(words[i:i + 3]))
    for ngram in ngrams:
        if ngram[0] in cities_by_first_letter:
            for key, value in cities_by_first_letter[ngram[0]].items():
                if value['city_id'] not in matched:
                    if ratio(key, ngram) > 0.95:
                        matched[value['city_id']] = {
                                'feature': 'city',
                                'match': key,
                                'city_id': value['city_id'],
                                'state_id': value['state_id'],
                                'country_id': value['country_id'],
                                'country_code': value['country_code'],
                                'population': value['population'],
                            }

    return [item for item in matched.values()]


def detect_country_by_code(text, countries_by_code):
    return [{
            'feature': 'country_code',
            'match': key,
            'city_id': value['city_id'],
            'state_id': value['state_id'],
            'country_id': value['country_id'],
            'country_code': value['country_code'],
            'population': value['population'],
            } for key, value in countries_by_code.items() if key in cleanup_and_tokenize(text)]


def detect_country_by_emoji(text, countries_by_emoji):
    result = []
    regexp_flag_emoji = re.compile(u"([\U0001F1E6-\U0001F1FF]{2})", flags=re.UNICODE)
    # regexp_all_emoji = re.compile('[\U0002712\U0002714\U0002716\U000271d\U0002721\U0002728\U0002733\U0002734\U0002744\U0002747\U000274c\U000274e\U0002753-\U0002755\U0002757\U0002763\U0002764\U0002795-\U0002797\U00027a1\U00027b0\U00027bf\U0002934\U0002935\U0002b05-\U0002b07\U0002b1b\U0002b1c\U0002b50\U0002b55\U0003030\U000303d\U0001f004\U0001f0cf\U0001f170\U0001f171\U0001f17e\U0001f17f\U0001f18e\U0001f191-\U0001f19a\U0001f201\U0001f202\U0001f21a\U0001f22f\U0001f232-\U0001f23a\U0001f250\U0001f251\U0001f300-\U0001f321\U0001f324-\U0001f393\U0001f396\U0001f397\U0001f399-\U0001f39b\U0001f39e-\U0001f3f0\U0001f3f3-\U0001f3f5\U0001f3f7-\U0001f4fd\U0001f4ff-\U0001f53d\U0001f549-\U0001f54e\U0001f550-\U0001f567\U0001f56f\U0001f570\U0001f573-\U0001f579\U0001f587\U0001f58a-\U0001f58d\U0001f590\U0001f595\U0001f596\U0001f5a5\U0001f5a8\U0001f5b1\U0001f5b2\U0001f5bc\U0001f5c2-\U0001f5c4\U0001f5d1-\U0001f5d3\U0001f5dc-\U0001f5de\U0001f5e1\U0001f5e3\U0001f5ef\U0001f5f3\U0001f5fa-\U0001f64f\U0001f680-\U0001f6c5\U0001f6cb-\U0001f6d0\U0001f6e0-\U0001f6e5\U0001f6e9\U0001f6eb\U0001f6ec\U0001f6f0\U0001f6f3\U0001f910-\U0001f918\U0001f980-\U0001f984\U0001f9c0\U0003297\U0003299\U000a9\U000ae\U000203c\U0002049\U0002122\U0002139\U0002194-\U0002199\U00021a9\U00021aa\U000231a\U000231b\U0002328\U0002388\U00023cf\U00023e9-\U00023f3\U00023f8-\U00023fa\U00024c2\U00025aa\U00025ab\U00025b6\U00025c0\U00025fb-\U00025fe\U0002600-\U0002604\U000260e\U0002611\U0002614\U0002615\U0002618\U000261d\U0002620\U0002622\U0002623\U0002626\U000262a\U000262e\U000262f\U0002638-\U000263a\U0002648-\U0002653\U0002660\U0002663\U0002665\U0002666\U0002668\U000267b\U000267f\U0002692-\U0002694\U0002696\U0002697\U0002699\U000269b\U000269c\U00026a0\U00026a1\U00026aa\U00026ab\U00026b0\U00026b1\U00026bd\U00026be\U00026c4\U00026c5\U00026c8\U00026ce\U00026cf\U00026d1\U00026d3\U00026d4\U00026e9\U00026ea\U00026f0-\U00026f5\U00026f7-\U00026fa\U00026fd\U0002702\U0002705\U0002708-\U000270d\U000270f]|\U00023\U00020e3|\U0002a\U00020e3|\U00030\U00020e3|\U00031\U00020e3|\U00032\U00020e3|\U00033\U00020e3|\U00034\U00020e3|\U00035\U00020e3|\U00036\U00020e3|\U00037\U00020e3|\U00038\U00020e3|\U00039\U00020e3|\U0001f1e6[\U0001f1e8-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f2\U0001f1f4\U0001f1f6-\U0001f1fa\U0001f1fc\U0001f1fd\U0001f1ff]|\U0001f1e7[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ef\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1fe\U0001f1ff]|\U0001f1e8[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ee\U0001f1f0-\U0001f1f5\U0001f1f7\U0001f1fa-\U0001f1ff]|\U0001f1e9[\U0001f1ea\U0001f1ec\U0001f1ef\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1ff]|\U0001f1ea[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ed\U0001f1f7-\U0001f1fa]|\U0001f1eb[\U0001f1ee-\U0001f1f0\U0001f1f2\U0001f1f4\U0001f1f7]|\U0001f1ec[\U0001f1e6\U0001f1e7\U0001f1e9-\U0001f1ee\U0001f1f1-\U0001f1f3\U0001f1f5-\U0001f1fa\U0001f1fc\U0001f1fe]|\U0001f1ed[\U0001f1f0\U0001f1f2\U0001f1f3\U0001f1f7\U0001f1f9\U0001f1fa]|\U0001f1ee[\U0001f1e8-\U0001f1ea\U0001f1f1-\U0001f1f4\U0001f1f6-\U0001f1f9]|\U0001f1ef[\U0001f1ea\U0001f1f2\U0001f1f4\U0001f1f5]|\U0001f1f0[\U0001f1ea\U0001f1ec-\U0001f1ee\U0001f1f2\U0001f1f3\U0001f1f5\U0001f1f7\U0001f1fc\U0001f1fe\U0001f1ff]|\U0001f1f1[\U0001f1e6-\U0001f1e8\U0001f1ee\U0001f1f0\U0001f1f7-\U0001f1fb\U0001f1fe]|\U0001f1f2[\U0001f1e6\U0001f1e8-\U0001f1ed\U0001f1f0-\U0001f1ff]|\U0001f1f3[\U0001f1e6\U0001f1e8\U0001f1ea-\U0001f1ec\U0001f1ee\U0001f1f1\U0001f1f4\U0001f1f5\U0001f1f7\U0001f1fa\U0001f1ff]|\U0001f1f4\U0001f1f2|\U0001f1f5[\U0001f1e6\U0001f1ea-\U0001f1ed\U0001f1f0-\U0001f1f3\U0001f1f7-\U0001f1f9\U0001f1fc\U0001f1fe]|\U0001f1f6\U0001f1e6|\U0001f1f7[\U0001f1ea\U0001f1f4\U0001f1f8\U0001f1fa\U0001f1fc]|\U0001f1f8[\U0001f1e6-\U0001f1ea\U0001f1ec-\U0001f1f4\U0001f1f7-\U0001f1f9\U0001f1fb\U0001f1fd-\U0001f1ff]|\U0001f1f9[\U0001f1e6\U0001f1e8\U0001f1e9\U0001f1eb-\U0001f1ed\U0001f1ef-\U0001f1f4\U0001f1f7\U0001f1f9\U0001f1fb\U0001f1fc\U0001f1ff]|\U0001f1fa[\U0001f1e6\U0001f1ec\U0001f1f2\U0001f1f8\U0001f1fe\U0001f1ff]|\U0001f1fb[\U0001f1e6\U0001f1e8\U0001f1ea\U0001f1ec\U0001f1ee\U0001f1f3\U0001f1fa]|\U0001f1fc[\U0001f1eb\U0001f1f8]|\U0001f1fd\U0001f1f0|\U0001f1fe[\U0001f1ea\U0001f1f9]|\U0001f1ff[\U0001f1e6\U0001f1f2\U0001f1fc]')
    for flag in regexp_flag_emoji.findall(text):
        code_points = tuple(ord(x) - 127397 for x in flag)
        country_code = "%c%c" % code_points
        if country_code in countries_by_emoji:
            result.append({
                'feature': 'country_emoji',
                'match': flag,
                'city_id': 0,
                'state_id': 0,
                'country_id': countries_by_emoji[country_code]['country_id'],
                'country_code': countries_by_emoji[country_code]['country_code'],
                'population': countries_by_emoji[country_code]['population']
            })

    return result


def detect_country_by_name(text, countries_by_name):
    return [{
        'feature': 'country_name',
        'match': key,
        'city_id': value['city_id'],
        'state_id': value['state_id'],
        'country_id': value['country_id'],
        'country_code': value['country_code'],
        'population': value['population'],
    } for key, value in countries_by_name.items() if key in text.lower()]


def detect_country_by_nationality(text, countries_by_nationality):
    return [{
        'feature': 'country_nationality',
        'match': key,
        'city_id': value['city_id'],
        'state_id': value['state_id'],
        'country_id': value['country_id'],
        'country_code': value['country_code'],
        'population': value['population'],
    } for key, value in countries_by_nationality.items() if key in cleanup_and_tokenize(text)]


def detect_country_by_state(text, countries_by_state):
    return [{
        'feature': 'country_state',
        'match': key,
        'city_id': value['city_id'],
        'state_id': value['state_id'],
        'country_id': value['country_id'],
        'country_code': value['country_code'],
        'population': value['population'],
    } for key, value in countries_by_state.items() if key in cleanup_and_tokenize(text)]


def detect_country_by_domain(text, countries_by_domain):
    result = []
    for item in countries_by_domain:
        for match in item['rx'].findall(text):
            result.append({
                'feature': 'country_domain',
                'match': match,
                'city_id': 0,
                'state_id': 0,
                'country_id': item['country_id'],
                'country_code': item['country_code'],
                'population': item['population']
            })

    return result
