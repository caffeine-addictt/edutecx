/**
 * Access token fetcher
 * @returns {string | null} csrfAccessToken
 */
const getAccessToken = () => {
  const cookieArray = document.cookie.split('; ');
  for (let token of cookieArray) {
    if (token.startsWith('csrf_access_token')) {
      return token.split('=')[1];
    };
  };
};



/**
  * Get Cart Items
  * @returns {string[]}
  */
const getCartItems = () => {
  return JSON.parse(localStorage.getItem('cart')) || new Array();
};


// Document withReload as a boolean with a default value of false
/**
 * Clear Cart
 * @param [boolean] withReload
 * @returns {void}
 */
const clearCart = (withReload = false) => {
  localStorage.removeItem('cart');

  if (withReload) {
    window.location.reload();
  };
};


/**
  * Add item to cart
  * @param {string} itemID
  * @param [boolean] withReload
  * @returns {void}
  */
const addCartItem = (itemID, withReload = false) => {
  let cart = getCartItems();
  cart.push(itemID);
  localStorage.setItem('cart', JSON.stringify(cart));

  if (withReload) {
    window.location.reload();
  };
};


/**
 * Remove item from cart
 * @param {string} itemID
 * @param {boolean} [withReload=false]
 * @returns {void}
 */
const removeCartItem = (itemID, withReload = false) => {
  let cart = getCartItems();
  cart = cart.filter((item) => item !== itemID);
  localStorage.setItem('cart', JSON.stringify(cart));

  if (withReload) {
    window.location.reload();
  };
};




/**
 * Generate HTML Element(s) from string representation
 * @param {string} html String representation of HTML
 * @param [boolean=true] trim Whether to trim `html` whitespace
 * @returns {HTMLElement | HTMLElement[] | null}
 */
const htmlToElement = (html, trim = true) => {
  html = trim ? html : html.trim();
  if (!html) return null;

  const template = document.createElement('template');
  template.innerHTML = html;

  const result = template.content.children;
  if (result.length === 1) return result[0];
  return result;
}




/**
 * Format String
 * @param {string} str
 * @param {{[key: string]: string}} params
 * @returns {string}
 */
const formatString = (str, params) => {
  let result = str;
  Object.keys(params).forEach((key) => {
    result = result.replace(`{${key}}`, params[key]);
  });
  return result;
}




/**
 * Force javascript to create a deep copy of a string
 * @param {string} str
 * @returns {string}
 */
const deepCopy = (str) => {
  return (' ' + str).slice(1)
}



/**
 * Wait
 * @param {number} ms
 */
const wait = (ms) => new Promise((resolve) => setTimeout(resolve, ms));




/**
 * In Array
 * @param {T} item
 * @param {Array.<T>} array
 * @template T
 */
const inArray = (item, array) => {
  return (array.indexOf(item) > -1);
};




/**
 * Compare if both arrays are equal
 * @param {Array.<T>} a
 * @param {Array.<U>} b
 * @template T
 * @template U
 */
const arrayIsEqual = (a, b) => {
  if (a.length !== b.length) return false;
  
  for (let i = 0; i < a.length; i++) {
    if (a[i] !== b[i]) return false;
  };
  return true;
}

