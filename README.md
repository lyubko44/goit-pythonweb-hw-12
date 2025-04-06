# Contacts API

This project is a Contacts API built using FastAPI, SQLAlchemy, and PostgreSQL. It supports CRUD operations for managing contacts, including searching by name, last name, or email, and retrieving contacts with upcoming birthdays.

## Setup Instructions

### Prerequisites

- Python 3.8+
- PostgreSQL
- `pip` (Python package installer)

### Installation

1. Clone the repository:
    ```sh
    git clone https://github.com/yourusername/contacts-api.git
    cd contacts-api
    ```

2. Create and activate a virtual environment:
    ```sh
    python -m venv venv
    source venv/bin/activate  # On Windows use `venv\Scripts\activate`
    ```

3. Install the dependencies:
    ```sh
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the root directory with the following content:
    ```dotenv
    DATABASE_URL=postgresql://user:password@localhost/dbname
    ```

5. Update the `.env` file with your PostgreSQL credentials.

### Database Setup

1. Initialize the database:
    ```sh
    python -c 'from database import init_db; init_db()'
    ```

### Running the Application

1. Start the FastAPI server:
    ```sh
    uvicorn main:app --reload
    ```

2. Open your browser and navigate to `http://127.0.0.1:8000/docs` to access the Swagger documentation.

## Project Structure

- `main.py`: The main application file containing the FastAPI app and endpoints.
- `models.py`: SQLAlchemy models for the database.
- `database.py`: Database configuration and initialization.
- `.env`: Environment variables for sensitive data.
- `requirements.txt`: Project dependencies.

## License

This project is licensed under the MIT License.