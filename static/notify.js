(async() => {
    // create and show the notification
    const showNotification = () => {
        console.debug('showNotification called');
        navigator.serviceWorker.getRegistration().then(function(reg) {
            var options = {
                body: 'Here is a notification body!',
                icon: 'images/example.png',
                vibrate: [100, 50, 100],
                data: {
                    dateOfArrival: Date.now(),
                    primaryKey: 1
                }
            };
            reg.showNotification('Hello world!', options);
            // close the notification after 10 seconds
            setTimeout(() => {
                reg.close();
            }, 10 * 1000);
            // navigate to a URL when clicked
            reg.addEventListener('click', () => {

                window.open('https://www.javascripttutorial.net/web-apis/javascript-notification/', '_blank');
            });
        });


    }

    // show an error message
    const showError = () => {
        const error = document.querySelector('.error');
        error.style.display = 'block';
        error.textContent = 'You blocked the notifications';
    }

    // check notification permission
    let granted = false;

    if (Notification.permission === 'granted') {
        granted = true;
    } else if (Notification.permission !== 'denied') {
        let permission = await Notification.requestPermission();
        granted = permission === 'granted' ? true : false;
    }

    // show notification or error
    granted ? showNotification() : showError();

})();