var data1 = "";
var theme = "";
var data2 = "";
var data = [];
var count = 0;
var score = 40;
var endGame = false;

function testClick(e) {
	e = e || window.event;
	if(e.keyCode == 13) {
		value = document.getElementById("next").value.toLowerCase();
		newObject("guesses", value, true);
		if(theme == value) {
			document.getElementById("theme").innerHTML = "Correct answer!";
			endGame = true;
			end();
		}
		else {
			document.getElementById("theme").innerHTML = "Wrong answer!";
		}
		document.getElementById("next").value = "";
		return false;
	}
	return true;
}

function newObject(name, value, save) {
	select = document.getElementById(name);
	select.readOnly = false;
	var op = document.createElement("option");
	var obj = value.toLowerCase();
	op.text = obj;
	if(save) {
		if(data1 != "")
			data1 += "||";
		data1 += obj;
	}
	op.selected = true;
	select.appendChild(op);
	select.readOnly = true;
}

function startGame(usuario, tema, dados) {
	timer = document.getElementById("timer");
	document.getElementById("start").disabled = true;
	
	theme = tema.toLowerCase();
	data2 = dados.toLowerCase();
	data = dados.toLowerCase().split("||");

	next = document.getElementById("next");
	next.readOnly = false;
	next.focus();

	startTimer(30, timer, usuario);
}

function nextHint() {
	if(count < data.length)
		newObject("hints", data[count++], false);
}

function end() {
	next = document.getElementById("next");
	next.value = "";
	next.readOnly = true;
	document.getElementById("data1").value = data1.toLowerCase();
	document.getElementById("data2").value = data2.toLowerCase();
	document.getElementById("count").value = count;
	document.getElementById("score").value = score;

	document.forms["sendData"].submit();
}

function startTimer(duration, display, username) {
	var timer = duration, minutes, seconds;
	setInterval(function() {
		minutes = parseInt(timer / 60, 10);
		seconds = parseInt(timer % 60, 10);

		minutes = minutes < 10 ? "0" + minutes : minutes;
		seconds = seconds < 10 ? "0" + seconds : seconds;
		display.textContent = "Time remaining: " + minutes + ":" + seconds;

		if(timer % 10 == 0 && !endGame) {
			if(timer > 0)
				nextHint();
			score -= 10;
		}

		if (!endGame && timer-- <= 0) {
			timer = 0;
			end();
		}
	}, 1000);
}

window.onload = function() {
	document.getElementById("start").disabled = false;
	document.getElementById("next").value = "";
	document.getElementById("theme").innerHTML = "";
}
