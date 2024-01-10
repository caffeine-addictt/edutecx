/**
 * Fetch Assignments
 * @type {Promise<Array.<{
*   id: string;
*   title: string;
*   description: string;
*   due_date: number;
*   requirement: string;
*   created_at: number;
* }>>}
*/
const fetchAssignments = async () => {
 try {
   const response = await fetch('/api/v1/assignment/list', {
     method: 'GET',
     headers: { 'X-CSRF-TOKEN': getAccessToken() }
   });

   if (response.ok) {
     const data = await response.json();
     return data.data || [];
   } else {
     console.error('Failed to fetch assignments:', response.statusText);
     return [];
   }
 } catch (error) {
   console.error('Error fetching assignments:', error);
   return [];
 }
};

/**
* Render Assignments
* @param {Array.<{
*   id: string;
*   title: string;
*   description: string;
*   due_date: number;
*   requirement: string;
*   created_at: number;
* }>} assignments
*/
const renderAssignments = (assignments) => {
 const container = $('#assignment__container');
 container.empty();

 if (assignments.length === 0) {
   container.append(`<p class="text-secondary fs-5 mb-0">No assignments available.</p>`);
 } else {
   assignments.forEach(assignmentData => {
     // Customize the rendering based on your assignment data structure
     const assignmentHtml = `
       <div class="assignment-item">
         <h3>${assignmentData.title}</h3>
         <p>${assignmentData.description}</p>
         <p>Due Date: ${new Date(assignmentData.due_date).toLocaleString()}</p>
         <p>Requirement: ${assignmentData.requirement}</p>
       </div>
     `;
     container.append(assignmentHtml);
   });
 }
};

// On DOM Render
$(async () => {
 assignmentList = await fetchAssignments();
 renderAssignments(assignmentList);
});

