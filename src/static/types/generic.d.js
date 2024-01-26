
/**
 * The generic json
 * @typedef _GenericAPIJSON
 * @property {number} status
 * @property {string} message
 */


/**
 * Successfuly json response
 * @typedef _SuccessfulAPIJSON
 * @property {200} status
 * @property {T} data
 * @template T
 * 
 * @typedef {_GenericAPIJSON & _SuccessfulAPIJSON<T>} WithDataJSON
 * @template T
 */


/**
 * API Json response
 * @typedef {_SuccessfulAPIJSON<T> | _GenericAPIJSON} APIJSON
 * @template T
 */
