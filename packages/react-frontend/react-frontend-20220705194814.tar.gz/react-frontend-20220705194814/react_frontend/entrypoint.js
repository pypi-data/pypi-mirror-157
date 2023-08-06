
try {
    new Function("import('/reactfiles/frontend/main-d6e0b2bc.js')")();
} catch (err) {
    var el = document.createElement('script');
    el.src = '/reactfiles/frontend/main-d6e0b2bc.js';
    el.type = 'module';
    document.body.appendChild(el);
}
