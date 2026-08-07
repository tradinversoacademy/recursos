(function () {
  "use strict";

  function renderLibraryCards() {
    var container = document.querySelector("[data-resource-list]");
    var catalog = window.TRADINVERSO_RESOURCES || [];
    if (!container || !catalog.length) return;
    // tools/build_library.py deja las tarjetas ya escritas en el HTML para que
    // sean indexables. Solo se generan aquí si por lo que sea faltan.
    if (container.querySelector("[data-resource-card]")) return;

    catalog.filter(function (resource) {
      return !resource.hidden;
    }).forEach(function (resource) {
      var card = document.createElement("article");
      card.className = "resource-list-card";
      card.dataset.resourceCard = "";
      card.dataset.category = resource.category;
      card.dataset.search = resource.search;

      var top = document.createElement("div");
      top.className = "resource-list-top";
      var symbol = document.createElement("span");
      symbol.className = "resource-symbol";
      symbol.textContent = resource.symbol;
      var type = document.createElement("span");
      type.className = "resource-list-type";
      type.textContent = resource.type;
      top.appendChild(symbol);
      top.appendChild(type);

      var title = document.createElement("h3");
      title.textContent = resource.title;
      var description = document.createElement("p");
      description.textContent = resource.description;
      var link = document.createElement("a");
      link.href = "recursos/" + resource.slug + "/index.html";
      link.innerHTML = "";
      link.appendChild(document.createTextNode(resource.cta + " "));
      var arrow = document.createElement("span");
      arrow.setAttribute("aria-hidden", "true");
      arrow.textContent = "→";
      link.appendChild(arrow);

      card.appendChild(top);
      card.appendChild(title);
      card.appendChild(description);
      card.appendChild(link);
      container.appendChild(card);
    });
  }

  renderLibraryCards();

  var searchInput = document.querySelector("[data-library-search]");
  var filterButtons = Array.from(document.querySelectorAll("[data-library-filter]"));
  var cards = Array.from(document.querySelectorAll("[data-resource-card]"));
  var sections = Array.from(document.querySelectorAll("[data-resource-section]"));
  var totalCount = document.querySelector("[data-total-count]");
  var visibleCount = document.querySelector("[data-visible-count]");
  var emptyState = document.querySelector("[data-library-empty]");
  var activeFilter = "todos";

  if (totalCount) {
    totalCount.textContent = String(cards.length);
  }

  function normalize(value) {
    return value
      .toLowerCase()
      .normalize("NFD")
      .replace(/[\u0300-\u036f]/g, "")
      .trim();
  }

  function updateLibrary() {
    var query = normalize(searchInput ? searchInput.value : "");
    var shown = 0;

    cards.forEach(function (card) {
      var categoryMatches = activeFilter === "todos" || card.dataset.category === activeFilter;
      var searchableText = normalize(card.dataset.search + " " + card.textContent);
      var searchMatches = !query || searchableText.indexOf(query) !== -1;
      var isVisible = categoryMatches && searchMatches;

      card.hidden = !isVisible;
      if (isVisible) shown += 1;
    });

    sections.forEach(function (section) {
      section.hidden = !section.querySelector("[data-resource-card]:not([hidden])");
    });

    if (visibleCount) {
      visibleCount.textContent = shown + (shown === 1 ? " recurso" : " recursos");
    }

    if (emptyState) {
      emptyState.hidden = shown !== 0;
    }
  }

  filterButtons.forEach(function (button) {
    button.addEventListener("click", function () {
      activeFilter = button.dataset.libraryFilter;
      filterButtons.forEach(function (item) {
        var isActive = item === button;
        item.classList.toggle("is-active", isActive);
        item.setAttribute("aria-pressed", String(isActive));
      });
      updateLibrary();
    });
  });

  if (searchInput) {
    searchInput.addEventListener("input", updateLibrary);
  }

  updateLibrary();
})();
