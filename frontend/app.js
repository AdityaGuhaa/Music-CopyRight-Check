const analyzeBtn = document.getElementById("analyzeBtn");
const audioInput = document.getElementById("audioFile");

const statusDiv = document.getElementById("status");
const resultDiv = document.getElementById("result");

analyzeBtn.addEventListener("click", async () => {
    const file = audioInput.files[0];

    if (!file) {
        alert("Please select an audio file first.");
        return;
    }

    // Reset UI
    resultDiv.classList.add("hidden");
    statusDiv.classList.remove("hidden");
    statusDiv.textContent = "Listening to the audio… 🔊";

    const formData = new FormData();
    formData.append("file", file);

    try {
        const response = await fetch("http://127.0.0.1:8000/analyze-audio", {
            method: "POST",
            body: formData
        });

        if (!response.ok) {
            throw new Error("Server returned " + response.status);
        }

        const data = await response.json();

        statusDiv.classList.add("hidden");

        if (!data.success) {
            alert(data.message || "Song could not be recognized.");
            return;
        }

        // ===== Fill Basic Metadata =====
        document.getElementById("title").textContent = data.title || "Unknown";
        document.getElementById("artists").textContent = (data.artists || []).join(", ");
        document.getElementById("confidence").textContent =
            data.confidence_score !== undefined ? data.confidence_score : "N/A";

        // ===== Copyright Label =====
        document.getElementById("copyrightLabel").textContent =
            "Copyright details available below";

        // ===== Official PRO Links =====
        if (data.official_search_links) {
            const bmiLink = document.getElementById("bmiLink");
            const ascapLink = document.getElementById("ascapLink");
            const socanLink = document.getElementById("socanLink");

            bmiLink.href = data.official_search_links.bmi;
            ascapLink.href = data.official_search_links.ascap;
            socanLink.href = data.official_search_links.socan;

            bmiLink.style.display = "inline";
            ascapLink.style.display = "inline";
            socanLink.style.display = "inline";
        }

        // ===== Detailed Copyright & Licensing Info =====
        const report = data.copyright_report || {};

        // ---------- Publishers ----------
        const publishersList = document.getElementById("publishersList");
        publishersList.innerHTML = "";

        if (Array.isArray(report.publisher) && report.publisher.length > 0) {
            report.publisher.forEach(p => {
                const li = document.createElement("li");
                li.textContent = p;
                publishersList.appendChild(li);
            });
        } else {
            publishersList.innerHTML = "<li>Not available</li>";
        }

        // ---------- Master Rights Holders ----------
        const mastersList = document.getElementById("mastersList");
        mastersList.innerHTML = "";

        if (Array.isArray(report.master_rights_holder) && report.master_rights_holder.length > 0) {
            report.master_rights_holder.forEach(m => {
                const li = document.createElement("li");
                li.textContent = m;
                mastersList.appendChild(li);
            });
        } else {
            mastersList.innerHTML = "<li>Not available</li>";
        }

        // ---------- PROs ----------
        const prosList = document.getElementById("prosList");
        prosList.innerHTML = "";

        if (Array.isArray(report.pros) && report.pros.length > 0) {
            report.pros.forEach(p => {
                const li = document.createElement("li");
                li.textContent = p;
                prosList.appendChild(li);
            });
        } else {
            prosList.innerHTML = "<li>Not available</li>";
        }

        // ---------- Composition Licensing Paths ----------
        const compositionList = document.getElementById("compositionLicenses");
        compositionList.innerHTML = "";

        if (
            report.licensing_paths &&
            Array.isArray(report.licensing_paths.composition) &&
            report.licensing_paths.composition.length > 0
        ) {
            report.licensing_paths.composition.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                compositionList.appendChild(li);
            });
        } else {
            compositionList.innerHTML = "<li>Not available</li>";
        }

        // ---------- Master Recording Licensing Paths ----------
        const masterLicensesList = document.getElementById("masterLicenses");
        masterLicensesList.innerHTML = "";

        if (
            report.licensing_paths &&
            Array.isArray(report.licensing_paths.master_recording) &&
            report.licensing_paths.master_recording.length > 0
        ) {
            report.licensing_paths.master_recording.forEach(item => {
                const li = document.createElement("li");
                li.textContent = item;
                masterLicensesList.appendChild(li);
            });
        } else {
            masterLicensesList.innerHTML = "<li>Not available</li>";
        }

        // ---------- Source Links ----------
        const sourcesList = document.getElementById("sourcesList");
        sourcesList.innerHTML = "";

        if (Array.isArray(report.source_links) && report.source_links.length > 0) {
            report.source_links.forEach(src => {
                const li = document.createElement("li");
                li.textContent = src;
                sourcesList.appendChild(li);
            });
        } else {
            sourcesList.innerHTML = "<li>Not available</li>";
        }

        // ===== Show result =====
        resultDiv.classList.remove("hidden");

    } catch (err) {
        console.error("Analyze error:", err);
        alert("Error connecting to backend. Is FastAPI running?");
        statusDiv.classList.add("hidden");
    }
});
