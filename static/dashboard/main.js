// Personal Dashboard Logic (T007 - T011)

async function fetchData(endpoint, containerId, renderFn) {
    const container = document.getElementById(containerId);
    try {
        const response = await fetch(`/dashboard/${endpoint}`);
        const data = await response.json();
        renderFn(data, container);
    } catch (error) {
        console.error(`Failed to fetch ${endpoint}:`, error);
        container.innerHTML = `<p style="color: #ef4444; font-size: 0.875rem;">Error loading ${endpoint}.</p>`;
    }
}

function renderJobCards(data, container) {
    const jobs = data.jobs || [];
    if (jobs.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No recent jobs found.</p>';
        return;
    }
    container.innerHTML = '';
    jobs.forEach(item => {
        const job = item.content;
        const card = document.createElement('div');
        card.className = 'job-card';
        card.style.cssText = `padding: 0.75rem; background: #2d3748; border-radius: 0.5rem; margin-bottom: 0.5rem; cursor: pointer; border: 1px solid transparent; transition: all 0.2s ease;`;
        card.innerHTML = `<h3 style="font-size: 0.875rem; font-weight: 600; color: #ffffff;">${job.title || 'Role'}</h3><p style="font-size: 0.75rem; color: #a0aec0;">${job.company || 'Company'}</p>`;
        card.onclick = () => job.url && window.open(job.url, '_blank');
        container.appendChild(card);
    });
}

function renderSkills(data, container) {
    const skills = data.skills || [];
    if (skills.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No skill gaps analyzed yet.</p>';
        return;
    }
    container.innerHTML = '';
    skills.forEach(report => {
        const div = document.createElement('div');
        div.style.cssText = 'margin-bottom: 1rem; border-left: 2px solid #4f46e5; padding-left: 0.75rem;';
        div.innerHTML = `
            <p style="font-size: 0.875rem; font-weight: 600; color: #fff;">${report.job_title}</p>
            <p style="font-size: 0.75rem; color: #10b981;">Matched: ${report.matched_skills?.length || 0}</p>
            <p style="font-size: 0.75rem; color: #f59e0b;">Missing: ${report.missing_skills?.length || 0}</p>
        `;
        container.appendChild(div);
    });
}

function renderSkillChart(data, container) {
    const skills = data.trending_skills || [];
    if (skills.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No skill data available.</p>';
        return;
    }
    container.innerHTML = '';
    const maxCount = Math.max(...skills.map(s => s.count));

    skills.forEach(skill => {
        const percentage = (skill.count / maxCount) * 100;
        const div = document.createElement('div');
        div.style.cssText = 'margin-bottom: 0.75rem;';
        div.innerHTML = `
            <div style="display: flex; justify-content: space-between; font-size: 0.75rem; margin-bottom: 0.25rem;">
                <span style="color: #fff; font-weight: 500;">${skill.name}</span>
                <span style="color: var(--text-muted);">${skill.count}</span>
            </div>
            <div style="width: 100%; height: 6px; background: #374151; border-radius: 3px; overflow: hidden;">
                <div style="width: ${percentage}%; height: 100%; background: #4f46e5; border-radius: 3px;"></div>
            </div>
        `;
        container.appendChild(div);
    });
}

function renderInterviews(data, container) {
    const history = data.interviews || [];
    if (history.length === 0) {
        container.innerHTML = '<p style="color: var(--text-muted); font-size: 0.875rem;">No mock interviews completed.</p>';
        return;
    }
    container.innerHTML = '';
    history.forEach(item => {
        const div = document.createElement('div');
        div.style.cssText = 'margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 1px solid #374151;';
        div.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 0.875rem; font-weight: 600; color: #fff;">${item.job_title}</span>
                <span style="font-size: 0.75rem; font-weight: 700; color: #10b981;">Score: ${item.score}/10</span>
            </div>
            <p style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">${item.feedback || 'Practice session recorded.'}</p>
        `;
        container.appendChild(div);
    });
}

// Initial load
document.addEventListener('DOMContentLoaded', () => {
    fetchData('jobs', 'jobs-container', renderJobCards);
    fetchData('analytics/skills', 'analytics-container', renderSkillChart);
    fetchData('notifications', 'notifications-container', renderNotifications);
    fetchData('interviews', 'interviews-container', renderInterviews);
});
