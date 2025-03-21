document.getElementById('search-form').addEventListener('submit', function(e) {
    e.preventDefault(); // Prevent form submission

    const query = document.getElementById('default-search').value.trim();
    const suggestionsList = document.getElementById('suggestions-list');

    if (query.length > 0) {
        axios.get(`/search_suggestions/?query=${encodeURIComponent(query)}`)
            .then(response => {
                const { courses, institutions } = response.data;
                suggestionsList.innerHTML = '';

                if (courses.length === 0 && institutions.length === 0) {
                    suggestionsList.innerHTML = '<li style="padding: 8px; color: #666;">No results found</li>';
                } else {
                    // Display courses if available
                    if (courses.length > 0) {
                        const courseHeader = document.createElement('li');
                        courseHeader.textContent = 'Courses';
                        courseHeader.style.fontWeight = 'bold';
                        suggestionsList.appendChild(courseHeader);

                        courses.forEach(course => {
                            const li = document.createElement('li');
                            li.textContent = course.course_name;
                            li.style.padding = '8px';
                            li.style.cursor = 'pointer';
                            li.addEventListener('click', () => {
                                document.getElementById('default-search').value = course.course_name;
                                suggestionsList.innerHTML = '';
                                suggestionsList.style.display = 'none';
                            });
                            suggestionsList.appendChild(li);
                        });
                    }

                    // Display institutions if available
                    if (institutions.length > 0) {
                        const institutionHeader = document.createElement('li');
                        institutionHeader.textContent = 'Institutions';
                        institutionHeader.style.fontWeight = 'bold';
                        suggestionsList.appendChild(institutionHeader);

                        institutions.forEach(institution => {
                            const li = document.createElement('li');
                            li.textContent = institution.institution_name;
                            li.style.padding = '8px';
                            li.style.cursor = 'pointer';
                            li.addEventListener('click', () => {
                                document.getElementById('default-search').value = institution.institution_name;
                                suggestionsList.innerHTML = '';
                                suggestionsList.style.display = 'none';
                            });
                            suggestionsList.appendChild(li);
                        });
                    }
                }
                suggestionsList.style.display = 'block';
            })
            .catch(error => {
                console.error('Error fetching suggestions:', error);
            });
    } else {
        suggestionsList.innerHTML = '<li style="padding: 8px; color: #666;">Please enter a valid search query</li>';
        suggestionsList.style.display = 'block';
    }
});

// Hide suggestions when clicking outside
document.addEventListener('click', (e) => {
    const searchDiv = document.querySelector('.search-div');
    if (!searchDiv.contains(e.target)) {
        document.getElementById('suggestions-list').style.display = 'none';
    }
});