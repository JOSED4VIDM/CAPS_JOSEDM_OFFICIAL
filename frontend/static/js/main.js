document.addEventListener("DOMContentLoaded", function () {
    const menuToggle = document.querySelector(".menu-toggle");
    const navigation = document.querySelector("#main-navigation");

    if (menuToggle && navigation) {
        menuToggle.addEventListener("click", () => {
            const isOpen = menuToggle.getAttribute("aria-expanded") === "true";
            menuToggle.setAttribute("aria-expanded", String(!isOpen));
            menuToggle.setAttribute("aria-label", isOpen ? "Abrir menú" : "Cerrar menú");
            navigation.classList.toggle("is-open", !isOpen);
        });

        navigation.addEventListener("click", (event) => {
            if (event.target.closest("a")) {
                menuToggle.setAttribute("aria-expanded", "false");
                menuToggle.setAttribute("aria-label", "Abrir menú");
                navigation.classList.remove("is-open");
            }
        });
    }

    const productGrid = document.querySelector(".product-grid");
    if (!productGrid) return;

    const cards = Array.from(productGrid.querySelectorAll(".product-card"));
    const filters = Array.from(document.querySelectorAll("[data-category-filter]"));
    const searchInput = document.querySelector("#catalog-search");
    const sortSelect = document.querySelector("#catalog-sort");
    const count = document.querySelector(".catalog-count");
    const noResults = document.querySelector(".no-results");
    let activeCategory = "all";

    const updateCatalog = () => {
        const query = searchInput ? searchInput.value.trim().toLocaleLowerCase() : "";
        const visibleCards = [];

        cards.forEach((card) => {
            const matchesCategory = activeCategory === "all" || card.dataset.category === activeCategory;
            const matchesSearch = card.dataset.name.includes(query);
            const isVisible = matchesCategory && matchesSearch;
            card.classList.toggle("is-hidden", !isVisible);
            if (isVisible) visibleCards.push(card);
        });

        const sortMode = sortSelect ? sortSelect.value : "featured";
        visibleCards.sort((first, second) => {
            if (sortMode === "price-asc") return Number(first.dataset.price) - Number(second.dataset.price);
            if (sortMode === "price-desc") return Number(second.dataset.price) - Number(first.dataset.price);
            if (sortMode === "name") return first.dataset.name.localeCompare(second.dataset.name);
            return cards.indexOf(first) - cards.indexOf(second);
        });

        visibleCards.forEach((card) => productGrid.appendChild(card));
        if (count) count.textContent = `${visibleCards.length} ${visibleCards.length === 1 ? "producto" : "productos"}`;
        if (noResults) noResults.hidden = visibleCards.length > 0;
    };

    filters.forEach((filter) => {
        filter.addEventListener("click", () => {
            activeCategory = filter.dataset.categoryFilter;
            filters.forEach((item) => {
                const isActive = item === filter;
                item.classList.toggle("is-active", isActive);
                item.setAttribute("aria-pressed", String(isActive));
            });
            updateCatalog();
        });
    });

    if (searchInput) searchInput.addEventListener("input", updateCatalog);
    if (sortSelect) sortSelect.addEventListener("change", updateCatalog);
    updateCatalog();
});
