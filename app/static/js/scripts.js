function toggleModal(id) {
    const modal = document.getElementById(id);
    modal.classList.toggle('hidden');
    modal.classList.toggle('active');
}

document.querySelectorAll('.currency-card').forEach(card => {
    card.addEventListener('click', () => {
        card.classList.toggle('active');
    });
});
