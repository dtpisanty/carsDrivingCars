var dateP; //Dom element for the date
var cars; //Array of cars from JSON
var idx=1; //Current car to show
const numCars=10; //Number of trips to animate (0 = show all)
function preload() {
  //Get car data from JSON file...
  let url ='trips.json';
  httpGet(url, function(response) {
    cars = response ; //and store it into files
  });
}

function setup() {
    // Create canvas and asign DOM variables
    var canvas=createCanvas(800,400);
    canvas.parent('canvas');
    dateP=select("#date");
}

function draw() {
    //Draw canvas outline
    stroke('#cecece');
    strokeWeight(3);
    noFill();
    rect(0,0,width,height);
    // Check that cars has data from JSON
    if(cars){
        if(numCars>0 && cars.length>numCars){
            cars=cars.slice(cars.length-numCars,cars.length);
        }
        if(mouseX<width){
            //Calculate at which x position to change car
            var increment=width/(cars.length-1);
            if (mouseX>increment*idx && mouseX<width){
                idx++;
            }
            if (mouseX<increment*(idx-1) && mouseX>0){
                idx--;
            }
            //Calculate interpolation amount based on mouseX
            var amount=(mouseX%increment)/increment;
            if(amount>1)
                amount=1.0;
            if(amount<0)
                amount=0;
        }else{
            amount=1.0;
            idx=cars.length-1;
        }
        //Clear canvas with transparent rect (Delay effect)
        noStroke();
        fill(255,255,255,60);
        rect(0,0,width,height);
        noFill();
        //Move canvas left and up to center car
        push();
        translate(-140,-400);
        //Draw wheels
        strokeWeight(10);
        stroke('black');
        for(i=0;i<2;i++){
            circle.apply(this,cars[0].wheels[i]);
        }
        //Draw base
        fill('black');
        noStroke();
        rect.apply(this,cars[0].base);
        //Calculate fill colour interpolation
        var fills=[color(cars[idx-1].fill),color(cars[idx].fill)];
        var gVal=lerp(fills[0].levels[1],fills[1].levels[1],amount);
        fill(255,gVal,0);
        strokeWeight(2);
        stroke('black');
        //Calculate geometry based on interpolation amount
        var back=[lerp(cars[idx-1].tri[0],cars[idx].tri[0],amount),
                lerp(cars[idx-1].tri[1],cars[idx].tri[1],amount),
                lerp(cars[idx-1].tri[2],cars[idx].tri[2],amount),
                lerp(cars[idx-1].tri[3],cars[idx].tri[3],amount),
                lerp(cars[idx-1].tri[4],cars[idx].tri[4],amount),
                lerp(cars[idx-1].tri[5],cars[idx].tri[5],amount)
                ];
        var middle=[lerp(cars[idx-1].rect[0],cars[idx].rect[0],amount),
                lerp(cars[idx-1].rect[1],cars[idx].rect[1],amount),
                lerp(cars[idx-1].rect[2],cars[idx].rect[2],amount),
                lerp(cars[idx-1].rect[3],cars[idx].rect[3],amount),
                lerp(cars[idx-1].rect[4],cars[idx].rect[4],amount),
                lerp(cars[idx-1].rect[5],cars[idx].rect[5],amount),
                lerp(cars[idx-1].rect[6],cars[idx].rect[6],amount),
                lerp(cars[idx-1].rect[7],cars[idx].rect[7],amount),
                ];
        var front=[lerp(cars[idx-1].quad[0],cars[idx].quad[0],amount),
                lerp(cars[idx-1].quad[1],cars[idx].quad[1],amount),
                lerp(cars[idx-1].quad[2],cars[idx].quad[2],amount),
                lerp(cars[idx-1].quad[3],cars[idx].quad[3],amount),
                lerp(cars[idx-1].quad[4],cars[idx].quad[4],amount),
                lerp(cars[idx-1].quad[5],cars[idx].quad[5],amount),
                lerp(cars[idx-1].quad[6],cars[idx].quad[6],amount),
                lerp(cars[idx-1].quad[7],cars[idx].quad[7],amount),
                ];
        //Draw geometry
        triangle.apply(this,back)
        quad.apply(this,middle)
        quad.apply(this,front)
        pop();
        fill('black');
        noStroke();
        //Adjust date to Mexico City timezone (UTC-6)
        const dateTime=new Date(cars[idx].timestamp.substring(0,4)+"-"+cars[idx].timestamp.substring(4,6)+"-"+cars[idx].timestamp.substring(6,8)+" "+cars[idx].timestamp.substring(8,10)+":"+cars[idx].timestamp.substring(10,12));
        dateTime.setHours(dateTime.getHours()-6);
        // Display date in date <p>
        dateP.html(dateTime.toLocaleString('en-UK'));
    }
}
