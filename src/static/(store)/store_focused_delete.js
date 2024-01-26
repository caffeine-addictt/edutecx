
// On DOM Render
$(() => {
  // Delete Textbook Flow
  $('#delete-textbook-button').on('click', e => {
    $('#delete-textbook-modal').modal('show');
  });

  $('#close-delete-textbook-modal-big').on('click', e => $('#delete-textbook-modal').modal('hide'));
  $('#close-delete-textbook-modal-small').on('click', e => $('#delete-textbook-modal').modal('hide'));

  $('#confirmed-delete-textbook').on('click', async e => {
    $('#delete-textbook-modal').modal('hide');
    renderToast('Deleting textbook...', 'info');
    
    /**
     * Delete textbook
     * @type {{status: number; message: string;}}
     */
    const response = await fetch('/api/v1/textbook/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': getAccessToken()
      },
      body: JSON.stringify({ textbook_id: textbook_id })
    }).then(async res => await res.json());

    if (response.status === 200) {
      renderToast(response.message, 'success');
      window.location = '/store';
    } else {
      renderToast(response.message, 'danger');
    };

});
});


