document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("addStudentForm");
    const message = document.getElementById("formMessage");
    const submitBtn = document.getElementById("submitBtn");

    if (!form) {
        return;
    }

    function showMessage(text, type) {
        message.textContent = text;
        message.className = "form-message " + type;
    }

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const body = {
            first_name: form.elements["first_name"].value,
            last_name: form.elements["last_name"].value,
            student_number: form.elements["student_number"].value,
            email: form.elements["email"].value,
            phone_number: form.elements["phone_number"].value,
            course: form.elements["course"].value,
            faculty: form.elements["faculty"].value,
            password: form.elements["password"].value
        };

        submitBtn.disabled = true;
        message.className = "form-message";

        try {
            const result = await apiPost("/api/students", body);

            if (result.status === 401) {
                window.location.href = "/login";
                return;
            }

            if (result.status === 201 && result.data.student) {
                const s = result.data.student;
                showMessage(
                    "Student added: " + s.Name + " (" + s.Student_Number + "). " +
                    "They can now log in with their student number and the password you set.",
                    "success"
                );
                form.reset();
            } else {
                showMessage(
                    result.data.message || "Could not add the student.",
                    "error"
                );
            }
        } catch (err) {
            showMessage("Network error. Please try again.", "error");
        } finally {
            submitBtn.disabled = false;
        }
    });
});
