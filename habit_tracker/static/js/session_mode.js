/**
 * Session Mode Logic - Handles the distraction-free focus timer.
 */

document.addEventListener('DOMContentLoaded', () => {
    // Apply theme settings if they exist in localStorage (since we don't have the full Dashboard obj here)
    const mode = localStorage.getItem('theme') || 'light';
    const accent = localStorage.getItem('accent') || 'indigo';

    if (mode === 'dark') {
        document.body.setAttribute('data-theme', 'dark');
    }
    document.body.setAttribute('data-accent', accent);

    const sessionDataEl = document.getElementById('sessionData');
    if (!sessionDataEl) return;

    const sessionId = sessionDataEl.getAttribute('data-session-id');
    const durationMins = parseInt(sessionDataEl.getAttribute('data-duration'), 10) || 25;

    // For testing/demo purposes, if you want real minutes, use durationMins * 60
    // Let's use 10 seconds for quick testing if duration is e.g., 25.
    // In production: let timeLeft = durationMins * 60;

    // We will use actual minutes as requested:
    let timeLeft = durationMins * 60;

    const timerDisplay = document.getElementById('timerDisplay');
    const cancelBtn = document.getElementById('cancelSessionBtn');

    let timerInterval = null;

    function updateDisplay() {
        const m = Math.floor(timeLeft / 60);
        const s = timeLeft % 60;
        timerDisplay.innerText = `${m.toString().padStart(2, '0')}:${s.toString().padStart(2, '0')}`;
    }

    async function finishSession() {
        clearInterval(timerInterval);
        timerDisplay.innerText = "00:00";
        try {
            const res = await fetch(`/api/session/finish/${sessionId}`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                // Redirect to dashboard and trigger reflection popup
                window.location.href = `/dashboard?reflection_session_id=${sessionId}`;
            }
        } catch (err) {
            console.error("Error finishing session", err);
            // Fallback redirect
            window.location.href = '/dashboard';
        }
    }

    async function cancelSession() {
        clearInterval(timerInterval);
        try {
            await fetch(`/api/session/cancel/${sessionId}`, { method: 'POST' });
        } catch (err) {
            console.error("Error cancelling session", err);
        }
        window.location.href = '/dashboard';
    }

    cancelBtn.addEventListener('click', () => {
        if (confirm("Are you sure you want to cancel this session? Your progress will not be saved.")) {
            cancelSession();
        }
    });

    updateDisplay();
    timerInterval = setInterval(() => {
        timeLeft--;
        updateDisplay();

        if (timeLeft <= 0) {
            finishSession();
        }
    }, 1000);
});
