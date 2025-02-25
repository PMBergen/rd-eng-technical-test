"""
Implementation of the OPCUA Reader Interface
"""

import csv

from asyncua import Client, Node


class OpcuaReader:
    """
    Opcua Reader
    """

    @staticmethod
    async def get_list_of_nodes(client: Client, nodes_list_file: str, namespace: str) -> list[Node]:
        """
        Get the list of nodes from a file, replace the namespace index and return the list

        Args:
            nodes_list_file (str): filename, a csv list of nodes
            client(Client): the client to use
            namespace (str): the namespace to use

        Returns:
            list[Node]: list of nodes to subscribe
        """

        idx = await client.get_namespace_index(uri=namespace)

        node_list_strings = OpcuaReader.read_nodes_strings(nodes_list_file, idx)

        nodes = []
        for node_strs in node_list_strings:
            nodes.append(await client.nodes.objects.get_child(node_strs))

        return nodes

    @staticmethod
    def read_nodes_strings(node_list_file: str, namespace_index: str) -> list[list[str]]:
        """
        Reads the nodes from the list and replaces the index
        Args:
            node_list_file (str): path to the file
            namespace_index (str): index of the namespace to use
        """
        list_of_nodes = []

        with open(node_list_file) as csvfile:
            csv_reader = csv.reader(csvfile)
            for node_strs in csv_reader:
                list_of_nodes.append([f"{namespace_index}:{node_str}" for node_str in node_strs])

        return list_of_nodes
