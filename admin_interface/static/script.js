const API_BASE = '/api';

async function fetchModels() {
    try {
        console.log('[DEBUG] Fetching free models from API...');
        const response = await fetch(`${API_BASE}/free-models`);
        const data = await response.json();
        console.log('[DEBUG] Free models received:', data.models);
        return data.models;
    } catch (error) {
        console.error('[DEBUG] Error fetching models:', error);
        return [];
    }
}

async function addModel() {
    const nameInput = document.getElementById('modelName');
    const aliasInput = document.getElementById('modelAlias');
    const descInput = document.getElementById('modelDescription');
    
    const modelName = nameInput.value.trim();
    const modelAlias = aliasInput.value.trim();
    const modelDescription = descInput.value.trim();
    
    if (!modelName || !modelAlias) {
        showMessage('Please enter model name and alias', 'error');
        return;
    }
    
    try {
        console.log('[DEBUG] Adding model:', { name: modelName, alias: modelAlias, description: modelDescription });
        const response = await fetch(`${API_BASE}/free-models`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ 
                name: modelName,
                alias: modelAlias,
                description: modelDescription
            }),
        });
        
        if (!response.ok) {
            const error = await response.json();
            throw new Error(error.detail || 'Failed to add model');
        }
        
        const data = await response.json();
        console.log('[DEBUG] Model added successfully:', data);
        nameInput.value = '';
        aliasInput.value = '';
        descInput.value = '';
        renderModels(data.models);
        showMessage('Model added successfully', 'success');
    } catch (error) {
        console.error('[DEBUG] Error adding model:', error);
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
            <div class="model-details">
                <span class="model-name">${escapeHtml(model.alias || model.name)}</span>
                <span class="model-id">${escapeHtml(model.name)}</span>
                ${model.description ? `<span class="model-description">${escapeHtml(model.description)}</span>` : ''}
            </div>
            <button class="delete-btn" onclick="removeModel('${escapeHtml(model.name)}')">Remove</button>
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
