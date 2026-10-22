const EL = {
  btnIniciar: document.getElementById('btnIniciar'),
  btnReiniciar: document.getElementById('btnReiniciar'),
  tabuleiro: document.getElementById('tabuleiro'),
  tempo: document.getElementById('tempo'),
  jogadas: document.getElementById('jogadas'),
  pares: document.getElementById('pares'),
  totalPares: document.getElementById('totalPares'),
  nivelLabel: document.getElementById('nivelLabel'),
  tplCarta: document.getElementById('tplCarta'),

  modal: document.getElementById('modalFim'),
  tituloModal: document.getElementById('tituloModal'),
  resNivel: document.getElementById('resNivel'),
  resTempo: document.getElementById('resTempo'),
  resJogadas: document.getElementById('resJogadas'),
  btnProximo: document.getElementById('btnProximo'),
  btnFechar: document.getElementById('btnFechar'),
};

// agora temos 6 níveis, cada um com range e tamanho de carta
const LEVELS = [
  { nome:"Nível 1", range:[1,4], cardMin:320 },
  { nome:"Nível 2", range:[5,8], cardMin:320 },
  { nome:"Nível 3", range:[9,12], cardMin:320 },
  { nome:"Nível 4", range:[13,15], cardMin:380 },
  { nome:"Nível 5", range:[16,18], cardMin:420 },
  { nome:"Nível 6", range:[19,20], cardMin:480 }
];

let state = {
  levelIndex:0, deck:[], abertas:[], achados:0,
  jogadas:0, cronometro:null, segundos:0, lock:false, memorizando:false
};

function formatTime(t){const m=Math.floor(t/60).toString().padStart(2,"0");const s=(t%60).toString().padStart(2,"0");return `${m}:${s}`;}
function startTimer(){stopTimer();state.segundos=0;EL.tempo.textContent="00:00";state.cronometro=setInterval(()=>{state.segundos++;EL.tempo.textContent=formatTime(state.segundos)},1000);}
function stopTimer(){if(state.cronometro){clearInterval(state.cronometro);state.cronometro=null;}}

function shuffle(a){for(let i=a.length-1;i>0;i--){const j=Math.floor(Math.random()*(i+1));[a[i],a[j]]=[a[j],a[i]];}return a;}
function getImagePath(tipo,n){return tipo==="numero"?`numeros/Slide${n}.png`:`quantidade/${n}.jpg`;}

function criarDeck(range){const [ini,fim]=range;const d=[];for(let v=ini;v<=fim;v++){d.push({valor:v,tipo:"numero",img:getImagePath("numero",v)});d.push({valor:v,tipo:"quantidade",img:getImagePath("quantidade",v)});}return shuffle(d);}
function criarCarta(item){const frag=EL.tplCarta.content.cloneNode(true);const btn=frag.querySelector(".carta");const verso=frag.querySelector(".carta__face--verso");const img=document.createElement("img");img.src=item.img;img.alt=item.tipo+" "+item.valor;verso.appendChild(img);btn.dataset.valor=item.valor;btn.dataset.tipo=item.tipo;btn.addEventListener("click",()=>handleCliqueCarta(btn));return btn;}
function renderTabuleiro(deck){EL.tabuleiro.innerHTML="";const frag=document.createDocumentFragment();deck.forEach(it=>frag.appendChild(criarCarta(it)));EL.tabuleiro.appendChild(frag);}

function iniciarNivel(){
  const lvl=LEVELS[state.levelIndex];
  // aumenta o tamanho das cartas conforme nível
  document.documentElement.style.setProperty('--card-min', `${lvl.cardMin}px`);

  state.deck=criarDeck(lvl.range);
  state.abertas=[]; state.achados=0; state.jogadas=0; state.lock=false;
  stopTimer(); 
  EL.jogadas.textContent="0"; EL.pares.textContent="0";
  EL.totalPares.textContent=String(state.deck.length/2);
  EL.nivelLabel.textContent=lvl.nome;
  renderTabuleiro(state.deck);

  // memorização: vira todas por 5 segundos
  const cartas=[...EL.tabuleiro.querySelectorAll(".carta")];
  cartas.forEach(c=>c.classList.add("is-flipada"));
  state.lock=true; state.memorizando=true;
  setTimeout(()=>{
    cartas.forEach(c=>c.classList.remove("is-flipada"));
    state.lock=false; state.memorizando=false;
    startTimer();
  },5000);
}

function handleCliqueCarta(btn){
  if(state.lock||btn.classList.contains("is-flipada"))return;
  btn.classList.add("is-flipada");
  state.abertas.push({el:btn,valor:+btn.dataset.valor,tipo:btn.dataset.tipo});
  if(state.abertas.length===2){
    state.lock=true; state.jogadas++; EL.jogadas.textContent=state.jogadas;
    const[a,b]=state.abertas;const ok=(a.valor===b.valor&&a.tipo!==b.tipo);
    if(ok){
      a.el.disabled=b.el.disabled=true;
      state.achados++; EL.pares.textContent=state.achados;
      state.abertas=[]; state.lock=false;
      if(state.achados===state.deck.length/2){stopTimer();abrirModalFim();}
    }else{
      setTimeout(()=>{a.el.classList.remove("is-flipada");b.el.classList.remove("is-flipada");state.abertas=[];state.lock=false;},800);
    }
  }
}

function abrirModalFim(){
  const ultimo=state.levelIndex===LEVELS.length-1;
  EL.tituloModal.textContent=ultimo?"Parabéns! Concluiu todos os níveis 🎉":"Nível concluído 🎉";
  EL.resNivel.textContent=LEVELS[state.levelIndex].nome;
  EL.resTempo.textContent=formatTime(state.segundos);
  EL.resJogadas.textContent=state.jogadas;
  EL.btnProximo.textContent=ultimo?"Recomeçar":"Próximo nível";
  EL.modal.setAttribute("aria-hidden","false");
}
function fecharModal(){EL.modal.setAttribute("aria-hidden","true");}
function proximoNivel(){const ultimo=state.levelIndex===LEVELS.length-1;if(ultimo){state.levelIndex=0;}else{state.levelIndex++;}fecharModal();iniciarNivel();}

EL.btnIniciar.addEventListener("click",()=>{state.levelIndex=0;iniciarNivel();});
EL.btnReiniciar.addEventListener("click",()=>{state.levelIndex=0;iniciarNivel();});
EL.btnProximo.addEventListener("click",proximoNivel);
EL.btnFechar.addEventListener("click",fecharModal);

EL.nivelLabel.textContent="—";
