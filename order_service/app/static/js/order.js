document.addEventListener('DOMContentLoaded', () => {
    const count_inputs = document.querySelectorAll('input[name="quantity"]');
    const id_inputs = document.querySelectorAll('.dish_id');
    const prices = document.querySelectorAll('.price');
    const total_count = document.querySelector('#total_count');
    const total_price = document.querySelector('#total_price');
    const submitButton = document.querySelector('#submit-button');
    const specialRequestsInput = document.querySelector('#textArea');
    const logoutButton = document.querySelector('#logout-button');


    count_inputs.forEach((price_input, index) => {
        price_input.addEventListener("input", function () {
            onInputChange(price_input, index);
        });

        observeElement(price_input, "value", function (oldValue, newValue) {
            onInputChange(price_input, index);
        });
    });

    function onInputChange(input, index) {
        let count = 0;
        let price = 0;
        count_inputs.forEach(price_input => {
            count += parseInt(price_input.value);
        });
        total_count.textContent = count;

        for (let i = 0; i < count_inputs.length; i++) {
            let input_val = parseInt(count_inputs[i].value);
            price += input_val * parseFloat(prices[i].innerText);
            count += input_val;
            total_count.textContent = (count / 2).toString();
            total_price.textContent = price.toFixed(2);
        }
    }

    submitButton.addEventListener('click', (event) => {
        event.preventDefault();
        createOrder();
    });

    logoutButton.addEventListener('click', (event) => {
        event.preventDefault();
        logout();
    });

    function createOrder() {
        submitButton.disabled = true;

        const request = new XMLHttpRequest();

        const data = {};
        data['special_requests'] = specialRequestsInput.value;
        data['dishes'] = [];

        for (let i = 0; i < count_inputs.length; i++) {
            let dish_id = parseInt(id_inputs[i].value);
            let dish_quantity = parseInt(count_inputs[i].value);
            let dish_total_price = parseFloat(prices[i].innerText) * dish_quantity;
            dish_total_price = dish_total_price.toFixed(2);
            if (dish_quantity > 0) {
                data.dishes.push({'id': dish_id, "quantity": dish_quantity, "total_price": dish_total_price});
            }
        }

        const jsonString = JSON.stringify(data);
        request.open('POST', '/api/new-order');
        request.withCredentials = true;
        request.setRequestHeader('Content-type', 'application/json');
        request.send(jsonString);

        request.addEventListener('load', () => {
                submitButton.disabled = false;
                const status = JSON.parse(request.response)['status'];
                if (status === 'OK') {
                    const order_id = JSON.parse(request.response)['order']['id'];
                    if (window.confirm(`\n                 ----- УСПЕХ! ID ВАШЕГО ЗАКАЗА: ${order_id} ----- \n\nДля просмотра информации о заказе, нажмите "ok"`)) {
                        window.location.href = `/api/order?id=${order_id}`;
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


function observeElement(element, property, callback, delay = 0) {
    let elementPrototype = Object.getPrototypeOf(element);
    if (elementPrototype.hasOwnProperty(property)) {
        let descriptor = Object.getOwnPropertyDescriptor(elementPrototype, property);
        Object.defineProperty(element, property, {
            get: function () {
                return descriptor.get.apply(this, arguments);
            },
            set: function () {
                let oldValue = this[property];
                descriptor.set.apply(this, arguments);
                let newValue = this[property];
                if (typeof callback == "function") {
                    setTimeout(callback.bind(this, oldValue, newValue), delay);
                }
                return newValue;
            }
        });
    }
}
