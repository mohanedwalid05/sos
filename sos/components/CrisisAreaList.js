import {
  List,
  ListItem,
  ListItemText,
  Typography,
  Box,
  Chip,
  LinearProgress,
  Collapse,
} from "@mui/material";
import { useState } from "react";
import { ExpandMore, ExpandLess } from "@mui/icons-material";

export default function CrisisAreaList({ areas, selectedCategory }) {
  const [expandedArea, setExpandedArea] = useState(null);

  const handleClick = (areaId) => {
    setExpandedArea(expandedArea === areaId ? null : areaId);
  };

  const getUrgencyColor = (urgency) => {
    if (urgency >= 4) return "error";
    if (urgency >= 2.5) return "warning";
    return "success";
  };

  const getSecurityColor = (level) => {
    const colors = {
      safe: "success",
      caution: "warning",
      dangerous: "error",
      extreme: "error",
    };
    return colors[level.toLowerCase()] || "default";
  };

  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Crisis Areas
      </Typography>
      <List>
        {areas.map((area) => {
          // Filter needs based on selected category
          const relevantNeeds = selectedCategory
            ? { [selectedCategory]: area.needs[selectedCategory] }
            : area.needs;

          return (
            <Box key={area.id} sx={{ mb: 2 }}>
              <ListItem
                button
                onClick={() => handleClick(area.id)}
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
                      <Typography variant="subtitle1">{area.name}</Typography>
                      <Chip
                        size="small"
                        label={`Urgency: ${area.urgency.toFixed(1)}`}
                        color={getUrgencyColor(area.urgency)}
                      />
                      <Chip
                        size="small"
                        label={area.security}
                        color={getSecurityColor(area.security)}
                      />
                    </Box>
                  }
                  secondary={`Population: ${area.population.toLocaleString()}`}
                />
                {expandedArea === area.id ? <ExpandLess /> : <ExpandMore />}
              </ListItem>

              <Collapse
                in={expandedArea === area.id}
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
                    Current Needs:
                  </Typography>
                  {Object.entries(relevantNeeds).map(([category, amount]) => (
                    <Box key={category} sx={{ mb: 1 }}>
                      <Box
                        sx={{
                          display: "flex",
                          justifyContent: "space-between",
                          mb: 0.5,
                        }}
                      >
                        <Typography variant="body2">{category}</Typography>
                        <Typography variant="body2" color="text.secondary">
                          {amount} needed
                        </Typography>
                      </Box>
                      <LinearProgress
                        variant="determinate"
                        value={Math.min(
                          ((area.current_inventory[category]?.length || 0) /
                            amount) *
                            100,
                          100
                        )}
                        color={getUrgencyColor(area.urgency)}
                      />
                    </Box>
                  ))}

                  <Typography variant="subtitle2" sx={{ mt: 2, mb: 1 }}>
                    Additional Information:
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Weather: {area.weather_conditions}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    Reachability: {area.reachability}
                  </Typography>
                  {area.last_donation_received && (
                    <Typography variant="body2" color="text.secondary">
                      Last Donation:{" "}
                      {new Date(
                        area.last_donation_received.timestamp
                      ).toLocaleDateString()}
                    </Typography>
                  )}
                </Box>
              </Collapse>
            </Box>
          );
        })}
      </List>
    </Box>
  );
}
