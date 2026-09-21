document.addEventListener("DOMContentLoaded", function () {

    const students = {

        QR0001: {
            firstName: "Lerato",
            lastName: "Molefe",
            studentNumber: "ST2025001",
            email: "lerato.molefe@richfield.ac.za",
            course: "Bachelor of Science in Information Technology",
            faculty: "Information Technology",
            cardStatus: "Active",
            expiry: "31 December 2027",
            moduleCode: "CC101",
            moduleName: "Cloud Computing",
            venue: "Lab 1",
            day: "Monday",
            time: "09:00"
        },

        QR0002: {
            firstName: "Sipho",
            lastName: "Naidoo",
            studentNumber: "ST2025002",
            email: "sipho.naidoo@richfield.ac.za",
            course: "Diploma in Information Technology",
            faculty: "Information Technology",
            cardStatus: "Active",
            expiry: "31 December 2027",
            moduleCode: "IOT102",
            moduleName: "Internet of Things",
            venue: "Lab 2",
            day: "Tuesday",
            time: "10:00"
        },

        QR0003: {
            firstName: "Ayanda",
            lastName: "Smith",
            studentNumber: "ST2025003",
            email: "ayanda.smith@richfield.ac.za",
            course: "Bachelor of Business Administration",
            faculty: "Business and Management",
            cardStatus: "Active",
            expiry: "31 December 2027",
            moduleCode: "CYB103",
            moduleName: "Cybersecurity",
            venue: "Lab 3",
            day: "Wednesday",
            time: "11:00"
        },

        QR0004: {
            firstName: "Thabo",
            lastName: "Johnson",
            studentNumber: "ST2025004",
            email: "thabo.johnson@richfield.ac.za",
            course: "Diploma in Business Management",
            faculty: "Business and Management",
            cardStatus: "Active",
            expiry: "31 December 2027",
            moduleCode: "SD104",
            moduleName: "Software Development",
            venue: "Lab 4",
            day: "Thursday",
            time: "09:00"
        }

    };


    const parameters =
        new URLSearchParams(
            window.location.search
        );


    const qrValue =
        parameters.get("qr");


    const verificationContent =
        document.getElementById(
            "verificationContent"
        );


    const moduleSection =
        document.getElementById(
            "moduleSection"
        );


    const invalidSection =
        document.getElementById(
            "invalidSection"
        );


    const verificationBanner =
        document.getElementById(
            "verificationBanner"
        );


    const verificationIcon =
        document.getElementById(
            "verificationIcon"
        );


    const verificationTitle =
        document.getElementById(
            "verificationTitle"
        );


    const verificationMessage =
        document.getElementById(
            "verificationMessage"
        );


    const confirmAccessBtn =
        document.getElementById(
            "confirmAccessBtn"
        );


    function showInvalidQR() {

        verificationContent.style.display =
            "none";

        moduleSection.style.display =
            "none";

        invalidSection.style.display =
            "block";
    }


    if (!qrValue || !students[qrValue]) {

        showInvalidQR();

        return;
    }


    const student =
        students[qrValue];


    const initials =
        student.firstName.charAt(0) +
        student.lastName.charAt(0);


    document.getElementById(
        "studentPhoto"
    ).textContent = initials;


    document.getElementById(
        "studentName"
    ).textContent =
        student.firstName +
        " " +
        student.lastName;


    document.getElementById(
        "studentNumber"
    ).textContent =
        student.studentNumber;


    document.getElementById(
        "studentEmail"
    ).textContent =
        student.email;


    document.getElementById(
        "studentCourse"
    ).textContent =
        student.course;


    document.getElementById(
        "studentFaculty"
    ).textContent =
        student.faculty;


    document.getElementById(
        "cardExpiry"
    ).textContent =
        student.expiry;


    document.getElementById(
        "cardStatus"
    ).textContent =
        student.cardStatus;


    document.getElementById(
        "qrCode"
    ).textContent =
        qrValue;


    document.getElementById(
        "moduleCode"
    ).textContent =
        student.moduleCode;


    document.getElementById(
        "moduleName"
    ).textContent =
        student.moduleName;


    document.getElementById(
        "moduleVenue"
    ).textContent =
        student.venue;


    document.getElementById(
        "moduleDay"
    ).textContent =
        student.day;


    document.getElementById(
        "moduleTime"
    ).textContent =
        student.time;


    const now =
        new Date();


    document.getElementById(
        "scanTime"
    ).textContent =
        now.toLocaleTimeString(
            [],
            {
                hour: "2-digit",
                minute: "2-digit"
            }
        );


    const cardBadge =
        document.getElementById(
            "cardBadge"
        );


    cardBadge.textContent =
        student.cardStatus;


    if (student.cardStatus === "Active") {

        document.getElementById(
            "cardStatus"
        ).classList.add(
            "success-text"
        );

        cardBadge.classList.add(
            "active"
        );

    }

    else {

        verificationBanner.classList.add(
            "denied"
        );


        verificationIcon.textContent =
            "×";


        verificationTitle.textContent =
            "Access Denied";


        verificationMessage.textContent =
            "This digital access card is not active.";


        document.getElementById(
            "cardStatus"
        ).classList.add(
            "danger-text"
        );


        cardBadge.classList.add(
            student.cardStatus.toLowerCase()
        );


        confirmAccessBtn.disabled =
            true;

    }


    confirmAccessBtn.addEventListener(
        "click",
        function () {

            const attendanceStatus =
                document.getElementById(
                    "attendanceStatus"
                );


            attendanceStatus.textContent =
                "Present";


            attendanceStatus.classList.add(
                "success-text"
            );


            confirmAccessBtn.textContent =
                "Access Confirmed ✓";


            confirmAccessBtn.disabled =
                true;


            alert(
                student.firstName +
                " " +
                student.lastName +
                " has been granted access."
            );

        }
    );

});