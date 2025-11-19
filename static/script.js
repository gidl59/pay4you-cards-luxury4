document.addEventListener("DOMContentLoaded", function () {
  const callLinks = document.querySelectorAll(".js-call-link");

  callLinks.forEach((link) => {
    link.addEventListener("click", function (e) {
      const number = this.dataset.number || this.getAttribute("href");
      const msg = `Vuoi chiamare questo numero?\n\n${number}`;
      const ok = window.confirm(msg);
      if (!ok) {
        e.preventDefault();
      }
    });
  });
});
