/* ── TRAMPO Radio Bar — player fixo no rodapé ── */
(function() {

const STATIONS = [
  { name:"Jovem Pan FM",    url:"https://playerservices.streamtheworld.com/api/livestream-redirect/JOVEMPANFM_SC",  emoji:"📻" },
  { name:"Rádio Globo SP",  url:"https://playerservices.streamtheworld.com/api/livestream-redirect/RDGLOBOSP_SC",   emoji:"🎙️" },
  { name:"CBN",             url:"https://playerservices.streamtheworld.com/api/livestream-redirect/CBN_SPSC",        emoji:"📰" },
  { name:"89 FM Rock",      url:"https://playerservices.streamtheworld.com/api/livestream-redirect/RADIO89FMSC",     emoji:"🎸" },
  { name:"Antena 1",        url:"https://playerservices.streamtheworld.com/api/livestream-redirect/ANTENA1SC",       emoji:"🎵" },
  { name:"Band FM",         url:"https://playerservices.streamtheworld.com/api/livestream-redirect/BANDFMSC",        emoji:"🎶" },
];

let current = 0, playing = false;
const audio = document.createElement("audio");
audio.preload = "none";
document.body.appendChild(audio);

const bar = document.createElement("div");
bar.id = "radio-bar";
bar.innerHTML = `
<style>
#radio-bar{
  position:fixed;bottom:0;left:0;right:0;z-index:1000;
  background:linear-gradient(135deg,#0f172a,#1e293b);
  color:#fff;display:flex;align-items:center;gap:12px;
  padding:8px 20px;box-shadow:0 -4px 20px rgba(0,0,0,.3);
  font-family:'Segoe UI',sans-serif;font-size:13px;
}
#radio-bar .rb-logo{font-size:18px;flex-shrink:0}
#radio-bar .rb-name{flex:1;min-width:0;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;color:#e2e8f0}
#radio-bar .rb-name strong{color:#10b981}
#radio-bar button{background:none;border:none;cursor:pointer;color:#94a3b8;font-size:16px;padding:4px 6px;border-radius:6px;transition:all .15s;flex-shrink:0}
#radio-bar button:hover{background:rgba(255,255,255,.1);color:#fff}
#radio-bar .rb-play{background:#10b981!important;color:#fff!important;border-radius:50%!important;width:34px;height:34px;font-size:14px!important;display:flex;align-items:center;justify-content:center}
#radio-bar .rb-play:hover{background:#059669!important}
#radio-bar select{background:rgba(255,255,255,.1);border:none;color:#e2e8f0;border-radius:6px;padding:4px 8px;font-size:12px;cursor:pointer;flex-shrink:0}
#radio-bar select option{background:#1e293b;color:#e2e8f0}
#radio-bar .rb-eq{display:inline-flex;gap:2px;align-items:flex-end;height:16px;margin-left:4px}
#radio-bar .rb-eq span{width:3px;background:#10b981;border-radius:1px;animation:rbeq .8s ease-in-out infinite}
#radio-bar .rb-eq span:nth-child(1){height:6px;animation-delay:0s}
#radio-bar .rb-eq span:nth-child(2){height:12px;animation-delay:.2s}
#radio-bar .rb-eq span:nth-child(3){height:8px;animation-delay:.1s}
#radio-bar .rb-eq.paused span{animation-play-state:paused;height:4px!important}
#radio-bar .rb-vol{width:70px;-webkit-appearance:none;height:3px;border-radius:2px;background:#334155;outline:none;cursor:pointer}
#radio-bar .rb-vol::-webkit-slider-thumb{-webkit-appearance:none;width:12px;height:12px;border-radius:50%;background:#10b981}
@keyframes rbeq{0%,100%{transform:scaleY(1)}50%{transform:scaleY(1.8)}}
body{padding-bottom:56px}
</style>
<span class="rb-logo" id="rb-emoji">📻</span>
<div class="rb-name"><strong id="rb-name">Rádio TRAMPO</strong>
  <span class="rb-eq paused" id="rb-eq"><span></span><span></span><span></span></span>
</div>
<select id="rb-select" onchange="rbSelect(this.value)">
  ${STATIONS.map((s,i)=>`<option value="${i}">${s.emoji} ${s.name}</option>`).join("")}
</select>
<button onclick="rbPrev()" title="Anterior">⏮</button>
<button class="rb-play" id="rb-play" onclick="rbToggle()">▶</button>
<button onclick="rbNext()" title="Próxima">⏭</button>
<input type="range" class="rb-vol" min="0" max="100" value="70" oninput="rbVol(this.value)" title="Volume">
<button onclick="rbClose()" title="Fechar rádio" style="color:#475569;font-size:12px">✕</button>
`;
document.body.appendChild(bar);

function rbLoad(idx) {
  current = (idx + STATIONS.length) % STATIONS.length;
  const s = STATIONS[current];
  document.getElementById("rb-name").textContent = s.name;
  document.getElementById("rb-emoji").textContent = s.emoji;
  document.getElementById("rb-select").value = current;
  audio.src = s.url;
  audio.volume = document.querySelector(".rb-vol").value / 100;
}

function rbToggle() {
  if (playing) {
    audio.pause(); playing = false;
  } else {
    if (!audio.src || audio.src === location.href) rbLoad(current);
    audio.play().catch(() => {});
    playing = true;
  }
  _rbUpdateUI();
}

function rbNext() { rbLoad(current + 1); if (playing) { audio.play().catch(()=>{}); } }
function rbPrev() { rbLoad(current - 1); if (playing) { audio.play().catch(()=>{}); } }
function rbSelect(i) { rbLoad(parseInt(i)); if (playing) { audio.play().catch(()=>{}); } }
function rbVol(v) { audio.volume = v / 100; }
function rbClose() { audio.pause(); bar.style.display="none"; document.body.style.paddingBottom="0"; }

function _rbUpdateUI() {
  document.getElementById("rb-play").textContent = playing ? "⏸" : "▶";
  document.getElementById("rb-eq").classList.toggle("paused", !playing);
}

audio.addEventListener("error", () => { playing = false; _rbUpdateUI(); });
audio.addEventListener("playing", () => { playing = true; _rbUpdateUI(); });

// Não carrega automaticamente — espera o user clicar
rbLoad(0);
})();
