
/**
 * Render Cancel Modal Error
 * @param {string} message
 * @returns {void}
 */
const renderCancelModalError = (message) => {
  $('#cancel-subscription-error').text(message);
  $('#cancel-subscription-error-parent').removeClass('d-none');
};


/**
 * Clear Cancel Modal Error
 * @returns {void}
 */
const clearCancelModalError = () => {
  $('#cancel-subscription-error').text('');
  $('#cancel-subscription-error-parent').addClass('d-none');
};


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




// On Render
$(() => {
  /** @type {JQuery<HTMLButtonElement>} */
  const upgradeButton = $('#upgrade-subscription');

  /** @type {JQuery<HTMLButtonElement>} */
  const cancelButton = $('#cancel-subscription');
  /** @type {JQuery<HTMLDivElement>} */
  const cancelSubscriptionModal = $('#cancel-subscription-modal');




  // Buttons
  upgradeButton.on('click', async () => await getSubscription('Unlimited'));
  cancelButton.on('click', () => cancelSubscriptionModal.modal('show'));




  // Modal hooks
  cancelSubscriptionModal.find('#confirmed-cancel-subscription').on('click', async () => {
    let closeModal = true;

    try {
      const response = await fetch('/api/v1/stripe/cancel-subscription', {
        method: 'POST',
        headers: {
          'X-CSRF-Token': getAccessToken(),
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          subscription_id: subID
        })
      }).then(res => res.json()).catch(err => console.log(err));

      if (!response || response.status !== 200) {
        renderToast(response ? response.message.toString() : 'Something went wrong!', 'danger');
        renderCancelModalError(response ? response.message.toString() : 'Something went wrong!');
        closeModal = false;
      }
      else {
        renderToast(response.message, 'success');
        closeModal = true;
      };
    }
    finally {
      if (closeModal) {
        cancelSubscriptionModal.modal('hide');
        clearCancelModalError();
      }
    };
  })
  cancelSubscriptionModal.find('#close-cancel-subscription-modal-big').on('click', () => {
    cancelSubscriptionModal.modal('hide');
    clearCancelModalError();
  });
  cancelSubscriptionModal.find('#close-cancel-subscription-modal-small').on('click', () => {
    cancelSubscriptionModal.modal('hide');
    clearCancelModalError();
  });
});
