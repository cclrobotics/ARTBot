var app = app || {};

app.view = function($, model) {
	let that = {};
	const DOM = {
		limitReached: $('.limit-reached')
		, colorContainer: $('#color-container')
		, drawMode: $('#draw')
		, eraseMode: $('.erase-mode')
		, titleInput: $('input#title')
		, emailInput: $('input#email')
		, drawSubmit: $('.draw-submit>.submit-button')
		, quickFill: $('.quick-fill')
		, pixelCanvas: $('.pixel-canvas')
		, successModal: $('#success-modal')
		, errorModal: $('#error-modal')
		, errorBody: $('#error-modal').find('.error-msg')
	}

	that.canvas = function(canvas) {
		let that = {};
		const pixels = canvas.find('td');

		that.fill = function(color) {
			pixels.css('background-color', color || "");
		};

		that.reset = function() {
			that.fill(null);
		};

		function getPixelAt(x, y) {
			return canvas.find('tr#Y'+y).find('#X'+x);
		}

		that.set = function(color, x, y) {
			let pixel = getPixelAt(x,y);
			pixel.css('background-color', color || "");
		};

		that.unset = function(x, y) {
			that.set(null, x, y);
		};

		function getPixelLocation(node) {
			return {
				x: parseInt(node.id.substring(1))
				, y: parseInt(node.parentNode.id.substring(1))
			};
		}

		that.register = {
			onMousedown: function(handler) {
				canvas.on('mousedown', function(event) {
					if (event.target.tagName == 'TD') {
						handler(getPixelLocation(event.target));
					}
				});
			}
			, onMouseup: function(handler) {
				canvas.on('mouseup', function(event) {
					handler();
				});
			}
			, onMouseleave: function(handler) {
				canvas.on('mouseleave', function(event) {
					handler();
				});
			}
			, onMouseover: function(handler) {
				canvas.on('mouseover', function(event) {
					if (event.target.tagName == 'TD') {
						handler(getPixelLocation(event.target));
					}
				});
			}
			, onDblclick: function(handler) {
				canvas.on('dblclick', function(event) {
					handler(getPixelLocation(event.target));
				});
			}
		};

		return that;
	}(DOM.pixelCanvas);

	that.quickFill = function(quickFill) {
		let that = {};
		that.register = {
			onClick: function(handler) {
				quickFill.on('click', function(event) {
					event.preventDefault();
					handler();
				});
			}
		};
		return that;
	}(DOM.quickFill);

	that.colorPicker = function(colorPicker) {
		let that = {};
		let selected = null;

		that.pick = function(colorId) {
			if (selected) {
				selected.removeClass('selected-color');
			}
			selected = colorPicker
				.find('[data-color-id="'+colorId+'"]')
				.addClass('selected-color');
		};

		that.add = function(id, color) {
			colorPicker.append(
				'<div class="color-picker" data-color-id="'
				+id
				+'" style="background:'+color+';"></div>'
			);
		};
		that.register = {
			onClick: function(handler) {
				colorPicker.on('click', function(event) {
					event.preventDefault();
					if (event.target.className == 'color-picker') {
						handler(parseInt(event.target.dataset.colorId));
					}
				});
			}
		};

		return that;
	}(DOM.colorContainer);

	that.drawMode = function(draw) {
		let that = {};
		that.select= function() {
			draw.addClass('selected-mode');
		};
		that.unselect= function() {
			draw.removeClass('selected-mode');
		};
		that.register = {
			onClick: function(handler) {
				draw.on('click', function(event) {
					event.preventDefault();
					draw.blur();
					handler();
				});
			}
		};
		return that;
	}(DOM.drawMode);

	that.eraseMode = function(erase) {
		let that = {};
		that.select = function() {
			erase.addClass('selected-mode');
		};
		that.unselect = function() {
			erase.removeClass('selected-mode');
		};
		that.register = {
			onClick: function(handler) {
				erase.on('click', function(event) {
					event.preventDefault();
					erase.blur();
					handler();
				});
			}
		};
		return that;
	}(DOM.eraseMode);

	that.email = function(email) {
		let that = {};
		that.val = function() {
			return email.val();
		};
		that.reset = function() {
			email.val('');
		};
		that.error = {
			set: function() {
				email.addClass('has-error');
			}
			, unset: function() {
				email.removeClass('has-error');
			}
		};
		that.register = {
			onKeypress: function(handler) {
				email.on('keypress', function(event) {
					if (!handler(event.key)) {
						event.preventDefault();
					}
				});
			}
		};

		return that;
	}(DOM.emailInput);

	that.title = function(title) {
		let that = {};
		that.val = function() {
			return title.val();
		};
		that.reset = function() {
			title.val('');
		};
		that.error = {
			set: function() {
				title.addClass('has-error');
			}
			, unset: function() {
				title.removeClass('has-error');
			}
		};
		that.register = {
			onKeypress: function(handler) {
				title.on('keypress', function(event) {
					if (!handler(event.key)) {
						event.preventDefault();
					}
				});
			}
		};
		return that;
	}(DOM.titleInput);

	that.successModal = function(modal) {
		let that = {};
		const close = modal.find('.close');

		that.show = function() {
			modal.css('display', 'block');
		};
		that.hide = function() {
			modal.css('display', 'none');
		};
		that.register = {
			onHide: function(handler) {
				close.on('click', function(event) {
					event.preventDefault();
					handler();
				});
				modal.on('click', function(event) {
					event.preventDefault();
					if (event.target.id == 'success-modal') {
						handler();
					}
				});
			}
		};
		return that;
	}(DOM.successModal);

	that.errorModal = function(modal) {
		let that = {};
		const body = modal.find('.error-msg');
		const close = modal.find('.close');

		that.show = function(message) {
			body.text(message);
			modal.css('display', 'block');
		};
		that.hide = function() {
			modal.css('display', 'none');
		}
		that.register = {
			onHide: function(handler) {
				close.on('click', function(event) {
					event.preventDefault();
					handler();
				});
				modal.on('click', function(event) {
					event.preventDefault();
					if (event.target.id == 'error-modal') {
						handler();
					}
				});
			}
		};
		return that;
	}(DOM.errorModal);

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
	}(DOM.drawSubmit);

	return that;
};
