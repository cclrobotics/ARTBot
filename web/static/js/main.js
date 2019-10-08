const sizePicker = document.querySelector('.size-picker');
const pixelCanvas = document.querySelector('.pixel-canvas');
const quickFill = document.querySelector('.quick-fill');
const eraseMode = document.querySelector('.erase-mode');
const drawMode = document.querySelector('.draw-mode');
const drawSubmit = document.querySelector('.draw-submit');
const colorContainer = document.querySelector('#color-container');

const successModal = document.getElementById("success-modal");
const successClose = document.getElementsByClassName("close")[0];
const successText = document.getElementsByClassName("response-text")[0];

const errorModal = document.getElementById("error-modal");
const errorClose = document.getElementsByClassName("close")[1];
const errorText = document.getElementsByClassName("response-text")[1];

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

let colorChoice = "pink"; // Tracks the current color

makeColorPicker();

function makeGrid() {
  let gridHeight = 26
  let gridWidth = 39
  // If grid already present, clears any cells that have been filled in
  while (pixelCanvas.firstChild) {
    pixelCanvas.removeChild(pixelCanvas.firstChild);
  }
  // Creates rows and cells
  for (let i = 1; i <= gridHeight; i++) {
    let gridRow = document.createElement('tr');
    pixelCanvas.appendChild(gridRow);
    for (let j = 1; j <= gridWidth; j++) {
      let gridCell = document.createElement('td');
      gridRow.appendChild(gridCell);
      // Fills in cell with selected color upon mouse press ('mousedown', unlike 'click', doesn't also require release of mouse button)
      gridCell.addEventListener('mousedown', function() {
        const color = document.querySelector('.color-picker').value;
        this.style.backgroundColor = color;
      });
    }
  }
}

makeGrid(26, 39);

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
  pixelCanvas.querySelectorAll('td').forEach(td => td.style.backgroundColor = colorChoice);
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

  var xhr = new XMLHttpRequest();
  var csrf_token = document.querySelector("#csrf").value;
  var email = document.querySelector("#email").value;
  var title = document.querySelector("#title").value;
  data['email'] = email;
  data['title'] = title;
  data['art'] = canvasCoord;

  xhr.open("POST", '/receive_art', true);
  xhr.setRequestHeader('Content-type', 'application/json;charset=UTF-8');
  xhr.setRequestHeader('X-CSRFToken', csrf_token);
  xhr.send(JSON.stringify(
    data
  ));

  xhr.onloadend = function () {
    let status = xhr.status;
    let response = xhr.responseText;
    let modal;
    let text;
    let closer;
    

    if ((status < 300) && (status >= 200)) {
      modal = successModal;
      text = successText;
      closer = successClose;
    } else {
      modal = errorModal;
      text = errorText;
      closer = errorClose;
    }

    // update modal text
    text.innerHTML = response;

    // When we get a response, open the modal 
    modal.style.display = "block";

    // close the modal
    function closeModal(e) {
      if ((e.target == modal) || (e.target == closer)){
        modal.style.display = "none";
        // remove listener since we're done with modal
        e.target.removeEventListener(e.type, arguments.callee);
      }
    }

    window.addEventListener('click', closeModal);
  };

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