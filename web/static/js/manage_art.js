//put code to draw a table from JSON sent by API here
//also maybe rename it to describe exactly what it's doing

//it may need to be moved into one of the other js MVP files
//but I like leaving it seperate at least for now, because it means we won't load the script to get data unless the person has print permissions
//  plus the MVP theory, I think, suggests that each view gets its own presenter

function CreateTableFromJSON(printables) {
    // EXTRACT VALUE FOR HTML HEADER. 
    var col = [];
    for (var i = 0; i < printables.length; i++) {
        for (var key in printables[i]) {
            if (col.indexOf(key) === -1 && key != 'art') {
                col.push(key);
            }
        }
    }

    // CREATE DYNAMIC TABLE.
    var table = document.createElement("table");

    // CREATE HTML TABLE HEADER ROW USING THE EXTRACTED HEADERS ABOVE.

    var tr = table.insertRow(-1);                   // TABLE ROW.

    for (var i = 0; i < col.length; i++) {
        var th = document.createElement("th");      // TABLE HEADER.
        th.innerHTML = col[i];
        th.classList.add('print_grid');
        tr.appendChild(th);
    }

    // ADD JSON DATA TO THE TABLE AS ROWS.
    for (var i = 0; i < printables.length; i++) {

        tr = table.insertRow(-1);

        for (var j = 0; j < col.length; j++) {
            var tabCell = tr.insertCell(-1);
            if(col[j] != 'art' && col[j] != 'img_uri'){
                tabCell.innerHTML = printables[i][col[j]];
            } else {
                if(col[j] == 'img_uri'){
                    tabCell.innerHTML = '<img src=' + printables[i][col[j]] + '>'
                }
            }
            tabCell.classList.add('print_grid');
        }
        var tabCell = tr.insertCell(-1);
        tabCell.innerHTML = '<input type="checkbox" id = ' + printables[i].id + '><label for="' + + printables[i].id + '"> Select to print</label>'
    }

    // FINALLY ADD THE NEWLY CREATED TABLE WITH JSON DATA TO A CONTAINER.
    var divContainer = document.getElementById("grid");
    divContainer.innerHTML = "";
    divContainer.appendChild(table);
}

$(document).ready(function () {
	$.ajax({
        url: 'print_jobs'
        , type: 'GET'
        , dataType: 'json'
    })
    .done(function(data, textStatus, jqXHR) {
        CreateTableFromJSON(JSON.parse(data.data));
    });
});