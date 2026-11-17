(function(){
  var KEY = "yado-kuchikomi:saved";
  var saved = {};
  try { saved = JSON.parse(localStorage.getItem(KEY) || "{}") || {}; } catch (e) { saved = {}; }
  function store(){ try { localStorage.setItem(KEY, JSON.stringify(saved)); } catch (e) {} }
  var cards = Array.prototype.slice.call(document.querySelectorAll(".yado"));
  var today = new Date(Date.now() + 9 * 3600 * 1000).toISOString().slice(0, 10);
  cards.forEach(function(c){
    var added = c.getAttribute("data-added");
    var days = (Date.parse(today) - Date.parse(added)) / 86400000;
    if (days >= 0 && days < 7) {
      var s = document.createElement("span");
      s.className = "new"; s.textContent = "新着";
      c.querySelector(".marks").insertBefore(s, c.querySelector(".marks").firstChild);
    }
    var b = c.querySelector(".save");
    var id = c.getAttribute("data-id");
    b.setAttribute("aria-pressed", saved[id] ? "true" : "false");
    b.addEventListener("click", function(){
      if (saved[id]) { delete saved[id]; } else { saved[id] = 1; }
      b.setAttribute("aria-pressed", saved[id] ? "true" : "false");
      store();
      if (current === "saved") apply();
    });
  });
  var current = "all";
  if (!document.getElementById("count")) return;
  var buttons = Array.prototype.slice.call(document.querySelectorAll("nav.filters button"));
  function apply(){
    var n = 0;
    cards.forEach(function(c){
      var marks = (c.getAttribute("data-marks") || "").split(" ");
      var show = current === "all" || (current === "saved" ? !!saved[c.getAttribute("data-id")] : marks.indexOf(current) >= 0);
      c.hidden = !show;
      if (show) n++;
    });
    var label = {all: "紹介した宿", solo: "一人旅の宿", henro: "遍路宿", saved: "行ってみたい宿"}[current];
    document.getElementById("count").textContent = label + " " + n + "軒（追加した順）";
    document.getElementById("empty").hidden = !(current === "saved" && n === 0);
  }
  buttons.forEach(function(b){
    b.addEventListener("click", function(){
      current = b.getAttribute("data-filter");
      buttons.forEach(function(x){ x.setAttribute("aria-pressed", x === b ? "true" : "false"); });
      apply();
    });
  });
})();
