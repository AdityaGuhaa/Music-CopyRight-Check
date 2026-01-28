document.addEventListener("DOMContentLoaded", () => {

    const analyzeBtn = document.getElementById("analyzeBtn");
    const fileInput = document.getElementById("audioFile");
    const statusDiv = document.getElementById("status");
    const resultDiv = document.getElementById("result");

    if (!analyzeBtn || !fileInput || !statusDiv || !resultDiv) {
        console.error("Critical DOM elements not found. Check index.html IDs.");
        return;
    }

    analyzeBtn.addEventListener("click", async () => {
        if (!fileInput.files.length) {
            alert("Please select an audio file first.");
            return;
        }

        const file = fileInput.files[0];
        const formData = new FormData();
        formData.append("file", file);

        statusDiv.classList.remove("hidden");
        statusDiv.textContent = "Listening to the audio… 🔊";
        resultDiv.classList.add("hidden");

        analyzeBtn.disabled = true;
        analyzeBtn.textContent = "Analyzing...";

        try {
            const response = await fetch("http://127.0.0.1:8000/analyze-audio", {
                method: "POST",
                body: formData
            });

            if (!response.ok) {
                const text = await response.text();
                throw new Error(`Server error: ${response.status} - ${text}`);
            }

            const data = await response.json();
            console.log("API Response:", data);

            if (!data.success) {
                throw new Error("Analysis failed on backend");
            }

            // Basic info
            document.getElementById("title").textContent = data.title || "-";
            document.getElementById("artists").textContent = (data.artists || []).join(", ");
            document.getElementById("confidence").textContent = data.confidence_score + "%";

            // Summary
            document.getElementById("copyrightLabel").textContent = "Copyrighted";
            document.getElementById("summary").textContent =
                "This track is registered with official rights organizations and requires proper licensing.";

            // PRO links
            document.getElementById("bmiLink").href = data.official_search_links.bmi;
            document.getElementById("ascapLink").href = data.official_search_links.ascap;
            document.getElementById("socanLink").href = data.official_search_links.socan;

            // Utility to clear lists
            const clear = (id) => {
                const el = document.getElementById(id);
                if (el) el.innerHTML = "";
            };

            clear("publishersList");
            clear("mastersList");
            clear("prosList");
            clear("compositionLicenses");
            clear("masterLicenses");
            clear("sourcesList");

            // Fill lists
            (data.copyright_report.publisher || []).forEach(p => {
                const li = document.createElement("li");
                li.textContent = p;
                document.getElementById("publishersList").appendChild(li);
            });

            (data.copyright_report.master_rights_holder || []).forEach(m => {
                const li = document.createElement("li");
                li.textContent = m;
                document.getElementById("mastersList").appendChild(li);
            });

            (data.copyright_report.pros || []).forEach(p => {
                const li = document.createElement("li");
                li.textContent = p;
                document.getElementById("prosList").appendChild(li);
            });

            (data.copyright_report.licensing_paths.composition || []).forEach(c => {
                const li = document.createElement("li");
                li.textContent = c;
                document.getElementById("compositionLicenses").appendChild(li);
            });

            (data.copyright_report.licensing_paths.master_recording || []).forEach(m => {
                const li = document.createElement("li");
                li.textContent = m;
                document.getElementById("masterLicenses").appendChild(li);
            });

            (data.copyright_report.source_links || []).forEach(s => {
                const li = document.createElement("li");
                const a = document.createElement("a");
                a.href = s;
                a.target = "_blank";
                a.textContent = s;
                li.appendChild(a);
                document.getElementById("sourcesList").appendChild(li);
            });

            statusDiv.classList.add("hidden");
            resultDiv.classList.remove("hidden");

            // Auto-scroll to report
            resultDiv.scrollIntoView({ behavior: "smooth" });

        } catch (err) {
            console.error("Frontend error:", err);
            statusDiv.textContent = "❌ Error: " + err.message;
        } finally {
            analyzeBtn.disabled = false;
            analyzeBtn.textContent = "Analyze →";
        }
    });

});
