var app = app || {};

app.presentation = function(view, model) {
	let that = {};
	let isSubmitDisabled = false;
	let isMousedown = false;
	let hasJobBoardError = false;

	const defaultErrorMessage = 'An unexpected error occurred. Try resubmitting later!';

	const confirmMessage = 'This will generate a printing protocol for a robot and '
						 +'mark all selected art as in-process. Are you sure?';

	const codeToMessage = {
		'joblist_empty': 'Select a job to manage'
	};

	const emptyJobListMessage = '[Click A Row To Select]';


	function isEmptyJobList() {
		return model.jobs.noneSelected();
	}

	function enableSubmit() {
		if (!isEmptyJobList()) {
			view.submit.enable();
			view.errorOverlay.hide();
			isSubmitDisabled = false;
		}
	}

	function ui_action_by_id(action, id) {
		if(['select','unselect','hover', 'unhover'].includes(action)){
			let job = view.board.getJob(id);
			view.board[action](job);
		}
	};

	view.board.register.onClick(function(job) {
		if (model.jobs.isSelected(job)) {
			model.jobs.unselect(job);
			ui_action_by_id('unselect', job);
			view.selectedJobList.removeJob(job);
			if(model.jobs.noneSelected()){view.selectedJobList.showPlaceholder();}
		} else {
			model.jobs.select(job);
			img_url = model.jobs.get_img_url(job);
			ui_action_by_id('select', job);
			view.selectedJobList.addJob(job, img_url);
			if (isSubmitDisabled) { enableSubmit(); }
		}
	});

	view.submit.register.onClick(function() {
		if (!isSubmitDisabled) {
			isSubmitDisabled = true;
			view.submit.disable();
		}
		if (isEmptyJobList()) {
			view.errorOverlay.show(codeToMessage['joblist_empty']);
			hasJobBoardError = true;
			return;
		}
		model.jobs.submit('TEST_USER'); //TODO: Replace with logged-in user
	});

	view.successModal.register.onHide(function() {
		view.board.clear();
		view.selectedJobList.clear();
		model.jobs.clear();
		model.jobs.reset();
		model.jobs.get();
	});

	function createJobBoard(printables) {
		var col = [];
		for (var id_key in printables) {
			delete printables[id_key].art //art not used in display
			for (var key in printables[id_key]) {
				if (col.indexOf(key) === -1) {
					col.push(key);
				}
			}
		}

		view.board.initialize_headers(col);
	
		for (var id_key in printables) {
			job = printables[id_key];
			view.board.add(job);
		}
	}

	function errorsToMessage(errors) {
		let errorMessage = defaultErrorMessage;
		for (let i=0; i!=errors.length; ++i) {
			let code = errors[i].code;
			if (codeToMessage.hasOwnProperty(code)) {
				errorMessage = codeToMessage[code];
				break;
			}
		}
		return errorMessage;
	}

	let notificationHandlers = {
		'JOB_DATA': function(action) {
			createJobBoard(action.payload.job_data);
		}
		, 'PRINT_REQ_SUBMIT': function(action) {
			if (action.error) {
				view.warningModal.show(errorsToMessage(action.payload));
			} else {
				view.successModal.update(action.payload.msg, action.payload.procedure_uri)
				view.submissionModal.hide();
				view.successModal.show();
			}
			view.submit.enable();
		}
	};

	that.notify = function(action) {
		if (notificationHandlers.hasOwnProperty(action.type)) {
			notificationHandlers[action.type](action);
		}
	};

	return that;
};
