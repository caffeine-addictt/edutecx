
// On DOM Render
$(() => {
  $('#delete-textbook-button').on('click', async () => {
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
      window.location.href = `/store`;
    }
    else renderToast(response.message, 'danger');
  });
});
