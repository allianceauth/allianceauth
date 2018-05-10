/**
* Get a duration string like countdown.js
* e.g. "1y 2d 3h 4m 5s"
* @param duration moment.duration
*/
function getDurationString(duration) {
    var out = "";
    if (duration.years()) {
        out += duration.years() + 'y ';
    }
    if (duration.months()) {
        out += duration.months() + 'm ';
    }
    if (duration.days()) {
        out += duration.days() + 'd ';
    }
    return out + duration.hours() + "h " + duration.minutes() + "m " + duration.seconds() + "s";
}


function getCurrentEveTimeString() {
    return moment().utc().format('dddd LL HH:mm:ss')
}
