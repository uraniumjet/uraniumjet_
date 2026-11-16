(function () {
  "use strict";
  document.documentElement.classList.add("js");

  // Mobile menu
  var toggle = document.querySelector(".nav-toggle");
  var nav = document.getElementById("primary-nav");
  function closeMenu() {
    nav.classList.remove("is-open");
    toggle.setAttribute("aria-expanded", "false");
    toggle.textContent = "Menu";
  }
  if (toggle && nav) {
    toggle.addEventListener("click", function () {
      var open = nav.classList.toggle("is-open");
      toggle.setAttribute("aria-expanded", open ? "true" : "false");
      toggle.textContent = open ? "Close" : "Menu";
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape" && nav.classList.contains("is-open")) {
        closeMenu();
        toggle.focus();
      }
    });
  }

  // Contact form: stop double sends, and move focus to the error message
  var form = document.querySelector("form.form");
  if (form) {
    var button = form.querySelector("button[type=submit]");
    var label = button ? button.textContent : "";
    form.addEventListener("submit", function () {
      if (button) {
        button.disabled = true;
        button.textContent = button.getAttribute("data-sending") || "Sending...";
      }
    });
    window.addEventListener("pageshow", function (e) {
      if (e.persisted && button) {
        button.disabled = false;
        button.textContent = label;
      }
    });
    var alertBox = document.getElementById("form-alert");
    if (alertBox) alertBox.focus();
  }
})();
