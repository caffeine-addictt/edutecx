
// On DOM Render
$(async () => {
  /** @type {JQuery<HTMLParagraphElement>} */
  const activeUsers = $('#active-users');

  /** @type {JQuery<HTMLParagraphElement>} */
  const totalRevenue = $('#total-revenue');

  /** @type {JQuery<HTMLParagraphElement>} */
  const totalTextbooks = $('#total-textbooks');


  /** @type {APIJSON<AdminStatsGetData> | void} */
  const response = await fetch('/api/v1/admin/stats', {
    headers: { 'X-CSRF-Token': getAccessToken() }
  }).then(res => res.json()).catch(err => console.log(err));

  if (!response || response.status !== 200) renderToast(response ? response.message : 'Something went wrong!', 'danger');
  else {
    activeUsers.text(response.data.user_count);
    totalRevenue.text(`$${response.data.revenue}`);
    totalTextbooks.text(response.data.textbook_count);
  };
});
