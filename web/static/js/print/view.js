var app = app || {};

app.view = function($, model) {
	let that = {};
	const DOM = {
		sidebarLeft: $('#sidebar-left')
		, sidebarRight : $('#sidebar-right')
		, submissionModal: $('#submission-modal')
		, submissionBox: $('#submission-block')
		, submissionModalBtn: $('#submit-show')
		, printSubmit: $('.print-submit>.submit-button')
		, jobBoard: $('.job-board')
		, jobHeader: $('.job-header')
		, boardContainer: $('.board-container')
		, selectedJobList: $('#selected-jobs')
		, selectedJobsPlaceholder: $('#selected-jobs-placeholder')
		, successModal: $('#success-modal')
		, errorModal: $('#error-modal')
		, errorBody: $('#error-modal').find('.error-msg')
		, loginModal: $('#login-modal')
		, loginMsg: $('#login-msg')
		, loginForm: $('#login-form')
		, userLabel: $("#user-label")
		, expand: $('.expand')
	}

	const columnDisplay = { //using arrow functions for readability
		'img_uri': (val) => '<img class="job-data" src=' + val + '>'
		,'status': (val) => val.split("SubmissionStatus.")[1]
		,'submit_date': (val) => val.split("T")[0] + "<br>" + val.split("T")[1].split(".")[0]
	}

	// Initialise tooltips
	$('[data-toggle="tooltip"]').tooltip()

	that.board = function(board) {
		let that = {};
		const jobs = board.find('tr.job-data');

		function make_element(ele_type, payload, ele_class, ele_id){
			let opening = '<' + ele_type
			let middle = '>';
			if(ele_class){middle = ' class="' + ele_class + '"' + middle;}
			if(ele_id){middle = ' id="' + ele_id + '"' + middle;}
			let closing = payload + '</' + ele_type + '>';
			return opening + middle + closing;
		}

		that.initialize_headers = function(headers){
			let tr = '<tr class="job-header">';
			for (let i = 0; i < headers.length; i++) {
				cell_html = make_element('th', headers[i]);
				tr = tr + cell_html;
			}
			tr = tr + '</tr>';
			board.append(tr);
		}

		that.jobs = jobs;

		that.add = function(job) {
			let tr = '<tr class="job-data" id=ID' + job['id'] + '>';	
			for (const key in job) {
				content = (columnDisplay[key] || function(x){return x;})(job[key]);
				cell_html = make_element('td', content, 'job-data');
				tr = tr + cell_html;
			}
			tr = tr + '</tr>';
			board.append(tr);
		};
		
		that.select = function(job) {
			job.css('background-color', "aliceblue" || "");
		};

		that.unselect = function(job) {
			job.css('background-color', "");
		};

		that.hover = function(job) { //not implemented
			job.css('border', "3px solid");
		};

		that.unhover = function(job) { //not implemented
			console.log(job);
			job.css('border', "silver 1px dotted;");
		};

		that.reset = function() {
			for (var i = 0; i < jobs.length; i++){
				let job = jobs[i];
				that.unselect(job);
			}
		};

		that.clear = function() {
			board.html("");
		}

		that.getJob = function(id) {
			return board.find('tr#ID'+id);
		};

		function getJobID(node) {
			return parseInt(node.id.substring(2));
		};

		that.register = {
			onClick: function(handler) {
				board.on('click', function(event) {
					if (event.target.tagName == 'TD') {
						handler(getJobID(event.target.parentNode));
					}
				});
			}
			, onMouseleave: function(handler) { //not implemented
				board.on('mouseleave', function(event) {
					if (event.target.tagName == 'TD') {
						handler(getJobID(event.target.parentNode));
					}
				});
			}
			, onMouseover: function(handler) { //not implemented
				board.on('mouseover', function(event) {
					if (event.target.tagName == 'TD') {
						handler(getJobID(event.target.parentNode));
					}
				});
			}
		};

		return that;
	}(DOM.jobBoard);

	that.selectedJobList = function(selectedJobList, selectedJobsPlaceholder) {
		let that = {};

		that.showPlaceholder = function() {
			selectedJobsPlaceholder.show();
		}

		that.addJob = function(job_id, job_url){
			selectedJobsPlaceholder.hide();
			selectedJobList.append(
				`<div id=ID${job_id}>
					<br>
					<span class='list-label'> ID ${job_id} | </span>
					<img class='list-img' src=${job_url}>
				</div>`
			)
		}

		that.removeJob = function(job_id){
			let to_remove = selectedJobList.find("div#ID" + job_id);
			to_remove.remove();
		}

		that.clear = function(){
			selectedJobsPlaceholder.detach();
			selectedJobList.html("");
			selectedJobList.prepend(selectedJobsPlaceholder);
			selectedJobsPlaceholder.show();
		}

		that.disable = function() {
			selectedJobList.html("");
		}

		return that;
	}(DOM.selectedJobList, DOM.selectedJobsPlaceholder)

	that.successModal = function(modal) {
		let that = {};

		that.show = function() {
			modal.modal();
		};

		that.update = function(msg,link) {
			let msg_space = modal.find("p#output-messages");
			msg_space.html(msg.join('<br>'));

			modal.on('click', '#procedure-link', function(){document.location=link});
		};

		that.register = {
			onHide: function(handler) {
				modal.on('hide.bs.modal', handler);
			}
		};
		return that;
	}(DOM.successModal);

	that.errorOverlay = function(submissionBox) {
		let error = submissionBox.find('#submission-error');
		let content = error.find('.content');
		let submit = $('.print-submit')
		let that = {};

		that.show = function(message) {
			content.text(message);
			submit.hide();
			error.show();
		};
		that.hide = function() {
			error.hide();
			submit.show();
		};

		return that;
	}(DOM.submissionBox);

	that.warningModal = function(modal, content) {
		let that = {};

		that.show = function(message) {
			content.text(message);
			modal.modal();
		}
		return that;
	}(DOM.errorModal, DOM.errorBody);

	that.login = function(modal, msg, form) {
		let that = {};

		let user_input = form.find('#login-username')
		let password_input = form.find('#login-password')

		that.show = function() {
			modal.modal({'backdrop':'static'});
		}

		that.hide = function() {
			modal.modal('hide');
		}

		that.fail = function(message) {
			msg.text(message);
			user_input.addClass('has-error');
			password_input.addClass('has-error');
		}

		that.reset = function(message) {
			user_input.removeClass('has-error');
			password_input.removeClass('has-error');
		}

		that.register = {
			onSubmit: function(handler) {
				form.on('submit', function(event) {
					event.preventDefault();
					handler(user_input[0].value, password_input[0].value);
				});
			}
			, onChange: function(handler) {
				user_input.on('change', function(event) {
					handler();
				});
				password_input.on('change', function(event) {
					handler();
				});
			}
		}

		return that;
	}(DOM.loginModal, DOM.loginMsg, DOM.loginForm);

	that.userLabel = function(label) {
		let that = {};

		that.update = function(user) {
			label.html("<b>Logged-in as:</b><br>" + user);
		};

		that.clear = function() {
			label.text = null;
		};
		
		return that;
	}(DOM.userLabel);
	
	that.submit = function(submit) {
		let that = {};
		that.disable = function() {
			submit.prop('disabled', true);
		};
		that.enable = function() {
			submit.prop('disabled', false);
		};
		that.register = {
			onClick: function(handler) {
				submit.on('click', function(event) {
					event.preventDefault();
					submit.blur();
					handler();
				});
			}
		};
		return that;
	}(DOM.printSubmit);

	that.submissionModal = function(modal) {
		let that = {};
		that.hide = function() {
			modal.modal('hide');
		};
		return that;
	}(DOM.submissionModal);

	let layout = function(sidebarLeft, sidebarRight, modal) {
		let modalBody = modal.find('.modal-body');
		let submissionBoxSidebar = sidebarRight;
		let submissionBox = submissionBoxSidebar.find('#submission-block');

		function getWindowSize() {
			return $(window).width();
		}

		function getSubmissionBoxContainer() {
			let size = getWindowSize();
			let container = sidebarRight;
			if (size < 992) {
				container = modalBody;
			} else if (size < 1200) {
				container = sidebarLeft;
			}
			return container;
		}

		function switchSubmissionBox(sidebar) {
			if (sidebar === submissionBoxSidebar) { return; }
			submissionBox.detach();
			submissionBox.toggleClass("mt-3");
			submissionBox.addClass('info-block');
			if (sidebar === sidebarLeft) {
				submissionBox.appendTo(sidebar);
			} else {
				if (sidebar === modal) {
					submissionBox.removeClass('info-block');
				}
				submissionBox.prependTo(sidebar);
			}
			submissionBoxSidebar = sidebar;
		}

		switchSubmissionBox(getSubmissionBoxContainer());

		$(window).resize(function() {
			switchSubmissionBox(getSubmissionBoxContainer());
		});

	}(DOM.sidebarLeft, DOM.sidebarRight, DOM.submissionModal);

	DOM.expand.on('click', function() {
		DOM.boardContainer.toggleClass('max-width-98');
		DOM.sidebarLeft.toggleClass('d-flex');
		DOM.sidebarLeft.toggleClass('d-none');
	});

	DOM.submissionModalBtn.on('click', function() {
		DOM.submissionModal.modal();
	});

	return that;
};
