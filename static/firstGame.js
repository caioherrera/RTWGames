var userID, gameID, theme;
var userData = [];

$(document).ready(function() {

	userID = $("#userID").text();
	gameID = $("#gameID").text();
	theme = $("#theme").text();

	$("#divGame").hide();
	$("#message").html("Waiting for your opponent...<br>");
    
	var data = {"gameID": gameID};
	var calls = setInterval(isGameReady, 500);
	
	function isGameReady() {

		$.ajax({
			url: "/ajax_isGameReady",
			data: JSON.stringify(data),
			contentType: "application/json;charset=UTF-8",
			type: "POST",
			success: function(response) {
				result = response["result"];
				if(result) {
					clearInterval(calls);
					$("#message").html("Opponent found!<br><br>");
					$("#divGame").show();
				}
			},
			error: function(request, status, error) {
				$("#message").text(request.responseText);
			}
		});

	};
});

function testClick(e) {
	e = e || window.event;
	if(e.keyCode == 13) {
		addData();
		return false;
	}
	return true;
}

function addData() {
	var d = $("#txtNext").val();
	if(d != "") {
		userData.push(d);
		$("#lstPrevious").prop("readOnly", false);
		$("#lstPrevious").append($("<option>", { value: userData.length, text: d }));
		$("#lstPrevious").prop("readOnly", true);
	}
	$("#txtNext").val("");
	$("#txtNext").focus();
}

function startTimer(duration) {
	var timer = duration;
	var minutes, seconds;
	
	var calls = setInterval(decTimer, 1000);

	function decTimer() {

		minutes = parseInt(timer / 60, 10);
		seconds = parseInt(timer % 60, 10);

		$("#timer").text("Time remaining: " + (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds);

		if(timer-- <= 0) {
			timer = 0;
			clearInterval(calls);	
			
			$("#txtNext").prop("readOnly", true);
			$("#divGame").hide();

			/* FAZER O ENVIO DE DADOS PARA O BACKEND VIA AJAX */ 
			var data = {"gameID": gameID, "userID": userID, "data": userData, "gameType": 1};
			var saved = false;
			
			$.ajax({
				url: "/ajax_saveData",
				data: JSON.stringify(data),
				contentType: "application/json;charset=UTF-8",
				type: "POST",
				success: function(response) { 
					saved = response["result"];
				}, 
				error: function(request, status, error) { 
					$("#message").text(request.responseText);
				}
			});	

			$("#message").html("Game Over!<br>Waiting for your opponent...<br>");

			//if(saved) {
		
            calls = setInterval(isGameOver, 500);
            data = {"gameID": gameID, "userID": userID};

            function isGameOver() {

                $.ajax({
                    url: "/ajax_isGameOver",
                    data: JSON.stringify(data),
                    contentType: "application/json;charset=UTF-8",
                    type: "POST",
                    success: function(response) {

                        myScore = response["myScore"];
                        opponentScore = response["opponentScore"];

                        if(myScore > -1) {
                            clearInterval(calls);

                            msgWinner = "";
                            if(myScore > opponentScore)
                                msgWinner = "You won!<br>";
                            else if(myScore < opponentScore)
                                msgWinner = "You lost!<br>";
                            else
                                msgWinner = "It's a draw!<br>";

                            $("#message").html("Game Over!<br>Your score is: " + myScore + " points.<br>"
                             + "Your opponent score is: " + opponentScore + " points.<br>" + msgWinner + "<br>");
                        }
                    },
                    error: function(request, status, error) {
                        $("#message").text(request.responseText);
                    }
                });
            }
        }
	};
}

function startGame() {

	$("#btnStart").prop("disabled", true);
	$("#txtTheme").prop("readOnly", true);
	$("#txtTheme").val(theme);
	$("#txtNext").prop("readOnly", false);
	$("#txtNext").focus();

	startTimer(30);

}
