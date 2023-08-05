var DateTime = luxon.DateTime;

function on_image_click(el) {
  var id = parseInt(el.getAttribute('data-id'));
  console.log(`on_image_click id=${id}`);
  const zoom = 17; // MAP.getZoom()
  MAP.setView([XS[id].lat, XS[id].lng], zoom);
}

Promise.all([
	fetch('http://127.0.0.1:5000/space'),
	fetch('http://127.0.0.1:5000/time')
]).then(function (responses) {
	return Promise.all(responses.map(function (response) {
		return response.json();
	}));
}).then(function (data) {
  [space, time] = data
  main(space.rows, time.tmin, time.tmax)
});

function main(images, TMIN, TMAX) {
  window.IDS = [];
  window.XS = {};
  window.exif_data = images;
  function reset() {
    for (const x of window.exif_data) {
      let id = x['id'];
      IDS.push(id);
      XS[id] = x;
    }
  }
  reset()

  var TILES = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 18,
      attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors, Points &copy 2012 LINZ'
    });
  var CENTER = L.latLng(47.67762580548492, 12.139356136322021);
  window.MAP = L.map('mapid', {center: CENTER, zoom: 13, layers: [TILES]});

  // https://github.com/Leaflet/Leaflet.markercluster#all-options
  var MARKERS = L.markerClusterGroup({
    disableClusteringAtZoom: 17,
    maxClusterRadius: 120,
  });

  function update_map(xs) {
    console.log(`update_map/${xs.length}`);
    var bounds = MAP.getBounds()
    var got_visible_markers = false;
    if (MARKERS) {
      MAP.removeLayer(MARKERS)
    }
    for (var x of xs) {
      var icon = L.icon({
        iconUrl: x.thumb,
        iconSize: [40, 40],
      });
      var marker = L.marker([x.lat, x.lng], {icon: icon, image_id: x.id});
      if (bounds.contains(marker.getLatLng())) {
        got_visible_markers = true;
      }
      var local_dt = DateTime.fromISO(x.dt).toFormat('yyyy-LL-dd HH:mm:ss');
      var popup_content = `<img src=${x.thumb} /><br/>${local_dt}`
      marker.bindPopup(popup_content, {
        maxWidth: "auto",
        autoPan: false,  // popup should not move the map. That's annoying.
        closeButton: false, // don't need it, because autoClose is true by default
        /* When you hover the marker at the top-most edge, then the popup opens and closes all the time.
        Put it a little bit higher, so it does not overlap with the marker. */
        offset: [0, -10],
      });
      // tooltip on hover
      marker.on('mouseover', function (e) {
        this.openPopup();
      });
      marker.on('mouseout', function (e) {
        this.closePopup();
      });
      MARKERS.addLayer(marker);
    }
    MAP.addLayer(MARKERS);
    // only change view if there would be nothing left
    if (got_visible_markers === false) {
      MAP.fitBounds(MARKERS.getBounds(), {animate: true});
    }
  }
  update_map(Object.values(XS))


  function get_visible_markers() {
    var bounds = MAP.getBounds()
    var result = [];
    MAP.eachLayer(function(layer) {
      // clusters
      if (layer instanceof L.MarkerCluster) {
        if(bounds.contains(layer.getLatLng())) {
          for (var m of layer.getAllChildMarkers()) {
            result.push(m);
          }
        }
      }
      // single layers
      else if(layer instanceof L.Marker) {
        var m = layer;
        if(bounds.contains(layer.getLatLng())) {
          result.push(m);
        }
      }
    });
    return result;
  }

  function get_map_xs() {
    var result = [];

    var ms = get_visible_markers();
    for (const m of ms) {
      if (m===undefined) {
        continue;
      } 
      var id = m.options.image_id;
      var x = XS[id];
      if (x===undefined) {
        continue;
      }
      result.push(x)
    };
    return result;
  }

  const MAX_IMAGES_SHOWN = 50;
  function update_images(xs) {
    console.log(`update_images/${xs.length}`);
    var body_of_images=``
    for (const a of xs) {
      // the hacks are real :>
      let d = a.dt.replace('T', ' ').slice(0,-6)
      body_of_images += `<div class="imwrap">
        <p>${d}</p>
        <img onclick="on_image_click(this)" data-id="${a.id}"src="${a.thumb}" />
      </div>`;
    }
    document.getElementById('images').innerHTML = body_of_images;
  }
  update_images(Object.values(XS).slice(0, MAX_IMAGES_SHOWN));

  function on_map_change(e) {
    console.log('on_map_change', e.type);
    var xs = get_map_xs().slice(0, MAX_IMAGES_SHOWN);
    update_images(xs);
    // endless event loop (plt redraw --> map zoom --> plt redraw) and vice versa :(
    // update_plt(xs);
    return false;
  }
  MAP.on('zoomend', on_map_change)
  MAP.on('moveend', on_map_change)


  function unpack(rows, key) {
    return rows.map(function(row) { return row[key]; });
  }

  function get_y(rows) {
    return new Array(rows.length).fill(1);
  }

  var trace1 = {
    type: 'scatter',
    mode: 'markers',
    x: exif_data.map(x => x['dt']),
    y: exif_data.map(x => x['alt'] || 400),
    text: exif_data.map(x => x['since_start']),
  }

  var data = [trace1];

  var layout = {
    xaxis: {
      autorange: true,
      type: 'date'
    },
    yaxis: {
      autorange: true,
      fixedrange: true,
      type: 'linear'
    },
      margin: {
      l: 5,
      r: 5,
      b: 20,
      t: 20,
      pad: 4
    },
  };

  function get_xs_by_date_range(t0, t1) {
    var t0 = new Date(t0);
    var t1 = new Date(t1);
    return Object.values(XS).filter(function(x) {
      var dt = new Date(x['dt']);
      return dt >= t0 && dt <= t1;
    })
  }

  var plt;
  function update_plt(xs) {
    console.log(`update_plt/${xs.length}`);
    var t0 = xs[0]['dt'];
    var t1 = xs[xs.length -1]['dt'];
    var update = {
      'xaxis.range[0]': t0,
      'xaxis.range[1]': t1,
      'xaxis.autorange': false,
    };
    Plotly.relayout(plt, update);
  }
  async function init_plt() {
    plt = await Plotly.newPlot('plotly', data, layout, {scrollZoom: true});
    plt.on('plotly_relayout', function(eventdata){
      console.log('plotly_relayout');
      // x-axis and y-axis ranges are attrs of the eventdata
      var x0 = eventdata['xaxis.range[0]'];
      var x1 = eventdata['xaxis.range[1]'];
      var tmin = x0 !== undefined ? x0 : TMIN;
      var tmax = x1 !== undefined ? x1 : TMAX;
      xs_by_date_range = get_xs_by_date_range(tmin, tmax).slice(0, MAX_IMAGES_SHOWN);
      console.debug('tdelta', tmin, tmin, `got ${xs_by_date_range.length} images to show`);
      update_map(xs_by_date_range);
      return false;
    })
  }
  init_plt()

  function update_footer(xs) {
    console.log(`update_footer/${xs.length}`);
    var kvs = [
      `count=${xs.length}`,
      `total=${XS.length}`,
    ].join(',')
    document.getElementById('footer').innerHTML = `<pre>${kvs}</pre>`
  }
  update_footer(Object.values(XS).slice(0, MAX_IMAGES_SHOWN));
}
