// Access token fetcher
const getAccessToken = () => {
  const cookieArray = document.cookie.split('; ')
  for (let token of cookieArray) {
    if (token.startsWith('csrf_access_token')) {
      return token.split('=')[1]
    }
  }
}
