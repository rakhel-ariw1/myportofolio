(() => {
    const app = document.getElementById("education-app");
    if (!app) return;

    const DUMMY_UUID = "00000000-0000-0000-0000-000000000000";
    const SEARCH_DELAY = 300;
    const config = {
        listUrl: app.dataset.listUrl,
        createUrl: app.dataset.createUrl,
        starUrlTemplate: app.dataset.starUrlTemplate,
        editUrlTemplate: app.dataset.editUrlTemplate,
        deleteUrlTemplate: app.dataset.deleteUrlTemplate,
        isAuthenticated: app.dataset.isAuthenticated === "true",
        isSuperuser: app.dataset.isSuperuser === "true",
        canEdit: app.dataset.canEdit === "true",
    };

    const elements = {
        loading: document.getElementById("education-loading"),
        error: document.getElementById("education-error"),
        empty: document.getElementById("education-empty"),
        grid: document.getElementById("education-grid"),
        retry: document.getElementById("education-retry"),
        searchForm: document.getElementById("education-search-form"),
        searchInput: document.getElementById("education-search-input"),
        modal: document.getElementById("education-form-modal"),
        openModalButton: document.getElementById("open-education-modal"),
        closeModalButton: document.getElementById("close-education-modal"),
        cancelModalButton: document.getElementById("cancel-education-modal"),
        form: document.getElementById("education-form"),
        formErrors: document.getElementById("education-form-errors"),
    };

    let searchTimer;
    let requestController;

    function escapeHtml(value) {
        return String(value ?? "")
            .replaceAll("&", "&amp;")
            .replaceAll("<", "&lt;")
            .replaceAll(">", "&gt;")
            .replaceAll('"', "&quot;")
            .replaceAll("'", "&#39;");
    }

    function getCookie(name) {
        const cookie = document.cookie
            .split(";")
            .map((item) => item.trim())
            .find((item) => item.startsWith(`${name}=`));
        return cookie ? decodeURIComponent(cookie.slice(name.length + 1)) : null;
    }

    function getCsrfToken() {
        return getCookie("csrftoken")
            || document.querySelector("[name=csrfmiddlewaretoken]")?.value
            || "";
    }

    function replaceUuid(urlTemplate, educationId) {
        return urlTemplate.replace(DUMMY_UUID, encodeURIComponent(educationId));
    }

    function setPageState(state) {
        elements.loading.classList.toggle("hide", state !== "loading");
        elements.error.classList.toggle("hide", state !== "error");
        elements.empty.classList.toggle("hide", state !== "empty");
        elements.grid.classList.toggle("hide", state !== "ready");
    }

    function buildEducationCard(item) {
        const educationId = escapeHtml(item.id);
        const institution = escapeHtml(item.nama_institusi);
        const level = escapeHtml(item.jenjang_label);
        const startYear = escapeHtml(item.tahun_mulai);
        const endYear = item.tahun_selesai ? escapeHtml(item.tahun_selesai) : "Sekarang";
        const description = escapeHtml(item.deskripsi || "Belum ada deskripsi.");
        const starCount = escapeHtml(item.star_count);
        const starNames = item.starred_by_names.length
            ? escapeHtml(item.starred_by_names.join(", "))
            : "Belum ada yang memberi star";
        const starLabel = item.is_starred ? "Batalkan star" : "Beri star";
        const starredClass = item.is_starred ? " is-starred" : "";

        const editAction = config.canEdit
            ? `<a class="button button-secondary" href="${replaceUuid(config.editUrlTemplate, educationId)}">Edit</a>`
            : "";
        const ownerActions = config.isSuperuser
            ? `
                <form class="education-delete-form" method="post" action="${replaceUuid(config.deleteUrlTemplate, educationId)}">
                    <input type="hidden" name="csrfmiddlewaretoken" value="${escapeHtml(getCsrfToken())}">
                    <button type="submit" class="button button-danger" data-institution="${institution}">Hapus</button>
                </form>
            `
            : "";

        const article = document.createElement("article");
        article.className = "education-card";
        article.innerHTML = `
            <div class="education-card__topline">
                <span class="education-category">${level}</span>
                <span class="education-years">${startYear} — ${endYear}</span>
            </div>
            <h2>${institution}</h2>
            <p class="education-description">${description}</p>
            <div class="education-card__footer">
                <button
                    type="button"
                    class="button education-star-button${starredClass}"
                    data-action="toggle-star"
                    data-education-id="${educationId}"
                    aria-pressed="${item.is_starred}"
                    title="${starNames}"
                >
                    <span aria-hidden="true">★</span>
                    <span class="education-star-label">${starLabel}</span>
                    <span class="star-count">${starCount}</span>
                </button>
                <div class="education-owner-actions">${editAction}${ownerActions}</div>
            </div>
        `;
        return article;
    }

    async function fetchEducation(query = elements.searchInput.value.trim()) {
        if (requestController) requestController.abort();
        requestController = new AbortController();
        setPageState("loading");

        const url = new URL(config.listUrl, window.location.origin);
        if (query) url.searchParams.set("q", query);

        try {
            const response = await fetch(url, {
                headers: { Accept: "application/json" },
                signal: requestController.signal,
            });
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const educationData = await response.json();
            elements.grid.replaceChildren(...educationData.map(buildEducationCard));
            setPageState(educationData.length ? "ready" : "empty");

            const browserUrl = new URL(window.location.href);
            query ? browserUrl.searchParams.set("q", query) : browserUrl.searchParams.delete("q");
            window.history.replaceState({}, "", browserUrl);
        } catch (error) {
            if (error.name === "AbortError") return;
            console.error("Gagal memuat data pendidikan:", error);
            setPageState("error");
        }
    }

    function formatApiErrors(errors) {
        return Object.entries(errors || {}).flatMap(([field, details]) =>
            (Array.isArray(details) ? details : [details]).map((detail) => `${field}: ${detail}`)
        );
    }

    function showFormErrors(messages) {
        elements.formErrors.replaceChildren();
        const list = document.createElement("ul");
        messages.forEach((message) => {
            const item = document.createElement("li");
            item.textContent = message;
            list.appendChild(item);
        });
        elements.formErrors.appendChild(list);
        elements.formErrors.classList.remove("hide");
    }

    function closeModal() {
        if (elements.modal?.open) elements.modal.close();
    }

    elements.searchInput.value = new URL(window.location.href).searchParams.get("q") || "";
    elements.searchInput.addEventListener("input", () => {
        window.clearTimeout(searchTimer);
        searchTimer = window.setTimeout(() => fetchEducation(), SEARCH_DELAY);
    });
    elements.searchForm.addEventListener("submit", (event) => {
        event.preventDefault();
        window.clearTimeout(searchTimer);
        fetchEducation();
    });
    elements.retry.addEventListener("click", () => fetchEducation());

    elements.grid.addEventListener("click", async (event) => {
        const button = event.target.closest('[data-action="toggle-star"]');
        if (!button) return;

        if (!config.isAuthenticated) {
            showToast("Login diperlukan", "Silakan login untuk memberi star.", "error");
            return;
        }

        button.disabled = true;
        try {
            const response = await fetch(
                replaceUuid(config.starUrlTemplate, button.dataset.educationId),
                {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                }
            );
            const result = await response.json().catch(() => ({}));
            if (!response.ok) throw new Error(result.detail || `HTTP ${response.status}`);

            button.classList.toggle("is-starred", result.is_starred);
            button.setAttribute("aria-pressed", String(result.is_starred));
            button.querySelector(".education-star-label").textContent = result.is_starred
                ? "Batalkan star"
                : "Beri star";
            button.querySelector(".star-count").textContent = result.star_count;
            button.title = result.starred_by_names.join(", ") || "Belum ada yang memberi star";
        } catch (error) {
            showToast("Star gagal diperbarui", error.message, "error");
        } finally {
            button.disabled = false;
        }
    });

    elements.grid.addEventListener("submit", async (event) => {
        if (!event.target.matches(".education-delete-form")) return;
        event.preventDefault();
        const button = event.submitter;
        if (!button || button.disabled) return;
        const institution = event.submitter?.dataset.institution || "pendidikan ini";
        if (!window.confirm(`Hapus riwayat pendidikan “${institution}”?`)) {
            return;
        }
        button.disabled = true;
        try {
            const response = await fetch(event.target.action, {
                method: "DELETE",
                headers: { Accept: "application/json", "X-CSRFToken": getCsrfToken() },
            });
            if (!response.ok) {
                const result = await response.json().catch(() => ({}));
                throw new Error(result.detail || `HTTP ${response.status}`);
            }
            showToast("Berhasil", "Riwayat pendidikan dihapus.", "success");
            await fetchEducation();
        } catch (error) {
            showToast("Gagal menghapus", error.message, "error");
        } finally {
            button.disabled = false;
        }
    });

    if (elements.form) {
        elements.openModalButton.addEventListener("click", () => elements.modal.showModal());
        elements.closeModalButton.addEventListener("click", closeModal);
        elements.cancelModalButton.addEventListener("click", closeModal);
        elements.modal.addEventListener("click", (event) => {
            if (event.target === elements.modal) closeModal();
        });

        elements.form.addEventListener("submit", async (event) => {
            event.preventDefault();
            const submitButton = elements.form.querySelector('[type="submit"]');
            submitButton.disabled = true;
            elements.formErrors.classList.add("hide");

            try {
                const fields = new FormData(elements.form);
                const payload = Object.fromEntries([
                    "nama_institusi", "jenjang", "tahun_mulai", "tahun_selesai", "deskripsi",
                ].map(name => [name, fields.get(name)]));
                payload.tahun_selesai = payload.tahun_selesai || null;
                const response = await fetch(config.createUrl, {
                    method: "POST",
                    headers: {
                        Accept: "application/json",
                        "Content-Type": "application/json",
                        "X-CSRFToken": getCsrfToken(),
                    },
                    body: JSON.stringify(payload),
                });
                const result = await response.json().catch(() => ({}));

                if (!response.ok) {
                    const messages = Object.keys(result).length
                        ? formatApiErrors(result)
                        : [`Permintaan gagal (HTTP ${response.status}).`];
                    showFormErrors(messages);
                    showToast("Pendidikan gagal ditambahkan", messages.join(" "), "error");
                    return;
                }

                elements.form.reset();
                closeModal();
                showToast("Berhasil", "Riwayat pendidikan ditambahkan.", "success");
                await fetchEducation();
            } catch (error) {
                console.error("Gagal menambah pendidikan:", error);
                showToast(
                    "Pendidikan gagal ditambahkan",
                    "Tidak dapat terhubung ke server. Silakan coba lagi.",
                    "error"
                );
            } finally {
                submitButton.disabled = false;
            }
        });
    }

    fetchEducation();
})();
