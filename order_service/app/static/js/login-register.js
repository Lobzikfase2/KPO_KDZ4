window.addEventListener('DOMContentLoaded', () => {
    let loginform = document.querySelector('#login-form');
    let registerForm = document.querySelector('#register-form');
    let loginSubmitButton = document.querySelector('#login-button');
    let registerSubmitButton = document.querySelector('#register-button');


    loginSubmitButton.addEventListener('click', (event) => {
        event.preventDefault();
        login(loginSubmitButton, loginform);
    });

    registerSubmitButton.addEventListener('click', (event) => {
        event.preventDefault();
        register(registerSubmitButton, registerForm);
    });
});


function login(submitButton, form) {
    submitButton.disabled = true;

    const request = new XMLHttpRequest();
    const formData = new FormData(form);
    const jsonObject = Object.fromEntries(formData);
    const jsonString = JSON.stringify(jsonObject);

    request.open('POST', `http://127.0.0.1:${ports['auth_port']}/api/login`);
    request.setRequestHeader('Content-type', 'application/json');
    request.withCredentials = true;
    request.send(jsonString);


    request.addEventListener('load', () => {
            submitButton.disabled = false;
            const status = JSON.parse(request.response)['status'];
            if (status === 'OK') {
                const user = JSON.parse(request.response)['user'];

                if (user['role'] === 'CLIENT') {
                    if (window.confirm(`\n                     ----- УСПЕХ! ID пользователя: ${user['id']} ----- \n\nДля перехода на страницу создания заказа, нажмите "ok"`)) {
                        window.location.replace('/create-order');
                    }
                } else {
                    if (window.confirm(`\n                     ----- УСПЕХ! ID пользователя: ${user['id']} ----- \n\nДля перехода на страницу управления блюдами, нажмите "ok"`)) {
                        window.location.replace('/dish');
                    }
                }
            } else if (status === 'failed') {
                const error = JSON.parse(request.response)['error'];
                alert(error);
            } else {
                alert('Что-то пошло не так! Попробуйте ещё раз');
            }
        }
    );
}

function register(submitButton, form) {
    submitButton.disabled = true;

    const request = new XMLHttpRequest();
    const formData = new FormData(form);
    const jsonObject = Object.fromEntries(formData);
    const jsonString = JSON.stringify(jsonObject);

    request.open('POST', `http://127.0.0.1:${ports['auth_port']}/api/register`);
    request.setRequestHeader('Content-type', 'application/json');
    request.withCredentials = true;
    request.send(jsonString);


    request.addEventListener('load', () => {
            submitButton.disabled = false;
            const status = JSON.parse(request.response)['status'];
            if (status === 'OK') {
                const user = JSON.parse(request.response)['user'];

                if (user['role'] === 'CLIENT') {
                    if (window.confirm(`\n                     ----- УСПЕХ! ID пользователя: ${user['id']} ----- \n\nДля перехода на страницу создания заказа, нажмите "ok"`)) {
                        window.location.replace('/create-order');
                    }
                } else {
                    if (window.confirm(`\n                     ----- УСПЕХ! ID пользователя: ${user['id']} ----- \n\nДля перехода на страницу управления блюдами, нажмите "ok"`)) {
                        window.location.replace('/dish');
                    }
                }
            } else if (status === 'failed') {
                const error = JSON.parse(request.response)['error'];
                alert(error);
            } else {
                alert('Что-то пошло не так! Попробуйте ещё раз.');
            }
        }
    );
}
