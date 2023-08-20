# Flask REST API with MySQL

This is a simple Flask-based REST API project that needs to:
1.	Receive historical data from CSV files
2.	Upload these files to the new DB
3.	Be able to insert batch transactions (1 up to 1000 rows) with one request

## Table of Contents

- [Getting Started](#getting-started)
  - [Prerequisites](#prerequisites)
  - [Installation](#installation)
- [Usage](#usage)
  - [Running the API](#running-the-api)
  - [Endpoints](#endpoints)
- [Contributing](#contributing)
- [License](#license)

## Getting Started

These instructions aim to assist anyone in running and testing the project locally. If you are not familiar with RDBMS, you can still proceed; however, you will likely need to refer to other tutorials, as you will require a running instance of a local database server to observe the API's functionality.

### Prerequisites

You need to have the following software installed:

- Python (>=3.6)
    will be provided a requirements.txt
- MySQL Server (also recommend SQLite and PostgreSQL)
    Server must be running on localhost
    DB structure will be provided considering a MySQL RDMS

