
/**
 * Handle form submiting
 * @param {SubmitEvent} e
 * @returns {Promise<void>}
 */
const handleSubmit = async (e) => {
  const data = new FormData(e.target);
  console.log(data);

  /**
   * @type {{status: 200; message: string; data: { textbook_id: string }}?}
   */
  const response = await fetch('/api/v1/textbook/create', {
    method: 'POST',
    headers: { 'X-CSRF-Token': getAccessToken() },
    body: data
  }).then(res => {
    if (res.ok) {
      return res.json();
    };
  });

  if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
  else {
    renderToast(response.message, 'success');
    window.location.href = `/store`;
  };
};


// Bootstrap validation and submit hook
$(() => {
  /** @type {HTMLFormElement} */
  const form = document.querySelector('.needs-validation')
  form.addEventListener('submit', async e => {
    e.preventDefault();
    form.classList.add('was-validated');

    if (form.checkValidity()) {
      handleSubmit(e);
    };
  }, false);
});
