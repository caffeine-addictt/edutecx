

// On Render
(() => {
  $("#login-navlink").attr('href', window.location.pathname === '/' ? '/login' : `/login?callbackURI=${encodeURI(window.location.pathname)}`);
  $("#register-navlink").attr('href', window.location.pathname === '/' ? '/register' : `/register?callbackURI=${encodeURI(window.location.pathname)}`);
});

