/** @odoo-module **/

document.addEventListener('DOMContentLoaded', function() {
    var video = document.getElementById('explanatoryVideo');
    if (video) {
        video.play();
    }
});

function validateEmail(input) {
    const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
    const emailError = document.getElementById('emailError');
    if (!emailPattern.test(input.value)) {
        emailError.style.display = 'block';
    } else {
        emailError.style.display = 'none';
    }
}

function validateLetters(input) {
    input.value = input.value.replace(/[^a-zA-Z\s]/g, '');
}

function toggleSurgeryField(select) {
    var surgeryField = document.getElementById('surgery_field');
    if (select.value === 'yes') {
        surgeryField.style.display = 'block';
    } else {
        surgeryField.style.display = 'none';
    }
}

function validateForm() {
    var name = document.getElementById('name').value;
    var surname = document.getElementById('surname').value;
    var namePattern = /^[A-Za-z\s]+$/;

    if (!namePattern.test(name)) {
        alert('Name can only contain letters and spaces.');
        return false;
    }

    if (!namePattern.test(surname)) {
        alert('Surname can only contain letters and spaces.');
        return false;
    }

    return true;
}
