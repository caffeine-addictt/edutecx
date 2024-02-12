
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
  console.log(responses);

  // Populate HTML
  responses.forEach((res, cart_count) => {
    if (res.status === 200) {
      const newElement = htmlToElement(formatString(deepCopy(itemTemplate), {
        title: res.data.title,
        price: res.data.price,
        id: res.data.id,
        image: res.data.cover_image,
        cart_count: cart_count + 1
      }));
      
      $(newElement).find('#delete-button').on('click', () => {
        removeCartItem(res.data.id, true);
        renderToast(`Removed ${res.data.title}`, "info");
      });
      
      $('#cart__items').append(newElement);
    };
  });

  $('#delete-button').on('click', () => {
    clearCart(true);
    renderToast('Cleared Cart', "info");
  });

  $('#payment-button').on('click', async () => await proceedToPayment());

  if (getCartItems().length === 0) {
    $('#payment-button').addClass('visually-hidden');
    $('#cart__items').append(htmlToElement(
      '<p class="h1 mt-5">No items added into cart.</p>'
    ));
  };

});
