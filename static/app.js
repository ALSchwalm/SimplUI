// Application State
const state = {
  comfyUrl: '',
  workflows: [],
  sliders: {},
  currentWorkflowName: '',
  currentWorkflowJson: null,
  isConnected: false,
  isGenerating: false,
  activeTab: 'settings',
  batchCount: 1,
  history: [], // Generated images history
  activePreviews: {}, // Active preview images by index
};

// DOM Elements
const elements = {
  connectionStatus: document.getElementById('connection-status'),
  advancedToggle: document.getElementById('advanced-toggle'),
  advancedSidebar: document.getElementById('advanced-sidebar'),
  workflowSelect: document.getElementById('workflow-select'),
  promptInput: document.getElementById('prompt-input'),
  generateBtn: document.getElementById('generate-btn'),
  generateBtnText: document.getElementById('generate-btn-text'),
  galleryGrid: document.getElementById('gallery-grid'),
  galleryEmptyState: document.getElementById('gallery-empty-state'),
  galleryProgress: document.getElementById('gallery-progress'),
  progressBarFill: document.getElementById('progress-bar-fill'),
  progressText: document.getElementById('progress-text'),
  batchCountSlider: document.getElementById('batch-count-slider'),
  batchCountValue: document.getElementById('batch-count-value'),
  dynamicControls: document.getElementById('dynamic-controls-container'),
  historyGrid: document.getElementById('history-grid'),
  tabSettings: document.getElementById('tab-settings'),
  tabHistory: document.getElementById('tab-history'),
  tabButtons: document.querySelectorAll('.tab-btn'),
};

// Initialize App
async function init() {
  setupEventListeners();
  await fetchConfig();
}

// Event Listeners Setup
function setupEventListeners() {
  // Advanced Sidebar Toggle
  elements.advancedToggle.addEventListener('change', (e) => {
    if (e.target.checked) {
      elements.advancedSidebar.classList.remove('collapsed');
    } else {
      elements.advancedSidebar.classList.add('collapsed');
    }
  });

  // Sidebar Tabs Switching
  elements.tabButtons.forEach(button => {
    button.addEventListener('click', () => {
      const tabName = button.getAttribute('data-tab');
      switchTab(tabName);
    });
  });

  // Workflow Selection Change
  elements.workflowSelect.addEventListener('change', async (e) => {
    const name = e.target.value;
    await selectWorkflow(name);
  });

  // Batch Count Slider
  elements.batchCountSlider.addEventListener('input', (e) => {
    state.batchCount = parseInt(e.target.value, 10);
    elements.batchCountValue.textContent = state.batchCount;
  });

  // Keyboard shortcut Ctrl+Enter / Cmd+Enter on prompt input
  elements.promptInput.addEventListener('keydown', (e) => {
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
      e.preventDefault();
      handleGenerateClick();
    }
  });

  // Generate Button Click
  elements.generateBtn.addEventListener('click', handleGenerateClick);
}

// Tab Switching logic
function switchTab(tabName) {
  state.activeTab = tabName;
  elements.tabButtons.forEach(btn => {
    if (btn.getAttribute('data-tab') === tabName) {
      btn.classList.add('active');
    } else {
      btn.classList.remove('active');
    }
  });

  if (tabName === 'settings') {
    elements.tabSettings.classList.remove('hidden');
    elements.tabHistory.classList.add('hidden');
  } else {
    elements.tabSettings.classList.add('hidden');
    elements.tabHistory.classList.remove('hidden');
    renderHistory();
  }
}

// Fetch App Config from Backend
async function fetchConfig() {
  try {
    const res = await fetch('/api/config');
    if (!res.ok) throw new Error('Failed to fetch config');
    
    const data = await res.json();
    state.comfyUrl = data.comfy_url;
    state.workflows = data.workflows;
    state.sliders = data.sliders;

    // Populate Workflows Dropdown
    populateWorkflows();
    
    // Check connection to ComfyUI
    await checkConnection();
    // Periodically check connection
    setInterval(checkConnection, 15000);

    // Load initial workflow
    if (state.workflows.length > 0) {
      await selectWorkflow(state.workflows[0].name);
    }
  } catch (error) {
    console.error('Config initialization error:', error);
    updateConnectionUI(false, 'Error reaching backend');
  }
}

// Populate Workflow dropdown
function populateWorkflows() {
  elements.workflowSelect.innerHTML = '';
  state.workflows.forEach(wf => {
    const option = document.createElement('option');
    option.value = wf.name;
    option.textContent = wf.name;
    elements.workflowSelect.appendChild(option);
  });
}

// Check Connection to ComfyUI
async function checkConnection() {
  if (!state.comfyUrl) {
    updateConnectionUI(false, 'No ComfyUI URL configured');
    return;
  }

  try {
    // Try to fetch object_info to verify connection
    const res = await fetch(`${state.comfyUrl}/object_info`, {
      method: 'GET',
      mode: 'cors'
    });
    
    if (res.ok) {
      state.isConnected = true;
      updateConnectionUI(true, 'Connected to ComfyUI');
    } else {
      throw new Error();
    }
  } catch (e) {
    state.isConnected = false;
    updateConnectionUI(false, 'ComfyUI Server Offline');
  }
}

// Update connection indicator UI
function updateConnectionUI(connected, text) {
  if (connected) {
    elements.connectionStatus.className = 'connection-status connected';
    elements.connectionStatus.querySelector('.status-text').textContent = text;
  } else {
    elements.connectionStatus.className = 'connection-status disconnected';
    elements.connectionStatus.querySelector('.status-text').textContent = text;
  }
}

// Select Workflow
async function selectWorkflow(name) {
  state.currentWorkflowName = name;
  try {
    const res = await fetch(`/api/workflows/${encodeURIComponent(name)}`);
    if (!res.ok) throw new Error('Failed to load workflow JSON');
    
    state.currentWorkflowJson = await res.json();
    
    // Update default prompt in prompt field
    const defaultPrompt = getPromptDefaultValue(state.currentWorkflowJson);
    if (defaultPrompt !== null) {
      elements.promptInput.value = defaultPrompt;
    }

    // Populate dynamic controls (to be implemented in Phase 3)
    renderDynamicControls();

  } catch (error) {
    console.error('Error loading workflow:', error);
  }
}

// Parse default prompt from workflow JSON
function getPromptDefaultValue(workflow) {
  if (!workflow) return null;
  // Search for any PrimitiveString or prompt input node titled "Prompt" or with "text" inputs
  for (const nodeId in workflow) {
    const node = workflow[nodeId];
    if (node._meta && node._meta.title === 'Prompt' && node.inputs && node.inputs.text !== undefined) {
      return node.inputs.text;
    }
  }
  return null;
}

// Render dynamic settings controls (placeholder for Phase 3)
function renderDynamicControls() {
  elements.dynamicControls.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">Advanced widgets will load here...</p>';
}

// Render history (placeholder for Phase 3)
function renderHistory() {
  if (state.history.length === 0) {
    elements.historyGrid.innerHTML = '<p style="grid-column: span 2; text-align: center; color: var(--text-muted); font-size: 13px; padding: 20px 0;">No history yet</p>';
    return;
  }
  
  elements.historyGrid.innerHTML = '';
  state.history.forEach(imgSrc => {
    const div = document.createElement('div');
    div.className = 'history-item';
    const img = document.createElement('img');
    img.src = imgSrc;
    div.appendChild(img);
    elements.historyGrid.appendChild(div);
  });
}

// Handle Generate Button Click (skeletal placeholder for Phase 3)
function handleGenerateClick() {
  console.log('Generate click handler (not yet connected to ComfyUI websocket/prompt API)');
}

// Run on page load
window.addEventListener('DOMContentLoaded', init);
