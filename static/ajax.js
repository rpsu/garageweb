document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('garageform');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);

        clearInput();
        fetch(form.action, {
                method: form.method,
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                console.debug(data);
            });
    });
    form.password.addEventListener('blur', function() {
        form.requestSubmit();
    });
});

function clearInput() {
    const input = document.getElementById('garagepwd');
    input.value = '';
    if (input.hasAttribute('disabled')) {
        input.removeAttribute('disabled');
    }
    input.focus();
}