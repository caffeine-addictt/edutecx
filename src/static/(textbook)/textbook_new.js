
// Hooks
$(() => {
  // Bootstrap 5 Form Validation
  (function () {
    'use strict'
  
    // Fetch all the forms we want to apply custom Bootstrap validation styles to
    var forms = document.querySelectorAll('.needs-validation')
  
    // Loop over them and prevent submission
    Array.prototype.slice.call(forms)
      .forEach(function (form) {
        form.addEventListener('submit', function (event) {
          if (!form.checkValidity()) {
            event.preventDefault()
            event.stopPropagation()
          }
  
          form.classList.add('was-validated')
        }, false)
      })
  })()

  $('#textbookForm').on('submit', async e => {
    e.preventDefault();

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
  });
});
