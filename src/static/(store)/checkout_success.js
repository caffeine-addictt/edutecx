
/**
 * Hit sale endpoint
 * @param {string} sessionID
 * @returns {Promise<void | APIJSON<StripeSessionStatus>>}
 */
const checkoutStatus = async (sessionID) => await fetch('/api/v1/checkout/status', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-TOKEN': getAccessToken()
  },
  body: JSON.stringify({ session_id: sessionID })
}).then(res => res.json()).catch(err => console.log(err));




$(async () => {
  const sessionID = window.location.search.split('session_id=')[1];

  if (!sessionID) {
    renderToast('Invalid session ID', 'error');
    // Render bad session id
    return;
  };

  let counter = 0;
  while (true) {
    const response = await checkoutStatus(sessionID);

    if (response?.status !== 200) {
      renderToast(response ? response.message : 'Something went wrong!', 'error');

      await wait( (2**counter + Math.random()) * 1000 );
      counter++;

      continue;
    };

    // Render success
    break;
  };
});
