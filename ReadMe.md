# Travel Booking Application

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
- [API Endpoints](#api-endpoints)
- [Models](#models)
- [License](#license)

## Introduction

The Travel Booking Application is a comprehensive system designed to manage users, flights, hotels, and bookings. It offers functionalities for user authentication, flight and hotel management, and booking creation and management.

## Features

- User registration and authentication
- Flight management (create, read, update, delete flights)
- Hotel management (create, read, update, delete hotels)
- Booking management (create, read, update, delete bookings)
- Validation for email and phone numbers

## Installation

### Prerequisites

- Python 3.x
- Flask
- SQLAlchemy

### Steps

1. **Clone the repository**

   ```sh
   git clone https://github.com/your-username/travel-booking-app.git
   cd travel-booking-app
   ```

2. **Create and activate a virtual environment**

   ```sh
   python -m venv venv
   source venv/bin/activate # On Windows use `venv\Scripts\activate`
   ```

3. **Install the dependencies**

   ```sh
   pip install -r requirements.txt
   ```

4. **Set up the database**

   ```sh
   flask db init
   flask db migrate
   flask db upgrade
   ```

5. **Run the application**
   ```sh
   flask run
   ```

## Usage

### Running the Server

To start the server, use the command:

```sh
flask run
```
