import { useEffect, useState, useRef, useCallback } from "react";
import {
  MapContainer,
  TileLayer,
  Marker,
  Popup,
  useMap,
  useMapEvents,
} from "react-leaflet";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import "leaflet.heat";
import AuthService from "../lib/auth";

// Fix for default markers in react-leaflet
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "/icons/marker-icon-2x.png",
  iconUrl: "/icons/marker-icon.png",
  shadowUrl: "/icons/marker-shadow.png",
});

// Custom marker icons
const crisisIcon = new L.Icon({
  iconUrl: "/icons/crisis-marker.png",
  iconRetinaUrl: "/icons/crisis-marker-2x.png",
  shadowUrl: "/icons/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const ngoIcon = new L.Icon({
  iconUrl: "/icons/ngo-marker.png",
  iconRetinaUrl: "/icons/ngo-marker-2x.png",
  shadowUrl: "/icons/marker-shadow.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

// Map bounds updater component
function BoundsUpdater({ onBoundsChange }) {
  const map = useMapEvents({
    moveend: () => {
      const bounds = map.getBounds();
      onBoundsChange({
        sw: {
          lat: bounds.getSouth(),
          lng: bounds.getWest(),
        },
        ne: {
          lat: bounds.getNorth(),
          lng: bounds.getEast(),
        },
      });
    },
  });
  return null;
}

// Heatmap component
function HeatmapLayer({ points }) {
  const map = useMap();
  const heatLayerRef = useRef(null);

  useEffect(() => {
    if (!map) return;

    // Remove existing heatmap layer if it exists
    if (heatLayerRef.current) {
      map.removeLayer(heatLayerRef.current);
    }

    // Create new heatmap layer if there are points
    if (points && points.length > 0) {
      const heatData = points.map((point) => [
        point.lat,
        point.lng,
        point.intensity,
      ]);

      heatLayerRef.current = L.heatLayer(heatData, {
        radius: 25,
        blur: 15,
        maxZoom: 10,
        max: 1.0,
        minOpacity: 0.3,
      }).addTo(map);
    }

    return () => {
      if (heatLayerRef.current) {
        map.removeLayer(heatLayerRef.current);
      }
    };
  }, [map, points]);

  return null;
}

// Heatmap data fetcher component
function HeatmapUpdater({ bounds, selectedCategory, onDataUpdate }) {
  const [error, setError] = useState(null);
  const abortControllerRef = useRef(null);

  useEffect(() => {
    // Cancel any previous request
    if (abortControllerRef.current) {
      abortControllerRef.current.abort();
    }

    // Create new controller for this request
    abortControllerRef.current = new AbortController();
    let isMounted = true;

    const fetchHeatmapData = async () => {
      try {
        if (!bounds || !bounds.sw || !bounds.ne) return;

        const params = new URLSearchParams({
          sw_lat: bounds.sw.lat.toFixed(6),
          sw_lng: bounds.sw.lng.toFixed(6),
          ne_lat: bounds.ne.lat.toFixed(6),
          ne_lng: bounds.ne.lng.toFixed(6),
        });

        // Only add category if it's not null
        if (selectedCategory) {
          params.append("category", selectedCategory);
        }

        const response = await AuthService.fetchWithAuth(
          `/api/heatmap?${params}`,
          {
            signal: abortControllerRef.current.signal,
          }
        );

        if (!response.ok) {
          const errorText = await response.text();
          throw new Error(
            errorText || `HTTP error! status: ${response.status}`
          );
        }

        const data = await response.json();
        if (isMounted) {
          onDataUpdate(data);
          setError(null);
        }
      } catch (error) {
        // Only log and set errors that aren't from aborting
        if (error.name !== "AbortError" && isMounted) {
          console.error("Error fetching heatmap data:", error);
          setError(error.message);
          // Clear heatmap data on error
          onDataUpdate({ points: [] });
        }
      }
    };

    fetchHeatmapData();

    return () => {
      isMounted = false;
      if (abortControllerRef.current) {
        abortControllerRef.current.abort();
      }
    };
  }, [bounds, selectedCategory, onDataUpdate]);

  return error ? (
    <div
      style={{
        position: "absolute",
        bottom: "20px",
        left: "20px",
        zIndex: 1000,
        backgroundColor: "#f44336",
        color: "white",
        padding: "10px",
        borderRadius: "4px",
        boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
      }}
    >
      Error: {error}
    </div>
  ) : null;
}

export default function CrisisMap({
  crisisAreas = [],
  ngos = [],
  selectedCategory,
  onBoundsChange,
}) {
  const [heatmapData, setHeatmapData] = useState({ points: [] });
  const [mapBounds, setMapBounds] = useState(null);
  const [center, setCenter] = useState([0, 0]);

  // Update center based on first crisis area or default to [0, 0]
  useEffect(() => {
    if (crisisAreas.length > 0 && crisisAreas[0].position) {
      setCenter([crisisAreas[0].position.lat, crisisAreas[0].position.lng]);
    }
  }, [crisisAreas]);

  const handleBoundsChange = useCallback(
    (bounds) => {
      setMapBounds(bounds);
      onBoundsChange?.(bounds);
    },
    [onBoundsChange]
  );

  const handleHeatmapData = useCallback((data) => {
    setHeatmapData(data);
  }, []);

  return (
    <MapContainer
      center={center}
      zoom={3}
      style={{ height: "100%", width: "100%" }}
      whenReady={(mapInstance) => {
        const bounds = mapInstance.target.getBounds();
        handleBoundsChange({
          sw: {
            lat: bounds.getSouth(),
            lng: bounds.getWest(),
          },
          ne: {
            lat: bounds.getNorth(),
            lng: bounds.getEast(),
          },
        });
      }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />

      <HeatmapLayer points={heatmapData.points} />

      {crisisAreas.map((area) => (
        <Marker
          key={area.id}
          position={[area.position.lat, area.position.lng]}
          icon={crisisIcon}
        >
          <Popup>
            <div className="crisis-popup">
              <h3>{area.name}</h3>
              <p>Urgency: {area.urgency?.toFixed(1) || 0}/5</p>
              <p>Population: {area.population?.toLocaleString() || 0}</p>
              <p>Security: {area.security || "Unknown"}</p>
              <div className="needs">
                <h4>Needs:</h4>
                <ul>
                  {Object.entries(area.needs || {}).map(
                    ([category, amount]) => (
                      <li key={category}>
                        {category}: {amount}
                      </li>
                    )
                  )}
                </ul>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}

      {ngos.map((ngo) => (
        <Marker
          key={ngo.id}
          position={[ngo.location.latitude, ngo.location.longitude]}
          icon={ngoIcon}
        >
          <Popup>
            <div className="ngo-popup">
              <h3>{ngo.name}</h3>
              <p>Status: {ngo.is_busy ? "Busy" : "Available"}</p>
              <p>Rating: {ngo.rating?.toFixed(1) || 0}/5</p>
              <div className="inventory">
                <h4>Inventory:</h4>
                <ul>
                  {Object.entries(ngo.inventory || {}).map(
                    ([category, supplies]) => (
                      <li key={category}>
                        {category}:{" "}
                        {Array.isArray(supplies)
                          ? supplies.reduce(
                              (sum, s) => sum + (s.quantity || 0),
                              0
                            )
                          : 0}
                      </li>
                    )
                  )}
                </ul>
              </div>
            </div>
          </Popup>
        </Marker>
      ))}

      <BoundsUpdater onBoundsChange={handleBoundsChange} />
      {mapBounds && (
        <HeatmapUpdater
          bounds={mapBounds}
          selectedCategory={selectedCategory}
          onDataUpdate={handleHeatmapData}
        />
      )}
    </MapContainer>
  );
}
