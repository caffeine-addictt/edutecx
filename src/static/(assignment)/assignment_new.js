
// Hooks
$(() => {
  const classroom_id = (new URL(location.href)).searchParams.get('classroomID');
  const submitButton = $('#submit');

  $('#assignmentForm').on('submit', async e => {
    e.preventDefault();
    e.stopPropagation();

    submitButton.attr('disabled', true);
    submitButton.text('Creating...');
    renderToast('Creating assignment...', 'info');

    const data = Object.fromEntries((new FormData(e.target)).entries());
    if (data.due_date && (((new Date()).getTime() - (new Date(data.due_date)).getTime()) >= 0)) return renderToast('Date cannot be in the past!', 'danger');
    data.due_date = data.due_date ? (new Date(data.due_date)).getTime() / 1000 : 'infinity';


    /**
     * @type {{status: 200; message: string; data: { assignment_id: string }}?}
     */
    const response = await fetch('/api/v1/assignment/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getAccessToken()
      },
      body: JSON.stringify({ ...data, classroom_id: classroom_id })
    }).then(res => res.json().catch(e => console.log(e)));

    if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
    else {
      renderToast(response.message, 'success');
      window.location.href = `/assignments/${response.data.assignment_id}`;
    };

    submitButton.attr('disabled', false);
    submitButton.text('Create Assignment');
  });
});
