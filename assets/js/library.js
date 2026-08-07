(function () {
  "use strict";

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
