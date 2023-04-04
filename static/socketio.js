document.addEventListener('DOMContentLoaded', () => {

    // Connect to websocket
    var socket = io.connect(
        location.protocol + '//' + document.domain + ':' + location.port, {transports: ['websocket']}
    );

    let player_room_id = false;
    let player1 = false;
    let player2 = false;
    let maria = false;


    socket.emit('start_game');

    socket.on('alert', data => {
        alert(data['message']);
    });

    socket.on('send_info_player_event', data => {
        player_room_id = data['player_room_id'];
        player1 = data['player1'];
        player2 = data['player2'];
    });

    socket.on('show_game_event', data => {

        window.alert("Game Started!");

        document.getElementsByClassName("game")[0].style.visibility = 'visible';
        const message = document.querySelector('#message');
        message.innerHTML = "Game Started! " + player1 + " VS " + player2;
        const name2 = document.querySelector('.name2');
        name2.innerHTML = player2;

    });

    socket.on('wait', data =>{
        document.getElementById("bottom_message").innerHTML = data['person_waiting'] + " is waiting...";
    });
    
    socket.on('result', data => {
        if (data['result'] === 'TIE'){
            document.getElementById("bottom_message").innerHTML = "It's a tie!";
        }else{
            if (data['result'] === 'player1'){
                const winner = document.getElementsByClassName("name1")[0].innerHTML
                document.getElementById("bottom_message").innerHTML = winner + " won!";
                document.getElementById("player1_score").innerHTML = parseInt(document.getElementById("player1_score").innerHTML) + 1
            }else{
                const winner = document.getElementsByClassName("name2")[0].innerHTML
                document.getElementById("bottom_message").innerHTML = winner + " won!";
                document.getElementById("player2_score").innerHTML = parseInt(document.getElementById("player2_score").innerHTML) + 1

            }
        }
    })

    document.querySelector('#leave_room_btn').onclick = () => {
            let player;
            const confirmed = window.confirm('Are you sure you want to leave the room?');

            if (confirmed) {
                if (username === player1) {
                    player = 'player1';
                }else{
                    player = 'player2';
                }
                // emit a "leave_room" event to the server
                socket.emit('leave_game_page', {'player': player, 'player_room_id': player_room_id});
            }
    }


    socket.on('clear_game_event', data => {

        document.getElementById("player1_score").innerHTML = '0';
        document.getElementById("player2_score").innerHTML = '0';
        document.getElementById("message").innerHTML = "The game room as closed.";
        document.getElementById("game_room_id").innerHTML = "";
        document.getElementById("bottom_message").innerHTML = "";
        document.getElementsByClassName("game")[0].style.visibility = 'hidden';
        document.getElementsByClassName("go_to_lobby")[0].style.visibility = 'visible';

        player_room_id = false;
        player1 = false;
        player2 = false;
        maria = false;

        window.alert(`The ${data['player']} left the room.`);

        // window.location.href = '/lobby';
    });


    document.querySelector('#rock').onclick = () => {
        let player_number;

        if (player1 === username) {
            player_number = "player1";
        } else {
            player_number = "player2";
        }
        if (maria === true){
            socket.emit('register_player_choice', {
                'player_number': player_number,
                'player1':player1,
                'player2':'MarIA',
                'choice':'rock',
                'player_room_id':player_room_id});

        }else {
        socket.emit('register_player_choice', {
            'player_number': player_number,
            'player1': player1,
            'player2': player2,
            'choice': 'rock',
            'player_room_id': player_room_id
        });
        }
    }

    document.querySelector('#paper').onclick = () => {
        let player_number;

        if (player1 === username) {
            player_number = "player1";
        } else {
            player_number = "player2";
        }
        if (maria === true){
            socket.emit('register_player_choice', {
                'player_number': player_number,
                'player1':player1,
                'player2':'MarIA',
                'choice':'paper',
                'player_room_id':player_room_id});

        }else {
        socket.emit('register_player_choice', {
            'player_number': player_number,
            'player1': player1,
            'player2': player2,
            'choice': 'paper',
            'player_room_id': player_room_id
        });
        }
    }

    document.querySelector('#scissor').onclick = () => {
        let player_number;

        if (player1 === username) {
            player_number = "player1";
        } else {
            player_number = "player2";
        }
        if (maria === true){
            socket.emit('register_player_choice', {
                'player_number': player_number,
                'player1':player1,
                'player2':'MarIA',
                'choice':'scissor',
                'player_room_id':player_room_id});

        }else {
        socket.emit('register_player_choice', {
            'player_number': player_number,
            'player1': player1,
            'player2': player2,
            'choice': 'scissor',
            'player_room_id': player_room_id
        });
        }
    }
});