import { useEffect, useRef, useState } from "react";
import { MapContainer, TileLayer, useMap, Marker, Popup } from "react-leaflet";
import L from "leaflet";
import "leaflet.heat";
import AuthService from "../lib/auth";

// Update marker icons
L.Icon.Default.mergeOptions({
  iconRetinaUrl: "/icons/marker-icon-2x.png",
  iconUrl: "/icons/marker-icon.png",
  shadowUrl: "/icons/marker-shadow.png",
});

const crisisIcon = new L.Icon({
  iconUrl: "/icons/crisis-marker.png",
  iconRetinaUrl: "/icons/crisis-marker-2x.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

const ngoIcon = new L.Icon({
  iconUrl: "/icons/ngo-marker.png",
  iconRetinaUrl: "/icons/ngo-marker-2x.png",
  iconSize: [25, 41],
  iconAnchor: [12, 41],
  popupAnchor: [1, -34],
  shadowSize: [41, 41],
});

function BoundsUpdater({ onBoundsChange }) {
  const map = useMap();

  useEffect(() => {
    if (!map) return;

    const updateBounds = () => {
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
    };

    map.on("moveend", updateBounds);
    updateBounds(); // Initial bounds

    return () => {
      map.off("moveend", updateBounds);
    };
  }, [map, onBoundsChange]);

  return null;
}

const HeatmapLayer = ({ points, gradient }) => {
  const map = useMap();
  const heatmapRef = useRef(null);

  useEffect(() => {
    if (!map || !points || points.length === 0) return;

    // Create heatmap data
    const data = {
      max: 1.0,
      data: points.map((point) => ({
        lat: point.lat,
        lng: point.lng,
        value: point.intensity,
        // Use satisfaction level to determine color
        satisfaction: point.satisfaction,
      })),
    };

    // Initialize heatmap if it doesn't exist
    if (!heatmapRef.current) {
      const heatmapConfig = {
        radius: 25,
        maxOpacity: 0.6,
        minOpacity: 0.1,
        blur: 0.75,
        gradient: gradient,
        // Custom color function to use satisfaction level
        valueToColor: function (value, point) {
          const satisfaction = point.satisfaction || 0;
          // Find the closest gradient stops
          const stops = Object.keys(gradient)
            .map(Number)
            .sort((a, b) => a - b);
          let lower = stops[0],
            upper = stops[stops.length - 1];

          for (let i = 0; i < stops.length - 1; i++) {
            if (satisfaction >= stops[i] && satisfaction <= stops[i + 1]) {
              lower = stops[i];
              upper = stops[i + 1];
              break;
            }
          }

          // Interpolate between colors
          const ratio = (satisfaction - lower) / (upper - lower);
          const lowerColor = gradient[lower].match(/\d+/g).map(Number);
          const upperColor = gradient[upper].match(/\d+/g).map(Number);

          const r = Math.round(
            lowerColor[0] + (upperColor[0] - lowerColor[0]) * ratio
          );
          const g = Math.round(
            lowerColor[1] + (upperColor[1] - lowerColor[1]) * ratio
          );
          const b = Math.round(
            lowerColor[2] + (upperColor[2] - lowerColor[2]) * ratio
          );

          return `rgb(${r},${g},${b})`;
        },
      };

      heatmapRef.current = new HeatmapOverlay(heatmapConfig);
      heatmapRef.current.addTo(map);
    }

    // Update heatmap data
    heatmapRef.current.setData(data);
  }, [map, points, gradient]);

  return null;
};

function WebSocketConnection({ onUpdate }) {
  useEffect(() => {
    const ws = new WebSocket(`ws://${window.location.hostname}:8000/ws`);

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      onUpdate(data);
    };

    ws.onerror = (error) => {
      console.error("WebSocket error:", error);
    };

    return () => {
      ws.close();
    };
  }, [onUpdate]);

  return null;
}

function HeatmapUpdater({ bounds, selectedCategory, onDataUpdate }) {
  const [error, setError] = useState(null);

  useEffect(() => {
    if (!bounds) return;

    const controller = new AbortController();

    const fetchHeatmapData = async () => {
      try {
        setError(null);
        const params = new URLSearchParams({
          sw_lat: bounds.sw.lat.toFixed(6),
          sw_lng: bounds.sw.lng.toFixed(6),
          ne_lat: bounds.ne.lat.toFixed(6),
          ne_lng: bounds.ne.lng.toFixed(6),
        });

        if (selectedCategory) {
          params.append("category", selectedCategory);
        }

        const response = await AuthService.fetchWithAuth(
          `/api/heatmap?${params}`,
          {
            signal: controller.signal,
          }
        );

        if (!response.ok) {
          const text = await response.text();
          throw new Error(text || "Failed to fetch heatmap data");
        }

        const data = await response.json();
        onDataUpdate(data);
      } catch (err) {
        if (err.name === "AbortError") return;
        console.error("Error fetching heatmap data:", err);
        setError(err.message);
        onDataUpdate({ points: [] }); // Clear heatmap on error
      }
    };

    fetchHeatmapData();

    return () => {
      controller.abort();
    };
  }, [bounds, selectedCategory, onDataUpdate]);

  if (error) {
    return (
      <div
        style={{
          position: "absolute",
          top: 10,
          left: "50%",
          transform: "translateX(-50%)",
          zIndex: 1000,
          backgroundColor: "#f44336",
          color: "white",
          padding: "6px 16px",
          borderRadius: 4,
          boxShadow: "0 2px 4px rgba(0,0,0,0.2)",
        }}
      >
        {error}
      </div>
    );
  }

  return null;
}

export default function CrisisMap({
  crisisAreas,
  ngos,
  selectedCategory,
  onBoundsChange,
}) {
  const [mapBounds, setMapBounds] = useState(null);
  const [heatmapData, setHeatmapData] = useState({ points: [], gradient: {} });
  const [center, setCenter] = useState([0, 0]);

  useEffect(() => {
    // Set initial center to first crisis area or default
    if (crisisAreas && crisisAreas.length > 0) {
      const firstArea = crisisAreas[0];
      setCenter([firstArea.position.lat, firstArea.position.lng]);
    } else {
      setCenter([0, 0]);
    }
  }, [crisisAreas]);

  const handleWebSocketUpdate = (data) => {
    // Trigger a heatmap refresh when relevant data changes
    if (
      data.type === "crisis_area_update" ||
      (data.type === "ngo_update" && data.is_busy !== undefined)
    ) {
      if (mapBounds) {
        // Re-fetch heatmap data
        setMapBounds({ ...mapBounds });
      }
    }
  };

  return (
    <MapContainer
      center={center}
      zoom={3}
      style={{ height: "100%", width: "100%" }}
    >
      <TileLayer
        attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors'
        url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
      />
      <BoundsUpdater onBoundsChange={setMapBounds} />
      <HeatmapUpdater
        bounds={mapBounds}
        selectedCategory={selectedCategory}
        onDataUpdate={setHeatmapData}
      />
      <HeatmapLayer
        points={heatmapData.points}
        gradient={heatmapData.gradient}
      />
      <WebSocketConnection onUpdate={handleWebSocketUpdate} />

      {crisisAreas?.map((area) => (
        <Marker
          key={area.id}
          position={[area.position.lat, area.position.lng]}
          icon={crisisIcon}
        >
          <Popup>
            <div>
              <h3>{area.name}</h3>
              <p>Population: {area.population.toLocaleString()}</p>
              <p>Security: {area.security}</p>
              <p>Weather: {area.weather_conditions}</p>
              <h4>Current Needs:</h4>
              <ul>
                {Object.entries(area.needs).map(([category, amount]) => (
                  <li key={category}>
                    {category}: {amount}
                  </li>
                ))}
              </ul>
            </div>
          </Popup>
        </Marker>
      ))}

      {ngos?.map((ngo) => (
        <Marker
          key={ngo.id}
          position={[ngo.location.latitude, ngo.location.longitude]}
          icon={ngoIcon}
        >
          <Popup>
            <div>
              <h3>{ngo.name}</h3>
              <p>Status: {ngo.is_busy ? "Busy" : "Available"}</p>
              <p>Rating: {ngo.rating.toFixed(1)}/5.0</p>
              <p>Response Time: {ngo.response_time_hours}h</p>
              <h4>Inventory:</h4>
              <ul>
                {Object.entries(ngo.inventory).map(([category, supplies]) => (
                  <li key={category}>
                    {category}:{" "}
                    {supplies.reduce((sum, s) => sum + s.quantity, 0)} units
                  </li>
                ))}
              </ul>
            </div>
          </Popup>
        </Marker>
      ))}
    </MapContainer>
  );
}
