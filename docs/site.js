// Visionneuse : clic sur une image de projet pour l'afficher en grand.
(() => {
  const links = [...document.querySelectorAll(".assets .zoom")];
  if (!links.length) return;
  const box = document.createElement("div");
  box.className = "lightbox";
  box.hidden = true;
  box.innerHTML = '<img alt=""><button class="prev" aria-label="Précédente">‹</button>' +
    '<button class="next" aria-label="Suivante">›</button><button class="close" aria-label="Fermer">×</button>';
  document.body.append(box);
  const img = box.querySelector("img");
  let i = 0;
  const show = (n) => { i = (n + links.length) % links.length; img.src = links[i].href; box.hidden = false; };
  const hide = () => { box.hidden = true; img.removeAttribute("src"); };
  links.forEach((a, n) => a.addEventListener("click", (e) => { e.preventDefault(); show(n); }));
  box.querySelector(".prev").onclick = (e) => { e.stopPropagation(); show(i - 1); };
  box.querySelector(".next").onclick = (e) => { e.stopPropagation(); show(i + 1); };
  box.querySelector(".close").onclick = hide;
  box.addEventListener("click", (e) => { if (e.target === box) hide(); });
  document.addEventListener("keydown", (e) => {
    if (box.hidden) return;
    if (e.key === "Escape") hide();
    if (e.key === "ArrowLeft") show(i - 1);
    if (e.key === "ArrowRight") show(i + 1);
  });
})();
