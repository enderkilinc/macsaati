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

  // filters (only on pages with controls)
  var q = document.getElementById("q"), comp = document.getElementById("comp"),
      turk = document.getElementById("turkOnly"), fta = document.getElementById("ftaOnly");
  if (!q) return;
  var norm = function(s){ return s.toLowerCase().normalize("NFD").replace(/[̀-ͯ]/g,"").replace(/ı/g,"i"); };
  function apply(){
    var qs = norm(q.value.trim()), c = comp.value, t = turk.checked, f = fta.checked;
    document.querySelectorAll(".day-sec").forEach(function(sec){
      var any = false;
      sec.querySelectorAll(".row").forEach(function(r){
        var ok = (c === "all" || r.dataset.comp === c) && (!t || r.dataset.turk === "1") &&
                 (!f || r.dataset.fta === "1") && (!qs || norm(r.dataset.q).indexOf(qs) > -1);
        r.classList.toggle("hidden", !ok); if (ok) any = true;
      });
      sec.classList.toggle("hidden", !any);
    });
  }
  [q, comp, turk, fta].forEach(function(el){ el.addEventListener(el === q ? "input" : "change", apply); });
})();
