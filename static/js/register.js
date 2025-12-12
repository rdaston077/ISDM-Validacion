// Inputs
const username = document.getElementById("id_username");
const email = document.getElementById("id_email");
const pass1 = document.getElementById("id_password1");
const pass2 = document.getElementById("id_password2");
const terms = document.getElementById("terms");
const submitBtn = document.getElementById("submitBtn");

// Checklist elementos
const reqLength = document.getElementById("req-length");
const reqNum = document.getElementById("req-number");
const reqUpper = document.getElementById("req-uppercase");
const reqSymbol = document.getElementById("req-symbol");

// Errores
const errorUsername = document.getElementById("error-username");
const errorEmail = document.getElementById("error-email");
const errorPass = document.getElementById("error-pass");

// Validación de email
function validateEmail() {
    const value = email.value.trim();
    const regex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

    errorEmail.textContent = regex.test(value) ? "" : "Email inválido";
}

// Validación username mínima
function validateUsername() {
    const value = username.value.trim();
    errorUsername.textContent = value.length >= 4 ? "" : "Debe tener al menos 4 caracteres";
}

// Checklist de contraseña
function validatePasswordStrength() {
    const pwd = pass1.value;

    validateItem(reqLength, pwd.length >= 8);
    validateItem(reqNum, /[0-9]/.test(pwd));
    validateItem(reqUpper, /[A-Z]/.test(pwd));
    validateItem(reqSymbol, /[^A-Za-z0-9]/.test(pwd));
}

function validateItem(element, condition) {
    element.className = condition ? "valid" : "invalid";
}

// Validación de coincidencia
function validatePasswordMatch() {
    errorPass.textContent =
        pass1.value === pass2.value ? "" : "Las contraseñas no coinciden";
}

// Mostrar / ocultar contraseña
document.querySelectorAll(".toggle-password").forEach(icon => {
    icon.addEventListener("click", () => {
        const target = document.getElementById(icon.dataset.target);
        
        const isHidden = target.type === "password";
        target.type = isHidden ? "text" : "password";
        
        if (isHidden) {
            icon.classList.remove("bi-eye");
            icon.classList.add("bi-eye-slash");
        } else {
            icon.classList.remove("bi-eye-slash");
            icon.classList.add("bi-eye");
        }
    });
});

// Validación general del formulario
function validateForm() {
    const allValid =
        errorUsername.textContent === "" &&
        errorEmail.textContent === "" &&
        errorPass.textContent === "" &&
        pass1.value.length > 0 &&
        pass2.value.length > 0 &&
        terms.checked;

    submitBtn.disabled = !allValid;
}

// Eventos
username.addEventListener("input", () => {
    validateUsername();
    validateForm();
});

email.addEventListener("input", () => {
    validateEmail();
    validateForm();
});

pass1.addEventListener("input", () => {
    validatePasswordStrength();
    validatePasswordMatch();
    validateForm();
});

pass2.addEventListener("input", () => {
    validatePasswordMatch();
    validateForm();
});

terms.addEventListener("change", validateForm);
