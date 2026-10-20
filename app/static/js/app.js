/* Termómetro de Riesgo · lógica de la interfaz.
   El formulario se construye con /api/metadata (campos y opciones del modelo
   guardado) y la predicción la hace el backend con /api/predict. */
(() => {
  "use strict";

  const $ = (sel, root = document) => root.querySelector(sel);
  const fieldsEl = $("#fields");
  const form = $("#form");
  const submitBtn = $("#btn-submit");
  const formError = $("#form-error");
  const CLASSES = ["Alto", "Medio", "Bajo"];
  const GROUP_ORDER = ["Operación", "Formalidad", "Digital", "Propietario y finanzas"];
  const nf = new Intl.NumberFormat("es-CO");
  let schema = [];

  // Caso de ejemplo (inventado, no pertenece a la base de entrenamiento).
  const EXAMPLE = {
    donde_funciona: "En su vivienda", como_lleva_cuentas: "Cuaderno, Excel o caja",
    visible_desde_la_calle: "Sí", zona: "Cabecera (urbana)", tiene_ayudantes: "Sí",
    acepta_transferencias: "Sí", tiene_nombre_comercial: "Sí", registrado_camara_comercio: "No",
    tiene_RUT: "No", usa_internet: "Sí", tiene_redes_sociales: "Sí",
    edad_propietario: 35, le_deja_al_mes_COP: 1200000,
  };

  const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));

  function controlHTML(f) {
    const id = `f-${f.nombre}`;
    if (f.tipo === "binaria" || (f.tipo === "categorica" && f.opciones.length <= 3)) {
      const opts = f.opciones.map((o) =>
        `<label><input type="radio" name="${f.nombre}" value="${esc(o)}"><span>${esc(o)}</span></label>`).join("");
      return `<div class="seg" role="radiogroup" aria-labelledby="${id}-label">${opts}</div>`;
    }
    if (f.tipo === "categorica") {
      const opts = f.opciones.map((o) => `<option value="${esc(o)}">${esc(o)}</option>`).join("");
      return `<select class="select" id="${id}" name="${f.nombre}" required>
                <option value="" disabled selected>Seleccione una opción</option>${opts}</select>`;
    }
    if (f.nombre === "le_deja_al_mes_COP") {
      return `<div class="input-affix"><span>$</span>
                <input class="input" id="${id}" name="${f.nombre}" inputmode="numeric" autocomplete="off"
                       placeholder="Ej.: ${nf.format(f.mediana_entrenamiento)}" required></div>`;
    }
    return `<input class="input" id="${id}" name="${f.nombre}" type="number" inputmode="numeric"
                   min="${f.minimo}" max="${f.maximo}" step="${f.paso}" placeholder="${f.minimo} a ${f.maximo}" required>`;
  }

  function renderForm(fields) {
    const groups = GROUP_ORDER.map((g) => [g, fields.filter((f) => f.grupo === g)]).filter(([, fs]) => fs.length);
    fieldsEl.innerHTML = groups.map(([g, fs], i) => `
      <fieldset class="group">
        <legend class="group__title"><span class="group__num">${i + 1}</span>${esc(g)}</legend>
        <div class="group__grid">
          ${fs.map((f) => `
            <div class="field ${f.nombre === "le_deja_al_mes_COP" ? "field--wide" : ""}" data-field="${f.nombre}">
              <label class="field__label" id="f-${f.nombre}-label" for="f-${f.nombre}">${esc(f.pregunta)}</label>
              ${controlHTML(f)}
              ${f.ayuda ? `<span class="field__help">${esc(f.ayuda)}</span>` : ""}
              <span class="field__error" aria-live="polite"></span>
            </div>`).join("")}
        </div>
      </fieldset>`).join("");

    const money = $('[name="le_deja_al_mes_COP"]');
    money.addEventListener("input", () => {
      const digits = money.value.replace(/\D/g, "").slice(0, 9);
      money.value = digits ? nf.format(Number(digits)) : "";
    });
    form.addEventListener("input", (e) => clearFieldError(e.target.name));
    form.addEventListener("change", (e) => clearFieldError(e.target.name));
  }

  function readForm() {
    const data = {};
    for (const f of schema) {
      const els = form.elements[f.nombre];
      let v = els.value;
      if (f.tipo === "numerica") {
        v = f.nombre === "le_deja_al_mes_COP" ? v.replace(/\D/g, "") : v.trim();
        data[f.nombre] = v === "" ? null : Number(v);
      } else {
        data[f.nombre] = v || null;
      }
    }
    return data;
  }

  function validate(data) {
    const errors = {};
    for (const f of schema) {
      const v = data[f.nombre];
      if (v === null || v === undefined || Number.isNaN(v)) { errors[f.nombre] = "Este campo es obligatorio."; continue; }
      if (f.tipo === "numerica") {
        if (v < f.minimo || v > f.maximo) errors[f.nombre] = `Debe estar entre ${nf.format(f.minimo)} y ${nf.format(f.maximo)}.`;
        else if (f.nombre === "edad_propietario" && !Number.isInteger(v)) errors[f.nombre] = "Use un número entero de años.";
      }
    }
    return errors;
  }

  function clearFieldError(name) {
    const el = name && $(`[data-field="${name}"]`);
    if (el) { el.classList.remove("is-invalid"); $(".field__error", el).textContent = ""; }
  }

  function showErrors(errors) {
    let first = null;
    for (const [name, msg] of Object.entries(errors)) {
      const el = $(`[data-field="${name}"]`);
      if (!el) continue;
      el.classList.add("is-invalid");
      $(".field__error", el).textContent = msg;
      first = first || el;
    }
    const general = errors._;
    const n = Object.keys(errors).filter((k) => k !== "_").length;
    formError.hidden = false;
    formError.textContent = general || `Revise ${n === 1 ? "1 campo" : n + " campos"} marcados en rojo.`;
    if (first) first.scrollIntoView({ behavior: "smooth", block: "center" });
  }

  function setLoading(on) {
    submitBtn.disabled = on;
    submitBtn.classList.toggle("is-loading", on);
    $(".btn__label", submitBtn).textContent = on ? "Clasificando…" : "Clasificar negocio";
  }

  function renderResult(r) {
    $("#result-empty").hidden = true;
    const card = $("#result-card");
    card.hidden = false;
    card.classList.remove("reveal"); void card.offsetWidth; card.classList.add("reveal");

    const badge = $("#verdict-badge");
    badge.textContent = `Riesgo ${r.nivel_riesgo}`;
    badge.dataset.cls = r.nivel_riesgo;
    document.querySelectorAll("#meter span").forEach((s) => s.classList.toggle("is-on", s.dataset.cls === r.nivel_riesgo));
    $("#meter").setAttribute("aria-label", `Nivel de riesgo: ${r.nivel_riesgo}`);
    $("#verdict-text").textContent = r.explicacion;

    const scores = r.puntajes_por_clase || {};
    $("#scores").innerHTML = CLASSES.map((c) => {
      const pct = Math.round((scores[c] || 0) * 100);
      return `<div class="score"><span class="score__name">${c}</span>
                <div class="score__track"><div class="score__bar" data-cls="${c}" data-w="${pct}"></div></div>
                <span class="score__val">${pct} %</span></div>`;
    }).join("");
    requestAnimationFrame(() => document.querySelectorAll(".score__bar").forEach((b) => { b.style.width = b.dataset.w + "%"; }));
    $("#scores-note").textContent = r.nota_puntajes || "";

    const steps = (r.reglas_aplicadas || []).map((s) => `<li>${esc(s)}</li>`);
    steps.push(`<li class="path__end"><span>Grupo de negocios parecidos → <strong>${esc(r.nivel_riesgo)}</strong></span></li>`);
    $("#path").innerHTML = steps.join("");
    $("#scope").textContent = r.alcance;

    if (window.matchMedia("(max-width: 979px)").matches) card.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  async function onSubmit(e) {
    e.preventDefault();
    formError.hidden = true;
    schema.forEach((f) => clearFieldError(f.nombre));
    const data = readForm();
    const errors = validate(data);
    if (Object.keys(errors).length) { showErrors(errors); return; }
    setLoading(true);
    try {
      const res = await fetch("/api/predict", {
        method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(data),
      });
      const body = await res.json().catch(() => ({}));
      if (!res.ok) {
        if (body.campos && Object.keys(body.campos).length) showErrors(body.campos);
        else { formError.hidden = false; formError.textContent = body.error || "No fue posible clasificar el negocio."; }
        return;
      }
      renderResult(body);
    } catch {
      formError.hidden = false;
      formError.textContent = "No hay conexión con el servidor. Verifique que la aplicación esté en ejecución.";
    } finally {
      setLoading(false);
    }
  }

  function fill(values) {
    for (const [k, v] of Object.entries(values)) {
      const els = form.elements[k];
      if (!els) continue;
      if (els instanceof RadioNodeList) els.value = v;
      else els.value = k === "le_deja_al_mes_COP" ? nf.format(v) : v;
      clearFieldError(k);
    }
  }

  async function init() {
    try {
      const res = await fetch("/api/metadata");
      if (!res.ok) throw new Error();
      const meta = await res.json();
      schema = meta.campos;
      renderForm(schema);
      const m = meta.modelo || {};
      const f1 = typeof m.cv_f1_macro === "number" ? ` · F1 macro CV ${m.cv_f1_macro.toFixed(2).replace(".", ",")}` : "";
      $("#chip-modelo").textContent = `Modelo: ${m.nombre}${f1}`;
    } catch {
      fieldsEl.innerHTML = "";
      formError.hidden = false;
      formError.textContent = "No se pudo cargar el modelo. Recargue la página o inicie de nuevo el servidor.";
      submitBtn.disabled = true;
    }
  }

  form.addEventListener("submit", onSubmit);
  $("#btn-example").addEventListener("click", () => fill(EXAMPLE));
  $("#btn-edit").addEventListener("click", () => form.scrollIntoView({ behavior: "smooth", block: "start" }));
  $("#btn-new").addEventListener("click", () => {
    form.reset();
    schema.forEach((f) => clearFieldError(f.nombre));
    formError.hidden = true;
    $("#result-card").hidden = true;
    $("#result-empty").hidden = false;
    form.scrollIntoView({ behavior: "smooth", block: "start" });
  });
  init();
})();
