const DashboardTabs = {
    switchTab(tabId) {
        // Hide all contents
        document.getElementById('todayContent').style.display = 'none';
        document.getElementById('insightsContent').style.display = 'none';
        document.getElementById('historyContent').style.display = 'none';

        // Remove active class from all tabs
        document.getElementById('tabToday').classList.remove('active-tab');
        document.getElementById('tabInsights').classList.remove('active-tab');
        document.getElementById('tabHistory').classList.remove('active-tab');

        // Show selected content and set active tab
        document.getElementById(tabId + 'Content').style.display = 'block';

        let tabBtnId = '';
        if (tabId === 'today') tabBtnId = 'tabToday';
        else if (tabId === 'insights') tabBtnId = 'tabInsights';
        else if (tabId === 'history') tabBtnId = 'tabHistory';

        document.getElementById(tabBtnId).classList.add('active-tab');

        // Scroll to top
        window.scrollTo({ top: 0, behavior: 'smooth' });
    }
};

window.DashboardTabs = DashboardTabs;
