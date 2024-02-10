 
 // Hooks
$(() => {
  /** @type {HTMLFormElement} */
  const form = document.querySelector('.needs-validation')

  form.addEventListener('submit', async (/** @type {SubmitEvent} */e) => {
    e.preventDefault();
    form.classList.add('was-validated');

    if (form.checkValidity()) {
      await handleSubmit(e);
      form.classList.remove('was-validated');
      form.reset();
    };
  }, false);
});