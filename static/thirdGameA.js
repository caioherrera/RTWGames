var objects = "";

function testClick(e, number) {
	e = e || window.event;
	if(e.keyCode == 13) {
		newObject(number);
		return false;
	}
	return true;
}

function newObject(number) {
	var txt = "";
	if(number == 1) {
		txt = document.getElementById("key1").value.toLowerCase();
		document.getElementById("key2").focus();
	}
	else if(number == 2) {
		txt = document.getElementById("key2").value.toLowerCase();
		document.getElementById("key3").focus();
	}
	else {
		txt = document.getElementById("key3").value.toLowerCase();
		document.getElementById("ok").focus();
	}
	if(objects != "")
		objects += "||";
	objects += txt;
}

function startGame(usuario, tema) {
	//timer = document.getElementById("timer");
	document.getElementById("start").disabled = true;
	
	theme = document.getElementById("theme");
	theme.value = tema.toLowerCase();

	document.getElementById("key1").readOnly = false;
	document.getElementById("key2").readOnly = false;
	document.getElementById("key3").readOnly = false;
	document.getElementById("ok").disabled = false;
	document.getElementById("key1").focus();

//	startTimer(30, timer, usuario);
}

function sendForm() {
	document.getElementById("data").value = objects;
	document.forms["sendData"].submit();
}

/*function startTimer(duration, display, username) {
	var timer = duration, minutes, seconds;
	setInterval(function() {
		minutes = parseInt(timer / 60, 10);
		seconds = parseInt(timer % 60, 10);

		minutes = minutes < 10 ? "0" + minutes : minutes;
		seconds = seconds < 10 ? "0" + seconds : seconds;
		display.textContent = "Time remaining: " + minutes + ":" + seconds;

		if(timer-- <= 0) {
			next = document.getElementById("next");
			next.value = "";
			next.readOnly = true;
			timer = 0
			data = document.getElementById("data");
			data.value = objects;
			document.forms["sendData"].submit();
		}
	}, 1000);
}*/

window.onload = function() {
	document.getElementById("start").disabled = false;
	document.getElementById("key1").value = "";
	document.getElementById("key2").value = "";
	document.getElementById("key3").value = "";
	document.getElementById("ok").disabled = true;
	document.getElementById("theme").value = "";
}
