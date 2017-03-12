var userID, gameID, themes, hints;
var userData = {};
var countingData = 0;
var countingHints = 0;
var score = 35;
var givenHints = [];
var ended = false;

$(document).ready(function() {

    userID = $("#userID").text();
    gameID = $("#gameID").text();
    themes = $("#themes").text().split("||");
    hints = $("#hints").text().split("||");

    $("#message").html("Guess the theme of the round!<br><br>");

});

function testClick(e) {
    e = e || window.event;
    if(e.keyCode == 13) {
        var d = $("#txtNext").val();
        if(d != "") {
            verifyAnswer(d);
            addData(d);
        }
        return false;
    }
    return true;
}

function addData() {
    var d = $("#txtNext").val();
    if(d != "") {
        userData[d.toLowerCase()] = givenHints.slice();
        countingData++;

        $("#lstPrevious").prop("readOnly", false);
		$("#lstPrevious").append($("<option>", { value: countingData, text: d }));
		$("#lstPrevious").prop("readOnly", true);

    }
    $("#txtNext").val("");
	$("#txtNext").focus();
}

function startGame() {

	$("#btnStart").prop("disabled", true);
	$("#txtNext").prop("readOnly", false);
	$("#txtNext").focus();

	startTimer(30);
}

function nextHint() {
    if(countingHints < hints.length) {

        $("#lstHints").prop("readOnly", false);
		$("#lstHints").append($("<option>", { value: countingHints + 1, text: hints[countingHints] }));
		$("#lstHints").prop("readOnly", true);

		givenHints.push(hints[countingHints]);
		countingHints++;
    }
}

//TO-DO

function endGame() {
    $("#txtNext").prop("readOnly", true);
    $("#divGame").hide();

    var data = {"gameID": gameID, "userID": userID, "data": userData, "score": score, "gameType": 2};
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

    $("#message").html("Game Over!<br>Your score is: " + score + " points!<br>");
}

function startTimer(duration) {

    var timer = duration;
    var minutes, seconds;

    var calls = setInterval(decTimer, 1000);

    function decTimer() {

        minutes = parseInt(timer / 60, 10);
		seconds = parseInt(timer % 60, 10);

		$("#timer").text("Time remaining: " + (minutes < 10 ? "0" : "") + minutes + ":" + (seconds < 10 ? "0" : "") + seconds);

        var t = timer--;
        if(ended || t <= 0) {
            timer = 0;
            clearInterval(calls);
            endGame();
        }
        else if(t % 5 == 0) {
            score -= 5;
            nextHint();
        }
    };
}

function verifyAnswer(data) {
    data = data.toLowerCase();
    if(themes.indexOf(data) != -1) {
        $("#message").html("Correct answer! Congratulations!<br><br>");
        ended = true;
        endGame();
    }
    else
        $("#message").html("Wrong answer! Keep trying!<br><br>");
}
