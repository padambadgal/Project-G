function login() {
    let username = document.getElementById("username").value;
    let password = document.getElementById("password").value;

    fetch("/login", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ username, password })
    })
    .then(res => res.json())
    .then(data => {

        if (data.success) {

            if (data.role === "doctor") {
                window.location.href = "/doctor";
            } 
            else if (data.role === "patient") {
                window.location.href = "/patient";
            } 
            else {
                window.location.href = "/admin";
            }

        } else {
            alert(data.message);
        }
    });
}

function register() {
    let data = {
        username: document.getElementById("username").value,
        password: document.getElementById("password").value,
        full_name: document.getElementById("fullname").value,
        role: document.getElementById("role").value,
        email: document.getElementById("email").value,
        phone: document.getElementById("phone").value
    };

    fetch("/register", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data)
    })
    .then(res => res.json())
    .then(data => {
        alert(data.message);
    });
}