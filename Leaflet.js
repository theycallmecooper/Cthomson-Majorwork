import React, { useState, useEffect } from "react";
import { MapContainer, TileLayer, Marker, Popup } from "react-leaflet";
import "leaflet/dist/leaflet.css";

const DangerousSpeciesMap = () => {
  const [location, setLocation] = useState(null);
  const [species, setSpecies] = useState([]);

  useEffect(() => {
    if (navigator.geolocation) {
      navigator.geolocation.getCurrentPosition(
        (position) => {
          setLocation({
            lat: position.coords.latitude,
            lng: position.coords.longitude,
          });
          fetchSpecies(position.coords.latitude, position.coords.longitude);
        },
        (error) => console.error("Error getting location:", error)
      );
    }
  }, []);

  const fetchSpecies = async (lat, lng) => {
    // Fetch species data from your Flask API
    try {
      const response = await fetch(`/species?lat=${lat}&lng=${lng}`);
      const data = await response.json();
      setSpecies(data);  // Set the species data from the Flask API
    } catch (error) {
      console.error("Error fetching species:", error);
    }
  };

  return (
    <div style={{ height: "100vh" }}>
      {location ? (
        <MapContainer center={[location.lat, location.lng]} zoom={10} style={{ height: "100%", width: "100%" }}>
          <TileLayer url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png" />
          <Marker position={[location.lat, location.lng]}>
            <Popup>Your Location</Popup>
          </Marker>
          {species.map((sp) => (
            <Marker key={sp.id} position={[sp.lat, sp.lng]}>
              <Popup>
                <strong>{sp.name}</strong> <br />
                <em>{sp.scientificName}</em> <br />
                {sp.danger}
              </Popup>
            </Marker>
          ))}
        </MapContainer>
      ) : (
        <p>Loading location...</p>
      )}
    </div>
  );
};

export default DangerousSpeciesMap;