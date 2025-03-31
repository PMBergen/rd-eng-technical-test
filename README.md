# Palfinger technical test

Welcome to Palfinger technical test and congratulations to reach this step in the hiring process.

## Objectives of the test

It is two fold, you should go through the documentation and the implementation and find gaps in both code and requirements.

- Documentation review: Go through the documentation in Notes.md and find where it could be extended or corrected.
- Code review: Go through the code, understanding what it does and suggest ways to improve it, things like: patterns, file organization, more functional flavour, bad handling of edge cases, clear bugs, etc... in general, things that you think are important in a code base.
- Suggest unit tests that could be interesting given the documentation and the current implementation.

We are expecting **around 2 hours of work on the test**, if you find yourself expending more time you are probably over doing it.

## Non objectives of the test

- We do not require deep understanding of OPC-UA so don't focus on that part of the technology, it is a rabbit hole.
- Don't focus on performance, if you can find simple performance gains it is ok, but don't invest too much time on it.
- No implementation needed, just a clear explanation of the changes you would do is also good enough.

## Handing in your assessment

- All answers should be written in the notes.md file included in the repository
- You are not expected to place comments or other notes anywhere else. You are free to write elsewhere but only notes.md will be looked at

## Documentation

### Functional Requirements

OPC UA Data Collection:

- The system must connect to an OPC UA server using configurable connection parameters (server name, port, credentials).
- The system must read a list of OPC UA nodes from a CSV file.
- The system must subscribe to data changes from specified OPC UA nodes.

Data Processing:

- The system must process different data types (Boolean, Float, String, Integer) received from the OPC UA server.
- The system must validate incoming data rows before storage.
- The system must store timestamp and node name with each data value.

Data Storage:

- The system must buffer data in memory before writing to disk.
- The system must save collected data in Parquet file format.
- The system must generate filenames based on timestamps.
- The system must append new data to existing files when available.

Background Processing:

- The system must implement a background thread for periodic data flushing.
- The system must provide a mechanism to gracefully stop background threads.

### Non-Functional Requirements

Performance:

- The system must handle high-frequency data changes (subscription interval of 500ms).
- The system must support configurable buffer sizes to optimize memory usage and I/O operations.

Reliability:

- The system must handle disconnections from the OPC UA server.
- The system must log errors for invalid data rows and unexpected data types.
- The system must use locking mechanisms to prevent race conditions when accessing shared data.

Configurability:

The system must support configurable parameters for:

- OPC UA server connection details (hostname, port)
- Authentication credentials
- Buffer size
- Flush interval
- File paths for input nodes and output data

Logging:

- The system must provide logging at different levels (info, error, debug).
- The system must log errors for invalid data rows and connection issues.

Scalability:

- The system must handle multiple nodes efficiently.
- The system must use threading to manage I/O operations without blocking data collection.

Maintainability:

- The system must follow a modular structure with clear separation of concerns (readers, writers, data models).
- The system must use interface-based design to allow for different writer implementations.
