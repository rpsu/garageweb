document.addEventListener('DOMContentLoaded', function () {
    const form = document.getElementById('garageform');
    form.addEventListener('submit', function (e) {
        const button = document.getElementById('toggleButton');
        button.disabled = true

        const input = document.getElementById('garagepwd');
        input.value = '';
    });
})
