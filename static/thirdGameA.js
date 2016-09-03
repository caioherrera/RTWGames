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
	if(number == 1)
		document.getElementById("key2").focus();
	else if(number == 2)
		document.getElementById("key3").focus();
	else
		document.getElementById("ok").focus();
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

	objects = "";

	var txt1 = document.getElementById("key1").value.toLowerCase();
	var txt2 = document.getElementById("key2").value.toLowerCase();
	var txt3 = document.getElementById("key3").value.toLowerCase();

	if(txt1 != "") 
		objects += txt1;
	if(objects != "")
		objects += "||";	

	if(txt2 != "")
		objects += txt2;
	if(objects != "") 
		objects += "||";	
	
	if(txt3 != "")
		objects += txt3;
	if(objects != "")
		objects += "||";

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
