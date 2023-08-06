from typing import List


class Node:
    def __init__(self, verges: List['Verge'] = None, **node_data):
        self._node_data = node_data
        self.verges = verges or []

    @property
    def connected_nodes(self):
        """
        :return: nearly connected nodes, excluding self
        """
        verges = []
        for verge in self.verges:
            verges.append(verge.node1 if verge.node1 is not self else verge.node2)
        return verges

    def get_connected_tree(self, nodes: List['Node'] = None):
        """
        :param nodes: Already founded nodes. It needs for passing founded nodes from the top level when recursing
        :return: list of Node objects
        """
        found_nodes = nodes or []
        for node in self.connected_nodes:
            if node in found_nodes:
                continue

            found_nodes.append(node)
            node.get_connected_tree(nodes=found_nodes)

        return found_nodes

    def search_in_connected_tree(self, **filters):
        """
        This function getting tree of nodes, then filtering it by given filters.
        If some filter param is different in node data, it will not return.
        :param filters:
        :return:
        """
        filtered_nodes = []
        for node in self.get_connected_tree():
            for filter_ in filters:
                if filter_ not in node.node_data or node.node_data[filter_] != filters[filter_]:
                    continue
                filtered_nodes.append(node)
        return filtered_nodes

    def get_verges(self):
        return self.verges

    @property
    def node_data(self):
        return self._node_data

    def __str__(self):
        return f'Node=<{id(self)}> data={self.node_data}'

    def __repr__(self):
        return self.__str__()


class Verge:
    """
    Class that represents verges between Nodes.
    Use `verge = Verge(node1, node2)` to connected nodes.
    """
    def __init__(self, node1: Node, node2: Node, **verge_data):
        self._node1 = node1
        self._node2 = node2

        self.node1 = node1
        self.node2 = node2
        self.verge_data = verge_data

    @property
    def node1(self):
        return self._node1

    @property
    def node2(self):
        return self._node2

    @node1.setter
    def node1(self, node1_input_value):
        if not isinstance(node1_input_value, Node):
            raise ValueError(f'Cant connect first node {node1_input_value}. Incorrect type. It can be only Node')
        node1_input_value.verges.append(self)

    @node2.setter
    def node2(self, node2_input_value):
        if not isinstance(node2_input_value, Node):
            raise ValueError(f'Cant connect second node {node2_input_value}. Incorrect type. It can be only Node')
        node2_input_value.verges.append(self)

    def __str__(self):
        return f'Verge=<{id(self)}> data={self.verge_data}'

    def __repr__(self):
        return self.__str__()


class Graph:
    """
    Class that represents a Graph.
    It is optional class, and it is not required for work with Nodes and Verges functionality.
    """
    def __init__(self, nodes: List = None, verges: List = None, **graph_data):
        self.nodes = nodes or []
        self.verges = verges or []
        self._graph_data = graph_data

    def create_node(self, verges: List = None, **node_data):
        node = Node(verges=verges, **node_data)
        self.nodes.append(node)
        return node

    def create_verge(self, node1: Node, node2: Node, **verge_data):
        verge = Verge(node1=node1, node2=node2, **verge_data)
        self.verges.append(verge)
        return verge

    def get_node_by_index(self, index: int):
        if index >= len(self.nodes):
            raise IndexError('Not found node with given index')
        return self.nodes[index]