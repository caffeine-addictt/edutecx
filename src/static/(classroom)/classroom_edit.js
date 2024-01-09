const handleDeletePress = async e => {

  const response = await fetch('/api/v1/classroom/delete', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', 'X-CSRF-TOKEN': getAccessToken() },
    body: JSON.stringify({ classroom_id: window.location.href.split("/")[-1] })
  }).then(res => {
    if (res.ok) {
      return res.json();
    };
  });

  if (!response || response.status !== 200) {
    // Show error message
    // Here using jQuery to enable all other buttons
  }
  else {
    // Show success message
    window.location.href = '/classrooms';
  };
};
// On DOM Render
$(() => {
  $('#delete-class-button').on('click', handleDeletePress)
});