#!/bin/bash
set -euo pipefail

cd "$(dirname "$0")"
wget -c https://moment.github.io/luxon/global/luxon.min.js
wget -c https://unpkg.com/leaflet@1.7.1/dist/leaflet.js
wget -c https://unpkg.com/leaflet@1.7.1/dist/leaflet.js.map
wget -c https://unpkg.com/leaflet@1.7.1/dist/leaflet.css
wget -c https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js
wget -c https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/leaflet.markercluster.js.map
wget -c https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.min.css
wget -c https://cdnjs.cloudflare.com/ajax/libs/leaflet.markercluster/1.5.3/MarkerCluster.Default.min.css
