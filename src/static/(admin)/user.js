
/**
 * Fetch and draw graph
 * @returns {Promise<void>}
 */
const fetchGraphURI = async () => {
  renderToast('Drawing Graph...', 'info');

  /**
   * @type {Response}
   */
  const response = await fetch('/dashboard/graph', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({
      "graphFor": "User"
    })
  })

  if (!response.ok) return renderToast('Failed to fetch Graph', 'danger');
  const svg = await response.text();

  $('#svg-render').empty();
  $('#svg-render').append(htmlToElement(svg));
  console.log('Fetched SVG')
}




/**
 * Stream filtered query
 * @returns {Promise<void>}
 */
const fetchUserData = async () => {
  let searchParams = ((new URL(location.href)).searchParams)
  let criteria = searchParams.get('criteria')
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or'

  searchParams.set('requestFor', 'User')
  searchParams.set('criteria', criteria)

  response = await fetch(`/dashboard/get?${searchParams.toString()}`, {
    method: 'GET',
    headers: {
      'X-CSRF-TOKEN': getAccessToken()
    }
  }).then(async res => await res.json())

  if (response.status !== 200) throw new Error(response.message)

  /* TODO: Inject data at runtime */
  console.log('Fetched Data')
}


// Run in parallel
$(() => Promise.all([ fetchGraphURI(), fetchUserData() ])
  .then(values => console.log(values))
  .catch(err => console.log(err)))
