#!/usr/local/bin/python
# -*- coding: utf-8 -*-
"""
Copyright 2016 Eleftherios Anagnostopoulos for Ericsson AB

Licensed under the Apache License, Version 2.0 (the "License"); you may not use
this file except in compliance with the License. You may obtain a copy of the
License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software distributed
under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
CONDITIONS OF ANY KIND, either express or implied. See the License for the
specific language governing permissions and limitations under the License.
"""
import requests
import json
import time
from src.common.logger import log

host = 'http://127.0.0.1'
port = '2000'


class JSONResponseEncoder(json.JSONEncoder):
    def default(self, o):
        return o.__dict__


def get_bus_stops():
    url = host + ':' + port + '/get_bus_stops_dictionary_to_list'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {}
    request = requests.post(url, data=data, headers=headers)
    bus_stops = json.loads(request.text)

    for bus_stop in bus_stops:
        print bus_stop


def get_route_between_bus_stops(starting_bus_stop_name, ending_bus_stop_name):
    url = host + ':' + port + '/get_route_between_bus_stops'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {'starting_bus_stop_name': starting_bus_stop_name,
            'ending_bus_stop_name': ending_bus_stop_name}
    request = requests.post(url, data=data, headers=headers)

    # response = {'starting_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #             'ending_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #             'route': {'total_distance', 'total_time', 'node_osm_ids', 'points', 'distances_from_starting_node',
    #                       'times_from_starting_node', 'distances_from_previous_node', 'times_from_previous_node'}}
    response = json.loads(request.text)

    starting_bus_stop = response.get('starting_bus_stop')
    ending_bus_stop = response.get('ending_bus_stop')
    route = response.get('route')
    total_distance = route.get('total_distance')
    total_time = route.get('total_time')
    node_osm_ids = route.get('node_osm_ids')
    points = route.get('points')
    distances_from_starting_node = route.get('distances_from_starting_node')
    times_from_starting_node = route.get('times_from_starting_node')
    distances_from_previous_node = route.get('distances_from_previous_node')
    times_from_previous_node = route.get('times_from_previous_node')

    output = '\nRequest: get_route_between_bus_stops' + \
             '\nstarting_bus_stop: ' + str(starting_bus_stop) + \
             '\nending_bus_stop: ' + str(ending_bus_stop) + \
             '\ntotal_distance: ' + str(total_distance) +\
             '\ntotal_time: ' + str(total_time) +\
             '\nnode_osm_ids: ' + str(node_osm_ids) +\
             '\npoints: ' + str(points) +\
             '\ndistances_from_starting_node: ' + str(distances_from_starting_node) +\
             '\ntimes_from_starting_node: ' + str(times_from_starting_node) +\
             '\ndistances_from_previous_node: ' + str(distances_from_previous_node) +\
             '\ntimes_from_previous_node: ' + str(times_from_previous_node)

    print output


def get_multiple_routes_between_bus_stops(starting_bus_stop_name, ending_bus_stop_name, number_of_routes):
    url = host + ':' + port + '/get_multiple_routes_between_bus_stops'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {'starting_bus_stop_name': starting_bus_stop_name,
            'ending_bus_stop_name': ending_bus_stop_name,
            'number_of_routes': number_of_routes}
    request = requests.post(url, data=data, headers=headers, timeout=60)

    # response = {'starting_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #             'ending_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #             'routes': [{'total_distance', 'total_time', 'node_osm_ids', 'points', 'distances_from_starting_node',
    #                         'times_from_starting_node', 'distances_from_previous_node', 'times_from_previous_node'}]}
    response = json.loads(request.text)

    starting_bus_stop = response.get('starting_bus_stop')
    ending_bus_stop = response.get('ending_bus_stop')
    routes = response.get('routes')

    for route in routes:
        total_distance = route.get('total_distance')
        total_time = route.get('total_time')
        node_osm_ids = route.get('node_osm_ids')
        points = route.get('points')
        distances_from_starting_node = route.get('distances_from_starting_node')
        times_from_starting_node = route.get('times_from_starting_node')
        distances_from_previous_node = route.get('distances_from_previous_node')
        times_from_previous_node = route.get('times_from_previous_node')

        output = '\nRequest: get_multiple_routes_between_bus_stops' + \
                 '\nstarting_bus_stop: ' + str(starting_bus_stop) + \
                 '\nending_bus_stop: ' + str(ending_bus_stop) + \
                 '\ntotal_distance: ' + str(total_distance) +\
                 '\ntotal_time: ' + str(total_time) +\
                 '\nnode_osm_ids: ' + str(node_osm_ids) +\
                 '\npoints: ' + str(points) +\
                 '\ndistances_from_starting_node: ' + str(distances_from_starting_node) +\
                 '\ntimes_from_starting_node: ' + str(times_from_starting_node) +\
                 '\ndistances_from_previous_node: ' + str(distances_from_previous_node) +\
                 '\ntimes_from_previous_node: ' + str(times_from_previous_node)

        print output


def get_route_between_multiple_bus_stops(bus_stop_names):
    url = host + ':' + port + '/get_route_between_multiple_bus_stops'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {'bus_stop_names': bus_stop_names}
    request = requests.post(url, data=data, headers=headers)
    response = json.loads(request.text)

    # response = [{'starting_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #              'ending_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #              'route': {'total_distance', 'total_time', 'node_osm_ids', 'points', 'distances_from_starting_node',
    #                        'times_from_starting_node', 'distances_from_previous_node', 'times_from_previous_node'}}]

    for intermediate_response in response:
        starting_bus_stop = intermediate_response.get('starting_bus_stop')
        ending_bus_stop = intermediate_response.get('ending_bus_stop')
        intermediate_route = intermediate_response.get('route')
        total_distance = intermediate_route.get('total_distance')
        total_time = intermediate_route.get('total_time')
        node_osm_ids = intermediate_route.get('node_osm_ids')
        points = intermediate_route.get('points')
        distances_from_starting_node = intermediate_route.get('distances_from_starting_node')
        times_from_starting_node = intermediate_route.get('times_from_starting_node')
        distances_from_previous_node = intermediate_route.get('distances_from_previous_node')
        times_from_previous_node = intermediate_route.get('times_from_previous_node')

        output = '\nRequest: get_route_between_multiple_bus_stops' + \
                 '\nstarting_bus_stop: ' + str(starting_bus_stop) + \
                 '\nending_bus_stop: ' + str(ending_bus_stop) + \
                 '\ntotal_distance: ' + str(total_distance) +\
                 '\ntotal_time: ' + str(total_time) +\
                 '\nnode_osm_ids: ' + str(node_osm_ids) +\
                 '\npoints: ' + str(points) +\
                 '\ndistances_from_starting_node: ' + str(distances_from_starting_node) +\
                 '\ntimes_from_starting_node: ' + str(times_from_starting_node) +\
                 '\ndistances_from_previous_node: ' + str(distances_from_previous_node) +\
                 '\ntimes_from_previous_node: ' + str(times_from_previous_node)

        print output


def get_multiple_routes_between_multiple_bus_stops(bus_stop_names, number_of_routes):
    url = host + ':' + port + '/get_multiple_routes_between_multiple_bus_stops'
    headers = {'content-type': 'application/x-www-form-urlencoded'}
    data = {'bus_stop_names': bus_stop_names,
            'number_of_routes': number_of_routes}
    request = requests.post(url, data=data, headers=headers, timeout=60)
    response = json.loads(request.text)

    # response = [{'starting_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #              'ending_bus_stop': {'osm_id', 'name', 'point': {'longitude', 'latitude'}},
    #              'routes': [{'total_distance', 'total_time', 'node_osm_ids', 'points', 'distances_from_starting_node',
    #                          'times_from_starting_node', 'distances_from_previous_node',
    #                          'times_from_previous_node'}]}]

    for intermediate_response in response:
        starting_bus_stop = intermediate_response.get('starting_bus_stop')
        ending_bus_stop = intermediate_response.get('ending_bus_stop')
        intermediate_routes = intermediate_response.get('routes')

        for intermediate_route in intermediate_routes:
            total_distance = intermediate_route.get('total_distance')
            total_time = intermediate_route.get('total_time')
            node_osm_ids = intermediate_route.get('node_osm_ids')
            points = intermediate_route.get('points')
            distances_from_starting_node = intermediate_route.get('distances_from_starting_node')
            times_from_starting_node = intermediate_route.get('times_from_starting_node')
            distances_from_previous_node = intermediate_route.get('distances_from_previous_node')
            times_from_previous_node = intermediate_route.get('times_from_previous_node')

            output = '\nRequest: get_route_between_multiple_bus_stops' + \
                     '\nstarting_bus_stop: ' + str(starting_bus_stop) + \
                     '\nending_bus_stop: ' + str(ending_bus_stop) + \
                     '\ntotal_distance: ' + str(total_distance) +\
                     '\ntotal_time: ' + str(total_time) +\
                     '\nnode_osm_ids: ' + str(node_osm_ids) +\
                     '\npoints: ' + str(points) +\
                     '\ndistances_from_starting_node: ' + str(distances_from_starting_node) +\
                     '\ntimes_from_starting_node: ' + str(times_from_starting_node) +\
                     '\ndistances_from_previous_node: ' + str(distances_from_previous_node) +\
                     '\ntimes_from_previous_node: ' + str(times_from_previous_node)

            print output


if __name__ == '__main__':
    log(module_name='route_generator_test', log_type='INFO',
        log_message='get_route_between_multiple_bus_stops: starting')
    bus_stop_names = ['Centralstationen', 'Stadshuset', 'Skolgatan', 'Ekonomikum', 'Studentstaden', 'Rickomberga',
                      'Oslogatan', 'Reykjaviksgatan', 'Ekebyhus', 'Sernanders väg', 'Flogsta centrum']
    start_time = time.time()
    get_route_between_multiple_bus_stops(bus_stop_names=bus_stop_names)
    elapsed_time = time.time() - start_time
    log(module_name='mongodb_database_test', log_type='INFO',
        log_message='initialize_database_connection: finished - elapsed_time = ' + str(elapsed_time) + ' sec')