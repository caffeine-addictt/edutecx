
/**
 * Toast render starting time in milliseconds From `Date.getTime()`
 * @typedef {number} toastStartTime
*/


/**
 * Toast message string
 * @typedef {string} toastMessage
*/


/**
 * Supported toast categories
 * @typedef {'info' | 'success' | 'danger'} toastCategory
*/


/**
 * @typedef {Object} toastData
 * @property {string} title
 * @property {string} message
 * @property {string} type
 */


/**
 * Toast format saved in queue
 * @typedef {[toastCategory, toastMessage, toastStartTime?]} toastQueueEntry
 */
