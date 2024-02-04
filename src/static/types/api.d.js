
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
 * @typedef {Object} SaleGetData
 * @property {string} sale_id
 * @property {string} user_id
 * @property {string | null} discount_id
 * @property {string[]} textbook_ids
 * @property {'OneTime' | 'Subscription'} type
 * @property {number} total_cost
 * @property {boolean} paid
 * @property {number} paid_at
 */


/**
 * @typedef {Object} UserGetData
 * @property {string} user_id
 * @property {string} email
 * @property {string} username
 * @property {'Active' | 'Locked'} status
 * @property {'Student' | 'Educator' | 'Admin'} privilege
 * @property {string | null} profile_image
 * @property {number} created_at
 * @property {number} last_login
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


/**
 * @typedef {Object} SubmissionGetData
 * @property {string} submission_id
 * @property {string} student_id
 * @property {string} assignment_id
 * @property {string[]} comments
 * @property {string} snippet
 * @property {number} created_at
 * @property {number} updated_at
 */
