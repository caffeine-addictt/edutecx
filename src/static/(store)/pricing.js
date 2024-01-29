
/**
 * Hit Stripe Subscription endpoint
 * @param {'Unlimited'} tierType
 */
const getSubscription = async (tierType) => {
  if (!inArray(tierType, ['Unlimited'])) {
    return renderToast(`${tierType} is an invalid tier`, 'danger');
  };


  renderToast('Preparing our servers...', 'success');

  /**
   * @type {APIJSON<StripeSessionData>}
   */
  const response = await fetch('/api/v1/stripe/create-subscription-session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({ tier: tierType })
  }).then(res => res.json()).catch(err => console.log(err));

  if (response?.status === 401) window.location.href = '/login?callbackURI=' + encodeURIComponent(window.location.pathname);

  if (!response || response?.status !== 200) {
    renderToast(response ? response.message.toString() : 'Something went wrong!', 'danger');
    return;
  };
  try {
    renderToast('Redirecting to payment...', 'success');
    const stripe = Stripe(response.data.public_key);
    stripe.redirectToCheckout({ sessionId: response.data.session_id });
  }
  catch (err) {
    console.log(err);
    renderToast('Failed to redirect to stripe!', 'danger');
  };
};



/** Hooks */
$(() => {
  $('#unlimited_button').on('click', async e => await getSubscription('Unlimited'));
});
