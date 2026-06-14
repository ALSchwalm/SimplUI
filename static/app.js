// Application State
const state = {
  comfyUrl: '',
  useProxy: false,
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
  activePrompts: {}, // promptId -> { index: i, resolve: resolveFunc }
  currentlyExecutingPromptId: null,
  lastExecutingPromptId: null,
  lightboxImages: [],
  lightboxIndex: -1,
  lightboxSource: '',
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
  lightbox: document.getElementById('lightbox'),
  lightboxClose: document.getElementById('lightbox-close'),
  lightboxImage: document.getElementById('lightbox-image'),
  lightboxLeftZone: document.getElementById('lightbox-left-zone'),
  lightboxRightZone: document.getElementById('lightbox-right-zone'),
};

// Initialize App
async function init() {
  localStorage.clear();
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

  // Lightbox click zones
  elements.lightboxLeftZone.addEventListener('click', lightboxPrev);
  elements.lightboxRightZone.addEventListener('click', lightboxNext);
  
  // Close button
  elements.lightboxClose.addEventListener('click', () => closeLightbox(true));
  
  // Close by clicking backdrop
  elements.lightbox.addEventListener('click', (e) => {
    if (e.target === elements.lightbox) {
      closeLightbox(true);
    }
  });
  
  // Gallery item click to open lightbox
  elements.galleryGrid.addEventListener('click', (e) => {
    const clickedImg = e.target.closest('img');
    if (!clickedImg) return;
    
    // Check if the image belongs to a slot that is still generating (has preview-badge)
    const slot = clickedImg.closest('.gallery-item');
    if (slot && slot.querySelector('.preview-badge')) {
      return; // Do nothing for previews
    }
    
    openLightbox('gallery', clickedImg.getAttribute('src'));
  });
  
  // History item click to open lightbox
  elements.historyGrid.addEventListener('click', (e) => {
    const clickedImg = e.target.closest('img');
    if (!clickedImg) return;
    
    openLightbox('history', clickedImg.getAttribute('src'));
  });
  
  // Keyboard navigation
  document.addEventListener('keydown', (e) => {
    if (elements.lightbox.classList.contains('hidden')) return;
    
    if (e.key === 'ArrowLeft') {
      e.preventDefault();
      lightboxPrev();
    } else if (e.key === 'ArrowRight') {
      e.preventDefault();
      lightboxNext();
    } else if (e.key === 'Escape') {
      e.preventDefault();
      closeLightbox(true);
    }
  });
  
  // Popstate event for mobile back button integration
  window.addEventListener('popstate', () => {
    if (!elements.lightbox.classList.contains('hidden')) {
      closeLightbox(false);
    }
  });

  // Warn user before navigating away/reloading
  window.addEventListener('beforeunload', (e) => {
    e.preventDefault();
    e.returnValue = '';
  });
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

// Helper for fetching from ComfyUI with fallback proxy
async function fetchFromComfy(path, options = {}) {
  const url = state.useProxy ? `/comfy-proxy/${path}` : `${state.comfyUrl}/${path}`;
  try {
    const res = await fetch(url, { ...options, mode: 'cors' });
    return res;
  } catch (error) {
    if (!state.useProxy) {
      console.warn(`Direct connection to ComfyUI failed at ${url}. Falling back to proxy.`);
      state.useProxy = true;
      connectWebSocket();
      const fallbackUrl = `/comfy-proxy/${path}`;
      try {
        const fallbackRes = await fetch(fallbackUrl, options);
        return fallbackRes;
      } catch (fallbackError) {
        throw fallbackError;
      }
    }
    throw error;
  }
}

// Check Connection to ComfyUI
async function checkConnection() {
  if (!state.comfyUrl) {
    updateConnectionUI(false, 'No ComfyUI URL configured');
    return;
  }

  try {
    // Try to fetch object_info to verify connection
    const res = await fetchFromComfy('object_info', {
      method: 'GET'
    });
    
    if (res.ok) {
      state.objectInfo = await res.json();
      state.isConnected = true;
      const label = state.useProxy ? 'Connected to ComfyUI (via Proxy)' : 'Connected to ComfyUI';
      updateConnectionUI(true, label);
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

// Preset tables
const ASPECT_RATIOS = ["1:1", "4:3", "3:4", "16:9", "9:16", "3:2", "2:3", "7:9", "9:7", "1:2", "2:1"];
const PIXEL_COUNTS = ["0.25M", "0.5M", "1M", "1.5M", "2M"];

function calculateDimensions(aspectRatioStr, pixelCountM) {
  const totalPixels = pixelCountM * 1024 * 1024;
  let ratio = 1.0;
  try {
    const parts = aspectRatioStr.split(":");
    const wPart = parseFloat(parts[0]);
    const hPart = parseFloat(parts[1]);
    if (wPart && hPart) ratio = wPart / hPart;
  } catch (e) {
    ratio = 1.0;
  }
  
  const height = Math.sqrt(totalPixels / ratio);
  const width = height * ratio;
  
  const roundTo64 = (val) => Math.max(64, Math.round(val / 64.0) * 64);
  return {
    width: roundTo64(width),
    height: roundTo64(height)
  };
}

function findNearestPreset(width, height) {
  let bestDist = Infinity;
  let bestMatch = { ar: "1:1", pc: "1M" };
  
  for (const ar of ASPECT_RATIOS) {
    for (const pc of PIXEL_COUNTS) {
      const pcVal = parseFloat(pc.replace("M", ""));
      const dims = calculateDimensions(ar, pcVal);
      const dist = Math.sqrt(Math.pow(dims.width - width, 2) + Math.pow(dims.height - height, 2));
      if (dist < bestDist) {
        bestDist = dist;
        bestMatch = { ar, pc };
      }
    }
  }
  return bestMatch;
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

    // Render dynamic inputs in sidebar
    renderDynamicControls();

  } catch (error) {
    console.error('Error loading workflow:', error);
  }
}

// Parse default prompt from workflow JSON
function getPromptDefaultValue(workflow) {
  if (!workflow) return null;
  for (const nodeId in workflow) {
    const node = workflow[nodeId];
    if (node._meta && node._meta.title === 'Prompt' && node.inputs) {
      if (node.inputs.text !== undefined) return node.inputs.text;
      if (node.inputs.string !== undefined) return node.inputs.string;
      if (node.inputs.value !== undefined) return node.inputs.value;
    }
  }
  return null;
}

// Extract inputs from workflow JSON
function extractWorkflowInputs(workflow, objectInfo, slidersConfig) {
  const extracted = [];
  if (!workflow) return extracted;
  
  for (const nodeId in workflow) {
    const nodeData = workflow[nodeId];
    const title = (nodeData._meta && nodeData._meta.title) || `Node ${nodeId}`;
    const classType = nodeData.class_type || '';
    const nodeInputs = nodeData.inputs || {};
    const inputs = [];
    
    const isPromptNode = title.toLowerCase() === 'prompt';
    const hasWidth = 'width' in nodeInputs;
    const hasHeight = 'height' in nodeInputs;
    
    const nodeDef = objectInfo ? objectInfo[classType] : null;
    
    if (hasWidth && hasHeight) {
      inputs.push({
        name: 'Dimensions',
        type: 'dimensions',
        width_name: 'width',
        height_name: 'height',
        width_value: nodeInputs['width'],
        height_value: nodeInputs['height']
      });
    }
    
    for (const name in nodeInputs) {
      const value = nodeInputs[name];
      if (Array.isArray(value)) continue; // link
      
      if (isPromptNode && ['text', 'string', 'value'].includes(name)) continue;
      if (hasWidth && hasHeight && ['width', 'height'].includes(name)) continue;
      
      let inputType = 'str';
      let options = null;
      let sliderParams = {};
      
      if (nodeDef) {
        let inputDef = null;
        if (nodeDef.input && nodeDef.input.required) {
          inputDef = nodeDef.input.required[name];
        }
        if (!inputDef && nodeDef.input && nodeDef.input.optional) {
          inputDef = nodeDef.input.optional[name];
        }
        
        if (Array.isArray(inputDef) && inputDef.length > 0) {
          if (Array.isArray(inputDef[0])) {
            inputType = 'enum';
            options = inputDef[0];
          } else if (inputDef.length > 1 && typeof inputDef[1] === 'object' && inputDef[1] !== null) {
            const meta = inputDef[1];
            if ('min' in meta && 'max' in meta) {
              sliderParams.min = meta.min;
              sliderParams.max = meta.max;
              if ('step' in meta) sliderParams.step = meta.step;
            }
          }
        }
      }
      
      if (inputType !== 'enum') {
        if (typeof value === 'boolean') {
          inputType = 'bool';
        } else if (typeof value === 'number') {
          if (name.toLowerCase().includes('seed')) {
            inputType = 'seed';
          } else {
            inputType = 'number';
            if (slidersConfig && slidersConfig[name]) {
              inputType = 'slider';
              Object.assign(sliderParams, slidersConfig[name]);
            } else if ('min' in sliderParams && 'max' in sliderParams) {
              inputType = 'slider';
            }
          }
        }
      }
      
      const inputData = { name, type: inputType, value };
      if (inputType === 'seed') {
        inputData.randomize = value === 0 || value === '0';
      }
      if (options) {
        inputData.options = options;
      }
      if (inputType === 'slider') {
        Object.assign(inputData, sliderParams);
      }
      inputs.push(inputData);
    }
    
    if (inputs.length > 0) {
      extracted.push({ node_id: nodeId, title, inputs });
    }
  }
  return extracted;
}

// Render dynamic settings controls
function renderDynamicControls() {
  const container = elements.dynamicControls;
  container.innerHTML = '';
  
  if (!state.currentWorkflowJson) {
    container.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">No workflow loaded.</p>';
    return;
  }
  
  // Load saved overrides for this workflow
  const savedOverridesKey = `simplui_overrides_${state.currentWorkflowName}`;
  let savedOverrides = {};
  try {
    const raw = localStorage.getItem(savedOverridesKey);
    if (raw) savedOverrides = JSON.parse(raw);
  } catch (e) {
    console.error('Failed to parse saved overrides', e);
  }
  state.overrides = savedOverrides;
  
  const extracted = extractWorkflowInputs(state.currentWorkflowJson, state.objectInfo, state.sliders);
  
  if (extracted.length === 0) {
    container.innerHTML = '<p style="color: var(--text-muted); font-size: 13px;">No configurable nodes found.</p>';
    return;
  }
  
  extracted.forEach(node => {
    const nodeSection = document.createElement('div');
    nodeSection.className = 'node-section';
    nodeSection.style.marginBottom = '20px';
    nodeSection.style.borderBottom = '1px solid rgba(255, 255, 255, 0.05)';
    nodeSection.style.paddingBottom = '15px';
    
    const nodeHeader = document.createElement('h3');
    nodeHeader.textContent = node.title;
    nodeHeader.style.fontSize = '14px';
    nodeHeader.style.fontWeight = '600';
    nodeHeader.style.color = 'var(--primary)';
    nodeHeader.style.marginBottom = '12px';
    nodeSection.appendChild(nodeHeader);
    
    const controlsList = document.createElement('div');
    controlsList.className = 'controls-list';
    controlsList.style.display = 'flex';
    controlsList.style.flexDirection = 'column';
    controlsList.style.gap = '12px';
    
    node.inputs.forEach(input => {
      const widget = createWidget(node.node_id, input);
      controlsList.appendChild(widget);
    });
    
    nodeSection.appendChild(controlsList);
    container.appendChild(nodeSection);
  });
}

function createWidget(nodeId, input) {
  const group = document.createElement('div');
  group.className = 'settings-group';
  
  const key = `${nodeId}.${input.name}`;
  let val = state.overrides[key] !== undefined ? state.overrides[key] : input.value;
  
  // Save initial value to overrides if not set
  if (state.overrides[key] === undefined && input.type !== 'dimensions') {
    state.overrides[key] = val;
  }
  
  if (input.type === 'dimensions') {
    // Width and height keys
    const wKey = `${nodeId}.${input.width_name}`;
    const hKey = `${nodeId}.${input.height_name}`;
    
    let wVal = state.overrides[wKey] !== undefined ? state.overrides[wKey] : input.width_value;
    let hVal = state.overrides[hKey] !== undefined ? state.overrides[hKey] : input.height_value;
    
    state.overrides[wKey] = wVal;
    state.overrides[hKey] = hVal;
    
    const isExactKey = `${nodeId}.Dimensions.isExact`;
    let isExact = state.overrides[isExactKey] === true;
    
    group.className = 'aspect-ratio-widget';
    
    group.innerHTML = `
      <div class="aspect-ratio-header">
        <label>Dimensions</label>
        <button class="toggle-mode-btn" id="toggle-dim-${nodeId}">${isExact ? 'Use Aspect Ratio' : 'Use Custom Pixels'}</button>
      </div>
      
      <div class="aspect-ratio-controls ${isExact ? 'hidden' : ''}" id="ar-controls-${nodeId}">
        <div class="aspect-ratio-row">
          <select class="form-control" id="ar-select-${nodeId}">
            ${ASPECT_RATIOS.map(ar => `<option value="${ar}">${ar}</option>`).join('')}
          </select>
          <select class="form-control" id="pc-select-${nodeId}">
            ${PIXEL_COUNTS.map(pc => `<option value="${pc}">${pc}</option>`).join('')}
          </select>
        </div>
      </div>
      
      <div class="exact-controls ${isExact ? '' : 'hidden'}" id="exact-controls-${nodeId}">
        <div class="aspect-ratio-row">
          <input type="number" class="form-control" id="width-input-${nodeId}" value="${wVal}" placeholder="Width" step="64">
          <input type="number" class="form-control" id="height-input-${nodeId}" value="${hVal}" placeholder="Height" step="64">
        </div>
      </div>
    `;
    
    // Add event listeners inside widget
    setTimeout(() => {
      const toggleBtn = document.getElementById(`toggle-dim-${nodeId}`);
      const arControls = document.getElementById(`ar-controls-${nodeId}`);
      const exactControls = document.getElementById(`exact-controls-${nodeId}`);
      const arSelect = document.getElementById(`ar-select-${nodeId}`);
      const pcSelect = document.getElementById(`pc-select-${nodeId}`);
      const wInput = document.getElementById(`width-input-${nodeId}`);
      const hInput = document.getElementById(`height-input-${nodeId}`);
      
      // Initialize preset
      const preset = findNearestPreset(wVal, hVal);
      arSelect.value = preset.ar;
      pcSelect.value = preset.pc;
      
      toggleBtn.addEventListener('click', () => {
        isExact = !isExact;
        state.overrides[isExactKey] = isExact;
        saveOverrides();
        
        toggleBtn.textContent = isExact ? 'Use Aspect Ratio' : 'Use Custom Pixels';
        if (isExact) {
          arControls.classList.add('hidden');
          exactControls.classList.remove('hidden');
        } else {
          arControls.classList.remove('hidden');
          exactControls.classList.add('hidden');
          updateDimsFromPresets();
        }
      });
      
      function updateDimsFromPresets() {
        const ar = arSelect.value;
        const pc = parseFloat(pcSelect.value.replace('M', ''));
        const dims = calculateDimensions(ar, pc);
        wInput.value = dims.width;
        hInput.value = dims.height;
        state.overrides[wKey] = dims.width;
        state.overrides[hKey] = dims.height;
        saveOverrides();
      }
      
      arSelect.addEventListener('change', updateDimsFromPresets);
      pcSelect.addEventListener('change', updateDimsFromPresets);
      
      wInput.addEventListener('change', (e) => {
        state.overrides[wKey] = parseInt(e.target.value, 10);
        saveOverrides();
      });
      
      hInput.addEventListener('change', (e) => {
        state.overrides[hKey] = parseInt(e.target.value, 10);
        saveOverrides();
      });
    }, 0);
    
    return group;
  }
  
  // Label
  const label = document.createElement('label');
  label.textContent = input.name;
  group.appendChild(label);
  
  if (input.type === 'enum') {
    const select = document.createElement('select');
    select.className = 'form-control';
    input.options.forEach(opt => {
      const option = document.createElement('option');
      option.value = opt;
      option.textContent = opt;
      if (opt === val) option.selected = true;
      select.appendChild(option);
    });
    select.addEventListener('change', (e) => {
      state.overrides[key] = e.target.value;
      saveOverrides();
    });
    group.appendChild(select);
  } else if (input.type === 'bool') {
    group.className = 'settings-group';
    label.className = 'checkbox-label';
    label.innerHTML = `
      <input type="checkbox" ${val ? 'checked' : ''}>
      ${input.name}
    `;
    const checkbox = label.querySelector('input');
    checkbox.addEventListener('change', (e) => {
      state.overrides[key] = e.target.checked;
      saveOverrides();
    });
  } else if (input.type === 'slider') {
    label.innerHTML = `${input.name}: <span id="val-${nodeId}-${input.name}">${val}</span>`;
    const range = document.createElement('input');
    range.type = 'range';
    range.className = 'form-range';
    range.style.width = '100%';
    range.min = input.min !== undefined ? input.min : 0;
    range.max = input.max !== undefined ? input.max : 100;
    range.step = input.step !== undefined ? input.step : 1;
    range.value = val;
    
    range.addEventListener('input', (e) => {
      document.getElementById(`val-${nodeId}-${input.name}`).textContent = e.target.value;
      state.overrides[key] = parseFloat(e.target.value);
      saveOverrides();
    });
    group.appendChild(range);
  } else if (input.type === 'seed') {
    group.className = 'seed-widget';
    
    const randomizeKey = `${key}.randomize`;
    let isRandom = state.overrides[randomizeKey] !== undefined ? state.overrides[randomizeKey] : input.randomize;
    state.overrides[randomizeKey] = isRandom;
    
    group.innerHTML = `
      <div class="seed-row">
        <label>Seed</label>
        <label class="checkbox-label">
          <input type="checkbox" id="randomize-${nodeId}" ${isRandom ? 'checked' : ''}>
          Randomize
        </label>
      </div>
      <input type="number" class="form-control ${isRandom ? 'hidden' : ''}" id="seed-input-${nodeId}" value="${val}">
    `;
    
    setTimeout(() => {
      const randCheck = document.getElementById(`randomize-${nodeId}`);
      const seedIn = document.getElementById(`seed-input-${nodeId}`);
      
      randCheck.addEventListener('change', (e) => {
        isRandom = e.target.checked;
        state.overrides[randomizeKey] = isRandom;
        saveOverrides();
        if (isRandom) {
          seedIn.classList.add('hidden');
        } else {
          seedIn.classList.remove('hidden');
        }
      });
      
      seedIn.addEventListener('change', (e) => {
        state.overrides[key] = parseInt(e.target.value, 10);
        saveOverrides();
      });
    }, 0);
  } else if (input.type === 'number') {
    const num = document.createElement('input');
    num.type = 'number';
    num.className = 'form-control';
    num.value = val;
    num.addEventListener('change', (e) => {
      state.overrides[key] = parseFloat(e.target.value);
      saveOverrides();
    });
    group.appendChild(num);
  } else {
    const text = document.createElement('input');
    text.type = 'text';
    text.className = 'form-control';
    text.value = val;
    text.addEventListener('change', (e) => {
      state.overrides[key] = e.target.value;
      saveOverrides();
    });
    group.appendChild(text);
  }
  
  return group;
}

function saveOverrides() {
  const savedOverridesKey = `simplui_overrides_${state.currentWorkflowName}`;
  localStorage.setItem(savedOverridesKey, JSON.stringify(state.overrides));
}

// Render history
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

// WebSocket client connection setup
state.clientId = generateUUID();
let ws = null;

function generateUUID() {
  return 'xxxxxxxx-xxxx-4xxx-yxxx-xxxxxxxxxxxx'.replace(/[xy]/g, function(c) {
    var r = Math.random() * 16 | 0, v = c == 'x' ? r : (r & 0x3 | 0x8);
    return v.toString(16);
  });
}

function getWebSocketUrl() {
  if (state.useProxy) {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    return `${protocol}//${window.location.host}/comfy-ws?clientId=${state.clientId}`;
  }
  if (!state.comfyUrl) return null;
  let url = state.comfyUrl;
  url = url.replace(/^http/, 'ws');
  return `${url}/ws?clientId=${state.clientId}`;
}

let wsHasOpened = false;

function connectWebSocket() {
  const url = getWebSocketUrl();
  if (!url) return;
  
  if (ws) {
    ws.onopen = null;
    ws.onmessage = null;
    ws.onerror = null;
    ws.onclose = null;
    try { ws.close(); } catch(e){}
  }
  
  console.log(`Connecting WebSocket: ${url}`);
  ws = new WebSocket(url);
  wsHasOpened = false;
  
  ws.onopen = () => {
    console.log('WebSocket connection established.');
    wsHasOpened = true;
  };
  
  ws.onmessage = async (event) => {
    if (event.data instanceof Blob) {
      try {
        const buffer = await event.data.arrayBuffer();
        const view = new DataView(buffer);
        const eventType = view.getInt32(0);
        const imageType = view.getInt32(4);
        
        console.log(`WS Binary Message: eventType=${eventType}, imageType=${imageType}, size=${buffer.byteLength} bytes`);
        
        const promptId = state.currentlyExecutingPromptId || state.lastExecutingPromptId;
        const activePrompt = promptId ? state.activePrompts[promptId] : null;
        const slotIndex = activePrompt ? activePrompt.index : state.currentBatchIndex;

        if (eventType === 1) { // Live preview image
          const imageBytes = buffer.slice(8);
          const mime = imageType === 1 ? 'image/png' : 'image/jpeg';
          const blob = new Blob([imageBytes], { type: mime });
          const objectUrl = URL.createObjectURL(blob);
          updateLivePreview(objectUrl, slotIndex);
        } else if (eventType === 2) { // Final image (binary output)
          const imageBytes = buffer.slice(8);
          const mime = imageType === 1 ? 'image/png' : 'image/jpeg';
          const blob = new Blob([imageBytes], { type: mime });
          const objectUrl = URL.createObjectURL(blob);
          handleCompletedImage(objectUrl, slotIndex);
        }
      } catch (err) {
        console.error('Error parsing binary socket message:', err);
      }
      return;
    }
    
    try {
      const msg = JSON.parse(event.data);
      console.log('WS JSON Message:', msg);
      handleWebSocketMessage(msg);
    } catch (err) {
      console.error('Error parsing websocket message:', err);
    }
  };
  
  ws.onerror = (err) => {
    console.error('WebSocket error:', err);
  };
  
  ws.onclose = () => {
    console.log('WebSocket closed.');
    for (const pid in state.activePrompts) {
      const activePrompt = state.activePrompts[pid];
      if (activePrompt && activePrompt.resolve) {
        console.warn(`WebSocket closed. Resolving pending prompt resolver for ${pid}.`);
        activePrompt.resolve();
        activePrompt.resolve = null;
      }
    }
    if (!wsHasOpened && !state.useProxy) {
      console.warn('Direct WebSocket connection failed. Falling back to proxy.');
      state.useProxy = true;
      checkConnection();
      setTimeout(connectWebSocket, 1000);
    } else {
      console.log('Reconnecting WebSocket in 3s...');
      setTimeout(connectWebSocket, 3000);
    }
  };
}

function handleWebSocketMessage(msg) {
  const type = msg.type;
  const data = msg.data;
  if (!data) return;
  
  if (data.prompt_id) {
    state.lastExecutingPromptId = data.prompt_id;
    if (type !== 'executing' || data.node !== null) {
      state.currentlyExecutingPromptId = data.prompt_id;
    } else {
      state.currentlyExecutingPromptId = null;
    }
    
    // Auto-register prompt_id to avoid HTTP/WS race conditions
    if (!state.activePrompts[data.prompt_id]) {
      state.activePrompts[data.prompt_id] = {
        index: state.currentBatchIndex,
        resolve: null
      };
    }
    
    const activePrompt = state.activePrompts[data.prompt_id];
    if (activePrompt) {
      if (type === 'progress') {
        const val = data.value;
        const max = data.max;
        state.currentStep = val;
        state.maxSteps = max;
        updateProgressBar(val, max, activePrompt.index);
      } else if (type === 'executing') {
        if (data.node === null) {
          // Completed execution of prompt
          console.log(`Prompt completed: ${data.prompt_id}`);
          
          // Ensure the final image shown in the gallery slot is added to history
          const slotIndex = activePrompt ? activePrompt.index : state.currentBatchIndex;
          const slot = document.getElementById(`gallery-slot-${slotIndex}`);
          if (slot) {
            const badge = slot.querySelector('.preview-badge');
            if (badge) {
              badge.remove();
            }
            const img = slot.querySelector('img');
            if (img && img.src) {
              const imageUrl = img.src;
              if (!state.history.includes(imageUrl)) {
                state.history.unshift(imageUrl);
                saveHistoryToStorage();
              }
            }
          }

          if (activePrompt.resolve) {
            activePrompt.resolve();
            activePrompt.resolve = null;
          }
        }
      } else if (type === 'executed') {
        if (data.output && data.output.images) {
          // Generated images
          data.output.images.forEach(img => {
            const url = state.useProxy
              ? `/comfy-proxy/view?filename=${img.filename}&subfolder=${img.subfolder}&type=${img.type}`
              : `${state.comfyUrl}/view?filename=${img.filename}&subfolder=${img.subfolder}&type=${img.type}`;
            handleCompletedImage(url, activePrompt.index);
          });
        }
      }
    }
  }
}

// UI State & Generation Loop
async function handleGenerateClick() {
  if (state.isGenerating) {
    // If generating, this button acts as "Skip"
    handleSkip();
    return;
  }
  
  if (!state.isConnected) {
    alert('Cannot generate: ComfyUI server is offline.');
    return;
  }
  
  state.isGenerating = true;
  updateGenerateBtnUI();
  
  // Clear gallery
  elements.galleryGrid.innerHTML = '';
  elements.galleryGrid.classList.remove('hidden');
  elements.galleryEmptyState.classList.add('hidden');
  elements.galleryProgress.classList.remove('hidden');
  
  // Determine seeds
  let baseSeed = 0;
  // Get base seed node key
  let seedNodeKey = null;
  let randomize = false;
  
  for (const k in state.overrides) {
    if (k.endsWith('.randomize')) {
      randomize = state.overrides[k] === true;
      seedNodeKey = k.replace('.randomize', '');
      break;
    }
  }
  
  console.log('--- GENERATE CLICK DIAGNOSTICS ---');
  console.log('state.overrides:', JSON.stringify(state.overrides));
  console.log('seedNodeKey:', seedNodeKey);
  console.log('randomize:', randomize);
  
  if (seedNodeKey) {
    const rawSeed = state.overrides[seedNodeKey];
    baseSeed = randomize ? Math.floor(Math.random() * 9000000000000) : parseInt(rawSeed, 10);
    console.log('Parsed baseSeed:', baseSeed);
    // If randomized, update numeric seed widget value in UI and overrides so users can see the base seed used
    if (randomize) {
      state.overrides[seedNodeKey] = baseSeed;
      const seedInput = document.querySelector('[id^="seed-input-"]');
      if (seedInput) seedInput.value = baseSeed;
      saveOverrides();
    }
  } else {
    console.log('No seedNodeKey was detected. Overrides keys are:', Object.keys(state.overrides));
  }
  
  // Sequentially loop through batch count
  for (let i = 0; i < state.batchCount; i++) {
    if (!state.isGenerating) break; // User stopped/cancelled
    
    state.currentBatchIndex = i;
    state.currentStep = 0;
    state.maxSteps = 1;
    state.activePromptSkipped = false;
    updateProgressBar(0, 1);
    
    // Create current gallery slot for live preview & final image
    createGallerySlot(i);
    
    // Clone and prepare workflow json
    const workflow = JSON.parse(JSON.stringify(state.currentWorkflowJson));
    
    // Inject Prompt node
    let promptInjected = false;
    for (const nodeId in workflow) {
      const node = workflow[nodeId];
      if (node._meta && node._meta.title === 'Prompt' && node.inputs) {
        if (node.inputs.text !== undefined) {
          node.inputs.text = elements.promptInput.value;
          promptInjected = true;
        } else if (node.inputs.string !== undefined) {
          node.inputs.string = elements.promptInput.value;
          promptInjected = true;
        } else if (node.inputs.value !== undefined) {
          node.inputs.value = elements.promptInput.value;
          promptInjected = true;
        } else {
          node.inputs.text = elements.promptInput.value;
          promptInjected = true;
        }
      }
    }
    
    // Apply overrides
    for (const key in state.overrides) {
      if (key.includes('.')) {
        const parts = key.split('.');
        const nodeId = parts[0];
        const inputName = parts[1];
        
        // Skip UI settings like Dimension.isExact and randomize keys
        if (inputName === 'Dimensions' || key.endsWith('.randomize')) continue;
        
        if (workflow[nodeId] && workflow[nodeId].inputs) {
          let value = state.overrides[key];
          
          // Apply iteration-derived seeds
          if (key === seedNodeKey) {
            value = baseSeed + i;
          }
          
          workflow[nodeId].inputs[inputName] = value;
        }
      }
    }
    
    console.log(`--- Iteration ${i} ---`);
    for (const nodeId in workflow) {
      if (workflow[nodeId].class_type === 'KSampler') {
        console.log(`KSampler Node ${nodeId} seed value:`, workflow[nodeId].inputs.seed);
      }
    }
    
    try {
      const submitRes = await fetchFromComfy('prompt', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          prompt: workflow,
          client_id: state.clientId
        })
      });
      
      if (!submitRes.ok) throw new Error('Failed to submit prompt');
      const submitData = await submitRes.json();
      const promptId = submitData.prompt_id;
      state.currentPromptId = promptId;
      
      // Wait for WebSocket execution
      await new Promise((resolve) => {
        if (state.activePrompts[promptId]) {
          state.activePrompts[promptId].resolve = resolve;
        } else {
          state.activePrompts[promptId] = {
            index: i,
            resolve: resolve
          };
        }
      });
      
    } catch (err) {
      console.error(`Error generating batch item ${i}:`, err);
    }
    
    state.currentPromptId = null;
  }
  
  state.isGenerating = false;
  updateGenerateBtnUI();
  elements.galleryProgress.classList.add('hidden');
}

// Skip current batch iteration
async function handleSkip() {
  if (!state.currentPromptId) return;
  state.activePromptSkipped = true;
  try {
    await fetchFromComfy('interrupt', { method: 'POST' });
  } catch (err) {
    console.error('Error sending interrupt:', err);
  }
  
  // Remove partial preview image from the gallery slot
  const activeSlot = document.getElementById(`gallery-slot-${state.currentBatchIndex}`);
  if (activeSlot) {
    activeSlot.innerHTML = `<p style="color: var(--text-muted); font-size: 13px;">Skipped</p>`;
  }
  
  const activePrompt = state.activePrompts[state.currentPromptId];
  if (activePrompt && activePrompt.resolve) {
    activePrompt.resolve();
    activePrompt.resolve = null;
  }
}

// UI controls
function updateGenerateBtnUI() {
  const btn = elements.generateBtn;
  const txt = elements.generateBtnText;
  
  // Recreate the icon element to ensure Lucide can parse and replace it correctly
  let icon = btn.querySelector('.btn-icon');
  if (icon) {
    icon.remove();
  }
  
  let svgIcon = btn.querySelector('svg');
  if (svgIcon) {
    svgIcon.remove();
  }
  
  icon = document.createElement('i');
  icon.className = 'btn-icon';
  
  if (state.isGenerating) {
    btn.className = 'btn btn-danger';
    txt.textContent = 'Skip';
    icon.setAttribute('data-lucide', 'square');
  } else {
    btn.className = 'btn btn-primary';
    txt.textContent = 'Generate';
    icon.setAttribute('data-lucide', 'play');
  }
  
  btn.insertBefore(icon, txt);
  lucide.createIcons();
}

function updateProgressBar(val, max, index) {
  const idx = index !== undefined ? index : state.currentBatchIndex;
  const pct = Math.round((val / max) * 100);
  elements.progressBarFill.style.width = `${pct}%`;
  elements.progressText.textContent = `Batch Item ${idx + 1}/${state.batchCount}: ${pct}%`;
}

function createGallerySlot(index) {
  const slot = document.createElement('div');
  slot.className = 'gallery-item';
  slot.id = `gallery-slot-${index}`;
  slot.innerHTML = `
    <span class="preview-badge">Generating...</span>
    <span class="item-index-badge">${index + 1}</span>
  `;
  elements.galleryGrid.appendChild(slot);
}

function updateLivePreview(objectUrl, index) {
  const idx = index !== undefined ? index : state.currentBatchIndex;
  const slot = document.getElementById(`gallery-slot-${idx}`);
  if (!slot || state.activePromptSkipped) return;
  
  // Update or add image element
  let img = slot.querySelector('img');
  if (!img) {
    img = document.createElement('img');
    slot.appendChild(img);
  }
  img.src = objectUrl;
}

function handleCompletedImage(imageUrl, index) {
  const idx = index !== undefined ? index : state.currentBatchIndex;
  const slot = document.getElementById(`gallery-slot-${idx}`);
  if (!slot) return;
  
  slot.innerHTML = '';
  const img = document.createElement('img');
  img.src = imageUrl;
  slot.appendChild(img);
  
  const badge = document.createElement('span');
  badge.className = 'item-index-badge';
  badge.textContent = idx + 1;
  slot.appendChild(badge);
  
  // Add to session history
  state.history.unshift(imageUrl);
  saveHistoryToStorage();

  // If lightbox is open, dynamically refresh its images
  if (elements.lightbox && !elements.lightbox.classList.contains('hidden')) {
    updateLightboxImagesAndIndex();
  }
}

function saveHistoryToStorage() {
  if (state.activeTab === 'history') {
    renderHistory();
  }
}

// Lightbox functionality
function openLightbox(source, clickedImageUrl) {
  state.lightboxSource = source;
  updateLightboxImagesAndIndex(clickedImageUrl);
  
  if (state.lightboxImages.length === 0 || state.lightboxIndex < 0) return;
  
  elements.lightbox.classList.remove('hidden');
  updateLightboxImage();
  
  // Push state to history for mobile back button interception
  history.pushState({ lightboxOpen: true }, '');
}

function closeLightbox(shouldGoBack = true) {
  if (elements.lightbox.classList.contains('hidden')) return;
  
  elements.lightbox.classList.add('hidden');
  
  if (shouldGoBack) {
    if (history.state && history.state.lightboxOpen) {
      history.back();
    }
  }
}

function updateLightboxImagesAndIndex(targetUrl) {
  let imgs = [];
  if (state.lightboxSource === 'gallery') {
    const completedItems = Array.from(elements.galleryGrid.querySelectorAll('.gallery-item'))
      .filter(item => !item.querySelector('.preview-badge'));
    imgs = completedItems.map(item => item.querySelector('img')).filter(img => img !== null);
  } else if (state.lightboxSource === 'history') {
    const historyItems = Array.from(elements.historyGrid.querySelectorAll('.history-item'));
    imgs = historyItems.map(item => item.querySelector('img')).filter(img => img !== null);
  }
  
  state.lightboxImages = imgs.map(img => img.getAttribute('src'));
  
  if (targetUrl) {
    state.lightboxIndex = state.lightboxImages.indexOf(targetUrl);
  } else {
    const currentUrl = elements.lightboxImage.getAttribute('src');
    state.lightboxIndex = state.lightboxImages.indexOf(currentUrl);
  }
}

function updateLightboxImage() {
  if (state.lightboxIndex < 0 || state.lightboxIndex >= state.lightboxImages.length) return;
  elements.lightboxImage.src = state.lightboxImages[state.lightboxIndex];
}

function lightboxNext() {
  updateLightboxImagesAndIndex();
  if (state.lightboxImages.length === 0) return;
  state.lightboxIndex = (state.lightboxIndex + 1) % state.lightboxImages.length;
  updateLightboxImage();
}

function lightboxPrev() {
  updateLightboxImagesAndIndex();
  if (state.lightboxImages.length === 0) return;
  state.lightboxIndex = (state.lightboxIndex - 1 + state.lightboxImages.length) % state.lightboxImages.length;
  updateLightboxImage();
}

// Initial hook on WebSocket connection
connectWebSocket();

// Run on page load
window.addEventListener('DOMContentLoaded', init);

