const API_BASE = '/api';

async function fetchModels() {
    try {
        const response = await fetch(`${API_BASE}/free-models`);
        const data = await response.json();
        return data.models;
    } catch (error) {
        console.error('Error fetching models:', error);
        return [];
    }
}

async function addModel() {
    const input = document.getElementById('modelInput');
    const modelName = input.value.trim();
    
    if (!modelName) {
        showMessage('Please enter a model name', 'error');
        return;
    }
    
    try {
        const response = await fetch(`${API_BASE}/free-models`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ model_name: modelName }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add model');
        }
        
        const data = await response.json();
        input.value = '';
        renderModels(data.models);
        showMessage('Model added successfully', 'success');
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

async function removeModel(modelName) {
    try {
        const response = await fetch(`${API_BASE}/free-models/${encodeURIComponent(modelName)}`, {
            method: 'DELETE',
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to remove model');
        }
        
        const data = await response.json();
        renderModels(data.models);
        showMessage('Model removed successfully', 'success');
    } catch (error) {
        showMessage(error.message, 'error');
    }
}

function renderModels(models) {
    const container = document.getElementById('modelsList');
    
    if (models.length === 0) {
        container.innerHTML = '<p class="no-models">No free models configured</p>';
        return;
    }
    
    container.innerHTML = models.map(model => `
        <div class="model-item">
            <span class="model-name">${escapeHtml(model)}</span>
            <button class="delete-btn" onclick="removeModel('${escapeHtml(model)}')">Remove</button>
        </div>
    `).join('');
}

function showMessage(text, type) {
    const messageEl = document.getElementById('message');
    messageEl.textContent = text;
    messageEl.className = `message ${type}`;
    messageEl.style.display = 'block';
    
    setTimeout(() => {
        messageEl.style.display = 'none';
    }, 3000);
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Load models on page load
document.addEventListener('DOMContentLoaded', async () => {
    const models = await fetchModels();
    renderModels(models);
});

// Allow adding model with Enter key
document.getElementById('modelInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter') {
        addModel();
    }
});
