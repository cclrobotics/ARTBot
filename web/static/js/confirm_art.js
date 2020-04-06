function displayConfirmationMessage() {
	let token = document.getElementById('token').value;
	let id = document.getElementById('id').value;

	if (token == "" || id == "") {
		document.getElementById('token_invalid').hidden = false;
	} else {
		let xhr = new XMLHttpRequest();
		xhr.open('PUT', '/artpieces/'+id+'/confirmation/'+token, true);
		xhr.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
		xhr.responseType = 'json';
		xhr.onloadend = function () {
			let status = xhr.status;
			let response = xhr.response;
			let divToDisplay = (
				status >= 400 ? response.errors[0].code : response.data.confirmation.status
			);
			if (divToDisplay == 'not_found') {
				divToDisplay = 'token_invalid';
			}
			document.getElementById(divToDisplay).hidden = false;
		};
		xhr.send();
	}
}

displayConfirmationMessage();
