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
import time
from src.common.logger import log
from src.common.variables import timetables_starting_datetime_testing_value, timetables_ending_datetime_testing_value, \
    requests_min_departure_datetime_testing_value, requests_max_departure_datetime_testing_value
from src.look_ahead.look_ahead_handler import LookAheadHandler


class LookAheadHandlerTester(object):
    def __init__(self):
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='initialize_look_ahead_handler: starting')
        self.start_time = time.time()
        self.look_ahead_handler = LookAheadHandler()
        self.elapsed_time = time.time() - self.start_time
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='initialize_look_ahead_handler: finished - elapsed_time = '
                        + str(self.elapsed_time) + ' sec')

    def test_generate_bus_line(self, line_id, bus_stop_names):
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='test_generate_bus_line: starting')
        self.start_time = time.time()
        self.look_ahead_handler.generate_bus_line(
            line_id=line_id,
            bus_stop_names=bus_stop_names
        )
        elapsed_time = time.time() - self.start_time
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='test_generate_bus_line: finished - elapsed_time = '
                        + str(elapsed_time) + ' sec')

    def test_generate_timetables_for_bus_line_id(self, line_id):
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='generate_timetables_for_bus_line_id: starting')
        self.start_time = time.time()
        self.look_ahead_handler.generate_timetables_for_bus_line_id(
            line_id=line_id,
            timetables_starting_datetime=timetables_starting_datetime_testing_value,
            timetables_ending_datetime=timetables_ending_datetime_testing_value,
            requests_min_departure_datetime=requests_min_departure_datetime_testing_value,
            requests_max_departure_datetime=requests_max_departure_datetime_testing_value,
        )
        self.elapsed_time = time.time() - self.start_time
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='generate_timetables_for_bus_line_id: finished - elapsed_time = '
                        + str(self.elapsed_time) + ' sec')

    def test_generate_timetables_for_bus_lines(self):
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='generate_timetables_for_bus_lines: starting')
        self.start_time = time.time()
        self.look_ahead_handler.generate_timetables_for_bus_lines(
            timetables_starting_datetime=timetables_starting_datetime_testing_value,
            timetables_ending_datetime=timetables_ending_datetime_testing_value,
            requests_min_departure_datetime=requests_min_departure_datetime_testing_value,
            requests_max_departure_datetime=requests_max_departure_datetime_testing_value,
        )
        self.elapsed_time = time.time() - self.start_time
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='generate_timetables_for_bus_lines: finished - elapsed_time = '
                        + str(self.elapsed_time) + ' sec')

    def test_update_timetables_for_bus_line_id(self, line_id):
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='test_update_timetables_for_bus_line_id: starting')
        self.start_time = time.time()
        self.look_ahead_handler.update_timetables_of_bus_line_id(line_id=line_id)
        self.elapsed_time = time.time() - self.start_time
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='test_update_timetables_for_bus_line_id: finished - elapsed_time = '
                        + str(self.elapsed_time) + ' sec')

    def test_update_timetables_for_bus_lines(self):
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='test_update_timetables_for_bus_lines: starting')
        self.start_time = time.time()
        self.look_ahead_handler.update_timetables_of_bus_lines()
        self.elapsed_time = time.time() - self.start_time
        log(module_name='look_ahead_handler_test', log_type='INFO',
            log_message='test_update_timetables_for_bus_lines: finished - elapsed_time = '
                        + str(self.elapsed_time) + ' sec')


if __name__ == '__main__':
    bus_stop_names = [
        'Centralstationen', 'Stadshuset', 'Skolgatan', 'Ekonomikum', 'Studentstaden', 'Rickomberga',
        'Oslogatan', 'Reykjaviksgatan', 'Ekebyhus', 'Sernanders väg', 'Flogsta centrum', 'Sernanders väg',
        'Ekebyhus', 'Reykjaviksgatan', 'Oslogatan', 'Rickomberga', 'Studentstaden', 'Ekonomikum',
        'Skolgatan', 'Stadshuset', 'Centralstationen'
    ]
    tester = LookAheadHandlerTester()
    tester.test_generate_timetables_for_bus_line_id(line_id=1)
    # tester.test_generate_timetables_for_bus_lines()
    # tester.test_update_timetables_for_bus_line_id(line_id=1)
    # tester.test_update_timetables_for_bus_lines()
