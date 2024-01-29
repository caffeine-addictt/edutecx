
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


/**
 * @typedef {Object} ClassroomGetData
 * @property {string} id
 * @property {string} owner_id
 * @property {string[]} educator_ids
 * @property {string[]} student_ids
 * @property {string[]} textbook_ids
 * @property {string} title
 * @property {string} description
 * @property {string[]} assignments
 * @property {string | null} cover_image
 * @property {string} invite_id
 * @property {boolean} invite_enabled
 * @property {number} created_at
 * @property {number} updated_at
 */
