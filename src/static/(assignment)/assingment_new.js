// Hooks
$(() => {
  $('#assignmentForm').on('submit', async e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(e.target).entries());
    console.log(data);

    /**
     * @type {{status: number; message: string; data: { _id: string }?}}
     */
    const response = await fetch('/api/v1/assignment/create', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'X-CSRF-Token': getAccessToken()
      },
      body: JSON.stringify({
        title: data.assignmentTitle,
        description: data.assignmentDescription,
        classroom: data.classroom,
        due_date: data.assignmentDueDate,
        requirement: data.assignmentRequirements
      })
    }).then(res => {
      if (res.ok) {
        return res.json();
      }
    });

    if (!response || response.status !== 200) {
      renderToast(response ? response.message : 'Something went wrong!', 'danger');
    } else {
      renderToast(response.message, 'success');
      window.location.href = `/assignments/${response.data._id}`;
    }
  });
});