// Main JavaScript for GanaZone
// This file is intentionally separate so the repository includes JavaScript source code.

// Example helper: safe DOM selector
function gs(selector) {
    return document.querySelector(selector);
}

function gsa(selector) {
    return document.querySelectorAll(selector);
}

function hideElement(selector) {
    const el = gs(selector);
    if (el) el.style.display = 'none';
}

function showElement(selector) {
    const el = gs(selector);
    if (el) el.style.display = 'block';
}
