document.addEventListener("DOMContentLoaded", function () {
    const form = document.getElementById("studentForm");
    const message = document.getElementById("formMessage");
    const submitBtn = document.getElementById("submitBtn");
    const cancelBtn = document.getElementById("cancelBtn");
    const formTitle = document.getElementById("formTitle");
    const passwordInput = document.getElementById("password");
    const passwordLabel = document.getElementById("passwordLabel");
    const passwordHint = document.getElementById("passwordHint");
    const rowsEl = document.getElementById("studentRows");
    const emptyEl = document.getElementById("listEmpty");
    const countEl = document.getElementById("studentCount");
    const searchBox = document.getElementById("searchBox");

    if (!form) {
        return;
    }

    let editingId = null;      // null = adding, number = editing that student
    let students = [];

    function showMessage(text, type) {
        message.textContent = text;
        message.className = "form-message " + type;
    }

    function clearMessage() {
        message.className = "form-message";
        message.textContent = "";
    }

    function goLogin() {
        window.location.href = "/login";
    }

    async function request(method, url, body) {
        const options = {
            method: method,
            credentials: "same-origin",
            headers: { "Content-Type": "application/json" }
        };
        if (body !== undefined) {
            options.body = JSON.stringify(body);
        }
        const res = await fetch(url, options);
        let data = {};
        try {
            data = await res.json();
        } catch (err) {
            data = {};
        }
        return { status: res.status, data: data };
    }

    // ---------- form modes ----------

    function setAddMode() {
        editingId = null;
        form.reset();
        formTitle.textContent = "Add a student";
        submitBtn.textContent = "Add student";
        cancelBtn.style.display = "none";
        passwordInput.required = true;
        passwordLabel.textContent = "Temporary password *";
        passwordHint.textContent = "At least 8 characters. It is stored hashed, never as plain text.";
    }

    function setEditMode(student) {
        editingId = student.Student_ID;
        form.reset();
        form.elements["first_name"].value = student.First_Name || "";
        form.elements["last_name"].value = student.Last_Name || "";
        form.elements["student_number"].value = student.Student_Number || "";
        form.elements["email"].value = student.Email || "";
        form.elements["phone_number"].value = student.Phone_Number || "";
        form.elements["course"].value = student.Course || "";
        form.elements["faculty"].value = student.Faculty || "";
        // faculty not in the list (older data): add it so it is not lost
        if (form.elements["faculty"].value !== student.Faculty && student.Faculty) {
            const opt = document.createElement("option");
            opt.value = student.Faculty;
            opt.textContent = student.Faculty;
            form.elements["faculty"].appendChild(opt);
            form.elements["faculty"].value = student.Faculty;
        }
        formTitle.textContent = "Edit student: " + student.First_Name + " " + student.Last_Name;
        submitBtn.textContent = "Save changes";
        cancelBtn.style.display = "";
        passwordInput.required = false;
        passwordLabel.textContent = "New password (optional)";
        passwordHint.textContent = "Leave empty to keep their current password.";
        clearMessage();
        form.scrollIntoView({ behavior: "smooth", block: "start" });
    }

    function formBody() {
        return {
            first_name: form.elements["first_name"].value,
            last_name: form.elements["last_name"].value,
            student_number: form.elements["student_number"].value,
            email: form.elements["email"].value,
            phone_number: form.elements["phone_number"].value,
            course: form.elements["course"].value,
            faculty: form.elements["faculty"].value,
            password: form.elements["password"].value
        };
    }

    // ---------- list ----------

    function makeCell(text) {
        const td = document.createElement("td");
        td.textContent = text || "";
        return td;
    }

    function renderRows() {
        rowsEl.replaceChildren();

        students.forEach(function (s) {
            const tr = document.createElement("tr");
            tr.appendChild(makeCell(s.First_Name + " " + s.Last_Name));
            tr.appendChild(makeCell(s.Student_Number));
            tr.appendChild(makeCell(s.Email));
            tr.appendChild(makeCell(s.Course));
            tr.appendChild(makeCell(s.Faculty));

            const actions = document.createElement("td");
            actions.className = "row-actions";

            const edit = document.createElement("button");
            edit.type = "button";
            edit.className = "edit";
            edit.textContent = "Edit";
            edit.addEventListener("click", function () { setEditMode(s); });

            const remove = document.createElement("button");
            remove.type = "button";
            remove.className = "remove";
            remove.textContent = "Remove";
            remove.addEventListener("click", function () { removeStudent(s); });

            actions.appendChild(edit);
            actions.appendChild(remove);
            tr.appendChild(actions);
            rowsEl.appendChild(tr);
        });

        emptyEl.style.display = students.length ? "none" : "block";
        countEl.textContent = students.length ? "(" + students.length + ")" : "";
    }

    async function loadStudents() {
        const q = searchBox.value.trim();
        const result = await request(
            "GET", "/api/students" + (q ? "?q=" + encodeURIComponent(q) : "")
        );

        if (result.status === 401) {
            goLogin();
            return;
        }

        if (result.status === 200 && Array.isArray(result.data.students)) {
            students = result.data.students;
            renderRows();
        } else {
            showMessage(result.data.message || "Could not load students.", "error");
        }
    }

    async function removeStudent(s) {
        const name = s.First_Name + " " + s.Last_Name;
        const ok = window.confirm(
            "Remove " + name + " (" + s.Student_Number + ")?\n\n" +
            "This also deletes their QR card, attendance records and notifications. " +
            "It cannot be undone."
        );
        if (!ok) {
            return;
        }

        const result = await request("DELETE", "/api/students/" + s.Student_ID);

        if (result.status === 401) {
            goLogin();
            return;
        }

        if (result.status === 200) {
            if (editingId === s.Student_ID) {
                setAddMode();
            }
            showMessage("Removed " + name + " (" + s.Student_Number + ").", "success");
            await loadStudents();
        } else {
            showMessage(result.data.message || "Could not remove the student.", "error");
        }
    }

    // ---------- events ----------

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        submitBtn.disabled = true;
        clearMessage();

        try {
            const adding = editingId === null;
            const result = adding
                ? await request("POST", "/api/students", formBody())
                : await request("PUT", "/api/students/" + editingId, formBody());

            if (result.status === 401) {
                goLogin();
                return;
            }

            if ((adding && result.status === 201) || (!adding && result.status === 200)) {
                const body = formBody();
                const label = body.first_name.trim() + " " + body.last_name.trim() +
                              " (" + body.student_number.trim() + ")";
                if (adding) {
                    showMessage(
                        "Student added: " + label + ". They can now log in with their " +
                        "student number and the password you set.",
                        "success"
                    );
                } else {
                    showMessage(
                        "Saved changes for " + label +
                        (result.data.password_changed ? ". Password changed." : "."),
                        "success"
                    );
                }
                setAddMode();
                await loadStudents();
            } else {
                showMessage(result.data.message || "Something went wrong.", "error");
            }
        } catch (err) {
            showMessage("Network error. Please try again.", "error");
        } finally {
            submitBtn.disabled = false;
        }
    });

    cancelBtn.addEventListener("click", function () {
        setAddMode();
        clearMessage();
    });

    let searchTimer = null;
    searchBox.addEventListener("input", function () {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(loadStudents, 250);
    });

    setAddMode();
    loadStudents();
});
