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
  if (!inArray(category, ['info', 'success', 'danger'])) {
    throw new Error(`${category} is an invalid category`);
  };

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
  const toast = htmlToElement(formatString(template, { message: message }));

  
  // Time logic
  let interval;
  const start = new Date();

  interval = setInterval(() => {
    if ($(toast)) {
      $(toast).find('#time-counter').text( Math.round(((new Date()).getTime() - start.getTime()) / 1000) + 's Ago');
    }
    else {
      clearInterval(interval);
    }
  }, 1000);


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
 * @returns {Promise<Array.<string | Array.<'info' | 'success' | 'danger', string>>>}
 */
const getNotifications = async () => {

  /**
   * Fetched notifications
   * @type {{
   *   status: 200;
   *   message: string;
   *   data: Array.<string | ['info' | 'success' | 'danger', string]>;
   * } | null}
   */
  const data = await fetch('/api/v1/notify/get')
    .then(r => {
      if (r.ok) {
        return r.json();
      };
    });

  if (!data || (data.status !== 200)) return [
    ['danger', 'Failed to fetch notifications']
  ];

  return data.data
};




/**
 * Render notifications
 * @returns {Promise<void>}
 */
const renderNotifications = async () => {
  const notifications = await getNotifications();
  console.log(notifications);

  for (const notification of notifications) {
    const [category, message] = Array.isArray(notification) ? notification : [null, notification];
    renderToast(message, category);
  };
};




$(async () => {
  await renderNotifications();
});
