# Comments regarding technical assessment

## Overall Impresion

Give your sense of the code written, is it good, bad, somewhere between. Specific comments will be done below, think of this as a colleagues pull request and how you would talk to them.

The code is clean, well structured with no major issues that I could see. Asynchronous calls are used, which is standard method for buffering or streaming of data, which doesn't block the execution while the buffer is being handled, which is good. Handling of buffer is done by two triggers, timeout and buffer size triggers, which protects the buffer from overflow.

I saw potential improvements in locking mechanism, and one potential issue with appending data into the export file. I will explain more about this in export section of the document. Most of the code seems pretty good.

## Coding Style

Umbrella for naming standard/file structure/patterns/configuration and portability/scalability/maintainability

## Documentation

Comment on the documentation.md here

In the documentation I would add that the communication is implemented asynchronously, which allows non-blocking data reception and processing, which are provided as requirements. This also allows handling of high-frequency data changes.
I would explain how appending is done in the code. Since the appending is not the real appending (if it is not fixed as I will explain in the Export section), but when the data is applied first the existing data in the file is read, new data is appended to the existing data, and the final data (old + new) is rewritten to the file. This can be issue if the file gets large, and can be pointed out as a bottleneck and potential future improvement.
I would also mention how locking mechanism works, since it is not the most optimized locking, and if it is not fixed as suggested in the Export section, this can be pointed out as potential bottleneck if the reception of data is too fast.


## Export section

Comment on the files inside the export folder here

1. I think that the locking mechanism can be more optimized. Instead of using lock on the whole flush function, it can be used on the shared variables only, and read/write can be done outside of the thread locking. 
e.g.
shouldFlush = False
if data.is_valid():
	with self.lock:
		self.buffer.append(data.__dict__)
		if len(self.buffer) >= self.buffer_size:
			table_to_append = pa.Table.from_pylist(self.buffer)
			suffix = self.get_filename_suffix(time.localtime())
			self.filename = f"{self.output_file}{suffix}.parquet"
			shouldFlush = True
	if shouldFlush:
		flush(table_to_append)
This will unlock the threading lock while reading/writing, but flush would need to be protected in case of calling flush multiple times (e.g. buffer size trigger happens a bit before timeout trigger). This second call would be unnecessary, and should be rejected. This can be used by using flag which will say if flush is already in progress or not.

2. Currently, the granularity of the export file is on 1 minute. I would need info how much data is expected over time, since if needed, this granularity can be increased by adding seconds, or some IDs. This could be bottleneck if too much data is expected, which will make overhead in appending data into export file with current mechanism (reading existing data from the file, appending the new data to the original in the memory of the program, and then writing the whole data again into the same file).
The second approach would be using different library, which would support Parquet format, and real appending of the data to the file. But I am not familiar with this, and even if the library like this exist at all.

## OPCUA

Comment on why async is used and if its a good or bad use.
Do not go past this, assume OPCUA is functional in this technical assessment (the rabbit hole goes deep)

Async is required in use-cases like buffering and streaming of data, since we want to process data in buffers, while not blocking ourselves for additional calls from the servers with more data. This is the best solution for solving this requirement. With async we are processing data we got from input, and we are also ready for receiving new data. 

## Testing

Comment on testing and what tests you would 
Tests:

1. test that is_valid returns true if only one value is set
2. test that is_valid returns false if no value or more than one value is set
3. call add_data and flush to check if the data will be added to the export file
4. call add_data multiple times at once to see if it will corrupt the buffer
5. call add_data very frequently to check if handling the data will be done properly, if there is any loss, will buffer handling and flushing work well
6. provide some csv file for OPCUA and check if read_nodes_strings will return expected list of nodes
7. trigger datachange_notification periodically and check if it will write all the data in the export file. Check if the data will be corrupted, and if there is any loss
8. trigger datachange_notification very frequently, and measure in the code how much time it takes to append data into the file. Analyze how much the execution time is increasing as the existing data in the file is getting larger
9. trigger datachange_notification very frequently, and measure how much time it takes to execute read/write commands which are inside the lock in the flush command
