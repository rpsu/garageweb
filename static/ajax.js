document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('garageform');
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = new FormData(form);
        fetch(form.action, {
                method: form.method,
                body: formData,
            })
            .then(response => response.json())
            .then(data => {
                // handle response if needed
            });
    });
    form.password.addEventListener('blur', function() {
        form.requestSubmit();
    });
});