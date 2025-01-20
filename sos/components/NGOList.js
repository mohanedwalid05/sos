import {
  List,
  ListItem,
  ListItemText,
  Typography,
  Box,
  Chip,
  Rating,
  Collapse,
  CircularProgress,
} from "@mui/material";
import { useState } from "react";
import { ExpandMore, ExpandLess } from "@mui/icons-material";

export default function NGOList({ ngos, selectedCategory }) {
  const [expandedNGO, setExpandedNGO] = useState(null);

  const handleClick = (ngoId) => {
    setExpandedNGO(expandedNGO === ngoId ? null : ngoId);
  };

  const getStatusColor = (isBusy) => {
    return isBusy ? "error" : "success";
  };

  const getCredibilityColor = (score) => {
    if (score >= 0.8) return "success";
    if (score >= 0.5) return "warning";
    return "error";
  };

  const calculateTotalQuantity = (supplies = []) => {
    return supplies.reduce((sum, s) => sum + (s.quantity || 0), 0);
  };

  const getExpiringSupplies = (supplies = []) => {
    const oneWeekFromNow = new Date(Date.now() + 7 * 24 * 60 * 60 * 1000);
    return supplies.filter(
      (s) => s.expiry_date && new Date(s.expiry_date) <= oneWeekFromNow
    );
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        NGOs
      </Typography>
      <List>
        {ngos.map((ngo) => {
          // Filter inventory based on selected category
          const relevantInventory = selectedCategory
            ? { [selectedCategory]: ngo.inventory?.[selectedCategory] || [] }
            : ngo.inventory || {};

          return (
            <Box key={ngo.id} sx={{ mb: 2 }}>
              <ListItem
                button
                onClick={() => handleClick(ngo.id)}
                sx={{
                  bgcolor: "background.paper",
                  borderRadius: 1,
                  "&:hover": {
                    bgcolor: "action.hover",
                  },
                }}
              >
                <ListItemText
                  primary={
                    <Box sx={{ display: "flex", alignItems: "center", gap: 1 }}>
                      <Typography variant="subtitle1">{ngo.name}</Typography>
                      <Chip
                        size="small"
                        label={ngo.is_busy ? "Busy" : "Available"}
                        color={getStatusColor(ngo.is_busy)}
                      />
                      <Box
                        sx={{
                          display: "flex",
                          alignItems: "center",
                          ml: "auto",
                        }}
                      >
                        <Rating value={ngo.rating || 0} readOnly size="small" />
                      </Box>
                    </Box>
                  }
                  secondary={
                    <Box
                      sx={{
                        display: "flex",
                        alignItems: "center",
                        gap: 1,
                        mt: 0.5,
                      }}
                    >
                      <Typography variant="body2" color="text.secondary">
                        Response Time: {ngo.response_time_hours || 0}h
                      </Typography>
                      <CircularProgress
                        variant="determinate"
                        value={(ngo.credibility_score || 0) * 100}
                        size={16}
                        sx={{ ml: 1 }}
                        color={getCredibilityColor(ngo.credibility_score || 0)}
                      />
                    </Box>
                  }
                />
                {expandedNGO === ngo.id ? <ExpandLess /> : <ExpandMore />}
              </ListItem>

              <Collapse
                in={expandedNGO === ngo.id}
                timeout="auto"
                unmountOnExit
              >
                <Box
                  sx={{
                    p: 2,
                    bgcolor: "background.paper",
                    borderRadius: 1,
                    mt: 1,
                  }}
                >
                  <Typography variant="subtitle2" gutterBottom>
                    Available Supplies:
                  </Typography>
                  {Object.entries(relevantInventory).map(
                    ([category, supplies]) => {
                      const totalQuantity = calculateTotalQuantity(supplies);
                      const expiringSupplies = getExpiringSupplies(supplies);

                      return (
                        <Box key={category} sx={{ mb: 2 }}>
                          <Box
                            sx={{
                              display: "flex",
                              justifyContent: "space-between",
                              mb: 0.5,
                            }}
                          >
                            <Typography variant="body2">{category}</Typography>
                            <Typography variant="body2" color="text.secondary">
                              {totalQuantity} available
                            </Typography>
                          </Box>
                          {expiringSupplies.length > 0 && (
                            <Typography variant="caption" color="warning.main">
                              {expiringSupplies.length} items expiring within 7
                              days
                            </Typography>
                          )}
                        </Box>
                      );
                    }
                  )}

                  <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                    Additional Information:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Reach Radius: {ngo.reach_radius_km || 0}km
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Total Donations: {ngo.total_donations || 0}
                  </Typography>
                  {ngo.last_donation && (
                    <Typography variant="body2" color="text.secondary">
                      Last Donation:{" "}
                      {new Date(
                        ngo.last_donation.timestamp
                      ).toLocaleDateString()}
                    </Typography>
                  )}
                  <Typography variant="body2" color="text.secondary">
                    Specializations:{" "}
                    {(ngo.specializations || []).join(", ") || "None"}
                  </Typography>
                </Box>
              </Collapse>
            </Box>
          );
        })}
      </List>
    </Box>
  );
}
