document.addEventListener("DOMContentLoaded", () => {
    const forms = document.querySelectorAll(".compare-form");

    forms.forEach(form => {
        form.addEventListener("submit", async (e) => {
            // Stop the browser from doing a full page reload
            e.preventDefault();

            // Identify exactly which button (Compute Diff vs AI Summary) submitted the form
            // e.submitter can be null in some browsers — fall back to the clicked button
            const button = e.submitter || e.target.querySelector("button[data-action]:focus");
            if (!button) return;

            const baseEndpoint = form.getAttribute("data-endpoint");
            const actionSubpath = button.getAttribute("data-action");
            if (!actionSubpath) return; // button has no data-action, ignore
            const targetUrl = `${baseEndpoint}${actionSubpath}`;
            const isFileDownload = button.getAttribute("data-is-file") === "true";

            // Setup display targets
            // .result-box sits outside <form> in the parent .card, so search upward
            const resultBox = form.closest(".card").querySelector(".result-box");
            if (!resultBox) return;
            resultBox.classList.remove("d-none");
            resultBox.innerHTML = `
                <div class="d-flex align-items-center justify-content-center p-5 text-muted">
                    <div class="spinner-border text-primary me-3" role="status"></div>
                    <span>Processing documents...</span>
                </div>`;

            // Package the form data
            const formData = new FormData(form);

            try {
                const response = await fetch(targetUrl, {
                    method: "POST",
                    body: formData
                });

                if (!response.ok) {
                    const errData = await response.json();
                    throw new Error(errData.detail || "Processing run hit an error.");
                }

                // Handle Direct Binary Workbook Streams (Excel outputs)
                if (isFileDownload) {
                    const blob = await response.blob();
                    const downloadUrl = window.URL.createObjectURL(blob);
                    const a = document.createElement("a");
                    a.href = downloadUrl;
                    a.download = "comparison_result.xlsx";
                    document.body.appendChild(a);
                    a.click();
                    a.remove();

                    resultBox.innerHTML = `
                        <div class="alert alert-success d-flex align-items-center" role="alert">
                            <i class="bi bi-check-circle-fill me-2 fs-5"></i>
                            <div>Workbook delta generated successfully! Your download has started.</div>
                        </div>`;
                    return;
                }

                // Parse Standard Structured Responses
                const data = await response.json();
                renderOutput(resultBox, actionSubpath, data);

            } catch (error) {
                resultBox.innerHTML = `
                    <div class="alert alert-danger d-flex align-items-center" role="alert">
                        <i class="bi bi-exclamation-triangle-fill me-2 fs-5"></i>
                        <div><strong>Comparison Error:</strong> ${error.message}</div>
                    </div>`;
            }
        });
    });

    // Output DOM builder mapping to JSON backend structures
    function renderOutput(container, action, data) {
        container.innerHTML = "";

        if (action === "/compare" && data.similarity_score !== undefined) {
            const pct = (data.similarity_score * 100).toFixed(1);
            let diffHtml = `<div class="p-3 bg-dark text-white rounded-3 font-monospace small" style="max-height: 400px; overflow-y: auto;">`;

            if (data.new_lines.length === 0 && data.deleted_lines.length === 0) {
                diffHtml += `<span class="text-muted">// Identical content text matches perfectly.</span>`;
            } else {
                data.deleted_lines.forEach(line => {
                    diffHtml += `<div class="text-danger bg-danger-subtle px-1">${escapeHtml(line)}</div>`;
                });
                data.new_lines.forEach(line => {
                    diffHtml += `<div class="text-success bg-success-subtle px-1">${escapeHtml(line)}</div>`;
                });
            }
            diffHtml += `</div>`;

            container.innerHTML = `
                <div class="mb-3 d-flex align-items-center justify-content-between bg-light p-3 rounded-3">
                    <span class="fw-semibold">Index Matrix Similarity Score:</span>
                    <span class="badge bg-primary fs-6">${pct}% Match</span>
                </div>
                <h6 class="fw-bold text-secondary">Line Delta Trace</h6>
                ${diffHtml}`;
        }
        else if (action === "/summary" && data.summary) {
            container.innerHTML = `
        <div class="summary-card">
            <div class="summary-header">
                <i class="bi bi-stars me-2"></i>
                GenAI Analysis Executive Summary
            </div>

            <div class="summary-body markdown-body">
                ${marked.parse(data.summary)}
            </div>
        </div>`;
        }
        else if (action.includes("symmetric") && data.differences) {
            if (data.differences.length === 0) {
                container.innerHTML = `<div class="alert alert-info">No line deviations tracked across records.</div>`;
                return;
            }
            let rowsHtml = data.differences.map(row => `
                <tr>
                    <td><span class="badge bg-secondary">${escapeHtml(String(row.index || '-'))}</span></td>
                    <td class="font-monospace text-wrap">${escapeHtml(JSON.stringify(row))}</td>
                </tr>`).join('');

            container.innerHTML = `
                <h6 class="fw-bold text-dark mb-2">Cell Mutation Records Found (${data.differences.length})</h6>
                <div class="table-responsive rounded-3 border">
                    <table class="table table-striped table-hover mb-0 align-middle small">
                        <thead class="table-light"><tr><th>Row Key Index</th><th>Delta Properties</th></tr></thead>
                        <tbody>${rowsHtml}</tbody>
                    </table>
                </div>`;
        }
    }

    function escapeHtml(str) {
        return String(str).replace(/&/g, "&amp;").replace(/</g, "&lt;").replace(/>/g, "&gt;").replace(/"/g, "&quot;");
    }
});