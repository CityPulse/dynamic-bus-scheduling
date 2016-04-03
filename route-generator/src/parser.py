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
from imposm.parser import OSMParser
from path_finder import bus_road_types, find_path, standard_speed
from point import distance, Point
from address import Address
from mongo_connection import Connection
import re


# from multiprocessing import Process
import os
# import time
# import signal


class Parser(object):
    relations = None
    ways_filter = None
    nodes_filter = None
    relations_filter = None

    def __init__(self, osm_filename):
        """
        :param osm_filename: Directory of the input OSM file
        :type osm_filename: string
        """
        self.osm_filename = osm_filename
        self.points = {}
        self.nodes = {}
        self.ways = {}
        self.bus_stops = {}
        self.edges = {}
        self.address_book = {}

    def add_address(self, name, node_id, point):
        """
        Add an address to the address_book dictionary.

        :type name: string
        :type node_id: integer
        :type point: Point
        """
        if name is None or name == '' or node_id is None or point is None:
            return

        # document = {'name': name, 'node_id': node_id,
        #             'point': {'longitude': point.longitude, 'latitude': point.latitude}}

        # self.address_book.append(document)
        # self.connection.insert_address(name=name, node_id=node_id, point=point)

        if name not in self.address_book:
            self.address_book[name] = Address(name, node_id, point)
        else:
            self.address_book[name].add_node(node_id=node_id, point=point)

    def add_bus_stop(self, osm_id, name, point):
        """
        Add a bus_stop to the bus_stops dictionary.

        :type osm_id: integer
        :type name: string
        :type point: Point
        """
        # document = {'osm_id': osm_id, 'name': name,
        #             'point': {'longitude': point.longitude, 'latitude': point.latitude}}
        # self.bus_stops.append(document)
        # self.connection.insert_bus_stop(osm_id=osm_id, name=name, point=point)
        self.bus_stops[osm_id] = {'name': name, 'point': point}

    def add_edge(self, from_node, to_node, max_speed, road_type, way_id, traffic_density=None):
        """
        Add an edge to the edges dictionary.

        :param from_node: osm_id: integer
        :param to_node: osm_id: integer
        :type max_speed: float or integer
        :type road_type: string
        :param way_id: osm_id: integer
        :param traffic_density: A value between 0 and 1 indicating the density of traffic: float
        """
        if traffic_density is None:
            traffic_density = 0

        # document = {'from_node': from_node, 'to_node': to_node, 'max_speed': max_speed, 'road_type': road_type,
        #             'way_id': way_id, 'traffic_density': traffic_density}

        # self.edges.append(document)
        # self.connection.insert_edge(from_node=from_node, to_node=to_node, max_speed=max_speed, road_type=road_type,
        #                             way_id=way_id, traffic_density=traffic_density)

        if from_node in self.edges:
            self.edges[from_node].append({'to_node': to_node, 'max_speed': max_speed, 'road_type': road_type,
                                          'way_id': way_id, 'traffic_density': traffic_density})
        else:
            self.edges[from_node] = [{'to_node': to_node, 'max_speed': max_speed, 'road_type': road_type,
                                      'way_id': way_id, 'traffic_density': traffic_density}]
        #
        # if to_node not in self.edges:
        #     self.edges[to_node] = []

    def add_node(self, osm_id, tags, point):
        """
        Add a node to the nodes dictionary.

        :type osm_id: integer
        :type tags: {}
        :type point: Point
        """
        # document = {'osm_id': osm_id, 'tags': tags,
        #             'point': {'longitude': point.longitude, 'latitude': point.latitude}}
        # self.nodes.append(document)
        # self.connection.insert_node(osm_id=osm_id, tags=tags, point=point)
        self.nodes[osm_id] = {'tags': tags, 'point': point}

    def add_point(self, osm_id, point):
        """
        Add a point to the points dictionary.

        :type osm_id: integer
        :type point: Point
        """
        # document = {'osm_id': osm_id, 'point': {'longitude': point.longitude, 'latitude': point.latitude}}
        # self.points.append(document)
        # self.connection.insert_point(osm_id=osm_id, point=point)
        self.points[osm_id] = point

    def add_way(self, osm_id, tags, references):
        """
        Add a way to the ways dictionary.

        :type osm_id: integer
        :type tags: {}
        :param references: [osm_id]
        """
        # document = {'osm_id': osm_id, 'tags': tags, 'references': references}
        # self.ways.append(document)
        # self.connection.insert_way(osm_id=osm_id, tags=tags, references=references)
        self.ways[osm_id] = {'tags': tags, 'references': references}

    @staticmethod
    def address_range(number):
        """
        Turn address number format into a range. E.g. '1A-1C' to '1A','1B','1C'.

        :param number: string
        :return: generator
        """
        regular_expression = re.compile(
            '''
            ((?P<starting_address_number>(\d+))
            (?P<starting_address_letter> ([a-zA-Z]*))
            \s*-\s*
            (?P<ending_address_number>(\d+))
            (?P<ending_address_letter>([a-zA-Z]*)))
            ''',
            re.VERBOSE
        )
        match = regular_expression.search(number)

        if match:
            starting_number = match.groupdict()['starting_address_number']
            starting_letter = match.groupdict()['starting_address_letter']
            ending_number = match.groupdict()['ending_address_number']
            ending_letter = match.groupdict()['ending_address_letter']

            if starting_letter and ending_letter:
                for c in xrange(ord(starting_letter), ord(ending_letter) + 1):
                    yield '' + starting_number + chr(c)
            elif starting_number and ending_number:
                for c in xrange(int(starting_number), int(ending_number) + 1):
                    yield c
            else:
                yield '' + starting_number + starting_letter
        else:
            numbers = number.split(',')

            if len(numbers) > 1:
                for num in numbers:
                    yield num.strip()
            else:
                yield number

    def get_list_of_addresses(self):
        list_of_addresses = []

        for name, address in self.address_book.iteritems():
            for node_id, point in address.nodes:
                document = {'name': name, 'node_id': node_id,
                            'point': {'longitude': point.longitude, 'latitude': point.latitude}}
                list_of_addresses.append(document)

        return list_of_addresses

    def get_list_of_bus_stops(self):
        list_of_bus_stops = []

        for osm_id, values in self.bus_stops.iteritems():
            name = values.get('name')
            point = values.get('point')
            document = {'osm_id': osm_id, 'name': name,
                        'point': {'longitude': point.longitude, 'latitude': point.latitude}}
            list_of_bus_stops.append(document)

        return list_of_bus_stops

    def get_list_of_edges(self):
        list_of_edges = []

        for osm_id, list_of_values in self.edges.iteritems():
            for values in list_of_values:
                to_node = values.get('to_node')
                max_speed = values.get('max_speed')
                road_type = values.get('road_type')
                way_id = values.get('way_id')
                traffic_density = values.get('traffic_density')
                document = {'from_node': osm_id, 'to_node': to_node, 'max_speed': max_speed, 'road_type': road_type,
                            'way_id': way_id, 'traffic_density': traffic_density}
                list_of_edges.append(document)

        return list_of_edges

    def get_list_of_nodes(self):
        list_of_nodes = []

        for osm_id, values in self.nodes.iteritems():
            tags = values.get('tags')
            point = values.get('point')
            document = {'osm_id': osm_id, 'tags': tags,
                        'point': {'longitude': point.longitude, 'latitude': point.latitude}}
            list_of_nodes.append(document)

        return list_of_nodes

    def get_list_of_points(self):
        list_of_points = []

        for osm_id, point in self.points.iteritems():
            document = {'osm_id': osm_id, 'point': {'longitude': point.longitude, 'latitude': point.latitude}}
            list_of_points.append(document)

        return list_of_points

    def get_list_of_ways(self):
        list_of_ways = []

        for osm_id, values in self.ways.iteritems():
            tags = values.get('tags')
            references = values.get('references')
            document = {'osm_id': osm_id, 'tags': tags, 'references': references}
            list_of_ways.append(document)

        return list_of_ways

    def get_point_from_osm_id(self, osm_id):
        """
        Retrieve the point which correspond to a specific osm_id.

        :type osm_id: integer
        :return: Point
        """
        self.points.get(osm_id)
        # point = None
        # document = {'osm_id': osm_id, 'point': {'longitude': point.longitude, 'latitude': point.latitude}}
        #
        # for document in self.points:
        #     if document.get('osm_id') == osm_id:
        #         point_entry = document.get('point')
        #         point = Point(longitude=point_entry.get('longitude'), latitude=point_entry.get('latitude'))
        #         break
        #
        # return point

    def parse(self):
        parser = OSMParser(
            concurrency=2,
            coords_callback=self.parse_points,
            nodes_callback=self.parse_nodes,
            ways_callback=self.parse_ways,
            # relations_ callback=self.relations,
            # nodes_tag_filter=self.nodes_filter,
            # ways_tag_filter=self.ways_filter,
            # relations_tag_filter=self.relations_filter
        )
        parser.parse(self.osm_filename)

    def parse_address(self, osm_id, tags, point):
        """
        Parse the name, the street, and the house numbers which are related to an address, and add them to the
        address_book dictionary along with their corresponding osm_id val and points.

        :type osm_id: integer
        :param tags: {}
        :param point: Point
        """
        name = tags.get('name', '')
        street = tags.get('addr:street', '')
        house_number = tags.get('addr:housenumber', '')

        if name != '':
            self.add_address(name=name, node_id=osm_id, point=point)

        if street != '' and house_number != '':
            for num in self.address_range(house_number):
                address = street + ' ' + str(num)
                self.add_address(name=address, node_id=osm_id, point=point)

    def parse_edges(self, osm_id, tags, references):
        """
        Parse the edges which connect the nodes, bus_stops, and points of the map.

        :param osm_id: Corresponds to the osm_id of the way.
        :type osm_id: integer
        :type tags: {}
        :param references: [osm_id] The list of osm_id objects which are connected to each other.
        :type references: [integer]
        """
        oneway = tags.get('oneway', '') in ('yes', 'true', '1')
        max_speed = tags.get('maxspeed', standard_speed)
        road_type = tags.get('highway')

        for reference_index in range(len(references) - 1):
            self.add_edge(from_node=references[reference_index], to_node=references[reference_index + 1],
                          max_speed=max_speed, road_type=road_type, way_id=osm_id)

            if not oneway:
                self.add_edge(from_node=references[reference_index + 1], to_node=references[reference_index],
                              max_speed=max_speed, road_type=road_type, way_id=osm_id)

    def parse_nodes(self, nodes):
        """
        Parse the list of nodes and populate the corresponding dictionary.
        Parse the list of bus stops, which are included in the nodes, and populate the corresponding dictionary.
        Parse the list of addresses, where the nodes correspond to, and populate the corresponding dictionary.

        :type nodes: [(osm_id, tags, (longitude, latitude))]
        """
        for node in nodes:
            osm_id, tags, (longitude, latitude) = node
            point = Point(longitude=longitude, latitude=latitude)
            self.add_node(osm_id=osm_id, tags=tags, point=point)

            if all(term in tags for term in ['bus', 'name']):
                self.add_bus_stop(osm_id=osm_id, name=tags.get('name'), point=point)

            self.parse_address(osm_id=osm_id, tags=tags, point=point)

    def parse_points(self, coordinates):
        """
        Parse the list of points and populate the corresponding dictionary.

        :param coordinates: [(osm_id, longitude, latitude)]
        :type coordinates: [(integer, float, float)]
        """
        for osm_id, longitude, latitude in coordinates:
            point = Point(longitude=longitude, latitude=latitude)
            self.add_point(osm_id=osm_id, point=point)

    def parse_ways(self, ways):
        """
        Parse the list of ways and populate the corresponding dictionary
        with the ones that can be accessed by bus vehicles.

        :type ways: [()]
        """
        for way in ways:
            osm_id, tags, references = way

            if tags.get('motorcar') != 'no' and tags.get('highway') in bus_road_types:
                self.add_way(osm_id=osm_id, tags=tags, references=references)
                self.parse_edges(osm_id=osm_id, tags=tags, references=references)

            name = tags.get('name', '')
            if name != '':
                for reference in references:
                    self.add_address(name=name, node_id=reference,
                                     point=self.get_point_from_osm_id(osm_id=reference))

    # def print_address_book(self):
    #     print '-- Printing Address Book --'
    #     for name, values in self.address_book.iteritems():
    #         print 'Address: ' + name + ', Nodes:' + values.nodes_to_string()
    #         # print 'Address: ' + name + ', Center:' + values.get_center().coordinates_to_string()
    #
    # def print_bus_stops(self):
    #     print '-- Printing Bus Stops --'
    #     for osm_id, values in self.bus_stops.iteritems():
    #         print 'Bus_Stop: ' + str(osm_id) + ', Name: ' + str(values.get('name').encode('utf-8')) + \
    #               ', Point: ' + values.get('point').coordinates_to_string()
    #
    # def print_coordinates(self):
    #     print '-- Printing Coordinates --'
    #     for osm_id, point in self.points.iteritems():
    #         print 'Coordinates: ' + str(osm_id) + ', Point: ' + point.coordinates_to_string()
    #
    # def print_edges(self):
    #     print '-- Printing Edges --'
    #     for osm_id, list_of_values in self.edges.iteritems():
    #         for values in list_of_values:
    #             print 'From_Node: ' + str(osm_id) + ', To_Node: ' + str(values.get('to_node')) + \
    #                   ', Max_Speed: ' + str(values.get('max_speed')) + ', Way: ' + str(values.get('way_id'))
    #
    # def print_nodes(self):
    #     print '-- Printing Nodes --'
    #     for osm_id, values in self.nodes.iteritems():
    #         print 'Node: ' + str(osm_id) + ', Tags: ' + str(values.get('tags')) + \
    #               ', Point: ' + values.get('point').coordinates_to_string()
    #
    # def print_totals(self):
    #     print '-- Printing Totals --'
    #     print 'Number of Nodes: ', len(self.nodes)
    #     print 'Number of Coordinates: ', len(self.points)
    #     print 'Number of Ways: ', len(self.ways)
    #     print 'Number of Relations: ', len(self.relations)
    #
    # def print_ways(self):
    #     print '-- Printing Ways --'
    #     for osm_id, values in self.ways.iteritems():
    #         print 'Way: ' + str(osm_id) + ', Tags: ' + str(values.get('tags')) + \
    #               ', References: ' + str(values.get('references'))
    #
    # def test_edges(self):
    #     counter = 0
    #     for osm_id, list_of_values in self.edges.iteritems():
    #         for values in list_of_values:
    #             if values.get('to_node') not in self.points:
    #                 counter += 1
    #                 # print 'From_Node: ' + str(osm_id) + ', To_Node: ' + str(values.get('to_node'))
    #
    #     print counter


class MongoConnector(object):
    def __init__(self, parser, host, port):
        print 'Initializing MongoConnector'
        self.list_of_points = parser.get_list_of_points()
        print 'Points ok'
        self.list_of_nodes = parser.get_list_of_nodes()
        print 'Nodes ok'
        self.list_of_ways = parser.get_list_of_ways()
        print 'Ways ok'
        self.list_of_bus_stops = parser.get_list_of_bus_stops()
        print 'BusStops ok'
        self.list_of_edges = parser.get_list_of_edges()
        print 'Edges ok'
        self.list_of_addresses = parser.get_list_of_addresses()
        print 'Addresses ok'
        self.connection = Connection(host=host, port=port)
        print 'Connection ok'

    def populate_address_book(self):
        self.connection.insert_addresses(address_book=self.list_of_addresses)
        print 'MongoConnector: populate_address_book: ok'

    def populate_edges(self):
        self.connection.insert_edges(edges=self.list_of_edges)
        print 'MongoConnector: populate_edges: ok'

    def populate_nodes(self):
        self.connection.insert_nodes(nodes=self.list_of_nodes)
        print 'MongoConnector: populate_nodes: ok'

    def populate_points(self):
        self.connection.insert_points(points=self.list_of_points)
        print 'MongoConnector: populate_points: ok'

    def populate_bus_stops(self):
        self.connection.insert_bus_stops(bus_stops=self.list_of_bus_stops)
        print 'MongoConnector: populate_bus_stops: ok'

    def populate_ways(self):
        self.connection.insert_ways(ways=self.list_of_ways)
        print 'MongoConnector: populate_ways: ok'

    def populate_all_collections(self):
        print 'MongoConnector: populate_all_collections'
        self.populate_points()
        self.populate_nodes()
        self.populate_ways()
        self.populate_bus_stops()
        self.populate_edges()
        self.populate_address_book()

        # self.parser.populate_points()
        # print 'Points: ok'

        # self.parser.test_edges()
        # self.parser.print_nodes()
        # self.parser.print_edges()
        # self.parser.print_bus_stops()
        # self.parser.print_address_book()
        # print self.get_bus_stop_closest_to_coordinates(17.5945912, 59.8462059)
        # print self.get_bus_stops_within_distance(17.5945912, 59.8462059, 100)
        # print self.get_center_point_from_address_name('Forno Romano').coordinates_to_string()
        # Center:(17.6433065, 59.8579188)

        # points = []
        #
        # point = Point(longitude=1.0, latitude=1.0)
        # points.append(point)
        # point = Point(longitude=2.0, latitude=2.0)
        # points.append(point)
        # point = Point(longitude=3.0, latitude=3.0)
        # points.append(point)
        # point = Point(longitude=0.5, latitude=0.5)
        # points.append(point)
        #
        # point = Point(longitude=0.0, latitude=0.0)
        #
        # print closest_to(point, points)


# def printer():
#     # start_time = time.time()
#     pattern = ''
#
#     while (True):
#         # elapsed_time = time.time() - start_time
#         pattern += '='
#         print pattern,
#         time.sleep(1)

# class Tester(object):
#     """
#
#     """
#     def __init__(self):
#         self.edges = {}
#         self.points = {}
#         self.populate_points()
#         self.populate_edges()
#
#     def add_edge(self, from_node, to_node, max_speed, road_type=None, way_id=None, traffic_density=None):
#         """
#         Add an edge to the edges dictionary.
#
#         :param from_node: osm_id: integer
#         :param to_node: osm_id: integer
#         :type max_speed: float or integer
#         :type road_type: string
#         :param way_id: osm_id: integer
#         :param traffic_density: A value between 0 and 1 indicating the density of traffic: float
#         """
#         if road_type is None:
#             road_type = 'motorway'
#
#         if traffic_density is None:
#             traffic_density = 0
#
#         if from_node in self.edges:
#             self.edges[from_node].append({'to_node': to_node, 'max_speed': max_speed, 'road_type': road_type,
#                                           'way_id': way_id, 'traffic_density': traffic_density})
#         else:
#             self.edges[from_node] = [{'to_node': to_node, 'max_speed': max_speed, 'road_type': road_type,
#                                       'way_id': way_id, 'traffic_density': traffic_density}]
#
#         if to_node not in self.edges:
#             self.edges[to_node] = []
#
#     def add_point(self, osm_id, longitude, latitude):
#         """
#         Add a point to the points dictionary.
#
#         :type osm_id: integer
#         :type longitude: float
#         :type latitude: float
#         """
#         point = Point(longitude=longitude, latitude=latitude)
#         self.points[osm_id] = point
#
#     def populate_edges(self):
#         self.add_edge(from_node=1, to_node=2, max_speed=50)
#         self.add_edge(from_node=2, to_node=3, max_speed=50)
#         self.add_edge(from_node=3, to_node=4, max_speed=50)
#         self.add_edge(from_node=4, to_node=5, max_speed=50)
#
#     def populate_points(self):
#         self.add_point(osm_id=1, longitude=1.0, latitude=1.0)
#         self.add_point(osm_id=2, longitude=2.0, latitude=2.0)
#         self.add_point(osm_id=3, longitude=3.0, latitude=3.0)
#         self.add_point(osm_id=4, longitude=4.0, latitude=4.0)
#         self.add_point(osm_id=5, longitude=5.0, latitude=5.0)
#
#     def test(self):
#         print find_path(starting_node=1, ending_node=5, edges=self.edges, points=self.points)
#         print find_path(starting_node=2, ending_node=3, edges=self.edges, points=self.points)


if __name__ == '__main__':
    osm_filename = os.path.join(os.path.dirname(__file__), '../resources/map.osm')
    # connection = Connection(host='127.0.0.1', port=27017)
    parser = Parser(osm_filename=osm_filename)
    parser.parse()
    print 'Parser: ok'

    mongo = MongoConnector(parser=parser, host='127.0.0.1', port=27017)
    mongo.populate_all_collections()

    # Router(osm_filename=osm_filename)
    # Tester().test()

    # p = Process(target=printer, args=())
    # p.start()
    # time.sleep(10)
    # p.terminate()
    # p.join()


# def check_coordinates_list(self, coordinates_list):
    #     """
    #
    #     :param coordinates_list: [(longitude, latitude)]
    #     :return:
    #     """
    #     for index, coordinates in enumerate(coordinates_list):
    #
    #         if not self.coordinates_in_edges(longitude=coordinates[0], latitude=coordinates[1]):
    #             coordinates_list[index] = self.closest_coordinates_in_edges(coordinates)
    #
    #     return coordinates_list

    # def check_coordinates_in_edges(self, longitude, latitude):
    #     """
    #     Check if a pair of coordinates exists in the edges dictionary.
    #
    #     :type longitude: float
    #     :type latitude: float
    #     :return: boolean
    #     """
    #     return self.check_point_in_edges(point=Point(longitude=longitude, latitude=latitude))
    #
    # def check_point_in_edges(self, point):
    #     """
    #     Check if a point exists in the edges dictionary.
    #
    #     :type point: Point
    #     :return: boolean
    #     """
    #     for osm_id in self.edges:
    #         point_in_edge = self.edges.get(osm_id)
    #
    #         if point.equal_to_coordinates(longitude=point_in_edge.longitude, latitude=point_in_edge.latitude):
    #             return True
    #
    #     return False

    # def get_bus_stop_closest_to_coordinates(self, longitude, latitude):
    #     """
    #     Get the bus stop which is closest to a set of coordinates.
    #
    #     :type longitude: float
    #     :type latitude: float
    #     :return bus_stop: {osm_id, name, point}
    #     """
    #     provided_point = Point(longitude=longitude, latitude=latitude)
    #     minimum_distance = float('Inf')
    #     closest_bus_stop = None
    #
    #     bus_stops_cursor = self.connection.get_bus_stops()
    #
    #     for bus_stop in bus_stops_cursor:
    #         current_distance = distance(point_one=provided_point, longitude_two=bus_stop.get('point').get('longitude'),
    #                                     latitude_two=bus_stop.get('point').get('latitude'))
    #
    #         if current_distance == 0:
    #             closest_bus_stop = bus_stop
    #             break
    #         elif current_distance < minimum_distance:
    #             minimum_distance = current_distance
    #             closest_bus_stop = bus_stop
    #         else:
    #             pass
    #
    #     return closest_bus_stop
    #
    # def get_bus_stop_from_coordinates(self, longitude, latitude):
    #     """
    #     Get the bus_stop which corresponds to a set of coordinates.
    #
    #     :type longitude: float
    #     :type latitude: float
    #     :return bus_stop: {osm_id, name, point}
    #     """
    #     return self.connection.find_bus_stop_from_coordinates(longitude=longitude, latitude=latitude)
    #     # bus_stop = None
    #     #
    #     # for osm_id, values in self.bus_stops.iteritems():
    #     #     if values.get('point').equal_to_coordinates(longitude=longitude, latitude=latitude):
    #     #         values['osm_id'] = osm_id
    #     #         bus_stop = values
    #     #         break
    #     #
    #     # return bus_stop
    #
    # def get_bus_stop_from_name(self, name):
    #     """
    #     Get the bus_stop which corresponds to a name.
    #
    #     :type name: string
    #     :return bus_stop: {osm_id, name, point}
    #     """
    #     return self.connection.find_bus_stop_from_name(name=name)
    #     # name = name.lower()
    #     # bus_stop = None
    #     #
    #     # for osm_id, values in self.bus_stops.iteritems():
    #     #     if values.get('name').lower() == name:
    #     #         values['osm_id'] = osm_id
    #     #         bus_stop = values
    #     #         break
    #     #
    #     # return bus_stop
    #
    # def get_bus_stops_within_distance(self, longitude, latitude, maximum_distance):
    #     """
    #     Get the bus_stops which are within a distance from a set of coordinates.
    #
    #     :type longitude:
    #     :type latitude:
    #     :type maximum_distance:
    #     :return bus_stops: [{osm_id, name, point}]
    #     """
    #     provided_point = Point(longitude=longitude, latitude=latitude)
    #     bus_stops = []
    #     bus_stops_cursor = self.connection.get_bus_stops()
    #
    #     for bus_stop in bus_stops_cursor:
    #         current_distance = distance(point_one=provided_point, longitude_two=bus_stop.get('point').get('longitude'),
    #                                     latitude_two=bus_stop.get('point').get('latitude'))
    #
    #         if current_distance <= maximum_distance:
    #             bus_stops.append(bus_stop)
    #
    #     return bus_stops

    # def get_center_point_from_address_name(self, address_name):
    #     """
    #     Retrieve the point which corresponds to the center of a registered address.
    #
    #     :type address_name: string
    #     :return: Point
    #     """
    #     retrieved_center = None
    #
    #     if address_name in self.address_book:
    #         retrieved_center = self.address_book[address_name].get_center()
    #
    #     return retrieved_center

    # def get_closest_point_in_edges(self, point):
    #     """
    #     Retrieve the point which is closely to an input point and is contained at the edges.
    #
    #     :type point: Point
    #     :return closest_point: (osm_id, point)
    #     """
    #     minimum_distance = float('Inf')
    #     closest_point = None
    #
    #     points_of_edges = self.get_points_of_edges()
    #
    #     for osm_id, point_in_edge in points_of_edges.iteritems():
    #         distance_of_points = distance(point_one=point, point_two=point_in_edge)
    #
    #         if distance_of_points < minimum_distance:
    #             minimum_distance = distance_of_points
    #             closest_point = (osm_id, point_in_edge)
    #
    #     return closest_point

    # def get_point_from_osm_id(self, osm_id):
    #     """
    #     Retrieve the point which correspond to a specific osm_id.
    #
    #     :type osm_id: integer
    #     :return: Point
    #     """
    #     point = None
    #     # document = {'osm_id': osm_id, 'point': {'longitude': point.longitude, 'latitude': point.latitude}}
    #     document = self.connection.find_point(osm_id=osm_id)
    #     point_entry = document.get('point')
    #
    #     if point_entry is not None:
    #         point = Point(longitude=point_entry.get('longitude'), latitude=point_entry.get('latitude'))
    #
    #     return point

    # def get_points_dictionary(self):
    #     points_dictionary = {}
    #     points_cursor = self.connection.get_points()
    #
    #     for point_document in points_cursor:
    #         # {'osm_id': osm_id, 'point': {'longitude': point.longitude, 'latitude': point.latitude}}
    #         points_dictionary[point_document.get('osm_id')] = \
    #             Point(longitude=point_document.get('point').get('longitude'),
    #                   latitude=point_document.get('point').get('latitude'))
    #
    #     return points_dictionary

    # def get_points_of_edges(self):
    #     """
    #     Retrieve a dictionary containing the points of edges.
    #
    #     :return points_of_edges: {osm_id, point}
    #     """
    #     # edge_document = {'from_node', 'to_node', 'max_speed', 'road_type', 'way_id', 'traffic_density'}
    #     points_of_edges = {}
    #     edges_cursor = self.connection.get_edges()
    #     points_dictionary = self.get_points_dictionary()
    #
    #     for edge_document in edges_cursor:
    #         from_node = edge_document.get('from_node')
    #         to_node = edge_document.get('to_node')
    #
    #         if from_node not in points_of_edges:
    #             points_of_edges[from_node] = points_dictionary.get(from_node)
    #
    #         if to_node not in points_of_edges:
    #             points_of_edges[to_node] = points_dictionary.get(to_node)
    #
    #     return points_of_edges

    # def get_route_from_coordinates(self, starting_longitude, starting_latitude, ending_longitude, ending_latitude):
    #     """
    #     Find a route between two set of coordinates, using the A* algorithm.
    #
    #     :type starting_longitude: float
    #     :type starting_latitude: float
    #     :type ending_longitude: float
    #     :type ending_latitude: float
    #     :return route: [(osm_id, point, (distance_from_starting_node, time_from_starting_node))]
    #     """
    #     starting_point = Point(longitude=starting_longitude, latitude=starting_latitude)
    #     ending_point = Point(longitude=ending_longitude, latitude=ending_latitude)
    #     starting_osm_id, starting_point_in_edges = self.get_closest_point_in_edges(point=starting_point)
    #     ending_osm_id, ending_point_in_edges = self.get_closest_point_in_edges(point=ending_point)
    #
    #     route = find_path(starting_node=starting_osm_id, ending_node=ending_osm_id,
    #                       edges=self.edges, points=self.points)
    #     return route
