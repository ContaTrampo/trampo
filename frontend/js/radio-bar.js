/* ── TRAMPO Radio Bar — Radio Browser API ── */
(function () {

  const FALLBACK_STATIONS = [
    { name: "Jovem Pan FM",   url: "https://playerservices.streamtheworld.com/api/livestream-redirect/JOVEMPANFM_SC",  emoji: "📻" },
    { name: "Rádio Globo",    url: "https://playerservices.streamtheworld.com/api/livestream-redirect/RDGLOBOSP_SC",   emoji: "🎙️" },
    { name: "CBN",             url: "https://playerservices.streamtheworld.com/api/livestream-redirect/CBN_SPSC",       emoji: "📰" },
    { name: "89 FM Rock",     url: "https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO89FMSC",    emoji: "🎸" },
    { name: "Antena 1",       url: "https://playerservices.streamtheworld.com/api/livestream-redirect/ANTENA1SC",      emoji: "🎵" },
    { name: "Band FM",        url: "https://playerservices.streamtheworld.com/api/livestream-redirect/BANDFMSC",       emoji: "🎶" },
  ];

  let stations = [...FALLBACK_STATIONS];
  let current = 0, playing = false;
  const audio = new Audio();
  audio.preload = "none";

  /* ── Busca estações brasileiras na Radio Browser API ── */
  async function loadRadioBrowserStations() {
    try {
      // Pega lista de servidores disponíveis
      const dnsResp = await fetch("https://all.api.radio-browser.info/json/servers", {
        headers: { "User-Agent": "TRAMPO-Plataforma/1.0" }
      });
      const servers = await dnsResp.json();

      // Escolhe um servidor aleatório
      const server = servers[Math.floor(Math.random() * servers.length)].name;
      const apiBase = `https://${server}`;

      // Busca top 20 estações do Brasil com boa qualidade
      const resp = await fetch(
        `${apiBase}/json/stations/search?` +
        `countrycode=BR&limit=20&order=clickcount&reverse=true&hidebroken=true`,
        { headers: { "User-Agent": "TRAMPO-Plataforma/1.0" } }
      );

      const data = await resp.json();
      if (!Array.isArray(data) || data.length === 0) return;

      const emojis = ["📻", "🎙️", "🎵", "🎸", "🎶", "📰", "🎤", "🔊", "🎧", "📡"];

      stations = data
        .filter(s => s.url_resolved && s.name)
        .map((s, i) => ({
          name:  s.name.trim().slice(0, 28),
          url:   s.url_resolved,
          emoji: emojis[i % emojis.length],
          uuid:  s.stationuuid,
          apiBase,
        }));

      // Atualiza o select com as estações reais
      renderSelect();
      console.log(`✅ Radio Browser: ${stations.length} estações BR carregadas`);

    } catch (e) {
      console.log("⚠️ Radio Browser indisponível, usando fallback:", e.message);
    }
  }

  /* ── Reporta clique (ajuda o banco de dados da API) ── */
  function reportClick(station) {
    if (!station.uuid || !station.apiBase) return;
    fetch(`${station.apiBase}/json/url/${station.uuid}`, {
      method: "GET",
      headers: { "User-Agent": "TRAMPO-Plataforma/1.0" }
    }).catch(() => {});
  }

  /* ── Monta o HTML do player ── */
  const bar = document.createElement("div");
  bar.id = "radio-bar";
  bar.innerHTML = `
<style>
#radio-bar{
  position:fixed;bottom:0;left:0;right:0;z-index:1000;
  background:linear-gradient(135deg,#0f172a,#1e293b);
  color:#fff;display:flex;align-items:center;gap:12px;
  padding:8px 20px;box-shadow:0 -4px 20px rgba(0,0,0,.4);
  font-family:'Nunito','Segoe UI',sans-serif;font-size:13px;
  border-top:1px solid rgba(0,200,83,.2);
}
#radio-bar .rb-logo{font-size:20px;flex-shrink:0}
#radio-bar .rb-info{flex:1;min-width:0}
#radio-bar .rb-name{font-weight:700;color:#e2e8f0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;font-size:13px}
#radio-bar .rb-sub{font-size:11px;color:#64748b;margin-top:1px}
#radio-bar .rb-eq{display:inline-flex;gap:2px;align-items:flex-end;height:14px;margin-left:6px;vertical-align:middle}
#radio-bar .rb-eq span{width:3px;background:#00C853;border-radius:1px}
#radio-bar .rb-eq.playing span:nth-child(1){animation:rbeq .6s ease-in-out infinite;height:6px}
#radio-bar .rb-eq.playing span:nth-child(2){animation:rbeq .6s ease-in-out -.2s infinite;height:10px}
#radio-bar .rb-eq.playing span:nth-child(3){animation:rbeq .6s ease-in-out -.1s infinite;height:14px}
#radio-bar .rb-eq span{height:3px}
#radio-bar button{background:none;border:none;cursor:pointer;color:#94a3b8;font-size:16px;padding:5px 7px;border-radius:6px;transition:all .15s;flex-shrink:0}
#radio-bar button:hover{background:rgba(255,255,255,.1);color:#fff}
#radio-bar .rb-play{background:#00C853!important;color:#000!important;border-radius:50%!important;width:36px;height:36px;font-size:14px!important;display:flex!important;align-items:center!important;justify-content:center!important;font-weight:700!important}
#radio-bar .rb-play:hover{background:#00A846!important;transform:scale(1.08)}
#radio-bar select{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.1);color:#e2e8f0;border-radius:6px;padding:5px 8px;font-size:12px;cursor:pointer;flex-shrink:0;max-width:180px}
#radio-bar select option{background:#1e293b;color:#e2e8f0}
#radio-bar .rb-vol{width:70px;-webkit-appearance:none;height:3px;border-radius:2px;background:#334155;outline:none;cursor:pointer}
#radio-bar .rb-vol::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:12px;border-radius:50%;background:#00C853;cursor:pointer}
#radio-bar .rb-close{color:#475569!important;font-size:12px!important}
#radio-bar .rb-live{background:rgba(0,200,83,.15);color:#00C853;padding:2px 7px;border-radius:10px;font-size:10px;font-weight:700;letter-spacing:.5px;flex-shrink:0;display:none}
#radio-bar .rb-live.show{display:inline-block}
@keyframes rbeq{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.8)}}
body{padding-bottom:56px!important}
</style>

<span class="rb-logo" id="rb-emoji">📻</span>
<div class="rb-info">
  <div class="rb-name">
    <span id="rb-name">Rádio TRAMPO</span>
    <span class="rb-eq" id="rb-eq"><span></span><span></span><span></span></span>
  </div>
  <div class="rb-sub" id="rb-sub">Clique ▶ para ouvir</div>
</div>
<span class="rb-live" id="rb-live">● AO VIVO</span>
<select id="rb-select" onchange="rbSelect(this.value)"></select>
<button onclick="rbPrev()" title="Anterior">⏮</button>
<button class="rb-play" id="rb-play" onclick="rbToggle()">▶</button>
<button onclick="rbNext()" title="Próxima">⏭</button>
<input type="range" class="rb-vol" min="0" max="100" value="70"
       oninput="rbVol(this.value)" title="Volume">
<button class="rb-close" onclick="rbClose()" title="Fechar">✕</button>
`;
  document.body.appendChild(bar);

  function renderSelect() {
    const sel = document.getElementById("rb-select");
    if (!sel) return;
    sel.innerHTML = stations.map((s, i) =>
      `<option value="${i}">${s.emoji} ${s.name}</option>`
    ).join("");
    sel.value = current;
  }

  renderSelect(); // renderiza com fallback primeiro

  function rbLoad(idx) {
    current = ((idx % stations.length) + stations.length) % stations.length;
    const s = stations[current];
    document.getElementById("rb-name").textContent  = s.name;
    document.getElementById("rb-emoji").textContent = s.emoji;
    document.getElementById("rb-sub").textContent   = "Carregando…";
    document.getElementById("rb-select").value      = current;
    audio.src    = s.url;
    audio.volume = document.querySelector(".rb-vol").value / 100;
  }

  function rbToggle() {
    if (playing) {
      audio.pause();
      playing = false;
    } else {
      if (!audio.src || audio.src === location.href) rbLoad(current);
      audio.play().catch(() => {
        document.getElementById("rb-sub").textContent = "Erro — tente outra estação";
      });
      playing = true;
      reportClick(stations[current]);
    }
    _rbUI();
  }

  function rbNext()      { rbLoad(current + 1); if (playing) { audio.play().catch(() => {}); reportClick(stations[current]); } }
  function rbPrev()      { rbLoad(current - 1); if (playing) { audio.play().catch(() => {}); reportClick(stations[current]); } }
  function rbSelect(i)   { rbLoad(parseInt(i)); if (playing) { audio.play().catch(() => {}); reportClick(stations[current]); } }
  function rbVol(v)      { audio.volume = v / 100; }
  function rbClose()     { audio.pause(); bar.style.display = "none"; document.body.style.paddingBottom = "0"; }

  function _rbUI() {
    document.getElementById("rb-play").textContent = playing ? "⏸" : "▶";
    document.getElementById("rb-eq").classList.toggle("paused-eq", !playing);
    document.getElementById("rb-eq").classList.toggle("playing", playing);
    document.getElementById("rb-live").classList.toggle("show", playing);
  }

  audio.addEventListener("playing", () => {
    playing = true;
    document.getElementById("rb-sub").textContent = "Ao vivo";
    _rbUI();
  });
  audio.addEventListener("error", () => {
    playing = false;
    document.getElementById("rb-sub").textContent = "Erro — tente outra estação";
    _rbUI();
  });
  audio.addEventListener("waiting", () => {
    document.getElementById("rb-sub").textContent = "Carregando…";
  });

  // Expõe funções globalmente
  window.rbToggle = rbToggle;
  window.rbNext   = rbNext;
  window.rbPrev   = rbPrev;
  window.rbSelect = rbSelect;
  window.rbVol    = rbVol;
  window.rbClose  = rbClose;

  rbLoad(0);

  // Carrega estações reais em background sem bloquear a página
  loadRadioBrowserStations();

})();
