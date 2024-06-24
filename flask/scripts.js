document.addEventListener('DOMContentLoaded', function() {
    actualizarEstado();

    document.getElementById('iniciar').addEventListener('click', function() {
        fetch('/iniciar_movimiento', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                actualizarEstado();
            });
    });

    document.getElementById('detener').addEventListener('click', function() {
        fetch('/detener_movimiento', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                actualizarEstado();
            });
    });

    document.getElementById('configurar').addEventListener('click', function() {
        var parada = prompt("Ingresa la tarifa en parada (€/segundo):");
        var movimiento = prompt("Ingresa la tarifa en movimiento (€/segundo):");

        fetch('/configurar_tarifas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ parada: parseFloat(parada), movimiento: parseFloat(movimiento) })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
            actualizarEstado();
        });
    });

    document.getElementById('cambiar_contraseña').addEventListener('click', function() {
        var nueva_contraseña = prompt("Ingresa la nueva contraseña:");
        
        fetch('/cambiar_contraseña', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ nueva_contraseña: nueva_contraseña })
        })
        .then(response => response.json())
        .then(data => {
            console.log(data.message);
        });
    });

    document.getElementById('finalizar').addEventListener('click', function() {
        fetch('/finalizar_programa', { method: 'POST' })
            .then(response => response.json())
            .then(data => {
                console.log(data.message);
                actualizarEstado();
            });
    });

    function actualizarEstado() {
        fetch('/get_status', { method: 'GET' })
            .then(response => response.json())
            .then(data => {
                document.getElementById('estado').textContent = data.estado;
                document.getElementById('tiempo_total').textContent = data.tiempo_total.toFixed(2);
                document.getElementById('total_cobrar').textContent = data.total_a_cobrar.toFixed(2);
                document.getElementById('tarifa_actual').textContent = data.tarifa_actual.toFixed(2);
            });
    }
});
