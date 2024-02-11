
$(() => {
  /** @type {HTMLFormElement} */
  const form = document.querySelector('.needs-validation');

  /** @type {HTMLButtonElement} */
  const submitButton = $('#submit');


  /** 
   * Handle submitting
   * @return {Promise<void>}
   */
  const handleSubmit = async () => {
    submitButton.attr('disabled', true);
    submitButton.text('Processing...');
    renderToast('Processing...', 'info');

    // Trigger hidden form
    const newForm = $('<form><form>');
    newForm.attr('method', 'post');
    newForm.attr('action', '/login')

    $.each(Object.fromEntries((new FormData(form)).entries()), ([key, value]) => {
      const newField = $('<input></input>');

      newField.attr('type', 'hidden');
      newField.attr('name', key);
      newField.attr('value', value);

      newForm.append();
    });

    form.submit();

    submitButton.attr('disabled', false);
    submitButton.text('Login');
    form.classList.remove('was-validated');
  };


  form.addEventListener('submit', async (/** @type {SubmitEvent} */e) => {
    e.preventDefault();
    e.stopPropagation();
    form.classList.add('was-validated');

    if (form.checkValidity()) {
      await handleSubmit();
    };
  }, false);
});
