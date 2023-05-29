document.addEventListener('DOMContentLoaded', () => {
    const logoutButton = document.querySelector('#logout-button');


    logoutButton.addEventListener('click', (event) => {
        event.preventDefault();
        logout();
    });

    function logout() {
        logoutButton.disabled = true;
        const request = new XMLHttpRequest();
        request.open('GET', `http://127.0.0.1:${ports['auth_port']}/api/logout`);
        request.withCredentials = true;
        request.send();

        request.addEventListener('load', () => {
                logoutButton.disabled = false;
                const status = JSON.parse(request.response)['status'];
                if (status === 'OK' || request.status === 401) {
                    window.location.replace("/login")

                } else if (status === 'failed') {
                    const error = JSON.parse(request.response)['error'];
                    alert(error);
                } else {
                    alert('Что-то пошло не так! Попробуйте ещё раз');
                }
            }
        );
    }
});
