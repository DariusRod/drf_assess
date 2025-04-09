# Django REST Framework Blog API

CRUD operations on posts and comments, plus category management, like/dislike actions, filtering, and search.

## Setup Instructions

Follow these steps to set up the project locally:

1.  **Clone the Repository:**
    ```bash
    git clone <your-repository-url>
    cd <repository-directory-name>
    ```

2.  **Create a Python Virtual Environment:**
    It's highly recommended to use a virtual environment to manage project dependencies.
    ```bash
    python -m venv venv
    ```
    *(You can replace `venv` with your preferred environment name)*

3.  **Activate the Virtual Environment:**
    * On macOS and Linux:
        ```bash
        source venv/bin/activate
        ```
    * On Windows (Command Prompt/PowerShell):
        ```bash
        venv\Scripts\activate
        ```

4.  **Install Required Packages:**
    Make sure your virtual environment is activated.
    ```bash
    pip install -r requirements.txt
    ```
    *(Note: Ensure your requirements file is named `requirements.txt`)*

5.  **Apply Database Migrations:**
    This step creates the necessary database tables based on the project's models.
    ```bash
    python manage.py migrate
    ```
    *(Make sure you are in the directory containing `manage.py`)*

## Running the Development Server

1.  **Start the Server:**
    Ensure your virtual environment is activated and you are in the directory containing `manage.py`.
    ```bash
    python manage.py runserver
    ```

2.  **Access the API:**
    The development server will usually start at `http://127.0.0.1:8000/`.
    You can typically access the main API endpoints under the `/api/` prefix, for example:
    * API Root (listing endpoints): `http://127.0.0.1:8000/api/`
    * Posts List: `http://127.0.0.1:8000/api/posts/`
    * Categories List: `http://127.0.0.1:8000/api/categories/`

    You can explore the API using your browser (via the DRF Browsable API) or using API clients like Postman or Insomnia.