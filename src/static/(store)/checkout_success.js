
/**
 * Hit sale endpoint
 * @param {string} sessionID
 * @returns {Promise<void | APIJSON<StripeSessionStatus>>}
 */
const checkoutStatus = async (sessionID) => await fetch('/api/v1/stripe/status', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
    'X-CSRF-TOKEN': getAccessToken()
  },
  body: JSON.stringify({ session_id: sessionID })
}).then(res => res.json()).catch(err => console.log(err));




$(async () => {
  const fetchingContainer = $('#fetching__container');
  const successContainer = $('#success__container');
  const errorContainer = $('#error__container');
  const retryText = $('#retry_text');

  const searchParams = (new URL(window.location.href)).searchParams;
  const ses_id = searchParams.get('session_id')?.toLowerCase();


  /**
   * Control state
   * @param {'Success' | 'Error' | 'Fetching' | 'Hidden'} state
   * @returns {void}
   */
  const stateController = (state) => {
    console.log(fetchingContainer)
    if (state === 'Fetching') fetchingContainer.removeClass('visually-hidden'); else fetchingContainer.addClass('visually-hidden');
    if (state === 'Success') successContainer.removeClass('visually-hidden'); else successContainer.addClass('visually-hidden');
    if (state === 'Error') errorContainer.removeClass('visually-hidden'); else errorContainer.addClass('visually-hidden');
  };
  stateController('Hidden');


  if (!ses_id) {
    errorContainer.find('#error_text').text('No session ID found in URL');
    stateController('Error');
    return;
  };


  let counter = localStorage.getItem('cs_counter') || 0;
  while (true) {
    renderToast('Checking status...', 'info');
    stateController('Fetching');

    const response = await checkoutStatus(ses_id);

    if (response?.data?.paid) {
      renderToast('Success', 'success');
      stateController('Success');
      break;
    }

    if (!response || response.status !== 200) {
      renderToast(response ? response.message : 'Something went wrong!', 'danger');
      errorContainer.find('#error_text').text(response?.message ?? 'Something went wrong!');
      stateController('Error');
    };

    const start = (new Date()).getTime();
    const maxWait = (2 ** counter) + 5 + Math.random();
    localStorage.setItem('cs_counter', ++counter);

    while (true) {
      const diff = ((new Date()).getTime() - start) / 1000;
      if (diff > maxWait) break;

      retryText.text(`Retrying in ${Math.round(maxWait - diff, 2)}s...`);
      await wait(1000);
    };
  };
});
