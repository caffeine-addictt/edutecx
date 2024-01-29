
/**
 * Generate session and redirect to checkout page
 * @returns {Promise<void>}
 */
const proceedToPayment = async () => {
  renderToast('Preparing our servers...', 'success');

  /** @type {string[]} */
  const items = getCartItems();

  /**
   * @type {APIJSON<StripeSessionData>}
   */
  const response = await fetch('/api/v1/stripe/create-checkout-session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({ cart: items })
  }).then(res => res.json()).catch(err => console.log(err));

  if (response?.status === 200) {
    renderToast('Redirecting to payment...', 'success');
    const stripe = Stripe(response.data.public_key);
    stripe.redirectToCheckout({ sessionId: response.data.session_id });
  }
  else renderToast(response.message, 'danger');
};




$(async () => {
  /** @type {string[]} */
  const items = getCartItems();
  
  
  /** @type {Array.<Promise<APIJSON<TextbookGetData>>>} */
  const queryPayloads = [];

  for (const itemID of items) {
    queryPayloads.push(
      fetch(`/api/v1/textbook/get?textbook_id=${itemID}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      }).then(async res => await res.json()));
  }

  /** @type {Array.<APIJSON<TextbookGetData>>} */
  const responses = await Promise.all(queryPayloads);

  
  // Populate HTML
  responses.forEach(res => {
    if (res.status === 200) {
      $('#cart__items').append(
        `<div> <a href="/store/${res.data.id}">${res.data.title}</a> </div>`
      );
    }
  });

});
