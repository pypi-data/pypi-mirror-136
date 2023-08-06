# Simple Anaplan Connector Package

#### Introduction
This is a simple Anaplan connector intended to be used as a quick and easy way to mainly integrate with Anaplan using Python. This package does not include all API options. It uses the main calls to push data to anaplan via files, call a process, and export data.

#### Anaplan Integration Overview
The method of pushing data to Anaplan is common in the data warehousing space. Instead of pushing data in a transaction api (i.e. record by record), Anaplan utilizes a bulk data API which includes pushing delimitted files to a file location, and then copying the file into an Anaplan database. This is similar to Postgres and Snowflake's COPY INTO command.

#### Pushing Data Into Anaplan Overview
Before getting to the code, the high-level steps to pushing data into Anaplan is as follows:
1. Source the source data (e.g. ERP data) into a csv file
2. Use the csv file to manually import the data into Anaplan. This will create a "file" reference and fileId within Anaplan.
3. Obtain the fileId using this connector.
4. With the file and Anaplan fileID, push the file to Anaplan.
5. Create a process in Anaplan that includes the required actions for the data. 
6. Obtain the processId using this connector.
7. Run the processId with this connector.

**Notes:**
- I intentially built the connector to only use processes and not the actions directly. It is my belief that it is best practice to use processes since it is much easier to expand the actions within Anaplan than to manage the processes within Python.

#### Exporting Data from Anaplan

## Documentation in progress...