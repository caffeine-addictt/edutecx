
// Hooks
$(() => {
  $('#assignmentForm').on('submit', async e => {
    e.preventDefault();

    const data = Object.fromEntries((new FormData(e.target)).entries());

    if (data.date && (((new Date()).now() - (new Date(data.date)).now()) >= 0)) return renderToast('Date cannot be in the past!', 'danger');

    /**
     * @type {{status: 200; message: string; data: { assignment_id: string }}?}
     */
    const response = await fetch('/api/v1/assignment/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getAccessToken()
      },
      body: JSON.stringify({
        classroom_id: data.Id,
        title: data.Title,
        description: data.Description,
        due_date: data.date ? (new Date(data.date)).now() : null,
        requirements: data.requirements
      })
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
