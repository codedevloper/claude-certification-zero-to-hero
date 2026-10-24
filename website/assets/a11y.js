// Small accessibility fixes on top of Material for MkDocs.
document.addEventListener("DOMContentLoaded", function () {
  // The search overlay is a dialog without an accessible name.
  var search = document.querySelector('.md-search[role="dialog"]');
  if (search && !search.hasAttribute("aria-label")) search.setAttribute("aria-label", "Search the study guide");
});
