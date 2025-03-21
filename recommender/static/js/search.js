        $(document).ready(function () {
            $('#search-form').submit(function (e) {
                e.preventDefault(); // Prevent the default form submission

                const query = $('#default-search').val().trim();
                const suggestionsList = $('#suggestions-list');
                const csrfToken = $('input[name="csrfmiddlewaretoken"]').val();

                if (query.length > 0) {
                    $.ajax({
                        url: "{% url 'dashboard:search_suggestions' %}",
                        type: "GET",
                        data: {query: query},
                        headers: {"X-CSRFToken": csrfToken},
                        success: function (response) {
                            const {courses, institutions} = response;
                            suggestionsList.empty(); // Clear previous results

                            if (courses.length === 0 && institutions.length === 0) {
                                suggestionsList.append('<li style="padding: 8px; color: #666;">No results found</li>');
                            } else {
                                // Display courses
                                if (courses.length > 0) {
                                    suggestionsList.append('<li style="font-weight: bold; padding: 8px;">Courses</li>');
                                    courses.forEach(course => {
                                        suggestionsList.append(`<li style="padding: 8px; cursor: pointer;" data-value="${course.course_name}">${course.course_name}</li>`);
                                    });
                                }
                                // Display institutions
                                if (institutions.length > 0) {
                                    suggestionsList.append('<li style="font-weight: bold; padding: 8px;">Institutions</li>');
                                    institutions.forEach(institution => {
                                        suggestionsList.append(`<li style="padding: 8px; cursor: pointer;" data-value="${institution.institution_name}">${institution.institution_name}</li>`);
                                    });
                                }
                            }
                            suggestionsList.show();
                        },
                        error: function (error) {
                            console.error('Error fetching suggestions:', error);
                            suggestionsList.empty().append('<li style="padding: 8px; color: #666;">Error fetching results. Please try again.</li>').show();
                        }
                    });
                } else {
                    suggestionsList.empty().append('<li style="padding: 8px; color: #666;">Please enter a valid search query</li>').show();
                }
            });

            // Handle item selection
            $(document).on('click', '#suggestions-list li', function () {
                $('#default-search').val($(this).data('value'));
                $('#suggestions-list').hide();
            });

            // Hide suggestions when clicking outside
            $(document).click(function (e) {
                if (!$(e.target).closest('.search-div').length) {
                    $('#suggestions-list').hide();
                }
            });
        });