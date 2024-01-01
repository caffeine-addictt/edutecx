
/**
 * Fetch and set graph URI
 * @returns {Promise<void>}
 */
const fetchGraphURI = async () => {
  response = await fetch('/dashboard/graph', {
    method: 'POST',
    credentials: 'same-origin',
    headers: {
      'Content-Type': 'application/json',
      'X-CSRF-TOKEN': getAccessToken()
    },
    body: JSON.stringify({
      "graphFor": "Textbook"
    })
  }).then(async res => await res.json())

  if (response.status !== 200) throw new Error(response.message)

  $('#graph').attr('src', response.data.uri)
  console.log('Fetched URI: ' + response.data.uri)
}




/**
 * Stream filtered query
 * @returns {Promise<void>}
 */
const fetchUserData = async () => {
  let searchParams = ((new URL(location.href)).searchParams)
  let criteria = searchParams.get('criteria')
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or'

  searchParams.set('requestFor', 'Textbook')
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
