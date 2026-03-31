LIGHT_MARKER_SCRIPT = """
document.documentElement.dataset.theme = "light";
document.documentElement.classList.add("light");

const applyLightMarkerToBody = () => {
    if (!document.body) {
        return;
    }

    document.body.dataset.theme = "light";
    document.body.classList.add("light");
};

applyLightMarkerToBody();
document.addEventListener("DOMContentLoaded", applyLightMarkerToBody, { once: true });
"""


def setup(app):
    # sphinxcontrib-mermaid registers its runtime script at priority 500.
    # Inject the light marker first so Mermaid resolves the page as light.
    app.add_js_file(None, body=LIGHT_MARKER_SCRIPT, priority=400)
    return {"parallel_read_safe": True}
