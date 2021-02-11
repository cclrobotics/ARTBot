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

	let jobs = Jobs();

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
				jobs.load(JSON.parse(data.data));
				let job_data = jobs.data
				subject.notifyObservers({
					type: 'JOB_DATA'
					, error: false
					, payload: {
						job_data
					}
				});
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
		, submit: function(user) { //TODO: Log user as the printer
			$.ajax({
				url: 'procedure_request'
				, type: 'POST'
				, data: JSON.stringify({
					'ids': jobs.selected
				})
				, contentType: 'application/json'
				, dataType: 'json'
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
					type: 'PRINT_REQ_SUBMIT'
					, error: true
					, payload: jqXHR.responseJSON.errors
				});
			});
		}

	};

	that.register = function(...args) {
		args.forEach(elem => {
			subject.add(elem);
		});
	};

	return that;
};