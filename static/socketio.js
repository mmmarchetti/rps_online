/**
 * Main function to initialize the game.
 */
document.addEventListener('DOMContentLoaded', () => {

    window.addEventListener('beforeunload', confirmExit);
    window.addEventListener('unload', handleExit);

    // Connect to websocket
    const socket = io.connect(`${location.protocol}//${document.domain}:${location.port}`, { transports: ['websocket'] });
  
    let playerRoomId = false;
    let player1 = false;
    let player2 = false;
  
    // Request to start the game
    socket.emit('start_game');
  
    /**
     * Handle alert events from the server.
     */
    socket.on('alert', data => {
      window.alert(data.message);
    });
  
    /**
     * Set player information received from the server.
     */
    socket.on('send_info_player_event', data => {
      playerRoomId = data.player_room_id;
      player1 = data.player1;
      player2 = data.player2;
    });
  
    /**
     * Show game event from server.
     */
    socket.on('show_game_event', data => {
      window.alert('Game Started!');
  
      document.querySelector('.game').style.visibility = 'visible';
      document.querySelector('#message').innerHTML = `Game Started! ${player1} VS ${player2}`;
      document.querySelector('.name2').innerHTML = player2;
    });
  
    /**
     * Update the waiting message.
     */
    socket.on('wait', data => {
      document.querySelector('#bottom_message').innerHTML = `${data.person_waiting} is waiting...`;
    });
  
    /**
     * Update the opponent's choice when received from the server.
     */
    socket.on('update_opponent_choice', data => {
      const opponent = (username === player2) ? 'player1' : 'player2';
      const opponentChoice = data.choices[opponent];
  
      setChoiceImage(opponent, opponentChoice);
    });
  
    /**
     * Set the image for the player's choice.
     *
     * @param {string} player - Player identifier ('player1' or 'player2').
     * @param {string} choice - Choice of the player ('rock', 'paper', or 'scissor').
     */
    function setChoiceImage(player, choice) {
      const imagePath = `static/images/${choice}.png`;
      document.querySelector(`#${player}_choice`).src = imagePath;
    }

    /**
     * Confirm exit from the game.
     */
    function confirmExit(event) {
      if (playerRoomId) {
        const confirmationMessage = 'Are you sure you want to leave the game? The room will be closed.';
        event.returnValue = confirmationMessage;  // Deprecated, not shown to user
        return confirmationMessage;  // Deprecated, not shown to user
      }
    }

    /**
     * Handle exit from the game.
     */
    function handleExit() {
      if (playerRoomId) {
        const player = (username === player1) ? 'player1' : 'player2';
        socket.emit('leave_game_page', { player, player_room_id: playerRoomId });
      }
    }
    
  
    /**
   * Handle the result of the game received from the server.
   */
    socket.on('result', data => {
        let message = '';

        if (data.result === 'TIE') {
        message = "It's a tie!";
        } else {
            if (data['result'] === 'player1'){
                const winner = document.getElementsByClassName("name1")[0].innerHTML
                message = winner + " won!"
                document.getElementById("bottom_message").innerHTML = message;
                document.getElementById("player1_score").innerHTML = parseInt(document.getElementById("player1_score").innerHTML) + 1
            }else{
                const winner = document.getElementsByClassName("name2")[0].innerHTML
                message = winner + " won!"
                document.getElementById("bottom_message").innerHTML = message;
                document.getElementById("player2_score").innerHTML = parseInt(document.getElementById("player2_score").innerHTML) + 1

            }
        }

        document.querySelector('#bottom_message').innerHTML = message;
        // window.alert(message);

        setTimeout(() => {
        setChoiceImage('player1', 'logo');
        setChoiceImage('player2', 'logo');
        document.querySelector('.controls').style.visibility = 'visible';
        document.querySelector('#bottom_message').innerHTML = "Select your new move";
        }, 3000);

    });

  
    /**
     * Handle leave room button click event.
     */
    document.querySelector('#leave_room_btn').onclick = () => {
      const confirmed = window.confirm('Are you sure you want to leave the room?');
  
      if (confirmed) {
        const player = (username === player1) ? 'player1' : 'player2';
        socket.emit('leave_game_page', { player, player_room_id: playerRoomId });
      }
    }
  
    /**
     * Clear the game when the room is closed.
     */
    socket.on('clear_game_event', data => {
      document.querySelector('#player1_score').innerHTML = '0';
      document.querySelector('#player2_score').innerHTML = '0';
      document.querySelector('#message').innerHTML = 'The game room has closed.';
      document.querySelector('#game_room_id').innerHTML = '';
      document.querySelector('#bottom_message').innerHTML = '';
      document.querySelector('.game').style.visibility = 'hidden';
      document.querySelector('.controls').style.visibility = 'hidden';
      document.querySelector('.go_to_lobby').style.visibility = 'visible';
  
      playerRoomId = false;
      player1 = false;
      player2 = false;
  
      window.alert(`${data.player} left the room.`);
    });
  
    /**
     * Handle the click event for rock choice.
     */
    document.querySelector('#rock').onclick = () => {
      handleChoiceClick('rock');
    }
  
    /**
     * Handle the click event for paper choice.
     */
    document.querySelector('#paper').onclick = () => {
      handleChoiceClick('paper');
    }
  
    /**
     * Handle the click event for scissor choice.
     */
    document.querySelector('#scissor').onclick = () => {
      handleChoiceClick('scissor');
    }
  
    /**
     * Handle choice click events.
     *
     * @param {string} choice - Choice of the player ('rock', 'paper', or 'scissor').
     */
    function handleChoiceClick(choice) {
      const playerNumber = (player1 === username) ? 'player1' : 'player2';
  
      setChoiceImage(playerNumber, choice);

      document.querySelector('.controls').style.visibility = 'hidden';
  
      const payload = {
        player_number: playerNumber,
        player1,
        player2,
        choice,
        player_room_id: playerRoomId
      };
  
      socket.emit('register_player_choice', payload);
    }
});
    