$(document).ready(function () {
    let typingTimer;
    const typingDelay = 300;

    $('#default-search').on('input', function () {
        clearTimeout(typingTimer);
        const query = $(this).val().trim();
        console.log("Query being sent:", query);
        const suggestionsList = $('#suggestions-list');

        if (query.length === 0) {
            suggestionsList.empty().hide();
            return;
        }

        typingTimer = setTimeout(() => {
            $.ajax({
                url: "{% url 'dashboard:search_suggestions' %}",
                type: "GET",
                data: {query: query},
                success: function (response) {
                    const {courses, institutions} = response;
                    suggestionsList.empty();

                    if (courses.length === 0 && institutions.length === 0) {
                        suggestionsList.append('<li style="padding: 8px; color: #666;">No results found</li>');
                    } else {

                        if (courses.length > 0) {
                            suggestionsList.append('<li style="font-weight: bold; padding: 8px;">Courses</li>');
                            courses.forEach(course => {
                                suggestionsList.append(`<li style="padding: 8px; cursor: pointer;" data-value="${course.course_name}">${course.course_name}</li>`);
                            });
                        }

                        if (institutions.length > 0) {
                            suggestionsList.append('<li style="font-weight: bold; padding: 8px;">Institutions</li>');
                            institutions.forEach(institution => {
                                suggestionsList.append(`<li style="padding: 8px; cursor: pointer;" data-value="${institution.institution_name}">${institution.institution_name}</li>`);
                            });
                        }
                    }
                    suggestionsList.show();
                },
                error: function (xhr, status, error) {
                    suggestionsList.empty().append('<li style="padding: 8px; color: #666;">Error fetching results. Please try again.</li>').show();
                    console.error("Error:", error);
                }
            });
        }, typingDelay);
    });

    // Handle item selection
    $(document).on('click', '#suggestions-list li', function (event) {
        event.preventDefault(); // Prevent form submission
        $('#default-search').val($(this).data('value'));
        $('#suggestions-list').hide();
    });


    $(document).click(function (e) {
        if (!$(e.target).closest('.search-div').length) {
            $('#suggestions-list').hide();
        }
    });


    function handleSubmit(event) {
        event.preventDefault();

        let query = document.getElementById("default-search").value.trim();
        if (!query) return;


        let isCourseSearch = /course|program|degree/i.test(query);
        let isInstitutionSearch = /university|college|institution|academy/i.test(query);


        if (!isCourseSearch && !isInstitutionSearch) {
            alert("Please clarify your search. It seems like you're looking for both courses and institutions.");
            return;
        }

        let url = isCourseSearch ? `/search_suggestions_courses/?query=${query}` : `/search_suggestions_institutions/?query=${query}`;


        fetch(url)
            .then(response => response.json())
            .then(data => {
                if (isCourseSearch && data.courses.length > 0) {
                    let course = data.courses[0];
                    if (course && course.course_id) {
                        let courseId = course.course_id;
                        window.location.href = `/view_course/${courseId}`;
                    } else {
                        alert("No valid course ID found.");
                    }
                } else if (isInstitutionSearch && data.institutions.length > 0) {
                    let institution = data.institutions[0];
                    if (institution && institution.institution_id) {
                        let institutionId = institution.institution_id;
                        window.location.href = `/view_institution/${institutionId}`;
                    } else {
                        alert("No valid institution ID found.");
                    }
                } else {
                    alert(isCourseSearch ? "No courses found!" : "No institutions found!");
                }
            })
            .catch(error => console.error("Error:", error));
    }


    document.getElementById('search-form').addEventListener('submit', handleSubmit);
});

