function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

document.querySelectorAll('.star-button').forEach(button => {
    const projectId = button.dataset.projectId;
    const storageKey = `starred:${projectId}`;
    const countEl = button.querySelector('.star-count');

    function setStarred(starred) {
        button.classList.toggle('is-starred', starred);
        button.setAttribute('aria-pressed', starred);
    }

    // Ingat status star di browser ini
    setStarred(localStorage.getItem(storageKey) === '1');

    button.addEventListener('click', async () => {
        const wasStarred = button.classList.contains('is-starred');

        try {
            const response = await fetch(`/projects/star/${projectId}/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                body: JSON.stringify({ action: wasStarred ? 'unstar' : 'star' })
            });

            if (!response.ok) throw new Error(`Status ${response.status}`);

            const data = await response.json();
            countEl.textContent = data.star_count;
            setStarred(!wasStarred);
            localStorage.setItem(storageKey, wasStarred ? '0' : '1');
        } catch (error) {
            console.error('Error:', error);
        }
    });
});