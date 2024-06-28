import socket
import time
import re
import string


class Marker:
    def __init__(self, id, x, y, z):
        self.id = id
        self.x = x
        self.y = y
        self.z = z

    def distanceSquared(self, marker):
        return (self.x - marker.x) ** 2 + (self.z - marker.z) ** 2

    def center(markers_list):
        center_coordinates = [0, 0, 0]
        for markers in markers_list:
            center_coordinates[0] = center_coordinates[0] + markers.x
            center_coordinates[1] = center_coordinates[1] + markers.y
            center_coordinates[2] = center_coordinates[2] + markers.z

        for i in range(len(center_coordinates)):
            center_coordinates[i] = center_coordinates[i] / len(markers_list)

        return center_coordinates

    def colinear(markers_list):
        slope1 = (markers_list[0].z - markers_list[1].z) * (markers_list[0].x - markers_list[2].x)
        slope2 = (markers_list[0].z - markers_list[2].z) * (markers_list[0].x - markers_list[1].x)
        print(slope1)
        print(slope2)

        return abs(slope1 - slope2) < 0.01

    def print(self):
        print("Model_name: | Marker id: {} | Points xyz: [{},{},{}] | Is front: {}".format(self.id, self.x, self.y,
                                                                                           self.z))

    def __str__(self):
        return "Model_name: | Marker id: {} | Points xyz: [{},{},{}] | Is front: {}".format(self.id, self.x, self.y,
                                                                                            self.z)


def parse_marker_string(marker_string):
    marker_list = marker_string.split('#')[1:]  # Split the string by '#' and remove the empty first element
    markers = []
    for marker in marker_list:
        marker_info = marker.split('$')[1].split('[')
        try:
            id = int(marker_info[0])
            coords = marker_info[1][:-1].strip(']').split(',')
            x, y, z = map(float, coords)
        except:
            print("Error parsing marker string: {}".format(marker))
            continue
        markers.append(Marker(id, x, y, z))

    return markers


def set_socket_server():
    HOST = '192.168.31.103'  # The server's hostname or IP address
    PORT = 9999

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((HOST, PORT))
    return s


def recv_data(socket_server):
    header = socket_server.recv(10).decode()
    # print("cos")
    # print(header)
    message_length = int(header)
    data = socket_server.recv(message_length).decode()
    print(data)
    markers_list = parse_marker_string(data)
    return markers_list


def main():
    server = set_socket_server()
    while True:
        markers_list = recv_data(server)
        print(markers_list)


if __name__ == "__main__":
    main()