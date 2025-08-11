document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('garageform');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        const button = document.getElementById('toggleButton');
        button.disabled = true
        clearInput();

        fetch(form.action, {
                method: form.method,
                body: formData,
            })
            .then(response => console.debug(response.status, response.statusText))
            .then(() => {
                button.removeAttribute('disabled');
            })
;
    });
    // form.password.addEventListener('blur', function() {
    //     form.requestSubmit();
    // });
});

function clearInput() {
    const input = document.getElementById('garagepwd');
    input.value = '';
    if (input.hasAttribute('disabled')) {
        input.removeAttribute('disabled');
    }
    input.focus();
}