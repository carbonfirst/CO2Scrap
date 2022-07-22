#!/bin/env python3
# -*- coding: utf-8 -*-
# =========================================================================================================
# Author: Abel Souza
# Created date: 4/10/21
# Description: Carbon Intensity co2signal.com Scrapper. 
# =========================================================================================================
#
#    DISCLAIMER:
#
#    Any data collected in here is the exclusive property of Tomorrow and/or related parties. 
#    If in doubt about rights to use this data, please contact hello@tmrow.com
#
# -- END OF DISCLAIMER --

import sys
import argparse
import requests
import json
import itertools
import random
import logging
import csv
import time
import os

_counter = itertools.count()
api_url = "https://api.co2signal.com/v1/latest"
apitokens = {} # co2_signal.com API token keys to 'round-robin'. 
datacenters = []
zones = {}

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def add_token(user, token):
    apitokens[user] = token

def get_token():
    token = None
    if len(apitokens) == 0:
        logger.info("No tokens added! Use add_token(TOKEN) to add valid co2signal.com tokens!")
    else:
        token_id = next(_counter) % len(apitokens)
        for i, key in enumerate(apitokens):
            if i == token_id:
                token = key
        #token = apitokens[token_id % len(apitokens)]
    return token

def auth_header(auth_token):
    header = {'auth-token': auth_token}
    return header

'''
 The API has a rate limit of 30 requests per-hour per-auth-token. 
'''
def get_latest(api_url):
    token = get_token()
    if token == None:
        logger.warning("No token provided!")
        return (None, None)
    header = auth_header(apitokens[token])
    response = None
    try:
        response = requests.get(api_url, headers=header).json()
    except Exception as e:
        logger.warning("Error in get_latest(): {}".format(e))

    return (token, response)

def get_latest_perCountry(countryCode): 
    parameter = "?countryCode="
    country_url = api_url + parameter + countryCode
    return get_latest(country_url)

def get_latest_geoCor(lon, lat):
    lon_par = "?lon=" + str(lon)
    lat_par = "?lat=" + str(lat)
    geoCor_url = api_url + lon_par + lat_par
    return get_latest(geoCor_url)

def parse_request(latest, output_format='csv', print_out=True, output_file=None):
    """  Output Example: 
         {'_disclaimer': "This data is the exclusive property of Tomorrow and/or related parties. If you're in doubt about your rights to use this data, please contact hello@tmrow.com", 'status': 'ok', 'countryCode': 'FR', 'data': {'datetime': '2021-10-01T20:00:00.000Z', 'carbonIntensity': 38, 'fossilFuelPercentage': 3.5000000000000004}, 'units': {'carbonIntensity': 'gCO2eq/kWh'}}
    """
    parsed_list = None
    if output_format == 'csv':
        #if header == True:
        #    csv_header = 'datetime,status,countryCode,carbonIntensity,units,fossilFuelPercentage'
        try:
            parsed_list = [int(time.time()), latest['data']['datetime'], latest['status'], latest['countryCode'], latest['data']['carbonIntensity'], 'gCO2eq/kWh', latest['data']['fossilFuelPercentage']]
        except Exception as e:
            logger.warning("Error parsing the request output: {}".format(e))
            return None

    if print_out == True:
        logger.info(latest)
    return parsed_list

def save_zone_co2_intensity(zone, zone_csv_row, output_dir, dc=False):
    zone_file_path = os.path.join(output_dir, zone + ".csv")

    if not os.path.exists(zone_file_path):
       logger.info("Creating csv file for zone {} in {}".format(zone, output_dir)) 
       try:
           if dc:
               header = ["timestamp", "zone_datetime", "status", "provider", "code", "zone_name", "zone_carbon_intensity_avg", "zone_carbon_intensity_unit"]
           else:
               header = ["timestamp", "zone_datetime", "status", "zone_name", "carbon_intensity_avg", "carbon_intensity_unit", "fossilFuelPercentage"]
           zone_file = open(zone_file_path, "w", encoding='UTF8', newline='')
           zone_csv_writer = csv.writer(zone_file)
           zone_csv_writer.writerow(header)
       except Exception as e:
           logger.error("Error while creating and writing to csv file: {}".format(e))

    logger.info("Adding csv row for zone {} in {}".format(zone, output_dir))
    try:   
        zone_file = open(zone_file_path, "a", encoding='UTF8', newline='')
        zone_csv_writer = csv.writer(zone_file)
        zone_csv_writer.writerow(zone_csv_row)
    except Exception as e:
        logger.error("Error while opening and writing to csv file: {}".format(e))    

def exec_zones(output_dir):
    for zone in zones:
        logger.info('Requesting CO2 information from Zone {}'.format(zone))
        token, co2_zone_req = get_latest_perCountry(zone)
        if 'status' in co2_zone_req:
            if co2_zone_req['status'] == 'ok':
                zone_csv_row = parse_request(co2_zone_req)
                if zone_csv_row == None:
                    logger.error("Error retrieving data for zone region {}; not storing it.".format(zone))
                else:
                    #co2_int = random.randint(0, 1000)
                    zones[zone] = co2_zone_req
                    save_zone_co2_intensity(zone, zone_csv_row, output_dir)
                    # account data for each datacenter
                    for dc in datacenters:
                        #header = ["local_timestamp", "datetime", "status", "provider", "code", "zone_name", "zone_carbon_intensity_avg", "zone_carbon_intensity_unit"]
                        if dc['country_code'] == zone:
                            dc_name = dc['provider'] + '-' + dc['code']
                            dc_csv_row = [zone_csv_row[0], zone_csv_row[1], zone_csv_row[2], dc['provider'], dc['code'], dc['country_code'], zone_csv_row[4], zone_csv_row[5]]
                            save_zone_co2_intensity(dc_name + '-series', dc_csv_row, output_dir + 'providers', dc=True)
                            logger.info("Local CO2 info for provider {} stored in {}".format(dc_name, output_dir + 'providers'))
            else:
                logger.warning("Non-ok request status for token {}: {}".format(token, co2_zone_req))
                # check if zone has 'carbonIntensity' item and handle error
        else:
            req_out = co2_zone_req['message']
            logger.warning("API error in zone {}: {}".format(zone, req_out))
            logger.warning("Token: {}".format(token))
            #break
    logger.info(zones)

def parse_regions(regions_file):
    datacenters_file = open(regions_file,)
    regions_json = json.load(datacenters_file)

    # Fix this!
    for region in regions_json:
        if region['country_code'] != None:
            datacenters.append(region)
            zones[region['country_code']] = None

    #logger.info(datacenters)
    #logger.info(zones)

def parse_tokens(tokens_file):
    tokens_file = open(tokens_file,)
    tokens_json = json.load(datacenters_file)

    # Fix this!
    for region in regions_json:
        if region['country_code'] != None:
            datacenters.append(region)
            zones[region['country_code']] = None

def serve():
    parser = argparse.ArgumentParser(__name__)
    parser.add_argument("--auth-tokens", dest="auth_tokens", type=str, default='tokens.json', help="File with list of Authorization tokens (from co2signal.com) per-line")
    parser.add_argument("--regions-file", dest="regions", default="cloud_regions.json", type=str,
                        help="Input JSON file with Cloud Regions to collect Carbon Intensity from")
    parser.add_argument('--output_dir', required='--regions-file' in sys.argv, #only required if --regions-file is given
                        help="Directory to store Carbon Intensity for each Cloud Region")
    parser.add_argument("--country-zone", dest="country", type=str, nargs='+', help="Country Zone Name")
    parser.add_argument("--lon", dest="longitude", type=str,
                        help="Geographical Longitude")
    parser.add_argument("--lat", dest="latitude", type=str,
                        help="Geographical Latitude")
    parser.add_argument("--api_url", dest="api_url", type=str, default="https://api.co2signal.com/v1/latest",
                        help="co2signal.com/electricityMap API url if the default has been changed")
    parser.add_argument("--sleep", dest="sleep", type=float, default=900, help="Sleep time in seconds between API requests")

    args = parser.parse_args()
    build_parser(args)

def build_parser(args):
    logging.basicConfig(format="[%(levelname)s] %(asctime)s %(message)s")

    # Parse tokens
    tokens_file = open(args.auth_tokens,)
    tokens_json = json.load(tokens_file)
    for record in tokens_json:
        #print(record)
        add_token(record['user'], record['token'])
    #logger.info(apitokens)

    api_url = args.api_url

    if args.regions != None and args.country != None:
        logger.error("Pass only one argument, either regions or country!")
        args.regions = None

    if args.regions != None:
        parse_regions(args.regions)
        output_dir = os.path.abspath(args.output_dir)
        if os.path.exists(output_dir):
            exec_zones(args.output_dir)
        else:
            logger.error("Directory {} does not exist.".format(output_dir))

    else:
        if args.country != None:
            for country in args.country:
                token, latest = get_latest_perCountry(country)
                parsed_req = parse_request(latest)
                if parsed_req == None:
                    logger.error("Error retrieving data for zone region {}, not storing it: {}".format(country, latest))
                else:
                    print(parsed_req)
                    
            #latest_req = json.loads(latest_req_json)
        else:
            if args.lat != None and args.lon != None:
                latest = get_latest_geoCor(args.lon, args.lat)

    #print_request(latest, output_format='json')

if __name__ == "__main__":
    serve()
