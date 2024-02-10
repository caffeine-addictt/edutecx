
/**
 * Handle submit
 * @param {HTMLFormElement} form
 * @returns {Promise<void>}
 */
const handleSubmit = async (form) => {
  const submitButton = $('#submit');
  submitButton.attr('disabled', true);
  submitButton.text('Submitting...');
  renderToast('Submitting...', 'info');

  const data = new FormData(form);

  const response = await fetch('/contact-us', {
    method: 'POST',
    headers: { 'X-CSRF-Token': getAccessToken() },
    body: data
  }).then(res => res.json()).catch(e => console.log(e));

  if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
  else {
    renderToast(response.message, 'success');
    form.classList.remove('was-validated');
    form.reset();
  };

  submitButton.attr('disabled', false);
  submitButton.text('Submit');
};


// Hooks
$(() => {
  /** @type {HTMLFormElement} */
  const form = document.querySelector('.needs-validation')

  form.addEventListener('submit', async (/** @type {SubmitEvent} */e) => {
    e.preventDefault();
    e.stopPropagation();
    form.classList.add('was-validated');

    if (form.checkValidity()) {
      await handleSubmit(form);
    };
  }, false);
});
