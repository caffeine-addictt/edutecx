
/**
 * Classrooms List
 * @type {ClassroomGetData[]}
 */
let classroomList = [];

/** @type {AbortController?} */
let fetchController;




/**
 * Fetch Classrooms
 * @type {Promise<ClassroomGetData[]>}
 */
const fetchClassrooms = async () => {
  // Abort previous
  if (fetchController) fetchController.abort();
  fetchController = new AbortController();

  let searchParams = ((new URL(location.href)).searchParams);
  let criteria = searchParams.get('criteria');
  criteria = ['or', 'and'].includes(criteria) ? criteria : 'or';

  searchParams.set('criteria', criteria);


  /** @type {APIJSON<ClassroomGetData[]> | void} */
  const data = await fetch(`/api/v1/classroom/list?${searchParams.toString()}`, {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() },
    signal: fetchController.signal
  }).then(res => res.json()).catch(err => console.log(err));

  // Ignore aborted requests
  if (fetchController?.signal?.aborted) return classroomList;

  if (!data || data.status !== 200) {
    renderToast('Failed to fetch classrooms', 'danger');
    return data?.data || new Array();
  };

  return data.data
}


/**
 * Render Classrooms
 * @param {ClassroomGetData[]} [filteredList]
 * @returns {Promise<void>}
 */
const renderClassrooms = async (filteredList) => {
  const container = $('#classroom__container');
  container.empty();

  const toRender = filteredList || classroomList;
  
  if (!!!toRender.length && !location.search.length) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        You are not in any classrooms. 
        Join with an invite link or <a href='/classrooms/new'>create one</a>!
      </p>`
    ));

  }
  else if (!!!toRender.length) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        No classrooms found for the given search.
      </p>`
    ));

  }
  else {
    toRender.forEach(classroomData => {
      container.append(htmlToElement(formatString(deepCopy(tile), {
        title: classroomData.title,
        teacher: classroomData.owner_username,
        id: classroomData.id
      })));
    });
  };
};


/**
 * Filter
 * @param {'Name' | 'Created' | 'Owned'} by
 * @returns {classroomData[]}
 */
const filterClassrooms = (by) => {
  switch (by) {
    case 'Name-AZ':
      return classroomList.sort((a, b) => a.title.localeCompare(b.title));
    case 'Name-ZA':
      return classroomList.sort((a, b) => b.title.localeCompare(a.title));
    case 'Created-Newest':
      return classroomList.sort((a, b) => new Date(b.created_at) - new Date(a.created_at));
    case 'Created-Least':
      return classroomList.sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
    case 'Updated-Newest':
      return classroomList.sort((a, b) => new Date(b.updated_at) - new Date(a.updated_at));
    case 'Updated-Least':
      return classroomList.sort((a, b) => new Date(a.updated_at) - new Date(b.updated_at));
    case 'Owned':
      return classroomList.map(a => a.owner_id === user_id).sort((a, b) => a.title.localeCompare(b.title));
    default:
      return classroomList;
  };
};




// On DOM Render
$(async () => {
  classroomList = await fetchClassrooms();
  renderClassrooms(filterClassrooms('Name'));

  const searchInput = $('#searchbar');
  const searchButton = $('#searchButton');
  const sortDropdown = $('#sortby');

  // Update with current URL query
  const initialSearchParams = (new URL(location.href)).searchParams;
  searchInput.text(initialSearchParams.get('query') || '');
  sortDropdown.val(initialSearchParams.get('sort') || 'Name-AZ');

  /** @type {ReturnType<setTimeout>?} */
  let queryToRun;




  /**
   * 500ms debounce for search inputs
   * @param {string} [newQuery]
   * @returns {Promise<void>}
   */
  const runSearch = (newQuery) => {
    newQuery = newQuery || searchInput.text();
    searchInput.text(newQuery);

    if (queryToRun) clearTimeout(queryToRun);
    if (fetchController) fetchController.abort();

    queryToRun = setTimeout(async () => {
      const searchParams = ((new URL(location.href)).searchParams);
      if (searchInput.text()) searchParams.set('query', searchInput.text());
      else searchParams.delete('query');

      const stringifiedParams = searchParams.toString();
      if (stringifiedParams === location.search) return;

      // Modify URL
      const newURL = `${location.pathname}${stringifiedParams ? `?${stringifiedParams}` : ''}`;
      if (newURL === location.href) return;

      // Modify URL if possible else Reload
      if (window?.history?.pushState) {
        window.history.pushState({}, '', newURL);

        classroomList = await fetchClassrooms();
        renderClassrooms();
      }
      else {
        location.href = newURL;
      };
    }, 500);
  }




  // Hooks
  searchButton.on('click', () => runSearch());
  searchInput.on('input', (/** @type {JQuery.Input} */e) => {
    const trimed = e.target.value.trim();
    searchInput.text(trimed);
    runSearch(trimed);
  });

  sortDropdown.on('change', (/** @type {JQuery.ChangeEvent<HTMLInputElement>} */e) => {
    const sortOption = e.target.value;

    // Update URL
    const searchParams = ((new URL(location.href)).searchParams);
    searchParams.set('sort', sortOption);
    const stringifiedParams = searchParams.toString();
    if (stringifiedParams === location.search) return;

    // Modify URL
    const newURL = `${location.pathname}${stringifiedParams ? `?${stringifiedParams}` : ''}`;
    if (newURL === location.href) return;

    // Modify URL if possible else Reload
    if (window?.history?.pushState) {
      window.history.pushState({}, '', newURL);
      
      const filteredList = filterClassrooms(sortOption);
      renderClassrooms(filteredList);
    }
    else {
      location.href = newURL;
    };
  });

});
