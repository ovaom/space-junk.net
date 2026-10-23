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

// Formulaire de contact : envoi sans quitter la page.
(() => {
  const form = document.querySelector(".contact-form");
  if (!form) return;
  const status = form.querySelector(".form-status");
  const button = form.querySelector("button");
  form.addEventListener("submit", async (e) => {
    e.preventDefault();
    button.disabled = true;
    status.textContent = "Envoi…";
    try {
      const res = await fetch(form.action, {
        method: "POST",
        headers: { Accept: "application/json" },
        body: new FormData(form),
      });
      const json = await res.json();
      if (!json.success) throw new Error(json.message);
      form.reset();
      status.textContent = "Merci, votre message a bien été envoyé.";
    } catch {
      status.textContent = "L'envoi a échoué. Réessayez dans un instant.";
    } finally {
      button.disabled = false;
    }
  });
})();
