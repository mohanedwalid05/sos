"use client";

import { useState, useEffect } from "react";
import dynamic from "next/dynamic";
import {
  Box,
  Container,
  Grid,
  Paper,
  Alert,
  CircularProgress,
} from "@mui/material";
import CrisisAreaList from "../components/CrisisAreaList";
import NGOList from "../components/NGOList";
import SupplyCategories from "../components/SupplyCategories";
import AuthService from "../lib/auth";

// Dynamic import of map component to prevent SSR issues
const CrisisMap = dynamic(() => import("../components/CrisisMap"), {
  ssr: false,
  loading: () => (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      height="100%"
    >
      <CircularProgress />
    </Box>
  ),
});

export default function Home() {
  const [selectedCategory, setSelectedCategory] = useState(null);
  const [crisisAreas, setCrisisAreas] = useState([]);
  const [ngos, setNgos] = useState([]);
  const [mapBounds, setMapBounds] = useState({
    sw: { lat: 0, lng: 0 },
    ne: { lat: 0, lng: 0 },
  });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    // Initial data fetch
    fetchInitialData();
  }, []);

  const fetchInitialData = async () => {
    try {
      setLoading(true);
      setError(null);

      // Fetch crisis areas and NGOs in parallel
      const [areasResponse, ngosResponse] = await Promise.all([
        AuthService.fetchWithAuth("/api/crisis-areas"),
        AuthService.fetchWithAuth("/api/ngos"),
      ]);

      if (!areasResponse.ok || !ngosResponse.ok) {
        throw new Error("Failed to fetch initial data");
      }

      const [areasData, ngosData] = await Promise.all([
        areasResponse.json(),
        ngosResponse.json(),
      ]);

      setCrisisAreas(areasData);
      setNgos(ngosData);
    } catch (err) {
      console.error("Error fetching initial data:", err);
      setError("Failed to load data. Please try again later.");
    } finally {
      setLoading(false);
    }
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
  };

  const handleBoundsChange = (bounds) => {
    setMapBounds(bounds);
  };

  if (loading) {
    return (
      <Container
        maxWidth={false}
        sx={{
          height: "100vh",
          display: "flex",
          justifyContent: "center",
          alignItems: "center",
        }}
      >
        <CircularProgress />
      </Container>
    );
  }

  return (
    <Container maxWidth={false} sx={{ height: "100vh", py: 2 }}>
      {error && (
        <Alert severity="error" sx={{ mb: 2 }}>
          {error}
        </Alert>
      )}

      <Grid container spacing={2} sx={{ height: "100%" }}>
        {/* Left Sidebar */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, height: "100%", overflow: "auto" }}>
            <SupplyCategories
              selectedCategory={selectedCategory}
              onCategoryChange={handleCategoryChange}
            />
            <Box sx={{ mt: 2 }}>
              <CrisisAreaList
                areas={crisisAreas}
                selectedCategory={selectedCategory}
              />
            </Box>
          </Paper>
        </Grid>

        {/* Main Map Area */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ height: "100%" }}>
            <CrisisMap
              crisisAreas={crisisAreas}
              ngos={ngos}
              selectedCategory={selectedCategory}
              onBoundsChange={handleBoundsChange}
            />
          </Paper>
        </Grid>

        {/* Right Sidebar */}
        <Grid item xs={12} md={3}>
          <Paper sx={{ p: 2, height: "100%", overflow: "auto" }}>
            <NGOList ngos={ngos} selectedCategory={selectedCategory} />
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}
