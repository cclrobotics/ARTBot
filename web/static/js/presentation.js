var app = app || {};

app.presentation = function(view, model) {
	let that = {};
	let selectedColorId = null;
	let colormap = null;
	let drawMode = true;
	let hasEmailError = false;
	let hasTitleError = false;
	let isSubmitDisabled = false;
	let isMousedown = false;

	const defaultErrorMessage = 'An unexpected error occurred. Try resubmitting later!';

	const confirmMessage = 'This will fill all cells with the selected '
						 +'color and erase ALL art. Are you sure?';

	const codeToMessage = {
		'canvas_empty': 'Try drawing something for us to grow!'
		, 'email': 'Try entering a valid email address!'
		, 'title_length': 'Your title is too long. Try shortening it a tad!'
		, 'monthly_limit':
			"Note: We're a small community lab run entirely by volunteers, and we can only "
			+ "make so many artpieces each month. This month we've hit our limit. You can "
			+ "still draw art here, but the website won't accept submissions. Come back next "
			+ "month and we'll start fresh!"
		, 'user_limit':
			"Easy there, speed demon! We're a small volunteer-run, non-profit lab and there's "
			+ "a limit to how many works of art we can help make. Once we make your previous "
			+ "submission, submit another one! If there's an issue with your previous "
			+ "submission and you want to withdraw it, send us an email: ccl-artbot@gmail.com"
	};

	function isBlankCanvas() {
		return model.canvas.isEmpty();
	}

	function enableSubmit() {
		if (!hasTitleError && !hasEmailError && !isBlankCanvas()) {
			view.submit.enable();
			isSubmitDisabled = false;
		}
	}

	view.canvas.register.onMousedown(function(pixel) {
		if (selectedColorId == null) { return; }
		isMousedown = true;
		if (drawMode) {
			view.canvas.set(colormap[selectedColorId].rgba, pixel.x, pixel.y);
			model.canvas.set(selectedColorId, pixel);
			if (isSubmitDisabled) {
				enableSubmit();
			}
		} else {
			view.canvas.unset(pixel.x, pixel.y);
			model.canvas.unset(pixel);
		}
	});
	view.canvas.register.onMouseup(function() {
		isMousedown = false;
	});
	view.canvas.register.onMouseleave(function() {
		isMousedown = false;
	});
	view.canvas.register.onMouseover(function(pixel) {
		if (!isMousedown || selectedColorId == null) { return; }

		if (drawMode) {
			view.canvas.set(colormap[selectedColorId].rgba, pixel.x, pixel.y);
			model.canvas.set(selectedColorId, pixel);
		} else {
			view.canvas.unset(pixel.x, pixel.y);
			model.canvas.unset(pixel);
		}
	});
	view.canvas.register.onDblclick(function(pixel) {
		view.canvas.unset(pixel.x, pixel.y);
		model.canvas.unset(pixel);
	});

	view.colorPicker.register.onClick(function(colorId) {
		selectedColorId = colorId;
		view.colorPicker.pick(colorId);
	});

	view.quickFill.register.onClick(function() {
		if (selectedColorId != null && (isBlankCanvas() || confirm(confirmMessage))) {
			view.canvas.fill(colormap[selectedColorId].rgba);
			model.canvas.setAll(selectedColorId);
		}
	});

	function selectDrawMode() {
		if (drawMode) { return; }
		drawMode = true;
		view.eraseMode.unselect();
		view.drawMode.select();
	}

	view.drawMode.register.onClick(function() {
		selectDrawMode();
	});
	view.eraseMode.register.onClick(function() {
		if (!drawMode) { return; }
		drawMode = false;
		view.drawMode.unselect();
		view.eraseMode.select();
	});

	function isSpace(c) {
		return /[\s]/.test(c);
	}

	view.email.register.onKeypress(function(key) {
		if (isSpace(key)) {
			return false;
		}
		if (hasEmailError) {
			view.email.error.unset();
			hasEmailError = false;
			enableSubmit();
		}
		return true;
	});

	function isInvalidTitleChar(c) {
		return !/[\w\s]/.test(c);
	}

	view.title.register.onKeypress(function(key) {
		if (isInvalidTitleChar(key)) {
			return false;
		}
		if (hasTitleError) {
			view.title.error.unset();
			hasTitleError = false;
			enableSubmit();
		}
		return true;
	});

	view.submit.register.onClick(function() {
		let title = view.title.val();
		if (title.length == 0) {
			hasTitleError = true;
		}
		let email = view.email.val();
		if (email.length == 0) {
			hasEmailError = true;
		}
		if (!isSubmitDisabled) {
			isSubmitDisabled = true;
			view.submit.disable();
		}
		if (hasTitleError || hasEmailError) {
			hasTitleError && view.title.error.set();
			hasEmailError && view.email.error.set();
			return;
		}
		if (isBlankCanvas()) {
			view.errorModal.show(codeToMessage['canvas_empty']);
			return;
		}
		model.canvas.submit(email, title);
	});

	view.successModal.register.onHide(function() {
		view.canvas.reset();
		view.email.reset();
		view.title.reset();
		selectDrawMode();
		view.successModal.hide();
		model.canvas.reset();
	});

	view.errorModal.register.onHide(function() {
		view.errorModal.hide();
	});

	function createColorMap(colors) {
		let colormap = {};
		for (let i=0; i != colors.length; ++i) {
			let color = colors[i];
			colormap[color.id] = {name: color.name, rgba: 'rgba('+color.rgba.join()+')'};
		}
		return colormap;
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
		'CANVAS_META': function(action) {
			colormap = createColorMap(action.payload.colors);
			for (id in colormap) {
				view.colorPicker.add(id, colormap[id].rgba);
			}
		}
		, 'CANVAS_SUBMIT': function(action) {
			if (action.error) {
				view.errorModal.show(errorsToMessage(action.payload));
			} else {
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
