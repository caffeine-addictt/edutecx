
/**
 * Classrooms List
 * @type {ClassroomGetData[]}
 */
let classroomList = [];


/**
 * Fetch Classrooms
 * @type {Promise<ClassroomGetData[]>}
 */
const fetchClassrooms = async () => {

  /**
   * @type {APIJSON<ClassroomGetData[]> | void}
   */
  const data = await fetch('/api/v1/classroom/list', {
    method: 'GET',
    headers: { 'X-CSRF-TOKEN': getAccessToken() }
  }).then(res => res.json()).catch(err => console.log(err));

  if (!data || data.status !== 200) {
    renderToast('Failed to fetch classrooms', 'danger');
    if (data) console.log(data.message);
    return data?.data || new Array();
  };
  return data.data
}


/**
 * Render Classrooms
 * @param {ClassroomGetData[]?} filteredList
 * @param {string} searchQuery
 * @returns {Promise<void>}
 */
const renderClassrooms = async (filteredList, searchQuery) => {
  const container = $('#classroom__container');
  container.empty();

  const filteredClassrooms = filterClassrooms(filteredList || classroomList, searchQuery);
  
  if ((filteredList || classroomList).length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        You are not in any classrooms. 
        Join with an invite link or <a href='/classrooms/new'>create one</a>!
      </p>`
    ));
  } else if (filteredClassrooms.length === 0) {
    container.append(htmlToElement(
      `<p class="text-secondary fs-5 mb-0">
        No classrooms found for the given search.
      </p>`
    ));
  } else if (!filteredList) {
    template = deepCopy(tile);
    filteredClassrooms.forEach(classroomData => {
      container.append(htmlToElement(formatString(template, {
        title: classroomData.title,
        teacher: classroomData.owner_username,
        id: classroomData.id
      })));
    });
  } else {
    template = deepCopy(tile);
    const commonClassrooms = filteredClassrooms.filter(classroom =>
      filteredList.some(filtered => filtered.id === classroom.id)
    );

    commonClassrooms.forEach(classroomData => {
      container.append(htmlToElement(formatString(template, {
        title: classroomData.title,
        teacher: classroomData.owner_username,
        id: classroomData.id
      })));
    });
  }

};


/**
 * Handle Filtering
 * @param {ClassroomGetData[]} classrooms
 * @param {string} searchQuery
 * @returns {ClassroomGetData[]}
 */
const filterClassrooms = (classrooms, searchQuery) => {
  if (!searchQuery) {
    return classrooms; //Returns all classrooms if there's no search
  }
  return classrooms.filter(classroom =>
    classroom.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
    classroom.owner_username.toLowerCase().includes(searchQuery.toLowerCase())
    );
}


// On DOM Render
$(async () => {
  classroomList = await fetchClassrooms();
  renderClassrooms(null, ''); // Initialises render with no search

  const searchInput = $('#searchbar');
  const searchButton = $('#searchButton');
  const sortDropdown = $('#sortby');
  let sortedClassrooms;

  // Event listener for the search button
  searchButton.on('click', () => {
    const searchQuery = searchInput.val().trim();
    renderClassrooms(sortedClassrooms, searchQuery);
  });

  // Event listener for "Enter" key
  searchInput.on('keypress', (event) => {
    if (event.key === 'Enter') {
      const searchQuery = searchInput.val().trim();
      renderClassrooms(sortedClassrooms, searchQuery);
    }
  });

  // Event listener for sorting dropdown
  sortDropdown.on('change', () => {
    const sortOption = sortDropdown.val();

    if (sortOption === 'none') {
      sortedClassrooms = null;
    } else if (sortOption === 'name') {
      sortedClassrooms = [...classroomList].sort((a, b) => a.title.localeCompare(b.title));
    }
    renderClassrooms(sortedClassrooms, $('#searchbar').val().trim());
  });


});



