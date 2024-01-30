
/**
 * The generic json
 * @typedef _GenericAPIJSON
 * @property {number} status
 * @property {string} message
 */


/**
 * Successfuly json response
 * @typedef {_GenericAPIJSON & { status: 200; data: T }} APIJSON
 * @template T
 */
