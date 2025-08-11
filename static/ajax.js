document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('garageform');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const button = document.getElementById('toggleButton');
        button.disabled = true

        document.getElementById('garagepwd').value = ''

        fetch(() => {
            form.action, {
                method: form.method,
                body: formData,
            }
        })
        .then(response => console.debug(response.status, response.statusText))
        .then(response => console.debug(response))
        .then(() => {
            button.removeAttribute('disabled');
        });
    });
});
