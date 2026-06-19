/* Aurora v2 interactions (all fixed in-plugin; data-driven only) */
(function(){
  var root = document.documentElement;

  // loader hide
  window.addEventListener('load', function(){
    var l = document.querySelector('.au-loader');
    if (l) setTimeout(function(){ l.style.opacity = 0; l.style.visibility = 'hidden'; }, 850);
  });

  // section kicker numbering (sequential over sections that actually render)
  document.querySelectorAll('.kick .num').forEach(function(el, i){ el.textContent = String(i + 1).padStart(2, '0'); });

  // typewriter
  var t = document.getElementById('auType');
  if (t) {
    var words = []; try { words = JSON.parse(t.getAttribute('data-words') || '[]'); } catch(e){}
    if (words.length > 1) {
      var wi = 0, ci = 0, del = false;
      (function tick(){
        var w = words[wi];
        if (!del) { ci++; if (ci > w.length) { del = true; return setTimeout(tick, 1500); } }
        else { ci--; if (ci < 0) { del = false; wi = (wi + 1) % words.length; ci = 0; return setTimeout(tick, 240); } }
        t.textContent = w.slice(0, ci); setTimeout(tick, del ? 38 : 80);
      })();
    }
  }

  // count-up
  function countUp(el){
    var raw = el.getAttribute('data-raw') || el.textContent; el.setAttribute('data-raw', raw);
    var m = raw.match(/([^0-9-]*)(-?[0-9]+(?:\.[0-9]+)?)(.*)/); if (!m) return;
    var pre = m[1], num = parseFloat(m[2]), suf = m[3], dur = 1500, start = null, dec = m[2].indexOf('.') >= 0;
    requestAnimationFrame(function step(ts){
      if (!start) start = ts; var p = Math.min((ts - start) / dur, 1), e = 0.5 - Math.cos(p * Math.PI) / 2;
      el.textContent = pre + (dec ? (num * e).toFixed(1) : Math.round(num * e)) + suf;
      if (p < 1) requestAnimationFrame(step);
    });
  }

  // reveal + stagger (delay by index within the same parent)
  var rio = new IntersectionObserver(function(es){
    es.forEach(function(e){
      if (!e.isIntersecting) return;
      var el = e.target, sibs = Array.prototype.slice.call(el.parentNode.children).filter(function(c){return c.classList.contains('reveal');});
      var i = sibs.indexOf(el); el.style.transitionDelay = Math.min(i, 6) * 70 + 'ms';
      el.classList.add('in');
      rio.unobserve(el);
    });
  }, { threshold: .15 });
  document.querySelectorAll('.reveal').forEach(function(el){ rio.observe(el); });

  // count-up: dedicated observer (works for reveal cards AND hero teaser stats)
  var cio = new IntersectionObserver(function(es){
    es.forEach(function(e){ if (e.isIntersecting){ countUp(e.target); cio.unobserve(e.target); } });
  }, { threshold: .4 });
  document.querySelectorAll('.countup').forEach(function(el){ cio.observe(el); });

  // scroll progress + back-to-top + scroll-spy + timeline fill
  var pb = document.getElementById('auProgress');
  var topBtn = document.getElementById('auTop');
  var links = Array.prototype.slice.call(document.querySelectorAll('nav.bar .links a[href^="#"]'));
  var sections = links.map(function(a){ return document.querySelector(a.getAttribute('href')); });
  var tl = document.querySelector('.tl'), tlFill = document.getElementById('tlFill');
  var navBar = document.querySelector('nav.bar');

  function onScroll(){
    var h = root, sc = h.scrollTop, max = (h.scrollHeight - h.clientHeight) || 1;
    if (pb) pb.style.width = (sc / max * 100) + '%';
    if (navBar) navBar.classList.toggle('scrolled', sc > 40);
    if (topBtn) topBtn.classList.toggle('show', sc > 600);
    // scroll-spy
    var mid = sc + h.clientHeight * 0.32, active = -1;
    sections.forEach(function(s, i){ if (s && s.offsetTop <= mid) active = i; });
    links.forEach(function(a, i){ a.classList.toggle('active', i === active); });
    // timeline fill
    if (tl && tlFill) {
      var r = tl.getBoundingClientRect(), vh = h.clientHeight;
      var prog = (vh * 0.5 - r.top) / r.height; prog = Math.max(0, Math.min(1, prog));
      tlFill.style.height = (prog * 100) + '%';
    }
  }
  window.addEventListener('scroll', onScroll, { passive: true }); onScroll();
  if (topBtn) topBtn.addEventListener('click', function(){ window.scrollTo({ top: 0, behavior: 'smooth' }); });

  // theme toggle
  var saved = localStorage.getItem('pp-theme'); if (saved) root.setAttribute('data-theme', saved);
  var tg = document.getElementById('themeToggle');
  if (tg) tg.addEventListener('click', function(){
    var th = root.getAttribute('data-theme') === 'dark' ? 'light' : 'dark';
    root.setAttribute('data-theme', th); localStorage.setItem('pp-theme', th);
  });

  // mobile menu
  var burger = document.getElementById('auBurger'), navlinks = document.getElementById('navlinks');
  if (burger && navlinks) {
    burger.addEventListener('click', function(){ navlinks.classList.toggle('open'); });
    navlinks.querySelectorAll('a').forEach(function(a){ a.addEventListener('click', function(){ navlinks.classList.remove('open'); }); });
  }

  // hero cursor spotlight
  var hero = document.querySelector('.au-hero'), spot = document.getElementById('auSpot');
  if (hero && spot) hero.addEventListener('mousemove', function(e){
    var r = hero.getBoundingClientRect();
    spot.style.setProperty('--hx', (e.clientX - r.left) + 'px');
    spot.style.setProperty('--hy', (e.clientY - r.top) + 'px');
  });

  // glass spotlight + subtle tilt
  document.querySelectorAll('.glass').forEach(function(c){
    c.addEventListener('mousemove', function(e){
      var r = c.getBoundingClientRect(), x = e.clientX - r.left, y = e.clientY - r.top;
      c.style.setProperty('--mx', x + 'px'); c.style.setProperty('--my', y + 'px');
      var rx = ((y - r.height/2)/(r.height/2)) * -2.2, ry = ((x - r.width/2)/(r.width/2)) * 2.2;
      c.style.transform = 'perspective(900px) rotateX(' + rx + 'deg) rotateY(' + ry + 'deg) translateY(-3px)';
    });
    c.addEventListener('mouseleave', function(){ c.style.transform = ''; });
  });

  // chatbot (client-side, canned answers)
  var chatEl = document.getElementById('auChat');
  if (chatEl) {
    var qa = []; try { qa = JSON.parse(chatEl.getAttribute('data-chat') || '[]'); } catch(e){}
    var who = chatEl.getAttribute('data-name') || 'me';
    var btn = document.getElementById('auChatBtn'), body = document.getElementById('auCbody');
    var sugg = document.getElementById('auSugg'), input = document.getElementById('auCinput'), send = document.getElementById('auCsend');
    var STOP = {the:1,a:1,an:1,is:1,are:1,you:1,your:1,what:1,whats:1,tell:1,me:1,about:1,do:1,of:1,to:1,for:1,in:1,on:1,and:1,how:1,can:1,i:1,my:1};
    function add(txt, cls){ var d = document.createElement('div'); d.className = 'au-msg ' + cls; d.textContent = txt; body.appendChild(d); body.scrollTop = body.scrollHeight; }
    function tok(s){ return (s||'').toLowerCase().replace(/[^a-z0-9 ]/g,' ').split(/\s+/).filter(function(w){return w && !STOP[w];}); }
    function ans(q){ var qt = tok(q), best = null, bs = 0;
      qa.forEach(function(p){ var set = tok(p.q + ' ' + p.a), s = 0; qt.forEach(function(w){ if (set.indexOf(w) >= 0) s++; }); if (s > bs){ bs = s; best = p; } });
      return (best && bs > 0) ? best.a : "I can tell you about " + who + "'s experience, skills, impact, education and availability. Try a suggestion above, or use the Contact section."; }
    add("Hi! I'm " + who + "'s assistant. Ask me anything about their background.", 'bot');
    qa.slice(0, 4).forEach(function(p){ var b = document.createElement('button'); b.textContent = p.q;
      b.addEventListener('click', function(){ add(p.q, 'user'); setTimeout(function(){ add(p.a, 'bot'); }, 300); }); sugg.appendChild(b); });
    btn.addEventListener('click', function(){ chatEl.classList.toggle('open'); if (chatEl.classList.contains('open')) input.focus(); });
    function fire(){ var v = input.value.trim(); if (!v) return; input.value = ''; add(v, 'user'); setTimeout(function(){ add(ans(v), 'bot'); }, 350); }
    send.addEventListener('click', fire); input.addEventListener('keydown', function(e){ if (e.key === 'Enter') fire(); });
  }
})();
