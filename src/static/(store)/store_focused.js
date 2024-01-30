
/**
 * Add to cart
 * @param {MouseEvent} e
 * @returns {void}
 */
const handleAddToCart = (e) => {
  e.preventDefault();
  $('#add-to-cart-button').attr('disabled', true);
  $('#add-to-cart-button').text('Adding...');
  
  // Handle not logged in
  if (!getAccessToken()) {
    window.location.href = `/login?callbackURI=${encodeURI(window.location.pathname)}`;
    return;
  };

  if (getCartItems().includes(textbook_id)) renderToast('Already in cart', 'danger');
  else {
    addCartItem(textbook_id);
    renderToast('Added to cart', 'success');
  };

  $('#add-to-cart-button').attr('disabled', false);
  $('#add-to-cart-button').text('Add to Cart');
};


$(() => {
  $('#add-to-cart-button').on('click', handleAddToCart);
});
