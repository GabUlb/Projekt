var canvas,
    context,
    dragging = false,
    dragStartLocation,
    snapshot,
    permanentVes,
    currentPosition,
    waiting,
    requestNum,
    toAdd,
    identifier;


function getCanvasCoordinates(event) {
    var x = event.clientX - canvas.getBoundingClientRect().left,
        y = event.clientY - canvas.getBoundingClientRect().top;

    return {x: Math.round(x), y: Math.round(y)};
}

// function takeSnapshot() {
//     snapshot = context.getImageData(0, 0, canvas.width, canvas.height);
// }

// function restoreSnapshot() {
//     context.putImageData(snapshot, 0, 0);
// }

// function drawLine(position) {
//     context.beginPath();
//     context.moveTo(dragStartLocation.x, dragStartLocation.y);
//     context.lineTo(position.x, position.y);
//     context.stroke();
// }

// function drawCircle(position) {
//     var radius = Math.sqrt(Math.pow((dragStartLocation.x - position.x), 2) + Math.pow((dragStartLocation.y - position.y), 2));
//     context.beginPath();
//     context.arc(dragStartLocation.x, dragStartLocation.y, radius, 0, 2 * Math.PI, false);
// }

// function drawPolygon(position, sides, angle) {
//     var coordinates = [],
//         radius = Math.sqrt(Math.pow((dragStartLocation.x - position.x), 2) + Math.pow((dragStartLocation.y - position.y), 2)),
//         index = 0;

//     for (index = 0; index < sides; index++) {
//         coordinates.push({x: dragStartLocation.x + radius * Math.cos(angle), y: dragStartLocation.y - radius * Math.sin(angle)});
//         angle += (2 * Math.PI) / sides;
//     }

//     context.beginPath();
//     context.moveTo(coordinates[0].x, coordinates[0].y);
//     for (index = 1; index < sides; index++) {
//         context.lineTo(coordinates[index].x, coordinates[index].y);
//     }

//     context.closePath();
// }

// function draw(position) {

//     var fillBox = document.getElementById("fillBox"),
//         shape = document.querySelector('input[type="radio"][name="shape"]:checked').value,
//         polygonSides = document.getElementById("polygonSides").value;
//     if (shape === "circle") {
//         drawCircle(position);
//     }
//     if (shape === "line") {
//         drawLine(position);
//     }

//     if (shape === "polygon") {
//         drawPolygon(position, polygonSides, Math.PI / 4);
//     }

//     if (fillBox.checked) {
//         context.fill();
//     } else {
//         context.stroke();
//     }
// }
function dragStart(event) {
    dragging = true;
    permanentVes = document.getElementById("ves").value + ""
    dragStartLocation = getCanvasCoordinates(event);
    requestNum += 1
    // takeSnapshot();
}

function drag(event) {
    if (dragging === true) {
        // restoreSnapshot();
        currentPosition = getCanvasCoordinates(event);
        // draw(position, "polygon");
        addVes(false)
        document.getElementById("vesForm").getElementsByTagName("button")[0].click()
    }
}

function dragStop(event) {
    dragging = false;
    // restoreSnapshot();
    currentPosition = getCanvasCoordinates(event);
    // draw(position, "polygon");
}

function changeFillStyle(){
    context.fillStyle = this.value;
    event.stopPropagation();
}
function changeLineWidth(){
    context.lineWidth= this.value;
    event.stopPropagation();
}
function changeStrokeStyle(){
    context.strokeStyle= this.value;
    event.stopPropagation();
}

// function eraseCanvas() {
//     context.clearRect(0,0,canvas.width, canvas.height);
// }

function getRandomInt(max) {
    return Math.floor(Math.random() * max);
}

function init() {
    waiting = false
    canvas = document.getElementById("canvas");
    context = canvas.getContext('2d');
    requestNum = 0
    identifier = getRandomInt(2**16)
    var lineWidth = document.getElementById("lineWidth");
        fillColor = document.getElementById("fillColor");
        strokeColor = document.getElementById("strokeColor");
    //     clearCanvas = document.getElementById("clearCanvas");

    // context.fillStyle = fillColor.value;
    // context.lineWidth = lineWidth.value;
    // context.strokeStyle = strokeColor.value;
    // context.lineCap = 'round';


    canvas.addEventListener('mousedown', dragStart, false);
    canvas.addEventListener('mousemove', drag, false);
    canvas.addEventListener('mouseup', dragStop, false);
    lineWidth.addEventListener('input', changeLineWidth, false);
    fillColor.addEventListener('input', changeFillStyle, false);
    strokeColor.addEventListener('input', changeStrokeStyle, false);
    // clearCanvas.addEventListener('click', eraseCanvas, false);
    document.getElementById("vesForm").addEventListener("submit", handleSubmit);
    clearCanvas()
}

function clearCanvas(){
    document.getElementById("ves").value = "VES 1.0 800 500"
    document.getElementById("vesForm").getElementsByTagName("button")[0].click()
}

function showExample(){
    document.getElementById("ves").value = `VES v1.0 600 400
CLEAR #A3D0D4
#USI
FILL_CIRCLE 230 120 40 #000000
FILL_CIRCLE 235 125 20 #FFC1CB
FILL_CIRCLE 370 120 40 #000000
FILL_CIRCLE 365 125 20 #FFC1CB
#TELO
FILL_CIRCLE 300 380 130 #000000
FILL_CIRCLE 300 420 90 #FFFFFF
#HLAVA
FILL_CIRCLE 300 200 100 #FFFFFF
CIRCLE 300 200 100 10 #000000
#LAVE OKO
FILL_CIRCLE 260 180 30 #000000
FILL_CIRCLE 250 170 10 #FFFFFF
FILL_CIRCLE 265 185 5 #FFFFFF
#PRAVE OKO
FILL_CIRCLE 340 180 30 #000000
FILL_CIRCLE 330 170 10 #FFFFFF
FILL_CIRCLE 345 185 5 #FFFFFF
#NOS
FILL_TRIANGLE 290 210 310 210 300 220 #FFC1CB`
    document.getElementById("vesForm").getElementsByTagName("button")[0].click()
}

function handleSubmit(e) {
	e.preventDefault(); 
    if(!waiting){
        if(!dragging){
            requestNum += 1000
        }
        waiting = true
	    const ves = document.getElementById("ves").value; 
        const width = canvas.width
        const height = canvas.height

	    const formular = new URLSearchParams(); 
	    formular.append('ves', ves); 
        formular.append('width', width); 
        formular.append('height', height); 
        formular.append('requestNum', requestNum.toString() + ":" + identifier.toString())
        formular.append('toAdd', toAdd)

	    const url = this.action; 
	    const method = this.method; 
	    fetch(url, {method: method, body: formular}) 
	    	.then((res) => res.blob()) 
	    	.then((image) => {
                var savedImage = new Image()
                savedImage.onload = (event) => {
                    URL.revokeObjectURL(event.target.src)
                    context.drawImage(event.target, 0, 0)
                }
                savedImage.src = URL.createObjectURL(image);
                waiting = false
	    })
    }
}

function addVes(permanent){
    shape = document.querySelector('input[type="radio"][name="shape"]:checked').value
    fillBox = document.getElementById("fillBox")
    ves = document.getElementById("ves")
    ves.value = permanentVes
    toAdd = ""
    if (shape === "circle") {
        radius = Math.round(Math.sqrt(Math.pow((dragStartLocation.x - currentPosition.x), 2) + Math.pow((dragStartLocation.y - currentPosition.y), 2)));
        if (fillBox.checked){
            toAdd += "FILL_CIRCLE "+dragStartLocation.x+" "+dragStartLocation.y+" "+radius+" "+fillColor.value+"\n"
        }  // TODO: Add variable thickness
        toAdd += "CIRCLE "+dragStartLocation.x+" "+dragStartLocation.y+" "+radius+" "+lineWidth.value+" "+strokeColor.value
    }
    if (shape === "line") {
        toAdd += "LINE "+dragStartLocation.x+" "+dragStartLocation.y+" "+currentPosition.x+" "+currentPosition.y+" "+lineWidth.value+" "+strokeColor.value
        if (fillBox.checked){
            toAdd += "\nLINE "+dragStartLocation.x+" "+dragStartLocation.y+" "+currentPosition.x+" "+currentPosition.y+" "+Math.round(lineWidth.value/2)+" "+fillColor.value
        }
    }
    if (shape === "polygon") {
        if(polygonSides = document.getElementById("polygonSides").value == 4){
            if (fillBox.checked){
                toAdd += "FILL_RECT "+dragStartLocation.x+" "+dragStartLocation.y+" "+(currentPosition.x-dragStartLocation.x)+" "+(currentPosition.y-dragStartLocation.y)+" "+fillColor.value+"\n"
            }  // TODO: Add variable thickness
            toAdd += "RECT "+dragStartLocation.x+" "+dragStartLocation.y+" "+(currentPosition.x-dragStartLocation.x)+" "+(currentPosition.y-dragStartLocation.y)+" "+lineWidth.value+" "+strokeColor.value
        }
        else if(polygonSides = document.getElementById("polygonSides").value == 3){
            if (fillBox.checked){
                toAdd += "FILL_TRIANGLE "+dragStartLocation.x+" "+dragStartLocation.y+" "+currentPosition.x+" "+dragStartLocation.y+" "+Math.round((currentPosition.x+dragStartLocation.x)/2)+" "+currentPosition.y+" "+fillColor.value+"\n"
            }  // TODO: Add variable thickness
            toAdd += "TRIANGLE "+dragStartLocation.x+" "+dragStartLocation.y+" "+currentPosition.x+" "+dragStartLocation.y+" "+Math.round((currentPosition.x+dragStartLocation.x)/2)+" "+currentPosition.y+" "+lineWidth.value+" "+strokeColor.value
        }
    }
    ves.value = permanentVes + "\n" + toAdd
}

window.addEventListener('load', init, false);