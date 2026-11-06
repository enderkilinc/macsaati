(function(){
  var lang = document.body.dataset.lang || "en";
  var store = {
    get: function(k, d){ try{ var v = localStorage.getItem("macsaati:"+k); return v===null ? d : JSON.parse(v); }catch(e){ return d; } },
    set: function(k, v){ try{ localStorage.setItem("macsaati:"+k, JSON.stringify(v)); }catch(e){} }
  };
  // time zone toggle
  var tz = store.get("tz", lang === "tr" ? "tr" : "uk");
  function applyTz(){
    document.body.classList.toggle("tz-tr", tz === "tr");
    document.querySelectorAll(".tz button").forEach(function(b){ b.classList.toggle("on", b.dataset.tz === tz); });
  }
  document.querySelectorAll(".tz button").forEach(function(b){
    b.addEventListener("click", function(){ tz = b.dataset.tz; store.set("tz", tz); applyTz(); });
  });
  applyTz();

  // live / played status
  var now = Date.now();
  document.querySelectorAll(".row[data-iso]").forEach(function(r){
    var k = Date.parse(r.dataset.iso), st = r.querySelector(".st");
    if (!st) return;
    if (now >= k && now < k + 115*60000){ st.className = "tag live"; st.textContent = lang==="tr" ? "Canlı" : "Live"; }
    else if (now >= k + 115*60000){ st.className = "tag ft"; st.textContent = lang==="tr" ? "Oynandı" : "Played"; r.classList.add("past"); }
  });

  // collapsible competition groups (remembered per viewer)
  var collapsed = store.get("collapsed", {});
  var groups = document.querySelectorAll("details.grp");
  groups.forEach(function(g){
    if (collapsed[g.dataset.comp]) g.removeAttribute("open");
    g.addEventListener("toggle", function(){
      if (g._sync) return;
      collapsed[g.dataset.comp] = !g.open;
      if (!collapsed[g.dataset.comp]) delete collapsed[g.dataset.comp];
      store.set("collapsed", collapsed);
      // keep every group of the same competition in step
      groups.forEach(function(o){ if (o !== g && o.dataset.comp === g.dataset.comp && o.open !== g.open){ o._sync = true; o.open = g.open; setTimeout(function(){ o._sync = false; }, 0); } });
    });
  });
  function setAll(open){
    groups.forEach(function(g){ g._sync = true; g.open = open; setTimeout(function(){ g._sync = false; }, 0); });
    collapsed = {};
    if (!open) groups.forEach(function(g){ collapsed[g.dataset.comp] = true; });
    store.set("collapsed", collapsed);
  }
  var ca = document.getElementById("collapseAll"), ea = document.getElementById("expandAll");
  if (ca) ca.addEventListener("click", function(){ setAll(false); });
  if (ea) ea.addEventListener("click", function(){ setAll(true); });

  // filters (only on pages with controls)
  var q = document.getElementById("q"), comp = document.getElementById("comp"),
      turk = document.getElementById("turkOnly"), fta = document.getElementById("ftaOnly");
  if (!q) return;
  var norm = function(s){ return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/ı/g,"i"); };
  function apply(){
    var qs = norm(q.value.trim()), c = comp.value, t = turk.checked, f = fta.checked;
    document.querySelectorAll(".day-sec").forEach(function(sec){
      var anyDay = false;
      sec.querySelectorAll(".grp").forEach(function(g){
        var anyGrp = false;
        g.querySelectorAll(".row").forEach(function(r){
          var ok = (c === "all" || r.dataset.comp === c) && (!t || r.dataset.turk === "1") &&
                   (!f || r.dataset.fta === "1") && (!qs || norm(r.dataset.q).indexOf(qs) > -1);
          r.classList.toggle("hidden", !ok); if (ok) anyGrp = true;
        });
        g.classList.toggle("hidden", !anyGrp); if (anyGrp) anyDay = true;
        if (anyGrp && (qs || c !== "all" || t || f)) { g._sync = true; g.open = true; setTimeout(function(){ g._sync = false; }, 0); }
      });
      sec.classList.toggle("hidden", !anyDay);
    });
    document.querySelectorAll("h2.month").forEach(function(m){
      var el = m.nextElementSibling, any = false;
      while (el && !el.matches("h2.month")) { if (el.matches(".day-sec:not(.hidden)")) any = true; el = el.nextElementSibling; }
      m.classList.toggle("hidden", !any);
    });
  }
  [q, comp, turk, fta].forEach(function(el){ el.addEventListener(el === q ? "input" : "change", apply); });
})();
