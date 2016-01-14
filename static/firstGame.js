var objects = "";

function httpGetAsync(url, callback, args) {
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open("GET", url, true); // true for asynchronous 
    xmlHttp.send(args);
}

function testClick(e) {
	e = e || window.event;
	if(e.keyCode == 13) {
		newObject();
		return false;
	}
	return true;
}

function newObject() {
	select = document.getElementById("list");
	select.readOnly = false;
	var op = document.createElement("option");
	var obj = document.getElementById("next").value;
	op.text = obj;
	if(objects != "")
		objects += "||";
	objects += obj;
	document.getElementById("next").value = "";
	op.selected = true;
	select.appendChild(op);
	select.readOnly = true;
}

function startGame(usuario, tema) {
	timer = document.getElementById("timer");
	document.getElementById("start").disabled = true;
	
	theme = document.getElementById("theme");
	theme.value = tema;

	next = document.getElementById("next");
	next.readOnly = false;
	next.focus();

	startTimer(30, timer, usuario);
}

function startTimer(duration, display, username) {
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
			//NÃO SEI O QUE FAZER MAS É AQUI QUE EU TENHO QUE FAZER
			data = document.getElementById("data");
			data.value = objects;
			document.forms["sendData"].submit();
		}
	}, 1000);
}

window.onload = function() {
	document.getElementById("start").disabled = false;
	document.getElementById("next").value = "";
	document.getElementById("theme").value = "";
}
