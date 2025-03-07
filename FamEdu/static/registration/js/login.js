form = document.getElementById("login-form")
button = document.getElementById("login-button")

button.onclick = () => {
    form.style.animationName = 'login-animation';
    form.style.animationDuration = '1s';
}