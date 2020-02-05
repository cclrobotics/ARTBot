const sizePicker = document.querySelector('.size-picker');
const pixelCanvas = document.querySelector('.pixel-canvas');
const quickFill = document.querySelector('.quick-fill');
const eraseMode = document.querySelector('.erase-mode');
const drawMode = document.querySelector('.draw-mode');
const drawSubmit = document.querySelector('.draw-submit');
const colorContainer = document.querySelector('#color-container');
const limitReached = document.querySelector('.limit-reached');

const successModal = document.getElementById("success-modal");
const successClose = document.getElementsByClassName("close")[0];

const errorModal = document.getElementById("error-modal");
const errorClose = document.getElementsByClassName("close")[1];
const errorText = document.getElementsByClassName("response-text")[0];

successModal.addEventListener("click", function() {
	successModal.style.display = "none";
	resetInputFields();
});

errorModal.addEventListener("click", function() {
	errorModal.style.display = "none";
});

function codeToMessage(code) {
	let messages = {
		"monthly_limit": 
			"Note: We're a small community lab run entirely by volunteers, and we can only "
			+ "make so many artpieces each month. This month we've hit our limit. You can "
			+ "still draw art here, but the website won't accept submissions. Come back next "
			+ "month and we'll start fresh!"
		, "user_limit":
			"Easy there, speed demon! We're a small volunteer-run, non-profit lab and there's "
			+ "a limit to how many works of art we can help make. Once we make your previous "
			+ "submission, submit another one! If there's an issue with your previous "
			+ "submission and you want to withdraw it, send us an email: ccl-artbot@gmail.com"
	};
	return messages[code];
}

requests = function() {
	var artpieceMeta;

	return {
		getArtpieceMeta: function() {
			var xhr = new XMLHttpRequest();
			xhr.open('GET', '/artpieces', true);
			xhr.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
			xhr.responseType = "json"
			xhr.onloadend = function () {
				let status = xhr.status;
				let response = xhr.response;

				if ((status < 300) && (status >= 200)) {
					artpieceMeta = response.meta;
					if (limitReached.hidden && artpieceMeta.submission_limit_exceeded) {
						limitReached.innerHTML = '<hr>'
							+codeToMessage('monthly_limit')
							+'<hr>';
						limitReached.hidden = false;
					}
				}
			};
			xhr.send();
		}
		, createArtpiece: function(email, title, art) {
			var xhr = new XMLHttpRequest();
			xhr.open('POST', '/artpieces', true);
			xhr.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
			xhr.responseType = "json";
			xhr.send(JSON.stringify({'email': email, 'title': title, 'art': art}));

			xhr.onloadend = function () {
				let status = xhr.status;
				let response = xhr.response;
				let modal;
				let closer;

				if ((status < 300) && (status >= 200)) {
					modal = successModal;
				} else {
					modal = errorModal;
					let text = errorText;
					let errors = response.errors;
					// update modal text
					if (errors.length == 0) {
						text.innerHTML = "Oops... an unexpected error occurred!";
					} else {
						let code = errors[0]['code'];
						let title = errors[0]['title'];
						text.innerHTML = codeToMessage(code) || title;
					}
				}

				// When we get a response, open the modal 
				modal.style.display = "block";
			};
		}
	};
}();

requests.getArtpieceMeta();

function makeColorPicker() {
  let colors = [
      "pink",
      "orange",
      "teal",
      "yellow",
      "blue"
  ];
  colors.forEach(function(color) {
    let colorCircle = document.createElement('div');
    colorCircle.id = color;
    colorCircle.className = "color-picker";
    colorCircle.style.display = "inline-block";
    colorCircle.style.backgroundColor = color;
    colorCircle.style.margin = "5px";
    colorContainer.appendChild(colorCircle);

    if (color === "pink") {
      colorCircle.classList.add("selected-color");
    }
  }); 
}

function fillPixelCanvas(color) {
  pixelCanvas.querySelectorAll('td').forEach(td => td.style.backgroundColor = color);
}

function resetInputFields() {
  function resetPixelCanvas() {
    fillPixelCanvas(null);
  }

  resetPixelCanvas();
  document.querySelector("#email").value = "";
  document.querySelector("#title").value = "";
}

let colorChoice = "pink"; // Tracks the current color

makeColorPicker();

pixelCanvas.addEventListener('mousedown', function(e) {
    if (e.target.tagName !== 'TD') return;
    e.target.style.backgroundColor = colorChoice;
  });

// Enables color dragging with selected color (code for filling in single cell is above). (No click on 'draw' mode needed; this is default mode)
let down = false; // Tracks whether or not mouse pointer is pressed

// Listens for mouse pointer press and release on grid. Changes value to true when pressed, but sets it back to false as soon as released
pixelCanvas.addEventListener('mousedown', function(e) {
	down = true;
	pixelCanvas.addEventListener('mouseup', function() {
		down = false;
	});
  // Ensures cells won't be colored if grid is left while pointer is held down
  pixelCanvas.addEventListener('mouseleave', function() {
    down = false;
  });

  pixelCanvas.addEventListener('mouseover', function(e) {
    // While mouse pointer is pressed and within grid boundaries, fills cell with selected color. Inner if statement fixes bug that fills in entire grid
  	if (down) {
      // 'TD' capitalized because element.tagName returns upper case for DOM trees that represent HTML elements
      if (e.target.tagName === 'TD') {
      	e.target.style.backgroundColor = colorChoice;
      }
    }
  });
});
drawMode.style.background='linear-gradient(#f9f9f9 5%, #c5ddb5 100%)'

// Listens for clicks on the color-container.  If the target has color-picker class then update colorChoice
// variable with its background color and add border to selected element (remove border on previous).
colorContainer.addEventListener('click', function(e) {
  e.preventDefault();
  if (e.target.className === 'color-picker') {
    let selected = document.querySelector('.selected-color');
    selected.classList.remove("selected-color");
    colorChoice = e.target.style.backgroundColor;
    e.target.classList.add("selected-color");
  }   
});

// Adds color-fill functionality. e.preventDefault(); intercepts page refresh on button click
quickFill.addEventListener('click', function(e) {
  e.preventDefault();
  if (confirm('This will fill all cells with the selected color and erase ALL art. Are you sure?')) {
    fillPixelCanvas(colorChoice)
  } 
});

// Removes color from cell upon double-click
pixelCanvas.addEventListener('dblclick', e => {
  e.target.style.backgroundColor = null;
});

// NONDEFAULT DRAW AND ERASE MODES:

// Allows for drag and single-cell erasing upon clicking 'erase' button. Code for double-click erase functionality (Without entering erase mode) is above. Also note 'down' was set to false in variable above
eraseMode.addEventListener('click', function() {
  // Enables drag erasing while in erase mode
  pixelCanvas.addEventListener('mousedown', function(e) {
  	down = true;
  	pixelCanvas.addEventListener('mouseup', function() {
  		down = false;
  	});
    // Ensures cells won't be erased if grid is left while pointer is held down
    pixelCanvas.addEventListener('mouseleave', function() {
      down = false;
    });
    pixelCanvas.addEventListener('mouseover', function(e) {
      // While mouse pointer is pressed and within grid boundaries, empties cell contents. Inner if statement fixes bug that fills in entire grid
    	if (down) {
        if (e.target.tagName === 'TD') {
        	e.target.style.backgroundColor = null;
        }
      }
    });
  });
  // Enables single-cell erase while in erase mode
  pixelCanvas.addEventListener('mousedown', function(e) {
    e.target.style.backgroundColor = null;
  });
  eraseMode.style.background='linear-gradient(#f9f9f9 5%, #c5ddb5 100%)';
  drawMode.style.background='linear-gradient(#f9f9f9 5%, #e9e9e9 100%)';
});

// Allows user to return to (default) draw mode after using 'erase' button. Note 'down' was set to false in variable above
drawMode.addEventListener('click', function() {
  pixelCanvas.addEventListener('mousedown', function(e) {
  	down = true;
  	pixelCanvas.addEventListener('mouseup', function() {
  		down = false;
  	});
    // Ensures cells won't be colored if grid is left while pointer is held down
    pixelCanvas.addEventListener('mouseleave', function() {
      down = false;
    });
    pixelCanvas.addEventListener('mouseover', function(e) {
      // While mouse pointer is pressed and within grid boundaries, fills cell with selected color. Inner if statement fixes bug that fills in entire grid
    	if (down) {
        if (e.target.tagName === 'TD') {
        	e.target.style.backgroundColor = colorChoice;
        }
      }
    });
  });
  // Enables single-cell coloring while in draw mode
  pixelCanvas.addEventListener('mousedown', function(e) {
    if (e.target.tagName !== 'TD') return;
    e.target.style.backgroundColor = colorChoice;
  });
  drawMode.style.background='linear-gradient(#f9f9f9 5%, #c5ddb5 100%)';
  eraseMode.style.background='linear-gradient(#f9f9f9 5%, #e9e9e9 100%)';
});

drawSubmit.addEventListener('submit', function(e) {
  e.preventDefault();

  var canvasCoord = new Object();
  var data = new Object();
  var table = document.querySelector(".pixel-canvas");

  for (var i = 0, row; row = table.rows[i]; i++) {
    for (var j = 0, col; col = row.cells[j]; j++) {
     if (col.style.backgroundColor != "") {
      if (canvasCoord[col.style.backgroundColor]) {
       canvasCoord[col.style.backgroundColor].push([i,j]);
      } else {
        canvasCoord[col.style.backgroundColor] = [[i,j]];
      }
     }
   }
  }
  var email = document.querySelector("#email").value;
  var title = document.querySelector("#title").value;
  requests.createArtpiece(email, title, canvasCoord);
});



// SLIDESHOW CODE:

const _C = document.querySelector('.container'),
N = _C.children.length,NF = 30,
TFN = {
  'linear': function(k) { return k }, 
  'ease-in': function(k, e = 1.675) {
    return Math.pow(k, e)
  }, 
  'ease-out': function(k, e = 1.675) {
    return 1 - Math.pow(1 - k, e)
  }, 
  'ease-in-out': function(k) {
    return .5*(Math.sin((k - .5)*Math.PI) + 1)
  }, 
  'bounce-out': function (k, a = 2.75, b = 1.5) {
    return 1 - Math.pow(1 - k, a) * Math.abs(Math.cos(Math.pow(k, b) * (n + .5) * Math.PI));
  } };


let i = 0,x0 = null,locked = false,w,ini,fin,rID = null,anf,n;

function stopAni() {
  cancelAnimationFrame(rID);
  rID = null;
};

function ani(cf = 0) {
  _C.style.setProperty('--i', ini + (fin - ini) * TFN['bounce-out'](cf / anf));

  if (cf === anf) {
    stopAni();
    return;
  }

  rID = requestAnimationFrame(ani.bind(this, ++cf));
};

function unify(e) {return e.changedTouches ? e.changedTouches[0] : e;};

function lock(e) {
  x0 = unify(e).clientX;
  locked = true;
};

function drag(e) {
  e.preventDefault();

  if (locked) {
    let dx = unify(e).clientX - x0,f = +(dx / w).toFixed(2);

    _C.style.setProperty('--i', i - f);
  }
};

function move(e) {
  if (locked) {
    let dx = unify(e).clientX - x0,
    s = Math.sign(dx),
    f = +(s * dx / w).toFixed(2);

    ini = i - s * f;

    if ((i > 0 || s < 0) && (i < N - 1 || s > 0) && f > .2) {
      i -= s;
      f = 1 - f;
    }

    fin = i;
    anf = Math.round(f * NF);
    n = 2 + Math.round(f);
    ani();
    x0 = null;
    locked = false;
  }
};

function size() {w = window.innerWidth;};

size();
_C.style.setProperty('--n', N);

addEventListener('resize', size, false);

_C.addEventListener('mousedown', lock, false);
_C.addEventListener('touchstart', lock, false);

_C.addEventListener('mousemove', drag, false);
_C.addEventListener('touchmove', drag, false);

_C.addEventListener('mouseup', move, false);
_C.addEventListener('touchend', move, false);