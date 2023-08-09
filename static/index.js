
const ROUTE_TYPE = getRouteType();
document.title = "MBTA " + titleCase(ROUTE_TYPE) + " Realtime Map";

var map = L.map('map', {
    minZoom: 9,
    maxZoom: 20,
    maxBounds: L.latLngBounds(L.latLng(40, -74), L.latLng(44, -69)),
    fullscreenControl: true,
    fullscreenControlOptions: {
        position: 'topleft'
    }
}).setView([42.3519, -71.0552], ROUTE_TYPE == "COMMUTER_RAIL" ? 9 : 13);

var CartoDB_Positron = L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20,
}).addTo(map);
var CartoDB_DarkMatter = L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
    subdomains: 'abcd',
    maxZoom: 20,
});

var stop_layer = L.layerGroup().addTo(map);
var shape_layer = L.layerGroup().addTo(map);
var vehicle_layer = L.markerClusterGroup({ disableClusteringAtZoom: ROUTE_TYPE == "COMMUTER_RAIL" ? 10 : 12 }).addTo(map);
var parking_lots = L.layerGroup();

var stopsRealtime = plotStops(`/static/geojsons/${ROUTE_TYPE}/stops.json`, stop_layer).addTo(map);
var shapesRealtime = plotShapes(`/static/geojsons/${ROUTE_TYPE}/shapes.json`, shape_layer).addTo(map);
var vehiclesRealtime = plotVehicles("/vehicles", vehicle_layer).addTo(map);
var facilitiesRealtime = plotFacilities(`/static/geojsons/${ROUTE_TYPE}/park.json`, parking_lots);




controlSearch = L.control.search({
    layer: L.layerGroup([stop_layer, shape_layer, vehicle_layer, parking_lots]),
    initial: false,
    propertyName: 'name',
    zoom: 16,
    marker: false,
    textPlaceholder: "",
}).addTo(map);


var overlays = {
    "Vehicles": vehicle_layer,
    "Stops": stop_layer,
    "Shapes": shape_layer,
    "Parking Lots": parking_lots,
};

var baseMaps = {
    "Dark": CartoDB_DarkMatter,
    "Light": CartoDB_Positron
};

var layerControl = L.control.layers(baseMaps, overlays).addTo(map);

if (map.hasLayer(parking_lots) == true) {
    map.removeLayer(parking_lots);
}


controlSearch.on('search:locationfound', function(event) {
    event.layer.openPopup();
});


for (realtime of [stopsRealtime, shapesRealtime, facilitiesRealtime]) {

    realtime.on('update', function (e) {
        Object.keys(e.update,).forEach(function (id) {
            var feature = e.update[id];
            var wasOpen = this.getLayer(id).getPopup().isOpen();
            if (wasOpen === true) {
                this.getLayer(id).closePopup();
            }

            this.getLayer(id).bindPopup(feature.properties.popupContent, { maxWidth: "auto" });

            if (wasOpen === true) {
                this.getLayer(id).openPopup();
            }


        }.bind(this));
    });
}

vehiclesRealtime.on('update', function (e) {
    Object.keys(e.update,).forEach(function (id) {
        var feature = e.update[id];
        var wasOpen = this.getLayer(id).getPopup().isOpen();
        if (wasOpen === true) {
            this.getLayer(id).closePopup();
        }
        this.getLayer(id).bindPopup(feature.properties.popupContent, { maxWidth: "auto" });
        this.getLayer(id).setIcon(L.divIcon({
            html: feature.properties.icon,
            iconSize: [15, 15],
        }));
        if (wasOpen === true) {
            this.getLayer(id).openPopup();
        }


    }.bind(this));
});

map.on('zoomend', function () {
    if (map.getZoom() < 16) {
        map.removeLayer(parking_lots);
    }
    if (map.getZoom() >= 16){
        map.addLayer(parking_lots);
    }   
    console.log(map.getZoom());
});



function plotVehicles(url, layer) {

    return L.realtime(
        url,
        {
            interval: 15000,
            type: 'FeatureCollection',
            container: layer,
            cache: false,
            removeMissing: true,
            getFeatureId(f) {
                return f.id;
            },
            onEachFeature(f, l) {
                var icon = L.divIcon({
                    html: f.properties.icon,
                    iconSize: [15, 15],
                });
                l.bindPopup(f.properties.popupContent, { maxWidth: "auto" });
                l.bindTooltip(f.properties.name);
                l.setIcon(icon);
                l.setZIndexOffset(100);
            },
        }
    )
}

function plotStops(url, layer) {

    const stopIcon = L.icon({
        iconUrl: "/static/mbta.png",
        iconSize: [15, 15],
    });

    return L.realtime(
        url,
        {
            interval: 3600000,
            type: 'FeatureCollection',
            container: layer,   
            cache: false,
            removeMissing: true,
            getFeatureId(f) {
                return f.id;
            },
            onEachFeature(f, l) {
                // l.setStyle({ renderer: L.canvas({ padding: 0.5, tolerance: 10 }) });
                l.bindPopup(f.properties.popupContent, { maxWidth: "auto" });
                l.bindTooltip(f.properties.name);
                l.setIcon(stopIcon);
                l.setZIndexOffset(-100);
            },
        }
    )
}

function plotShapes(url, layer) {

    let polyLineRender = L.canvas({ padding: 0.5, tolerance: 10 });

    return L.realtime(
        url,
        {
            interval: 3600000,
            type: 'FeatureCollection',
            container: layer,
            cache: false,
            removeMissing: true,
            getFeatureId(f) {
                return f.id;
            },
            onEachFeature(f, l) {
                l.setStyle({
                    color: f.properties.color,
                    opacity: f.properties.opacity,
                    weight: 1.3,
                    renderer: polyLineRender
                });

                l.bindPopup(f.properties.popupContent, { maxWidth: "auto" });
                l.bindTooltip(f.properties.name);
            },
        }
    )
}


function plotFacilities(url, layer) {

    const facilityIcon = L.icon({
        iconUrl: "/static/parking.png",
        iconSize: [15, 15],
    });
    
    return L.realtime(
        url,
        {
            interval: 3600000,
            type: 'FeatureCollection',
            container: layer,
            cache: false,
            removeMissing: true,
            getFeatureId(f) {
                return f.id;
            },
            onEachFeature(f, l) {
                l.bindPopup(f.properties.popupContent, { maxWidth: "auto" });
                l.bindTooltip(f.properties.name);
                l.setIcon(facilityIcon);
                l.setZIndexOffset(-150);
            },
        }
    )
}


function showPredictionPopup() {
    var predictionPopup = document.getElementById("predictionPopup");
    predictionPopup.classList.toggle("show");
}
function showAlertPopup() {
    var alertPopup = document.getElementById("alertPopup");
    alertPopup.classList.toggle("show");
}
function showParkingPopup() {
    var parkingPopup = document.getElementById("parkingPopup");
    parkingPopup.classList.toggle("show");
}

function showBikePopup() {
    var bikePopup = document.getElementById("bikePopup");
    bikePopup.classList.toggle("show");
}


function getRouteType() {
    var tmp = null;
    $.ajax({
        'async': false,
        'type': "GET",
        'global': false,
        'dataType': 'html',
        'url': "/value",
        'data': { 'request': "", 'target': 'arrange_url', 'method': 'method_target' },
        'success': function (data) {
            tmp = data;
        }
    }
    );
    console.log(tmp)
    return tmp;
};

function titleCase(str, split = "_") {
    return str.toLowerCase().split(split).map(function (word) {
        return (word.charAt(0).toUpperCase() + word.slice(1));
    }).join(' ');
}