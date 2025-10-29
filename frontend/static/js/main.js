document.addEventListener("DOMContentLoaded", function () {
    const buttons = document.querySelectorAll(".primary-btn, .secondary-btn, .filter-button");
    buttons.forEach((button) => {
        button.addEventListener("mouseenter", () => button.style.transform = "translateY(-2px)");
        button.addEventListener("mouseleave", () => button.style.transform = "translateY(0)");
    });
});
