
// Bootstrap validation and submit hook
$(() => {
  /** @type {HTMLFormElement} */
  const form = document.querySelector('.needs-validation');
  const submitButton = $('#submit');


  /**
  * Handle form submitting
  * @param {SubmitEvent} e
  * @returns {Promise<void>}
  */
  const handleSubmit = async (e) => {
    submitButton.attr('disabled', true);
    submitButton.text('Creating...');
    renderToast('Creating textbook...', 'info');

    const data = new FormData(e.target);

    /**
    * @type {{status: 200; message: string; data: { textbook_id: string }}?}
    */
    const response = await fetch('/api/v1/textbook/create', {
      method: 'POST',
      headers: { 'X-CSRF-Token': getAccessToken() },
      body: data
    }).then(res => res.json()).catch(e => console.log(e));

    if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
    else {
      renderToast(response.message, 'success');
      window.location.href = `/store`;
    };

    submitButton.attr('disabled', false);
    submitButton.text('Create');
    form.classList.remove('was-validated');
  };


  // Handle submitting
  form.addEventListener('submit', async e => {
    e.preventDefault();
    form.classList.add('was-validated');

    if (form.checkValidity()) {
      await handleSubmit(e);
    };
  }, false);
});
