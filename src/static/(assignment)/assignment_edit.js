// On DOM Render
$(() => {
  // Update Assignment Details Flow
  $('#assignmentForm').on('submit', async e => {
    e.preventDefault();
    renderToast('Updating assignment...', 'info');

    const data = Object.fromEntries((new FormData(e.target)).entries());
    console.log(data);

    const response = await fetch('/api/v1/assignment/edit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getAccessToken(),
      },
      body: JSON.stringify({
        title: data.assignmentTitle,
        description: data.assignmentDescription,
        classroom: data.classroom,
        due_date: data.assignmentDueDate,
        requirement: data.assignmentRequirements,
      }),
    }).then(res => {
      if (res.ok) {
        return res.json();
      }
    });

    if (!response || response.status !== 200) {
      renderToast(response ? response.message : 'Something went wrong!', 'danger');
    } else {
      renderToast(response.message, 'success');
      window.location.href = `/assignment/${assignment_id}`;
    }
  });

  // Delete Assignment Flow
  $('#delete-assignment-button').on('click', e => {
    $('#delete-assignment-modal').modal('show');
  });

  $('#close-delete-assignment-modal-big').on('click', e => $('#delete-assignment-modal').modal('hide'));
  $('#close-delete-assignment-modal-small').on('click', e => $('#delete-assignment-modal').modal('hide'));

  $('#confirmed-delete-assignment').on('click', async e => {
    $('#delete-assignment-modal').modal('hide');
    renderToast('Deleting assignment...', 'info');

    const response = await fetch('/api/v1/assignment/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': getAccessToken(),
      },
      body: JSON.stringify({ assignment_id: assignment_id }),
    }).then(async res => await res.json());

    if (response.status === 200) {
      renderToast(response.message, 'success');
      window.location = '/assignments';
    } else {
      renderToast(response.message, 'danger');
    }
  });
});

