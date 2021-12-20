function realtimeClock(){
    var rtClock = new Date();
    var hrs = rtClock.getHours();
    var min = rtClock.getMinutes();
    var sec = rtClock.getSeconds();
    const monthNames = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
    const weekday = ["Sun", "Mon", "Tue", "Wed", "Thur", "Fri","Sat"]
    var date = weekday[today.getDay()] +','+today.getDate() +'-'+monthNames[(today.getMonth()+1)]+'-'+ today.getFullYear();


    var amPm = ( hrs < 12)? " AM" : " PM";

    hrs = ("0" + hrs).slice(-2);
    min = ("0" + min).slice(-2);
    sec  = ("0" + sec).slice(-2);

    document.getElementById('real_time').innerHTML = hrs + " : " + min + " : " + sec + amPm + " " + date
    var t = setTimeout(realtimeClock, 500);

}