var app = app || {};

app.subject = function() {
	const observers = [];
	return {
		add: function(item) {
			observers.push(item);
		}
		, notifyObservers: function(action) {
			observers.forEach(elem => {
				elem.notify(action);
			});
		}
	}
};

app.model = function() {
	let that = {};
	const subject = this.subject();

	function Jobs() {
		let that = {};
		const selected = [];
		const data = {};

		that.load = function(job_data){
			for (var i = 0; i < job_data.length; i++){
				item = job_data[i];
				data[item["id"]] = item;
			}
		}

		that.select = function (id) {
			if(selected.indexOf(id) < 0){
				selected.push(id);
			}
		}

		that.unselect = function (id) {
			index = selected.indexOf(id);
			if(index >= 0){
				selected.splice(index, 1);
			}
		}

		that.reset = function() {
			selected.length = 0;
		}

		that.clear = function() {
			for(key in data){
				delete data[key];
			}
		}

		that.selected = selected;

		that.data = data;

		return that;
	}

	function User() {
		let that = {};
		const info = {};

		function get_cookie(name) {
			const value = `; ${document.cookie}`;
			const parts = value.split(`; ${name}=`);
			if (parts.length === 2) return parts.pop().split(';').shift();
		}

		function load_name() {
			info['name'] = get_cookie("username");
			subject.notifyObservers({
				type: 'UPDATE_USER'
				, payload: {'name': info['name']}
			});
			return info['name']
		}

		that.load_name = function() {
			return load_name()
		}

		that.set_name = function(name) {
			document.cookie = "username=" + name;
			return load_name()
		}

		that.clear_name = function() {
			document.cookie = "username=; expires=Thu, 01 Jan 1970 00:00:00 UTC; path=/;";
			return load_name()
		}

		that.get_csrf_token = function(name) {
			return get_cookie("csrf_access_token")
		}

		that.name = info['name']

		return that;
	} 

	let jobs = Jobs();
	let user = User();

	that.jobs = {
		get: function() {
			$.ajax({
				url: 'print_jobs'
				, type: 'GET'
				, dataType: 'json'
				, cache: 'false'
			})
			.done(function(data, textStatus, jqXHR) {
				jobs.load(JSON.parse(data.data));
				let job_data = jobs.data
				subject.notifyObservers({
					type: 'JOB_DATA'
					, error: false
					, payload: {
						job_data
					}
				});
			})
			.fail(function(jqXHR, textStatus, errorThrown) {
				if(jqXHR.status==401){
					subject.notifyObservers({
						type: 'LOGIN_REQUIRED'
					})
				};
				if(jqXHR.status==403){
					subject.notifyObservers({
						type: 'NOT_AUTHORIZED'
					})
				};
			});
		}
		, select: function(id) {
			jobs.select(id);
		}
		, unselect: function(id) {
			jobs.unselect(id);
		}
		, reset: function() {
			jobs.reset();
		}
		, clear: function() {
			jobs.clear();
		}
		, isSelected(id) {
			return jobs.selected.includes(id);
		}
		, noneSelected: function() {
			return jobs.selected.length == 0;
		}
		, get_img_url: function(id) {
			return jobs.data[id].img_uri;
		}
		, submit: function() {
			$.ajax({
				url: 'procedure_request'
				, type: 'POST'
				, data: JSON.stringify({
					'ids': jobs.selected
				})
				, contentType: 'application/json'
				, dataType: 'json'
				, headers: {
					'X-CSRF-TOKEN': user.get_csrf_token()
				}
			})
			.done(function(data, textStatus, jqXHR) {
				subject.notifyObservers({
					type: 'PRINT_REQ_SUBMIT'
					, error: false
					, payload: data
				});
			})
			.fail(function(jqXHR, textStatus, errorThrown) {
				subject.notifyObservers({
					type: 'LOGIN_REQUIRED'
					, error: true
					, payload: jqXHR.responseJSON.errors
				});
			});
		}

	};

	that.user = {
		login: function(username, password) {
			$.ajax({
				url: 'user/login'
				, type: 'POST'
				, data: JSON.stringify({
					'username': username
					, 'password': password
				})
				, contentType: 'application/json'
				, dataType: 'json'
			})
			.done(function(data, textStatus, jqXHR) {
				subject.notifyObservers({
					type: 'LOGIN'
					, error: false
					, payload: data
				});
			})
			.fail(function(jqXHR, textStatus, errorThrown) {
				subject.notifyObservers({
					type: 'LOGIN_FAIL'
					, error: true
					, payload: jqXHR.responseJSON.errors
				});
			});
		}
		,set_name: function(name){
			user.set_name(name);
		}
		,clear_name: function(){
			user.clear_name();
		}
		,load_name: function(){
			user.load_name();
		}
	}

	that.register = function(...args) {
		args.forEach(elem => {
			subject.add(elem);
		});
	};

	return that;
};