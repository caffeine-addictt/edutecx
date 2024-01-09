
// Hooks
$(() => {
  $('#textbookForm').on('submit', async e => {
    e.preventDefault();

    const data = Object.fromEntries((new FormData(e.target)).entries());
    console.log(data);

    if (!/^([0-9]+(:[0-9]+)?)$/.test(data.requirements)) return renderToast('Invalid Page Number(s)!', 'danger');
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
        author: user_id,
        title: data.Title,
        description: data.Description,
        price: data.Price,
        discount: data.Discount
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
