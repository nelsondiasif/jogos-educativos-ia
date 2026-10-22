// ===============================
// Configuração: nomes das imagens
// Coloque suas imagens em ./imagens/ e ajuste abaixo
// ===============================
const IMAGENS = [
  "img1.jpg",
  "img2.jpg",
  "img3.jpg",
  "img4.jpg",
  "img5.jpg",
  "img6.jpg",
  "img7.jpg",
  "img8.jpg"
];
const PASTA = "imagens/"; // altere se suas imagens estiverem em outra pasta

// ===============================
// Estado do jogo
// ===============================
let primeira = null; // primeiro card clicado
let segunda = null;  // segundo card clicado
let travado = false; // trava enquanto comparamos
let movimentos = 0;
let acertos = 0;
let totalPares = 0;
let timerId = null;
let segundos = 0;

const $ = (sel) => document.querySelector(sel);
const $$ = (sel) => document.querySelectorAll(sel);
const elTabuleiro = $("#tabuleiro");
const elTempo = $("#tempo");
const elMov = $("#movimentos");
const elAcertos = $("#acertos");
const btnReiniciar = $("#btnReiniciar");
const modal = $("#modalVitoria");
const tempoFinal = $("#tempoFinal");
const movFinal = $("#movFinal");
const btnJogarNovamente = $("#btnJogarNovamente");

btnReiniciar.addEventListener("click", iniciarJogo);
btnJogarNovamente.addEventListener("click", () => { modal.hidden = true; iniciarJogo(); });

// Inicia ao carregar
window.addEventListener("DOMContentLoaded", iniciarJogo);

function iniciarJogo(){
  pararTimer();
  segundos = 0; atualizarTempo();
  movimentos = 0; elMov.textContent = movimentos;
  acertos = 0; elAcertos.textContent = acertos;
  primeira = segunda = null; travado = false;
  modal.hidden = true;

  // monta baralho duplicando as imagens
  const baralho = shuffle([...IMAGENS, ...IMAGENS].map((nome) => ({
    id: cryptoRandomId(),
    chave: nome, // chave para comparação
    src: PASTA + nome,
  })));
  totalPares = IMAGENS.length;

  // desenha
  elTabuleiro.innerHTML = "";
  for(const carta of baralho){
    const node = criarCard(carta);
    elTabuleiro.appendChild(node);
  }
}

function criarCard(carta){
  const tpl = document.getElementById("tpl-card");
  const el = tpl.content.firstElementChild.cloneNode(true);
  const img = el.querySelector("img");
  img.src = carta.src;
  img.alt = `Figura do par ${carta.chave}`;

  el.dataset.id = carta.id;
  el.dataset.key = carta.chave;
  el.addEventListener("click", () => virar(el));
  el.addEventListener("keydown", (ev)=>{
    if(ev.key === "Enter" || ev.key === " "){
      ev.preventDefault(); el.click();
    }
  });
  img.addEventListener("error", ()=>{
    // fallback simples caso a imagem não exista
    img.replaceWith(criarFallback(carta.chave));
  });
  return el;
}

function criarFallback(texto){
  const box = document.createElement("div");
  box.style.width = "100%";
  box.style.height = "100%";
  box.style.display = "grid";
  box.style.placeItems = "center";
  box.style.fontWeight = "800";
  box.style.fontSize = "clamp(16px, 2vw, 22px)";
  box.textContent = texto.replace(/\..+$/, "");
  return box;
}

function virar(btn){
  if(travado || btn.classList.contains("certa") || btn === primeira){
    return;
  }
  // inicia o cronômetro no primeiro movimento real
  if(movimentos === 0 && !timerId){
    iniciarTimer();
  }

  btn.classList.add("virada");
  btn.setAttribute("aria-pressed", "true");

  if(!primeira){
    primeira = btn;
    return;
  }

  segunda = btn;
  movimentos++; elMov.textContent = movimentos;
  comparar();
}

function comparar(){
  const ehPar = primeira.dataset.key === segunda.dataset.key;
  travado = true;

  if(ehPar){
    marcarCerto(primeira); marcarCerto(segunda);
    resetarSelecao();
    acertos++; elAcertos.textContent = acertos;
    if(acertos === totalPares){
      pararTimer();
      tempoFinal.textContent = elTempo.textContent;
      movFinal.textContent = movimentos;
      modal.hidden = false;
    }
  }else{
    marcarErrado(primeira); marcarErrado(segunda);
    setTimeout(()=>{
      desvirar(primeira); desvirar(segunda);
      resetarSelecao();
    }, 750);
  }
}

function marcarCerto(el){ el.classList.add("certa"); el.disabled = true; }
function marcarErrado(el){ el.classList.add("errada"); }
function desvirar(el){
  el.classList.remove("virada", "errada");
  el.setAttribute("aria-pressed", "false");
}
function resetarSelecao(){
  primeira = null; segunda = null; travado = false;
}

function shuffle(arr){
  for(let i=arr.length-1;i>0;i--){
    const j = Math.floor(Math.random()*(i+1));
    [arr[i], arr[j]] = [arr[j], arr[i]];
  }
  return arr;
}

function cryptoRandomId(){
  // id curto único por carta
  const a = new Uint8Array(6);
  (crypto.getRandomValues||window.msCrypto.getRandomValues).call(crypto, a);
  return [...a].map(x=>x.toString(16).padStart(2,"0")).join("");
}

function iniciarTimer(){
  timerId = setInterval(()=>{ segundos++; atualizarTempo(); }, 1000);
}
function pararTimer(){
  clearInterval(timerId); timerId = null;
}
function atualizarTempo(){
  const mm = String(Math.floor(segundos/60)).padStart(2,"0");
  const ss = String(segundos%60).padStart(2,"0");
  elTempo.textContent = `${mm}:${ss}`;
}