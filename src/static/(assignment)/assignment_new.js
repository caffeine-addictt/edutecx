// Hooks
$(() => {
  $('#assignmentRequirements').on('input', e => {
    e.target.value = e.target.value.replace(/([^0-9:]+)/gi, '');
  });

  $('#assignmentForm').on('submit', async e => {
    e.preventDefault();

    const data = Object.fromEntries(new FormData(e.target).entries());
    console.log(data);

    if (!/^([0-9]+(:[0-9]+)?)$/.test(data.assignmentRequirements)) {
      renderToast('Invalid Page Number(s)!', 'danger');
      return;
    }

    if (data.assignmentDueDate && new Date() >= new Date(data.assignmentDueDate)) {
      renderToast('Date cannot be in the past!', 'danger');
      return;
    }

    try {
      const response = await fetch('/api/v1/assignment/create', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-CSRF-Token': getAccessToken(),
        },
        body: JSON.stringify({
          title: data.assignmentTitle,
          description: data.assignmentDescription,
          due_date: data.assignmentDueDate,
          requirement: data.assignmentRequirements,
        }),
      });

      if (response.ok) {
        const responseData = await response.json();
        renderToast(responseData.message, 'success');
        window.location.href = `/assignment/${responseData.data.assignment_id}`;
      } else {
        const errorData = await response.json();
        renderToast(errorData.message || 'Something went wrong!', 'danger');
      }
    } catch (error) {
      console.error('Error:', error);
      renderToast('An error occurred. Please try again.', 'danger');
    }
  });
});
