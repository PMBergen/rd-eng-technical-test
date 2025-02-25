"""
Launches the export command
"""

import asyncio
import logging
import os
from typing import Any

from asyncua import Client, Node, ua
from asyncua.common.subscription import DataChangeNotif

from palopcua import config
from palopcua.export.opcua_client import get_client
from palopcua.export.opcua_reader import OpcuaReader
from palopcua.export.writer_file import WriterFile
from palopcua.export.datarow import DataRow

logging.basicConfig(level=logging.INFO)

_logger = logging.getLogger()


class SubscriptionHandler:
    """
    The SubscriptionHandler is used to handle the data that is received for the subscription.
    """

    def __init__(self, writer_file: WriterFile):
        """

        Args:
            file_writer (FileWriter): Pass a filewriter object for the subscription to store data
        """
        self.writer = writer_file

    async def datachange_notification(self, node: Node, val: Any, data: DataChangeNotif) -> None:
        """
        Callback for asyncua Subscription.
        This method will be called when the Client received a data change message from the Server.
        """
        data_row = DataRow(timestamp=data.monitored_item.Value.ServerTimestamp, name=node.nodeid.to_string())

        match data.monitored_item.Value.Value.VariantType:
            case ua.uatypes.VariantType.Float:
                data_row.float_value = data.monitored_item.Value.Value.Value
            case ua.uatypes.VariantType.String:
                data_row.str_value = data.monitored_item.Value.Value.Value
            case ua.uatypes.VariantType.Int64 | ua.uatypes.VariantType.Int32 | ua.uatypes.VariantType.Int16:
                data_row.int_value = data.monitored_item.Value.Value.Value
            case ua.uatypes.VariantType.Boolean:
                data_row.bool_value = bool(data.monitored_item.Value.Value.Value)
            case _:
                _logger.error(f"Datatype not found {data} {node}")

        if data_row.is_valid():
            self.writer.add_data(data_row)
        else:
            _logger.error(f"Invalid data row {data_row}")

    def status_change_notification(self, status: ua.StatusChangeNotification) -> None:
        """
        called for every status change notification from server
        """
        _logger.debug("status_change_notification %r", status)


async def main() -> None:
    client: Client = await get_client()
    nodes_file = os.path.join(config.PATH_DATA, "nodes.csv")
    data_file = os.path.join(config.PATH_DATA_EXPORT, "export")
    file_writer = WriterFile(
        buffer_size=config.OPCUA_CLIENT_BUFFER, output_file=data_file, flush_interval=config.OPCUA_CLIENT_FLUSH_INTERVAL
    )
    handler = SubscriptionHandler(file_writer)
    # We create a Client Subscription.
    subscription = await client.create_subscription(500, handler)
    nodes = await OpcuaReader.get_list_of_nodes(client, nodes_file, config.PALFINGER_INSTANCE_NAMESPACE)
    # We subscribe to data changes for two nodes (variables).

    await subscription.subscribe_data_change(nodes)

    while True:
        await asyncio.sleep(0.5)


if __name__ == "__main__":
    asyncio.run(main())
