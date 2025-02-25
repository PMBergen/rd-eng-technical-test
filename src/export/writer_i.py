"""
Writer interface
"""

from palopcua.export.datarow import DataRow


class WriterInterface:
    def add_data(self, data: DataRow) -> None:
        """

        Args:
            data (DataRow): Data to store
        """
        pass
