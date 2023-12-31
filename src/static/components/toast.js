// let infoTemplate = '';
// let successTemplate = '';
// let dangerTemplate = '';

/**
 * Render a toast
 * @param {string} message - The message to display
 * @param {'success' | 'info' | 'danger'} category - The category of the toast
 * @returns {void}
 */
const renderToast = (message, category) => {
  let template = '';
  if (category === 'info') {
    template = deepCopy(infoTemplate);
  }
  else if (category === 'success') {
    template = deepCopy(successTemplate);
  }
  else if (category === 'danger') {
    template = deepCopy(dangerTemplate);
  };


  /** @type {HTMLElement} */
  const toast = htmlToElement(formatString(template, { '{message}': message }));

  // Add to toast container
  $('#toast-stack-container').append(toast);

  // Show toast
  $(toast).toast('show');


  // Add hidden listener to cleanup on finish
  const observer = new MutationObserver(mutations => {
    for (const e of mutations) {
      if (e.target.classList.contains('hide')) {
        toast.remove();
      };
    };
  });

  observer.observe(toast, {
    attributes: true,
    attributeFilter: ['class'],
    childList: false,
    characterData: false
  });
}




/**
 * Fetch notifications
 * [category, message] or message
 *
 * @returns {Promise<{
 *   message: string
 *   status: 200
 *   data: Array.<
 *     string | Array.<'info' | 'success' | 'danger', string>>
 *   >
 * | {
 *     status: 404
 *     message: string
 *   }
 * >}
 */
const getNotifications = async () => {
  return fetch('/api/v1/notify/get')
    .then(r => r.json());
};




/**
 * Render notifications
 * @returns {Promise<void>}
 */
const renderNotifications = async () => {
  const notifications = await getNotifications();
  console.log(notifications);

  if (notifications.status === 200) {
    console.log(notifications.data);
    for (const notification of notifications.data) {
      const [category, message] = Array.isArray(notification) ? notification : [null, notification];
      renderToast(message, category);
    };
  };
};




$(async () => {
  await renderNotifications();
});
