var userID, gameID, theme;
var userData = [];
var score = 0;
const hints = 3;
const points = 5;

$(document).ready(function() {

	userID = $("#userID").text();
	gameID = $("#gameID").text();
	theme = $("#theme").text();

	$("#btnOk").prop("disabled", true);

	//weird for
	for(var i = 0; i < hints; i++)
		userData.push("");

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

function testClick(e, number) {
	e = e || window.event;
	
	var disabled = false;	

	for(var i = 0; i < hints; i++) {
		var value = $("#txtKey" + i).val();
		if(value == "")
			disabled = true;
	}

	$("#btnOk").prop("disabled", disabled);	

	if(e.keyCode == 13) {
		if(number < hints - 1)
			$("#txtKey" + (number + 1)).focus();
		else
			$("#btnOk").focus();
		return false;
	}
	return true;
}

function addData(number) {
	var key = "#txtKey" + number;
	var d = $(key).val();
	var disabled = false;

	if(d != "") {
		userData[number] = d;
		score += 5;
	}
}

function endGame() {
	$("#divGame").hide();

	score = 0;

	for(var i = 0; i < hints; i++)
		addData(i);

	var data = {"gameID": gameID, "userID": userID, "data": userData, "gameType": 3, "score": score};
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

	$("#message").html("You scored " + score + " points!<br>"
	+ "<a class='underlineLink' href='{{ url_for(\"thirdGameB\", game = game) }}'>Click here</a> to play the second part of this game.<br><br>");

}

function startGame() {
	$("#btnStart").prop("disabled", true);
	$("#btnOk").prop("disabled", true);
	$("#txtTheme").prop("readOnly", true);
	$("#txtTheme").val(theme);
	for(var i = 0; i < hints; i++) 
		$("#txtKey" + i).prop("readOnly", false);
	$("#txtKey0").focus();
}
