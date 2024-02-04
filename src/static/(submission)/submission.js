
// Add hooks
$(() => {
  var isSubmitting = false;

  /** @type {HTMLFormElement} */
  const form = $('#newCommentForm')

  form.on('submit', async (/** @type {SubmitEvent} */e) => {
    if (isSubmitting) return;
    isSubmitting = true;

    e.preventDefault();
    e.stopPropagation();
    renderToast('Processing...', 'info');

    // Handle Validation
    form.classList.add('was-validated');
    if (!form.checkValidity()) {
      isSubmitting = false;
      return;
    };

    // Handle Submit
    /** @type {{[key: string]: string}} */
    const data = Object.fromEntries((new FormData(form)).entries());
    data.submission_id = submission_id;

    const response = await fetch('/api/v1/comment/create', {
      method: 'POST',
      headers: {
        'X-CSRF-Token': getAccessToken(),
        'Content-Type': 'application/json'
      },
      body: data
    });

    if (response.ok) {
      renderToast('Commented!', 'success');
      window.location.reload();
    } else {
      try {
        /** @type {APIJSON<null>} */
        const json = await response.json();
        renderToast(json.message, 'danger');
      } catch {
        renderToast('Something went wrong!', 'danger');
      };
    };

    form.reset();
    isSubmitting = false;
  });
});
