
// On DOM Render
$(() => {

  // Update Class Details Flow
  
  $('#classroomForm').on('submit', async e => {
    e.preventDefault();
    renderToast('Updating class...', 'info');

    const data = Object.fromEntries((new FormData(e.target)).entries())
    console.log(data)

    /**
     * @type {{status: 200; message: string; data: { classroom_id: string }}?}
     */
    const response = await fetch('/api/v1/classroom/edit', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getAccessToken()
      },
      body: JSON.stringify({
        classroom_id: classroom_id,
        title: data.Title,
        description: data.Description,
        invite_enabled: data['Invite Enabled'] ? 'y' : 'n'
      })
    }).then(res => {
      if (res.ok) {
        return res.json();
      };
    });

    if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
    else {
      renderToast(response.message, 'success');
      window.location.href = `/classrooms/${classroom_id}`;
    };
  })


  // Delete Class Flow
  $('#delete-class-button').on('click', e => {
    $('#delete-class-modal').modal('show');
  });

  $('#close-delete-class-modal-big').on('click', e => $('#delete-class-modal').modal('hide'));
  $('#close-delete-class-modal-small').on('click', e => $('#delete-class-modal').modal('hide'));

  $('#confirmed-delete-class').on('click', async e => {
    $('#delete-class-modal').modal('hide');
    renderToast('Deleting class...', 'info');
    
    /**
     * Delete class
     * @type {{status: number; message: string;}}
     */
    const response = await fetch('/api/v1/classroom/delete', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-TOKEN': getAccessToken()
      },
      body: JSON.stringify({ classroom_id: classroom_id })
    }).then(async res => await res.json());

    if (response.status === 200) {
      renderToast(response.message, 'success');
      window.location = '/classrooms';
    } else {
      renderToast(response.message, 'danger');
    };

  });
});
