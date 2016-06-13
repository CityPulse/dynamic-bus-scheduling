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


class MultiplePathsNode(object):
    def __init__(self, osm_id, point):
        self.osm_id = osm_id
        self.point = point
        self.followed_paths = []

    def __str__(self):
        return str(self.osm_id)

    def add_followed_path(self, followed_path):
        if followed_path not in self.followed_paths:
            self.followed_paths.append(followed_path)

    def set_followed_paths(self, followed_paths_of_previous_node):
        # print followed_paths_of_previous_node

        if len(followed_paths_of_previous_node) > 0:
            for followed_path_of_previous_node in followed_paths_of_previous_node:
                followed_path = followed_path_of_previous_node + [{'osm_id': self.osm_id, 'point': self.point}]
                self.add_followed_path(followed_path=followed_path)
        else:
            followed_path = [self.osm_id]
            self.followed_paths.append(followed_path)

    def get_followed_paths(self):
        return self.followed_paths


class MultiplePathsSet(object):
    def __init__(self):
        self.node_osm_ids = []
        self.nodes = []

    def __len__(self):
        return len(self.node_osm_ids)

    def __contains__(self, node_osm_id):
        """
        Check if a node exists in the nodes list.

        :type node_osm_id: integer
        :return: boolean
        """
        return node_osm_id in self.node_osm_ids

    def __str__(self):
        return str(self.node_osm_ids)

    def push(self, new_node):
        """
        Insert a new node.

        :param new_node: Node
        """
        new_node_osm_id = new_node.osm_id
        self.node_osm_ids.append(new_node_osm_id)
        self.nodes.append(new_node)

    def pop(self):
        """

        :return:
        """
        node = self.nodes.pop(0)
        self.node_osm_ids.remove(node.osm_id)
        return node


def find_waypoints_between_two_nodes(starting_node_osm_id, ending_node_osm_id, edges, points):
    waypoints = []
    closed_set = {}
    open_set = MultiplePathsSet()

    starting_node = MultiplePathsNode(osm_id=starting_node_osm_id, point=points.get(starting_node_osm_id))
    starting_node.followed_paths = [[{'osm_id': starting_node.osm_id, 'point': starting_node.point}]]
    open_set.push(new_node=starting_node)

    while len(open_set) > 0:
        current_node = open_set.pop()
        # print 'current_node:', current_node.osm_id, 'open_set:', str(open_set)

        if current_node.osm_id == ending_node_osm_id:
            # print 'ok'
            for followed_path in current_node.get_followed_paths():
                waypoints.append(followed_path)
            current_node.followed_paths = []
            continue

        if current_node.osm_id not in edges or current_node.osm_id in closed_set:
            continue

        for edge in edges.get(current_node.osm_id):
            next_node_osm_id = edge.get('ending_node')
            # print edge

            if next_node_osm_id in closed_set:
                continue
            else:
                next_node = MultiplePathsNode(osm_id=next_node_osm_id, point=points.get(next_node_osm_id))
                next_node.set_followed_paths(followed_paths_of_previous_node=current_node.get_followed_paths())
                # print 'followed_paths_of_current_node:', current_node.get_followed_paths(), \
                #       'followed_paths_of_next_node:', next_node.get_followed_paths()
                open_set.push(new_node=next_node)

        closed_set[current_node.osm_id] = current_node

    return waypoints
