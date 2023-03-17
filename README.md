# Rock-Paper-Scissors RPS Online Game

This project is a web-based rock-paper-scissors game that allows users to play against the computer, with a friend, or with a random player online. The frontend is built with HTML, CSS, and JavaScript, while the backend uses Flask and Python. User information, game history, and rankings are stored in a database.

## Features

- Responsive design for various devices
- Play against the computer, a friend, or a random online player
- User login and authentication
- Ranking of best players

## Getting Started

These instructions will help you set up the project on your local machine for development and testing purposes.

### Prerequisites

- Python 3.7 or higher
- Node.js and npm
- A database management system (e.g., PostgreSQL, MySQL)

### Installation

1. Clone the repository to your local machine:
    ```
    \git clone https://github.com/yourusername/rock-paper-scissors.git
    ```

2. Navigate to the backend directory and install the required Python packages:
    ```
    cd rock-paper-scissors/backend
    pip install -r requirements.txt
    ```

3. Set up your database and update the `config.py` file with your database connection details.

4. Apply the database migrations:
    ```
    flask db upgrade
    ```

5. Navigate to the frontend directory and install the required npm packages:
    ```
    cd ../frontend
    npm install
    ```

### Running the Application

1. In the `backend` directory, run the Flask application:
    ```
    flask run
    ```

2. In the `frontend` directory, start the development server:
    ```
    npm start
    ```

3. Open your web browser and visit `http://localhost:3000` to access the game.

## Deployment

To deploy the application on AWS, follow the instructions in the [official AWS documentation](https://aws.amazon.com/getting-started/hands-on/deploy-python-application/) for deploying a Python web application.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
