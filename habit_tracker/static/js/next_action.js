/**
 * Primary Action Zone - Behavior Decision Engine Frontend
 * Handles fetching and starting the next recommended habit session.
 */

document.addEventListener('DOMContentLoaded', () => {
    fetchNextAction();
    checkReflectionPopup();
});

function checkReflectionPopup() {
    const urlParams = new URLSearchParams(window.location.search);
    const reflectionSessionId = urlParams.get('reflection_session_id');
    if (reflectionSessionId) {
        const modal = document.getElementById('reflectionModal');
        if (modal) {
            modal.setAttribute('data-session-id', reflectionSessionId);
            modal.classList.add('active');
        }
    }
}

async function submitReflection(type) {
    const modal = document.getElementById('reflectionModal');
    const sessionId = modal.getAttribute('data-session-id');

    if (!sessionId) return;

    try {
        await fetch(`/api/session/reflection/${sessionId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ reflection: type })
        });

        // Remove param from URL without reloading
        const url = new URL(window.location);
        url.searchParams.delete('reflection_session_id');
        window.history.replaceState({}, '', url);

        modal.classList.remove('active');

        if (window.Dashboard && window.Dashboard.showToast) {
            window.Dashboard.showToast('Reflection saved!', 'success');
        }
    } catch (err) {
        console.error('Error submitting reflection:', err);
    }
}


async function fetchNextAction() {
    const zone = document.getElementById('nextActionZone');
    const title = document.getElementById('nextActionTitle');
    const prob = document.getElementById('nextActionProbability');
    const windowEl = document.getElementById('nextActionWindow');
    const reason = document.getElementById('nextActionReason');
    const startBtn = document.getElementById('startSessionBtn');

    try {
        const res = await fetch('/api/next-action');
        const data = await res.json();

        if (data.habit_id || data.next_action) {
            zone.style.display = 'block';
            title.innerText = data.next_action;
            windowEl.innerText = data.window;
            reason.innerText = data.reason;

            if (data.success_probability !== null) {
                prob.innerText = `${data.success_probability}% Success Chance`;
                prob.style.display = 'inline-block';

                // Color coding probability
                prob.className = 'prob-tag';
                if (data.success_probability >= 70) prob.classList.add('prob-high');
                else if (data.success_probability >= 40) prob.classList.add('prob-mid');
                else prob.classList.add('prob-low');
            } else {
                prob.style.display = 'none';
            }

            if (data.habit_id) {
                startBtn.onclick = () => startSession(data.habit_id);
                startBtn.innerHTML = `<span>🚀</span> ${data.cta_label}`;
                startBtn.style.display = 'flex';
            } else {
                startBtn.style.display = 'none';
            }
        }
    } catch (err) {
        console.error('Error fetching next action:', err);
    }
}

async function startSession(habitId) {
    const startBtn = document.getElementById('startSessionBtn');

    try {
        startBtn.disabled = true;
        startBtn.innerHTML = `<span>⏳</span> Starting...`;

        const res = await fetch(`/api/session/start/${habitId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        const data = await res.json();

        if (data.status === 'started' || data.session_id) {
            // Redirect to session page
            window.location.href = `/session/${data.session_id}`;
        }
    } catch (err) {
        console.error('Error starting session:', err);
        startBtn.disabled = false;
        startBtn.innerHTML = `<span>🚀</span> Start Session`;
    }
}
