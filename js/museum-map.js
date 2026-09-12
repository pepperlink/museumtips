(function () {
  "use strict";

  var TILE_URL = "https://tile.openstreetmap.org/{z}/{x}/{y}.png";
  var TILE_ATTRIBUTION =
    '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors';

  var mapEl = document.getElementById("map");
  var fallbackEl = document.getElementById("map-unavailable");
  if (!mapEl || typeof L === "undefined") {
    return;
  }

  function showFallback() {
    mapEl.hidden = true;
    if (fallbackEl) {
      fallbackEl.hidden = false;
    }
  }

  function popupFromText(lines) {
    var root = document.createElement("div");
    var i;
    for (i = 0; i < lines.length; i += 1) {
      var line = lines[i];
      if (!line) {
        continue;
      }
      var p = document.createElement("div");
      p.textContent = line;
      root.appendChild(p);
    }
    return root;
  }

  function popupWithLink(name, href) {
    var root = document.createElement("div");
    var nameEl = document.createElement("div");
    nameEl.textContent = name;
    root.appendChild(nameEl);
    if (href) {
      var link = document.createElement("a");
      link.setAttribute("href", href);
      link.textContent = name;
      root.appendChild(link);
    }
    return root;
  }

  try {
    mapEl.hidden = false;

    var map = L.map(mapEl, {
      scrollWheelZoom: true,
      minZoom: 5,
      maxZoom: 19,
      zoomControl: true,
      dragging: true,
      keyboard: true,
    });

    L.tileLayer(TILE_URL, {
      maxZoom: 19,
      attribution: TILE_ATTRIBUTION,
      referrerPolicy: "strict-origin-when-cross-origin",
    }).addTo(map);

    if (mapEl.getAttribute("data-mode") === "overview") {
      var markerNodes = document.querySelectorAll("#map-markers [data-lat]");
      var bounds = [];
      var n;
      for (n = 0; n < markerNodes.length; n += 1) {
        var node = markerNodes[n];
        var oLat = parseFloat(node.getAttribute("data-lat"));
        var oLon = parseFloat(node.getAttribute("data-lon"));
        if (!isFinite(oLat) || !isFinite(oLon)) {
          continue;
        }
        var oName = node.getAttribute("data-name") || "";
        var href = node.getAttribute("data-href") || "";
        var oMarker = L.marker([oLat, oLon]).addTo(map);
        oMarker.bindPopup(popupWithLink(oName, href));
        bounds.push([oLat, oLon]);
      }
      if (bounds.length === 0) {
        throw new Error("no overview markers");
      }
      map.fitBounds(bounds);
    } else {
      var lat = parseFloat(mapEl.getAttribute("data-lat"));
      var lon = parseFloat(mapEl.getAttribute("data-lon"));
      if (!isFinite(lat) || !isFinite(lon)) {
        throw new Error("invalid coordinates");
      }
      map.setView([lat, lon], 16);
      var marker = L.marker([lat, lon]).addTo(map);
      marker.bindPopup(
        popupFromText([
          mapEl.getAttribute("data-name") || "",
          mapEl.getAttribute("data-address") || "",
        ])
      );
    }
  } catch (err) {
    showFallback();
  }
})();
