// HabitFlow Dashboard Logic
// Encapsulated in a professional module structure

const Dashboard = {
    init() {
        this.initTodayPlan();
        this.initCharts();
        this.initNotifications();
        this.fetchSuggestions();
        this.fetchWeeklyReport();
        this.loadThemeSettings();
        this.bindEvents();
    },

    loadThemeSettings() {
        const mode = localStorage.getItem('theme') || 'light';
        const accent = localStorage.getItem('accent') || 'indigo';
        this.setThemeMode(mode);
        this.setAccent(accent, false);
    },

    bindEvents() {
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }
    },

    toggleTheme() {
        const currentMode = document.documentElement.getAttribute('data-theme') === 'dark' ? 'dark' : 'light';
        this.setThemeMode(currentMode === 'dark' ? 'light' : 'dark');
    },

    setThemeMode(mode) {
        const html = document.documentElement;
        const iconMoon = document.querySelector('.icon-moon');
        const iconSun = document.querySelector('.icon-sun');

        if (mode === 'dark') {
            html.setAttribute('data-theme', 'dark');
            localStorage.setItem('theme', 'dark');
            if (iconMoon) iconMoon.style.display = 'none';
            if (iconSun) iconSun.style.display = 'inline';
        } else {
            html.removeAttribute('data-theme');
            localStorage.setItem('theme', 'light');
            if (iconMoon) iconMoon.style.display = 'inline';
            if (iconSun) iconSun.style.display = 'none';
        }
    },

    setAccent(color, showNotify = true) {
        document.documentElement.setAttribute('data-accent', color);
        localStorage.setItem('accent', color);

        // Update active dot in UI
        document.querySelectorAll('.accent-dot').forEach(dot => {
            dot.classList.remove('active');
            if (dot.getAttribute('onclick').includes(`'${color}'`)) {
                dot.classList.add('active');
            }
        });

        if (showNotify) this.showToast(`Accent set to ${color}`, 'success');
    },

    openSettings() {
        document.getElementById('settingsModal').classList.add('active');
    },

    initTodayPlan() {
        const container = document.getElementById('todayTimeline');
        const timerLabel = document.getElementById('nextHabitTimer');
        const section = document.getElementById('today-section');

        if (!container || !window.todayHabits) return;
        section.style.display = 'block';

        const updateTimeline = () => {
            const now = new Date();
            const currentTimeVal = now.getHours() * 60 + now.getMinutes();

            let nextHabitDiff = Infinity;
            let nextHabitName = "";
            let hasUpcoming = false;
            let allFinished = true;

            let html = '';

            window.todayHabits.forEach(h => {
                const startTime = h.startTime || "09:00";
                const endTime = h.endTime || "09:30";
                const [startH, startM] = startTime.split(':').map(Number);
                const [endH, endM] = endTime.split(':').map(Number);
                const startVal = startH * 60 + startM;
                const endVal = endH * 60 + endM;

                let status = 'upcoming';
                let statusLabel = 'Upcoming';
                let statusClass = 'status-upcoming';

                if (h.completed) {
                    status = 'completed'; statusLabel = 'Completed'; statusClass = 'status-completed';
                } else if (currentTimeVal > endVal) {
                    status = 'missed'; statusLabel = 'Missed'; statusClass = 'status-missed';
                } else if (currentTimeVal >= startVal && currentTimeVal <= endVal) {
                    status = 'active'; statusLabel = 'Happening Now'; statusClass = 'status-active';
                    allFinished = false;
                } else {
                    allFinished = false; hasUpcoming = true;
                    const diff = startVal - currentTimeVal;
                    if (diff > 0 && diff < nextHabitDiff) {
                        nextHabitDiff = diff; nextHabitName = h.name;
                    }
                }

                const formatTime = (h, m) => {
                    const ampm = h >= 12 ? 'PM' : 'AM';
                    return `${h % 12 || 12}:${m.toString().padStart(2, '0')} ${ampm}`;
                };

                html += `
                    <div class="timeline-item ${statusClass}" id="timeline-habit-${h.id}">
                        <div class="timeline-time">${formatTime(startH, startM)}</div>
                        <div class="timeline-content">
                            <div class="timeline-row">
                                <span class="timeline-icon">${h.completed ? '✅' : '⚡'}</span>
                                <span class="timeline-name">${h.name}</span>
                                <span class="timeline-badge">${statusLabel}</span>
                            </div>
                        </div>
                        ${status === 'active' && !h.completed ? `
                        <button class="timeline-check-btn" onclick="Dashboard.toggleHabitFromTimeline(${h.id})">Mark Done</button>` : ''}
                        ${status === 'missed' && !h.completed ? `
                        <button class="timeline-reschedule-btn" onclick="Dashboard.promptReschedule(${h.id}, '${h.startTime}')">⏱ Reschedule</button>` : ''}
                    </div>
                `;
            });

            container.innerHTML = html;
            if (timerLabel) {
                if (allFinished && window.todayHabits.some(h => h.completed)) {
                    timerLabel.innerText = "All habits finished for today 🎉";
                    timerLabel.className = 'timer-label completed';
                } else if (nextHabitDiff !== Infinity) {
                    const h = Math.floor(nextHabitDiff / 60);
                    const m = nextHabitDiff % 60;
                    timerLabel.innerText = `Next: ${nextHabitName} in ${h > 0 ? h + 'h ' : ''}${m}m`;
                    timerLabel.className = 'timer-label upcoming';
                }
            }
        };

        updateTimeline();
        setInterval(updateTimeline, 60000);
        window.updateTodayTimeline = updateTimeline;
    },

    toggleHabitFromTimeline(habitId) {
        // Toggle and then reload to sync all UI components (badges, buttons, timeline)
        const btn = document.querySelector(`button[data-habit-id="${habitId}"]`);
        if (btn) {
            btn.click();
            setTimeout(() => window.location.reload(), 1000);
        }
    },

    async promptReschedule(habitId, currentStartTime) {
        const newTime = prompt("Enter new start time (HH:MM) for today:", currentStartTime || "12:00");
        if (!newTime || !/^\d{2}:\d{2}$/.test(newTime)) return;

        try {
            const res = await fetch(`/api/habits/${habitId}/reschedule`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ new_time: newTime })
            });
            if ((await res.json()).success) window.location.reload();
        } catch (err) { console.error(err); }
    },

    initCharts() {
        if (!window.Chart) return;

        // Weekly Bar Chart
        if (document.getElementById('weeklyChart')) {
            new Chart(document.getElementById('weeklyChart'), {
                type: 'bar',
                data: {
                    labels: window.weeklyLabels,
                    datasets: [{
                        label: 'Habits Completed',
                        data: window.weeklyData,
                        backgroundColor: '#6366f1',
                        borderRadius: 4
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Pie Chart
        if (document.getElementById('pieChart')) {
            new Chart(document.getElementById('pieChart'), {
                type: 'doughnut',
                data: {
                    labels: window.habitLabels,
                    datasets: [{
                        data: window.habitData,
                        backgroundColor: ['#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', '#9966FF', '#FF9F40']
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }

        // Monthly Chart
        if (document.getElementById('monthlyChart')) {
            new Chart(document.getElementById('monthlyChart'), {
                type: 'line',
                data: {
                    labels: window.monthlyLabels,
                    datasets: [{
                        label: 'Check-ins',
                        data: window.monthlyValues,
                        borderColor: '#ec4899',
                        tension: 0.4,
                        fill: true,
                        backgroundColor: 'rgba(236, 72, 153, 0.1)'
                    }]
                },
                options: { responsive: true, maintainAspectRatio: false }
            });
        }
    },

    initNotifications() {
        if (Notification.permission !== "granted") Notification.requestPermission();
    },

    async fetchSuggestions() {
        try {
            const res = await fetch('/api/suggestions');
            const data = await res.json();
            const container = document.getElementById('suggestionsList');
            const coachCorner = document.getElementById('coachCorner');
            if (container && data.suggestions?.length > 0) {
                coachCorner.style.display = 'block';
                container.innerHTML = data.suggestions.map(s => `
                    <div class="suggestion-card" id="suggestion-${s.id}">
                        <div class="suggestion-content">
                            <div class="suggestion-message">${s.message}</div>
                            <div class="suggestion-meta">${s.habit_name}</div>
                        </div>
                        <div class="suggestion-actions">
                            <button class="btn-accept" onclick="Dashboard.acceptSuggestion(${s.id})">Accept</button>
                            <button class="btn-dismiss" onclick="Dashboard.dismissSuggestion(${s.id})">Dismiss</button>
                        </div>
                    </div>
                `).join('');
            } else if (coachCorner) {
                coachCorner.style.display = 'none';
            }
        } catch (err) { console.error('Error fetching suggestions:', err); }
    },

    async dismissSuggestion(id) {
        try {
            const res = await fetch(`/api/suggestions/${id}/dismiss`, { method: 'POST' });
            if ((await res.json()).success) {
                document.getElementById(`suggestion-${id}`).remove();
                if (document.getElementById('suggestionsList').children.length === 0) {
                    document.getElementById('coachCorner').style.display = 'none';
                }
            }
        } catch (err) { console.error(err); }
    },

    async acceptSuggestion(id) {
        try {
            const btn = document.querySelector(`#suggestion-${id} .btn-accept`);
            btn.disabled = true; btn.innerText = 'Applying...';
            const res = await fetch(`/api/suggestions/${id}/accept`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Suggestion applied!', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showToast(data.error || 'Failed', 'error');
                btn.disabled = false; btn.innerText = 'Accept';
            }
        } catch (err) { console.error(err); }
    },

    async fetchWeeklyReport() {
        try {
            const res = await fetch('/api/weekly-report');
            const data = await res.json();
            if (data?.report) {
                const r = data.report;
                const section = document.getElementById('weekly-review-section');
                if (section) section.style.display = 'block';

                const set = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };

                set('review-dates', `${new Date(r.week_start).toLocaleDateString()} - ${new Date(r.week_end).toLocaleDateString()}`);
                set('review-feedback', r.feedback);
                set('review-rate', r.completion_rate + '%');

                const pBar = document.getElementById('review-progress-bar');
                if (pBar) {
                    pBar.style.width = r.completion_rate + '%';
                    pBar.style.backgroundColor = r.completion_rate >= 80 ? '#10b981' : (r.completion_rate >= 50 ? '#f59e0b' : '#ef4444');
                }

                set('review-xp', `+${r.xp_awarded} XP`);
                set('review-strongest', r.strongest_habit);
                set('review-weakest', r.weakest_habit);
                set('review-suggestion', r.suggestion);

                const list = document.getElementById('review-plan-list');
                if (list) list.innerHTML = r.next_week_plan.map(p => `<li>${p}</li>`).join('') || '<li>No goals generated.</li>';
            }
        } catch (err) { console.error(err); }
    },

    async applyWeekPlan() {
        const btn = document.getElementById('btn-apply-plan');
        if (btn) { btn.disabled = true; btn.innerText = "Applying..."; }
        try {
            const res = await fetch('/api/weekly-report/apply-plan', { method: 'POST' });
            if ((await res.json()).success) {
                this.showToast('Plan applied!', 'success');
                setTimeout(() => window.location.reload(), 1000);
            }
        } catch (err) { console.error(err); if (btn) btn.disabled = false; }
    },

    async toggleHabit(btn, habitId) {
        try {
            btn.disabled = true;
            const res = await fetch(`/api/log_habit/${habitId}`);
            const data = await res.json();

            if (data.success) {
                const isComp = data.status === 'completed';
                this.showToast(isComp ? 'Habit logged!' : 'Log removed', 'success');
                this.updateXPUI(data.new_xp, data.new_level);
                if (data.achievements_unlocked?.length > 0) this.showBadgePopup(data.achievements_unlocked[0]);

                // Reload to accurately update all Jinja-rendered badges and state
                setTimeout(() => window.location.reload(), 1000);
            }
            btn.disabled = false;
        } catch (err) { console.error(err); btn.disabled = false; }
    },

    async markLate(habitId) {
        try {
            const res = await fetch(`/api/habits/${habitId}/late`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast(`Late check-in! +${data.xp_gained} XP`, 'success');
                setTimeout(() => window.location.reload(), 1000);
            }
        } catch (err) { console.error(err); }
    },

    async markPartial(habitId) {
        try {
            const res = await fetch(`/api/habits/${habitId}/partial`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast(`Partial check-in! +${data.xp_gained} XP`, 'success');
                setTimeout(() => window.location.reload(), 1000);
            }
        } catch (err) { console.error(err); }
    },

    async recoverStreak(habitId) {
        try {
            const res = await fetch(`/api/habits/${habitId}/recover`, { method: 'POST' });
            const data = await res.json();
            if (data.success) {
                this.showToast('Streak recovered! 🛡️', 'success');
                setTimeout(() => window.location.reload(), 1000);
            } else {
                this.showToast(data.error || 'Failed to recover', 'error');
            }
        } catch (err) { console.error(err); }
    },

    showToast(message, type = 'success') {
        const container = document.querySelector('.flash-messages') || document.body;
        const toast = document.createElement('div');
        toast.className = `flash-message ${type}`;
        toast.style.cssText = 'position:fixed; bottom:20px; right:20px; padding:12px 24px; border-radius:8px; color:white; font-weight:600; z-index:9999; animation: slideIn 0.3s ease-out;';
        toast.style.backgroundColor = type === 'success' ? '#10b981' : '#ef4444';
        toast.innerText = message;
        container.appendChild(toast);
        setTimeout(() => {
            toast.style.opacity = '0';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    },

    updateXPUI(newXP, newLevel) {
        const progress = newXP % 100;
        const fill = document.querySelector('.xp-fill');
        const text = document.querySelector('.xp-current');
        const lvl = document.querySelector('.level-badge');
        if (fill) fill.style.width = `${progress}%`;
        if (text) text.innerText = `${progress} / 100`;
        if (lvl) lvl.innerText = `Lvl ${newLevel}`;
    },

    showBadgePopup(badge) {
        document.getElementById('badgeIcon').innerText = badge.icon;
        document.getElementById('badgeTitle').innerText = badge.name;
        document.getElementById('badgeDesc').innerText = badge.description;
        document.getElementById('badgeModal').classList.add('active');
        if (window.confetti) window.confetti({ particleCount: 150, spread: 70, origin: { y: 0.6 } });
    },

    openEditHabit(btn) {
        const id = btn.getAttribute('data-id');
        const name = btn.getAttribute('data-name');
        const start = btn.getAttribute('data-start');
        const end = btn.getAttribute('data-end');
        const color = btn.getAttribute('data-color');
        const icon = btn.getAttribute('data-icon');

        document.getElementById('edit_habit_id').value = id;
        document.getElementById('edit_name').value = name;
        document.getElementById('edit_start_time').value = start || '';
        document.getElementById('edit_end_time').value = end || '';
        document.getElementById('edit_color').value = color || 'blue';
        document.getElementById('edit_icon').value = icon || '⭐';
        document.getElementById('editHabitModal').classList.add('active');
    },

    closeModal(modalId) {
        const modal = document.getElementById(modalId);
        if (modal) modal.classList.remove('active');
    }
};

Dashboard.init();
window.Dashboard = Dashboard; // Export for inline onclick handlers
