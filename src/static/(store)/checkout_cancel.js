
/**
 * Checkout Cancel
 * @param {string} sessionID
 * @returns {Promise<{status: number; message: string;}>}
 */
const checkoutCancel = async (sessionID) => await fetch('/api/v1/checkout/cancel', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({ session_id: sessionID })
  }).then(async res => await res.json());




$(async () => {
  const sessionID = window.location.search.split('session_id=')[1];

  if (!sessionID) {
    renderToast('Invalid session ID', 'error');
    // Render bad session id
    return;
  }

  
  let counter = 0;
  while (true) {
    const response = await checkoutCancel(sessionID);

    if (response.status !== 200) {
      renderToast(response.message, 'error');

      await wait( (2**counter + Math.random()) * 1000 );
      counter++;

      continue;
    };
    
    // Render success
    break;
  }
});

