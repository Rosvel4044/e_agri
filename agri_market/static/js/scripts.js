// agri_market/static/agri_market/js/scripts.js
function addToCart(productId) {
    fetch(`/api/cart/add/${productId}/`, { method: 'POST', headers: { 'Authorization': `Bearer ${localStorage.getItem('token')}` } })
        .then(response => response.json())
        .then(data => alert('Ajouté au panier !'))
        .catch(error => console.error('Erreur:', error));
}