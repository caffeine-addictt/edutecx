$('#classroomForm').on('submit', async e => {
  e.preventDefault();
  const data = Object.fromEntries((new FormData(e.target)).entries())
  console.log(data)
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
  }).then(async res => await res.json());

  if (response.status !== 200) renderToast(response.message, 'danger');
  else {
    renderToast(response.message, 'success');
    setTimeout(() => window.location.href = `/classrooms/${response.data.classroom_id}`, 500);
  };
});