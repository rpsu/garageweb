const restApiDoor = () => {
    var request = new XMLHttpRequest();
    const API_URL = '/api/door';
    request.open('GET', API_URL);
    request.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
    request.responseType = 'json';
    request.onload = () => {
        console.log(request)
        if (request.status === 200) {
            const resp = request.response;
            if (resp.status && resp.image && resp.color) {
                document.body.style.backgroundColor = resp.color;
                var image = document.getElementById('status-imge');
                image.src = '/static/images/' + resp.image
            }
        } else {
            console.warn(`Response code is ${this.status}`)
                // setTimeout(window.location = '/', 3000)
        }

    };
    console.info('Calling API URL', API_URL);
    request.send();
}
restApiDoor();


setInterval(restApiDoor, 15 * 1000)