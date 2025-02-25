import logging
import threading
import time
from datetime import datetime

import pyarrow as pa
import pyarrow.parquet as pq

from palopcua.export.writer_i import WriterInterface
from palopcua.export.datarow import DataRow

logger = logging.getLogger()


class WriterFile(WriterInterface):
    """
    Parquet writer, it has a buffer size and a flush interval
    """

    def __init__(self, buffer_size: int, output_file: str, flush_interval: int = 10) -> None:
        """
        Initializes the Parquet buffer.
        Args:
            buffer_size (int): Max number of records before flushing.
            output_file (str): Path to the Parquet file.
            flush_interval (int): Time in seconds to flush the buffer if not full.
        """
        self.buffer_size = buffer_size
        self.output_file = output_file
        self.flush_interval = flush_interval

        self.buffer: list[dict] = []
        self.lock = threading.Lock()
        self.last_flush_time = datetime.now()
        self.filename = ""
        # Start the background flusher thread
        self.running = True
        self.thread = threading.Thread(target=self.background_flush, daemon=True)
        self.thread.start()

    def add_data(self, data: DataRow) -> None:
        """
        Add data to the buffer.
        Args:
            data (DataRow): Data to add.
        """
        if data.is_valid():
            with self.lock:
                self.buffer.append(data.__dict__)
                if len(self.buffer) >= self.buffer_size:
                    self.flush()

    def flush(self) -> None:
        """
        Write the buffer to a Parquet file and clear it.
        """
        if not self.buffer:
            return

        table_to_append = pa.Table.from_pylist(self.buffer)
        suffix = self.get_filename_suffix(time.localtime())
        self.filename = f"{self.output_file}{suffix}.parquet"

        try:
            table_original_file = pq.read_table(
                source=self.filename, pre_buffer=False, use_threads=True, memory_map=True
            )  # Use memory map for speed.
        except FileNotFoundError:
            logger.info("File not found, creating new file")
            table_original_file = None

        handle = pq.ParquetWriter(self.filename, table_to_append.schema)
        if table_original_file:
            handle.write_table(table_original_file)
        handle.write_table(table_to_append)
        handle.close()

        # Clear the buffer and update the last flush time
        self.buffer.clear()
        self.last_flush_time = datetime.now()

    def background_flush(self) -> None:
        """
        Run in its own thread, periodically flush the buffer based on the flush interval.
        """
        while self.running:
            time.sleep(1)
            with self.lock:
                if (datetime.now() - self.last_flush_time).total_seconds() >= self.flush_interval:
                    self.flush()

    def get_filename_suffix(self, current_time: time.struct_time) -> str:
        """
        Gets a new filename based on timestamp

        """
        return time.strftime("%Y%m%d%H%M", current_time)

    def stop(self) -> None:
        """
        Stop the background thread and flush any remaining data.
        """
        self.running = False
        self.thread.join()
        with self.lock:
            self.flush()
