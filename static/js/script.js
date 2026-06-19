async function enviarActualizacion(id) {
    const cantidad = document.getElementById('cantidad').value;
    await fetch(`/actualizar-stock/${id}/${cantidad}`, { method: 'POST' });
    alert("Stock actualizado y verificado");
}