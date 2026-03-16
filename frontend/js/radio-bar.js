/* ── TRAMPO Radio Bar ── */
(function () {

  const STATIONS = [
    { name: "Jovem Pan FM",  emoji: "📻", url: "https://stream.zeno.fm/4d5e6g7h8i9j" },
    { name: "Rádio Globo",   emoji: "🎙️", url: "https://stream.zeno.fm/1a2b3c4d5e6f" },
    { name: "Band FM",       emoji: "🎵", url: "https://stream.zeno.fm/r9rrej0drdruv" },
    { name: "Antena 1",      emoji: "🎸", url: "https://antena1.hqserver.com.br/8020/stream" },
    { name: "CBN",           emoji: "📰", url: "https://stream.zeno.fm/yn65m6qpnqquv" },
    { name: "89 FM",         emoji: "🎶", url: "https://stream.zeno.fm/2un5eu09g6zuv" },
  ];

  let cur = 0, playing = false;
  const audio = new Audio();
  audio.preload = "none";
  audio.crossOrigin = "anonymous";

  const bar = document.createElement("div");
  bar.id = "radio-bar";
  bar.innerHTML = `
<style>
#radio-bar{
  position:fixed;bottom:0;left:0;right:0;z-index:9999;
  background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);
  color:#fff;display:flex;align-items:center;gap:10px;
  padding:0 20px;height:52px;
  box-shadow:0 -2px 20px rgba(0,0,0,.5);
  font-family:'Nunito','Segoe UI',sans-serif;font-size:13px;
  border-top:1px solid rgba(0,200,83,.25);
}
#radio-bar .rb-emoji{font-size:18px;flex-shrink:0}
#radio-bar .rb-info{flex:1;min-width:0;overflow:hidden}
#radio-bar .rb-name{font-weight:700;color:#e2e8f0;font-size:13px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
#radio-bar .rb-sub{font-size:10px;color:#64748b;margin-top:1px}
#radio-bar .rb-eq{display:inline-flex;gap:2px;align-items:flex-end;height:13px;margin-left:5px;vertical-align:middle}
#radio-bar .rb-eq span{width:3px;border-radius:1px;background:#00C853}
#radio-bar .rb-eq span:nth-child(1){height:4px}
#radio-bar .rb-eq span:nth-child(2){height:8px}
#radio-bar .rb-eq span:nth-child(3){height:13px}
#radio-bar .rb-eq.on span:nth-child(1){animation:eq .5s ease-in-out infinite}
#radio-bar .rb-eq.on span:nth-child(2){animation:eq .5s ease-in-out -.2s infinite}
#radio-bar .rb-eq.on span:nth-child(3){animation:eq .5s ease-in-out -.1s infinite}
@keyframes eq{0%,100%{transform:scaleY(.3)}50%{transform:scaleY(1)}}
#radio-bar .rb-live{background:rgba(0,200,83,.15);color:#00C853;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;flex-shrink:0;display:none}
#radio-bar .rb-live.on{display:inline-block}
#radio-bar select{background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.1);color:#e2e8f0;border-radius:6px;padding:4px 7px;font-size:12px;cursor:pointer;flex-shrink:0;max-width:160px}
#radio-bar select option{background:#1e293b}
#radio-bar .rb-btn{background:none;border:none;cursor:pointer;color:#94a3b8;font-size:15px;padding:5px 6px;border-radius:6px;transition:.15s;flex-shrink:0}
#radio-bar .rb-btn:hover{background:rgba(255,255,255,.1);color:#fff}
#radio-bar .rb-play{background:#00C853!important;color:#000!important;border-radius:50%!important;width:34px!important;height:34px!important;display:flex!important;align-items:center!important;justify-content:center!important;font-size:14px!important;font-weight:700!important}
#radio-bar .rb-play:hover{background:#00A846!important}
#radio-bar .rb-vol{width:65px;accent-color:#00C853;cursor:pointer;flex-shrink:0}
#radio-bar .rb-x{color:#475569!important;font-size:11px!important}
body{padding-bottom:52px}
</style>
<span class="rb-emoji" id="rb-emoji">📻</span>
<div class="rb-info">
  <div class="rb-name"><span id="rb-name">Rádio TRAMPO</span>
    <span class="rb-eq" id="rb-eq"><span></span><span></span><span></span></span>
  </div>
  <div class="rb-sub" id="rb-sub">Selecione uma estação e clique ▶</div>
</div>
<span class="rb-live" id="rb-live">● AO VIVO</span>
<select id="rb-sel" onchange="window._rb.sel(this.value)">
  ${STATIONS.map((s,i)=>`<option value="${i}">${s.emoji} ${s.name}</option>`).join("")}
</select>
<button class="rb-btn" onclick="window._rb.prev()" title="Anterior">⏮</button>
<button class="rb-btn rb-play" id="rb-play" onclick="window._rb.toggle()">▶</button>
<button class="rb-btn" onclick="window._rb.next()" title="Próxima">⏭</button>
<input type="range" class="rb-vol" min="0" max="100" value="70"
       oninput="window._rb.vol(this.value)" title="Volume">
<button class="rb-btn rb-x" onclick="window._rb.close()" title="Fechar">✕</button>
`;
  document.body.appendChild(bar);

  function load(idx) {
    cur = ((idx % STATIONS.length) + STATIONS.length) % STATIONS.length;
    const s = STATIONS[cur];
    document.getElementById("rb-name").textContent  = s.name;
    document.getElementById("rb-emoji").textContent = s.emoji;
    document.getElementById("rb-sub").textContent   = "Conectando…";
    document.getElementById("rb-sel").value         = cur;
    audio.src    = s.url;
    audio.volume = document.querySelector(".rb-vol").value / 100;
  }

  function ui() {
    const p = document.getElementById("rb-play");
    const eq = document.getElementById("rb-eq");
    const lv = document.getElementById("rb-live");
    if (p)  p.textContent = playing ? "⏸" : "▶";
    if (eq) eq.classList.toggle("on", playing);
    if (lv) lv.classList.toggle("on", playing);
  }

  audio.addEventListener("playing", () => {
    playing = true;
    document.getElementById("rb-sub").textContent = "Ao vivo";
    ui();
  });
  audio.addEventListener("waiting", () => {
    document.getElementById("rb-sub").textContent = "Conectando…";
  });
  audio.addEventListener("error", () => {
    playing = false;
    document.getElementById("rb-sub").textContent = "Falhou — tente outra";
    ui();
  });
  audio.addEventListener("pause", () => {
    playing = false;
    ui();
  });

  window._rb = {
    toggle() {
      if (playing) {
        audio.pause();
      } else {
        if (!audio.src || audio.src === location.href) load(cur);
        const p = audio.play();
        if (p) p.catch(() => {
          document.getElementById("rb-sub").textContent = "Clique novamente para tocar";
        });
      }
    },
    next()    { load(cur + 1); if (playing) audio.play().catch(()=>{}); },
    prev()    { load(cur - 1); if (playing) audio.play().catch(()=>{}); },
    sel(i)    { load(parseInt(i)); if (playing) audio.play().catch(()=>{}); },
    vol(v)    { audio.volume = v / 100; },
    close()   { audio.pause(); bar.remove(); document.body.style.paddingBottom = "0"; },
  };

  load(0);

  /* Busca estações reais da Radio Browser em background */
  setTimeout(async () => {
    try {
      const r = await fetch(
        "https://de1.api.radio-browser.info/json/stations/search" +
        "?countrycode=BR&limit=15&order=clickcount&reverse=true&hidebroken=true",
        { headers: { "User-Agent": "TRAMPO/1.0" } }
      );
      const data = await r.json();
      if (!Array.isArray(data) || !data.length) return;
      const emojis = ["📻","🎙️","🎵","🎸","🎶","📰","🎤","🔊","🎧","📡","🎼","🎹","🎺","🥁","🪗"];
      const live = data
        .filter(s => s.url_resolved && s.name && s.url_resolved.startsWith("http"))
        .slice(0, 15)
        .map((s, i) => ({ name: s.name.trim().slice(0,25), emoji: emojis[i%emojis.length], url: s.url_resolved }));
      if (!live.length) return;
      STATIONS.splice(0, STATIONS.length, ...live);
      const sel = document.getElementById("rb-sel");
      if (sel) {
        sel.innerHTML = STATIONS.map((s,i)=>`<option value="${i}">${s.emoji} ${s.name}</option>`).join("");
        sel.value = 0;
      }
      load(0);
    } catch(e) { /* mantém fallback */ }
  }, 2000);

})();
