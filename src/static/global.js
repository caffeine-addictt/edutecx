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
  * @returns {string[] | null}
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
