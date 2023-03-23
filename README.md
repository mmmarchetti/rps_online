# Rock-Paper-Scissors Web App
This project is part of an article that proposes to study the results of the interaction of two players from the perspective of Game Theory and Chaotic Dynamic Systems.
This is a web application that allows two players to play rock-paper-scissors against each other in real time using Flask and Flask-SocketIO. Users can sign up for an account, log in, view the leaderboard, and change their username.

## Installation
To use this application, follow these steps:

* Clone the repository to your local machine

* Set the environment variable SECRET_KEY to a .env file in the project root: SECRET_KEY=YOUR_SECRET_KEY

* Install Docker and Docker-compose

* run in your terminal:
```
docker-compose up --build
```

* Open your web browser and navigate to http://localhost:8080

## Usage
### Login/Logout

Users can log in by entering their username and password on the login page. If they do not have an account, they can sign up for one on the registration page. Once logged in, users can access their profile page, view the leaderboard, and play rock-paper-scissors against other users.

Users can log out by clicking the "Sign out" button on their profile page.

### Profile Page
The profile page displays the user's current username, number of wins, and rank on the leaderboard. Users can change their username by entering a new one in the form provided and clicking the "Save Changes" button.

### Leaderboard
The leaderboard displays all users in the database sorted by number of wins in descending order.

### Playing Rock-Paper-Scissors
To play rock-paper-scissors against another user, the user must first join a room by entering the room code on the lobby page. If a room with the given code does not exist, one will be created. Once two users have joined the same room, they can start playing rock-paper-scissors.

Each user selects their move by clicking on the corresponding button on the game screen. The winner of each round is displayed on both users' screens. The game ends when one user has won a predetermined number of rounds.

### License
This project is licensed under the MIT License 