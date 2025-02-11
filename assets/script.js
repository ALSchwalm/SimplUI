// Avoid accidental 'back'
window.onbeforeunload = function() { return true; }

function initStylePreviewOverlay() {
    let overlayVisible = false;
    const samplesPath = document.querySelector("meta[name='samples-path']").getAttribute("content")
    const overlay = document.createElement('div');
    const tooltip = document.createElement('div');
    tooltip.className = 'preview-tooltip';
    overlay.appendChild(tooltip);
    overlay.id = 'stylePreviewOverlay';
    document.body.appendChild(overlay);
    document.addEventListener('mouseover', function (e) {
        const label = e.target.closest('.style_selections label');
        if (!label) return;
        label.removeEventListener("mouseout", onMouseLeave);
        label.addEventListener("mouseout", onMouseLeave);
        overlayVisible = true;
        overlay.style.opacity = "1";
        const name = label.querySelector("span").textContent;
        overlay.style.backgroundImage = `url("${samplesPath.replace(
            "fooocus_v2",
            name.toLowerCase().replaceAll(" ", "_")
        ).replaceAll("\\", "\\\\")}")`;

        function onMouseLeave() {
            overlayVisible = false;
            overlay.style.opacity = "0";
            overlay.style.backgroundImage = "";
            label.removeEventListener("mouseout", onMouseLeave);
        }
    });
    document.addEventListener('mousemove', function (e) {
        if (!overlayVisible) return;
        overlay.style.left = `${e.clientX}px`;
        overlay.style.top = `${e.clientY}px`;
        overlay.className = e.clientY > window.innerHeight / 2 ? "lower-half" : "upper-half";
    });
}

function gradioApp() {
    const elems = document.getElementsByTagName('gradio-app');
    const elem = elems.length == 0 ? document : elems[0];

    if (elem !== document) {
        elem.getElementById = function(id) {
            return document.getElementById(id);
        };
    }
    return elem.shadowRoot ? elem.shadowRoot : elem;
}

/**
 * Get the currently selected top-level UI tab button (e.g. the button that says "Extras").
 */
function get_uiCurrentTab() {
    return gradioApp().querySelector('#tabs > .tab-nav > button.selected');
}

var uiUpdateCallbacks = [];
var uiAfterUpdateCallbacks = [];
var uiLoadedCallbacks = [];
var uiTabChangeCallbacks = [];
var optionsChangedCallbacks = [];
var uiAfterUpdateTimeout = null;
var uiCurrentTab = null;

/**
 * Register callback to be called at each UI update.
 * The callback receives an array of MutationRecords as an argument.
 */
function onUiUpdate(callback) {
    uiUpdateCallbacks.push(callback);
}

/**
 * Register callback to be called when the UI is loaded.
 * The callback receives no arguments.
 */
function onUiLoaded(callback) {
    uiLoadedCallbacks.push(callback);
}

/**
 * Register callback to be called soon after UI updates.
 * The callback receives no arguments.
 *
 * This is preferred over `onUiUpdate` if you don't need
 * access to the MutationRecords, as your function will
 * not be called quite as often.
 */
function onAfterUiUpdate(callback) {
    uiAfterUpdateCallbacks.push(callback);
}

function executeCallbacks(queue, arg) {
    for (const callback of queue) {
        try {
            callback(arg);
        } catch (e) {
            console.error("error running callback", callback, ":", e);
        }
    }
}

/**
 * Schedule the execution of the callbacks registered with onAfterUiUpdate.
 * The callbacks are executed after a short while, unless another call to this function
 * is made before that time. IOW, the callbacks are executed only once, even
 * when there are multiple mutations observed.
 */
function scheduleAfterUiUpdateCallbacks() {
    clearTimeout(uiAfterUpdateTimeout);
    uiAfterUpdateTimeout = setTimeout(function() {
        executeCallbacks(uiAfterUpdateCallbacks);
    }, 200);
}

var executedOnLoaded = false;

var onAppend = function(elem, f) {
    var observer = new MutationObserver(function(mutations) {
        mutations.forEach(function(m) {
            if (m.addedNodes.length) {
                f(m.addedNodes);
            }
        });
    });
    observer.observe(elem, {childList: true});
}

function addObserverIfDesiredNodeAvailable(querySelector, callback) {
    var elem = document.querySelector(querySelector);
    if (!elem) {
        window.setTimeout(() => addObserverIfDesiredNodeAvailable(querySelector, callback), 1000);
        return;
    }

    onAppend(elem, callback);
}

/**
 * Show reset button on toast "Connection errored out."
 */
addObserverIfDesiredNodeAvailable(".toast-wrap", function(added) {
    added.forEach(function(element) {
         if (element.innerText.includes("Connection errored out.")) {
             window.setTimeout(function() {
                document.getElementById("reset_button").classList.remove("hidden");
                document.getElementById("generate_button").classList.add("hidden");
                document.getElementById("skip_button").classList.add("hidden");
                document.getElementById("stop_button").classList.add("hidden");
            });
         }
    });
});

/**
 * Add a ctrl+enter as a shortcut to start a generation
 */
document.addEventListener('keydown', function(e) {
    const isModifierKey = (e.metaKey || e.ctrlKey || e.altKey);
    const isEnterKey = (e.key == "Enter" || e.keyCode == 13);

    if(isModifierKey && isEnterKey) {
        const generateButton = gradioApp().querySelector('button:not(.hidden)[id=generate-btn]');
        if (generateButton) {
            generateButton.click();
            e.preventDefault();
            return;
        }

        const stopButton = gradioApp().querySelector('button:not(.hidden)[id=stop-btn]')
        if(stopButton) {
            stopButton.click();
            e.preventDefault();
            return;
        }
    }
});

function on_style_selection_blur() {
    let target = document.querySelector("#gradio_receiver_style_selections textarea");
    target.value = "on_style_selection_blur " + Math.random();
    let e = new Event("input", {bubbles: true})
    Object.defineProperty(e, "target", {value: target})
    target.dispatchEvent(e);
}


function onLoad() {
    var mutationObserver = new MutationObserver(function(m) {
        if (!executedOnLoaded && gradioApp().querySelector('#generate-btn')) {
            executedOnLoaded = true;
            executeCallbacks(uiLoadedCallbacks);
        }

        executeCallbacks(uiUpdateCallbacks, m);
        scheduleAfterUiUpdateCallbacks();
        const newTab = get_uiCurrentTab();
        if (newTab && (newTab !== uiCurrentTab)) {
            uiCurrentTab = newTab;
            executeCallbacks(uiTabChangeCallbacks);
        }
    });
    mutationObserver.observe(gradioApp(), {childList: true, subtree: true});
    initStylePreviewOverlay();
}

onUiLoaded(async () => {
    document.querySelector('.style_selections').addEventListener('focusout', function (event) {
        setTimeout(() => {
            if (!this.contains(document.activeElement)) {
                on_style_selection_blur();
            }
        }, 200);
    });
})

if (document.readyState === "loading") {
  document.addEventListener("DOMContentLoaded", onLoad);
} else {
  onLoad();
}
