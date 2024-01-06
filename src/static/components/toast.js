// let infoTemplate = '';
// let successTemplate = '';
// let dangerTemplate = '';


/**
 * Fetch Toast Queue
  * @returns {['info' | 'success' | 'danger' | null | string, string][]}
  */
const getToastQueue = () => {
  return JSON.parse(localStorage.getItem('toastQueue')) || new Array();
};


/**
 * Clear Toast Queue
 * @returns {void}
 */
const clearToastQueue = () => {
  localStorage.removeItem('toastQueue');
};


/**
  * Add item to toast queue
  * @param {['info' | 'success' | 'danger' | null | string, string]} toastData
  * @returns {void}
  */
const addToToastQueue = (toastData) => {
  let queue = getToastQueue();
  queue.push(toastData);
  localStorage.setItem('toastQueue', JSON.stringify(queue));
};


/**
 * Remove first toast found in queue
 * @param {['info' | 'success' | 'danger' | null | string, string]} toastData
 * @returns {void}
 */
const removeFromToastQueue = (toastData) => {
  let queue = getToastQueue();
  queue.some((toastItem, index) => {
    if (arrayIsEqual(toastItem, toastData)) {
      queue.splice(index, 1);
      localStorage.setItem('toastQueue', JSON.stringify(queue));
      return true;
    };
  });
};




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


  // Add to toast queue (in case of reload)
  addToToastQueue([category, message]);


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

        // Remove from queue
        removeFromToastQueue([category, message]);
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

  const httpNotif = (!data || (data.status !== 200)) ? [['danger', 'Failed to fetch notifications']] : data.data;
  console.log(getToastQueue());

  return new Array(...httpNotif, ...getToastQueue());
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
