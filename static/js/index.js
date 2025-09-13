document.addEventListener("DOMContentLoaded", () => {
  const menuBtn = document.querySelector(".menu");
  const navUl = document.querySelector("nav ul");

  menuBtn.addEventListener("click", () => {
    navUl.classList.toggle("active");
  });
});
