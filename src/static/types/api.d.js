
/**
 * @typedef {Array.<toastMessage & toastData>} toastAPIGet
 */


/**
 * @typedef {Object} StripeSessionData
 * @property {string} session_id
 * @property {string} public_key
 */


/**
 * @typedef {Object} StripeSessionStatus
 * @property {string} user_id
 * @property {string} transaction_id
 * @property {number} total_cost
 * @property {number} paid_at
 * @property {number} created_at
 * @property {boolean} paid
 */


/**
 * @typedef {Object} TextbookGetData
 * @property {string} id
 * @property {string} author_id
 * @property {string} title
 * @property {string} description
 * @property {string[]} categories
 * @property {number} price
 * @property {string} uri
 * @property {'Available' | 'Unavailable' | 'DMCA'} status
 * @property {string | null} cover_image
 * @property {number} created_at
 * @property {number} updated_at
 */
