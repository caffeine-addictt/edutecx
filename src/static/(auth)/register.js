
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

    const data = new FormData(form);

    const response = await fetch('/api/v1/register', {
      method: 'POST',
      body: data
    }).then(res => res.json()).catch(e => console.log(e));

    if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
    else {
      renderToast(response.message, 'success');
      window.location.href = '/login';
    };

    submitButton.attr('disabled', false);
    submitButton.text('Submit');
    form.classList.remove('was-validated');
  };


  form.addEventListener('submit', async (/** @type {SubmitEvent} */e) => {
    e.preventDefault();
    form.classList.add('was-validated');

    if (form.checkValidity()) {
      await handleSubmit();
    };
  }, false);
});

