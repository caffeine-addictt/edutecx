
/**
 * Generate session and redirect to checkout page
 * @returns {Promise<void>}
 */
const proceedToPayment = async () => {
  renderToast('Preparing our servers...', 'success');

  /** @type {string[]} */
  const items = getCartItems();

  /**
   * @type {{
   *   status : 200;
   *   message: string;
   *   data: {
   *     public_key: string;
   *     session_id: string;
   *    }
   *  } | {
   *    status : 404;
   *    message: string;
   *  }}
   */
  const response = await fetch('/api/v1/stripe/create-checkout-session', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({ cart: items })
  }).then(async res => await res.json());

  if (response.status === 200) {
    renderToast('Redirecting to payment...', 'success');
    const stripe = Stripe(response.data.public_key);
    stripe.redirectToCheckout({ sessionId: response.data.session_id });
  }
  else renderToast(response.message, 'danger');
};




$(async () => {
  /** @type {string[]} */
  const items = getCartItems();
  
  
  /**
   * @type {Array.<
   *   Promise<{
   *     status : 200;
   *     message: string;
   *     data: {
   *       id         : string;
   *       author_name: string;
   *       author_id  : string;
   *       title      : string;
   *       description: string;
   *       categories : string[];
   *       price      : number;
   *       discount   : number;
   *       uri        : string;
   *       status     : string;
   *       cover_image: string?;
   *       created_at : number;
   *       updated_at : number;
   *     };
   *   } | {
   *    status : 404;
   *    message: string;
   *   }>
   *>}
   */
  const queryPayloads = [];

  for (const itemID of items) {
    queryPayloads.push(
      fetch(`/api/v1/textbook/get?textbook_id=${itemID}`, {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' }
      }).then(async res => await res.json()));
  }

  /**
   * @type {Array.<{
   *    status : 200;
   *    message: string;
   *    data: {
   *      id         : string;
   *      author_name: string;
   *      author_id  : string;
   *      title      : string;
   *      description: string;
   *      categories : string[];
   *      price      : number;
   *      discount   : number;
   *      uri        : string;
   *      status     : string;
   *      cover_image: string?;
   *      created_at : number;
   *      updated_at : number;
   *    };
   *  } | {
   *    status : 404;
   *    message: string;
   *  }
   * }>}
   */
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
