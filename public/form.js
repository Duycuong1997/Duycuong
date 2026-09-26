'use strict';

// Wires the shared validation rules (window.RegistrationValidation) to the form.
(function () {
  const form = document.getElementById('register-form');
  if (!form) return;

  const fieldMap = {
    lastName: 'L_NAME',
    firstName: 'F_NAME',
    lastKana: 'L_KANA',
    firstKana: 'F_KANA',
    email: 'EMAIL',
  };

  function readForm() {
    return {
      lastName: form.L_NAME.value,
      firstName: form.F_NAME.value,
      lastKana: form.L_KANA.value,
      firstKana: form.F_KANA.value,
      email: form.EMAIL.value,
    };
  }

  function clearErrors() {
    form.querySelectorAll('[data-error-for]').forEach((el) => {
      el.textContent = '';
    });
  }

  function showErrors(errors) {
    Object.entries(errors).forEach(([key, message]) => {
      const el = form.querySelector(`[data-error-for="${key}"]`);
      if (el) el.textContent = message;
    });
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    clearErrors();
    document.getElementById('success-msg').hidden = true;

    const { valid, errors } = window.RegistrationValidation.validateRegistration(readForm());

    if (valid) {
      document.getElementById('success-msg').hidden = false;
    } else {
      showErrors(errors);
      // Focus the first field with an error for accessibility.
      const firstKey = Object.keys(errors)[0];
      const input = document.getElementById(fieldMap[firstKey]);
      if (input) input.focus();
    }
  });
})();
