function toggleForm(formId) {
    // get the form and the overlay
    const form = document.getElementById(formId);
    const overlay = document.getElementById('overlay');

    // change the visible of the form and the overlay
    if (form.classList.contains('show')) {
        form.classList.remove('show');
        overlay.classList.remove('show');

        const formDiv = form.querySelector("form");
        formDiv.reset();
    } else {
        // close any open form before displaying the new one
        closeAllForms();
        form.classList.add('show');
        overlay.classList.add('show');
    }
}

function closeAllForms() {
    // close all the form and the overlay
    document.querySelectorAll('.form-container').forEach(form => form.classList.remove('show'));
    document.getElementById('overlay').classList.remove('show');
}