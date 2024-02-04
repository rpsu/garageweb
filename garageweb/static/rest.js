const statuses = {
    'open': {
        color: 'red',
        image: 'HouseRed.gif'
    },
    'closed': {
        color: 'green',
        image: 'HouseGreen.gif'
    },
    'between': {
        color: 'yellow',
        image: 'QuestionYellow.gif'
    },
}


let lastResponse = null;
const pollInterval = 15; // seconds

const apiCaller = () => {
    var request = new XMLHttpRequest();
    const API_URL = '/api/door';
    request.open('GET', API_URL);
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.responseType = 'json';
    request.onload = () => {
        if (!!request.status && request.status === 200) {
            const resp = request.response || null;

            if (resp.length) {
                if (resp != lastResponse) {
                doorStatusUpdater(resp);
                if (lastResponse != null) {
                    console.debug('Door status changed');
                    showNotification(resp);
                }
                lastResponse = resp;
                }
            }
        }
        else if (!resp || request.status !== 200) {
            console.warn(`Response code is ${request.status || 'unknown'}`);
        }
        else {
            console.warn(`Response is plain wrong.`);
        }
    };
    request.send();
}

// Trigger 1st call immediately.
apiCaller();

setInterval(() => {
    apiCaller();
}, pollInterval * 1000);


function doorStatusUpdater(doorStatus) {
    console.debug('doorStatusUpdater() executed with doorStatus:', doorStatus);
    document.body.className = statuses[doorStatus].color;
    var image = document.getElementById('statusImage');
    image.src = '/static/images/' + statuses[doorStatus].image
}


function showNotification(doorStatus) {
    Notification.requestPermission().then(function(permission) {
        if (permission === "granted") {
            var notification = new Notification("Door status: " + doorStatus);
            console.debug('Notification:', notification);
        }
    });
}

document.getElementById("notifyMe").addEventListener('click', function() {
    Notification.requestPermission().then(function(permission) {
        if (permission === "granted") {
            var notification = new Notification("Notifications enabled!");
        }
    });
});
