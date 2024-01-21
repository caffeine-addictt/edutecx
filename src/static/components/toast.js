// let infoTemplate = '';
// let successTemplate = '';
// let dangerTemplate = '';


const maxToasts = 3; // Maximum number of toasts to show at any one time
const minDisplayTime = 2000; // 2 seconds
const defaultLiveTime = 5000; // 5 seconds
const toastExpiryTime = 1000 * 60 * 5; // 5 minutes




/**
 * Fetch Toast Queue
 * @returns {toastQueueEntry[]}
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
 * @param {toastQueueEntry} toastQueueEntry
 * @returns {void}
 */
const addToToastQueue = (toastQueueEntry) => {
  let queue = getToastQueue();
  queue.push(toastQueueEntry);
  localStorage.setItem('toastQueue', JSON.stringify(queue));
};


/**
 * Remove first toast found in queue
 * @param {toastQueueEntry} toastQueueEntry
 * @returns {void}
 */
const removeFromToastQueue = (toastQueueEntry) => {
  let queue = getToastQueue();
  queue.some((toastItem, index) => {
    if (arrayIsEqual(toastItem, toastQueueEntry)) {
      queue.splice(index, 1);
      localStorage.setItem('toastQueue', JSON.stringify(queue));
      return true;
    };
  });
};




/**
 * Render a toast
 * @param {toastMessage} message - The message to display
 * @param {toastCategory} category - The category of the toast
 * @param {number?} displayTime - The time to display the toast
 * @param {boolean} [initialRender=false] - Whether this is the initial render
 * @returns {void}
 */
const renderToast = (message, category, displayTime, initialRender = false) => {
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


  
  
  // Time logic
  let interval;
  const start = new Date();
  const liveTime = displayTime || defaultLiveTime;
  
  // Add to toast queue (in case of reload)
  /** @type {toastQueueEntry} */
  const savedPayload = [category, message, displayTime || start.getTime()]
  if (!initialRender || (initialRender && !inArray(savedPayload, getToastQueue()))) {
    addToToastQueue(savedPayload);
  };

  console.log(savedPayload)


  /** @type {HTMLElement} */
  const toast = htmlToElement(formatString(template, { message: message, liveTime: liveTime }));

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
        removeFromToastQueue(savedPayload);
      };
    };
  });

  observer.observe(toast, {
    attributes: true,
    attributeFilter: ['class'],
    childList: false,
    characterData: false
  });
};




/**
 * Fetch notifications
 * [category, message] or message
 *
 * @returns {Promise<toastAPIGet>}
 */
const getNotifications = async () => {

  /**
   * Fetched notifications
   * @type {APIJSON<toastAPIGet> | null}
   */
  const data = await fetch('/api/v1/notify/get')
    .then(r => {
      if (r.ok) {
        return r.json();
      };
    });
  
  const httpNotif = (!data || (data.status !== 200)) ? [['danger', 'Failed to fetch notifications']] : data.data;

  return new Array(...httpNotif, ...getToastQueue());
};




/**
 * Fetches notifications and renders toasts
 * * Expired toasts are dropped
 * * Unrendered or interupted toasts are re-rendered, lasting between `minDisplayTime` and `defaultLiveTime`
 * @returns {Promise<void>}
 */
const renderNotifications = async () => {
  const notifications = await getNotifications();
  console.log('Rendering toasts:', notifications);

  for (const notification of notifications) {
    const [category, message, startTime] = Array.isArray(notification) ? notification : [null, notification];

    // Clean from queue
    removeFromToastQueue([category, message, startTime]);

    // Add dropping toast logic
    const passedTime = startTime ? (new Date()).getTime() - startTime : 0;
    if (startTime && (passedTime > toastExpiryTime)) {
      console.log('Expiry time reached, dropping toast');
      continue;
    };

    // Wait for existing toasts to run out
    while ($(document).find('.toast').length >= maxToasts) {
      await wait(1000);
    };

    // Introduce artificial stagger (max 0.5s)
    await wait(Math.random() * 500);

    renderToast(
      message,
      category,
      Math.min(Math.max(defaultLiveTime - passedTime, minDisplayTime), defaultLiveTime),
      true
    );
  };
};




$(async () => await renderNotifications());
