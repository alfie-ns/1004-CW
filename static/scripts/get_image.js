let slideIndex = 0;
const slides = document.getElementsByClassName("slide");
const prevBtn = document.getElementById("prevBtn");
const nextBtn = document.getElementById("nextBtn");

function showSlides(n) {
    if (n >= slides.length) { 
        slideIndex = 0;
    } 
    if (n < 0) { 
        slideIndex = slides.length - 1;
    }

    for (let i = 0; i < slides.length; i++) {
        slides[i].style.display = "none";
    }

    slides[slideIndex].style.display = "block";
}

function changeSlide(n) {
    showSlides(slideIndex += n);
}

prevBtn.addEventListener("click", () => changeSlide(-1));
nextBtn.addEventListener("click", () => changeSlide(1));

// Show the first slide initially
showSlides(slideIndex);
