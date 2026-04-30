/* ── Voting Booth JavaScript ──────────── */

document.addEventListener('DOMContentLoaded', () => {
    const cards = document.querySelectorAll('.candidate-card');
    const hiddenInput = document.getElementById('selected-candidate');
    const submitBtn = document.getElementById('submit-vote-btn');
    const confirmModal = document.getElementById('confirm-modal');
    const confirmName = document.getElementById('confirm-candidate-name');
    const confirmBtn = document.getElementById('confirm-vote');
    const cancelBtn = document.getElementById('cancel-vote');
    const voteForm = document.getElementById('vote-form');

    let selectedCard = null;

    // Candidate selection
    cards.forEach(card => {
        card.addEventListener('click', () => {
            cards.forEach(c => c.classList.remove('selected'));
            card.classList.add('selected');
            selectedCard = card;
            hiddenInput.value = card.dataset.candidateId;
            submitBtn.disabled = false;
            submitBtn.classList.remove('btn-secondary');
            submitBtn.classList.add('btn-primary');
        });
    });

    // Show confirmation modal
    if (submitBtn) {
        submitBtn.addEventListener('click', (e) => {
            e.preventDefault();
            if (!selectedCard) return;
            confirmName.textContent = selectedCard.dataset.candidateName;
            confirmModal.classList.add('active');
        });
    }

    // Confirm vote
    if (confirmBtn) {
        confirmBtn.addEventListener('click', () => {
            voteForm.submit();
        });
    }

    // Cancel vote
    if (cancelBtn) {
        cancelBtn.addEventListener('click', () => {
            confirmModal.classList.remove('active');
        });
    }

    // Close modal on overlay click
    if (confirmModal) {
        confirmModal.addEventListener('click', (e) => {
            if (e.target === confirmModal) confirmModal.classList.remove('active');
        });
    }
});
