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

	// Inefficient constructor | more idiomitic method doesn't allow for private vars
	function Canvas(size={x: 26, y:26}) {
		let that = {};
		let numOfColoredPixels = 0;
		let coloredPixels = initNulls(size.x);

		function initNulls(size) {
			let nullarray = [];
			for (let i = 0; i != size; ++i) {
				nullarray[i] = null;
			}
			return nullarray;
		}

		that.isColor = function(pixel, color) {
			if (coloredPixels[pixel.x] == null) {
				return color == null;
			}
			return coloredPixels[pixel.x][pixel.y] == color;
		};

		that.isColorless = function(pixel) {
			return that.isColor(pixel, null);
		};

		that.set = function(pixel, color) {
			if (coloredPixels[pixel.x] == null) {
				coloredPixels[pixel.x] = [];
				for (let i = 0; i != size.y; ++i) {
					coloredPixels[pixel.x][i] = null;
				}
			}
			if (coloredPixels[pixel.x][pixel.y] == null) {
				++numOfColoredPixels;
			}
			coloredPixels[pixel.x][pixel.y] = color;
		};

		that.setAll = function(color) {
			numOfColoredPixels = 0;
			for (let x = 0; x != size.x; ++x) {
				let colors_x = coloredPixels[x] || [];
				for (let y = 0; y != size.y; ++y) {
					++numOfColoredPixels;
					colors_x[y] = color;
				}
				coloredPixels[x] = colors_x;
			}
		};

		that.unset = function(pixel) {
			if (coloredPixels[pixel.x] == null) { return; }
			coloredPixels[pixel.x][pixel.y] = null;
			--numOfColoredPixels;
		};

		function addToColorMap(colorToPixelMap, colors, x) {
			for (let y = 0; y != size.y; ++y) {
				let color = colors[y];
				if (!color) { continue; }
				if (!colorToPixelMap.hasOwnProperty(color)) {
					colorToPixelMap[color] = [];
				}
				// pixels are passed as [y,x]
				colorToPixelMap[color].push([y,x]);
			}
		}

		that.asColorToPixelMap = function() {
			let colorToPixelMap = {};
			for (let x = 0; x != size.x; ++x) {
				let colors_x = coloredPixels[x];
				if (!colors_x) { continue; }
				addToColorMap(colorToPixelMap, colors_x, x);
			}
			return colorToPixelMap;
		};

		that.isEmpty = function() {
			return numOfColoredPixels == 0;
		};

		that.reset = function() {
			numOfColoredPixels = 0;
			coloredPixels = initNulls(size.x);
		};

		return that;
	}

	let canvas = Canvas();

	that.canvas = {
		meta: {
			get: function() {
				$.ajax({
					url: 'artpieces'
					, type: 'GET'
					, dataType: 'json'
				})
				.done(function(data, textStatus, jqXHR) {
					subject.notifyObservers({
						type: 'CANVAS_META'
						, error: false
						, payload: {
							colors: data.meta.bacterial_colors
						}
					});
				})
				.fail(function(jqXHR, textStatus, errorThrown) {
					subject.notifyObservers({
						type: 'CANVAS_META'
						, error: false
						, payload: {
							colors: data.meta.bacterial_colors
						}
					});
				});
			}
		}
		, set: function(colorId, pixel) {
			if (canvas.isColor(pixel, colorId)) { return; }
			canvas.set(pixel, colorId);
		}
		, setAll: function(colorId) {
			canvas.setAll(colorId);
		}
		, unset: function(pixel) {
			if (canvas.isColorless(pixel)) { return; }
			canvas.unset(pixel);
		}
		, submit: function(email, title) {
			$.ajax({
				url: 'artpieces'
				, type: 'POST'
				, data: JSON.stringify({
					'email': email
					, 'title': title
					, 'art': canvas.asColorToPixelMap()
				})
				, contentType: 'application/json'
				, dataType: 'json'
			})
			.done(function(data, textStatus, jqXHR) {
				subject.notifyObservers({
					type: 'CANVAS_SUBMIT'
					, error: false
					, payload: data
				});
			})
			.fail(function(jqXHR, textStatus, errorThrown) {
				subject.notifyObservers({
					type: 'CANVAS_SUBMIT'
					, error: true
					, payload: jqXHR.responseJSON.errors
				});
			});
		}
		, reset: function() {
			canvas.reset();
		}
		, isEmpty: function() {
			return canvas.isEmpty();
		}
	};

	that.register = function(...args) {
		args.forEach(elem => {
			subject.add(elem);
		});
	};

	return that;
};

