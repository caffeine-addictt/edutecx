
// Hooks
$(() => {
  $('#textbookForm').on('submit', async e => {
    e.preventDefault();

    const data = Object.fromEntries((new FormData(e.target)).entries());
    console.log(data);

    /**
     * @type {{status: 200; message: string; data: { assignment_id: string }}?}
     */
    const response = await fetch('/api/v1/assignment/create', {
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
      window.location.href = `/assignment/${response.data.assignment_id}`;
    };
  });
});
