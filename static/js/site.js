// Small helpers. The site works fully without this file.
(function () {
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("site-nav");
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        nav.classList.remove("is-open");
        toggle.setAttribute("aria-expanded", "false");
        toggle.focus();
      }
    });
  }
  // The live demo runs on a free server that sleeps. Ask it to wake up while the visitor reads.
  var main = document.querySelector("[data-wake]");
  if (main && window.fetch) {
    window.setTimeout(function () {
      fetch(main.getAttribute("data-wake"), { mode: "no-cors", cache: "no-store" }).catch(function () {});
    }, 1500);
  }
})();
