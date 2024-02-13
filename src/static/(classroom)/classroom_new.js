
// Hooks
$(() => {
  $('#classroomForm').on('submit', async e => {
    e.preventDefault();

    const data = Object.fromEntries((new FormData(e.target)).entries())
    console.log(data)

    /**
     * @type {{status: 200; message: string; data: { classroom_id: string }}?}
     */
    const response = await fetch('/api/v1/classroom/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getAccessToken()
      },
      body: JSON.stringify({
        title: data.Title,
        description: data.Description,
        invite_enabled: data['Invite Enabled'] || 'n'
      })
    }).then(res => res.json()).catch(err => console.log(err));

    if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
    else {
      renderToast(response.message, 'success');
      window.location.href = `/classrooms/${response.data.classroom_id}`;
    };
  });
});
