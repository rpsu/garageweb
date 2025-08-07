const restApiDoor = () => {
    var request = new XMLHttpRequest();
    const API_URL = '/api/door';
    request.open('GET', API_URL);
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.responseType = 'json';
    request.onload = () => {
        if (request.status === 200) {
            const resp = request.response;
            if (resp.status && resp.image && resp.color) {
                document.body.className = resp.color;
                var image = document.getElementById('status-imge');
                image.src = '/static/images/' + resp.image
            }
        } else {
            console.warn(`Response code is ${this.status}`)
        }
    };
    request.send();
}

// Call it immediately.
restApiDoor();

// Call it repeatedly.
setInterval(restApiDoor, 5 * 1000)