import { Box, Chip, Typography } from "@mui/material";
import { SupplyCategory } from "../lib/types";

const categories = [
  { value: SupplyCategory.FOOD, label: "Food", color: "#e57373" },
  { value: SupplyCategory.WATER, label: "Water", color: "#64b5f6" },
  { value: SupplyCategory.MEDICAL, label: "Medical", color: "#81c784" },
  { value: SupplyCategory.SHELTER, label: "Shelter", color: "#ba68c8" },
  { value: SupplyCategory.CLOTHING, label: "Clothing", color: "#fff176" },
  { value: SupplyCategory.HYGIENE, label: "Hygiene", color: "#90a4ae" },
];

export default function SupplyCategories({
  selectedCategory,
  onCategoryChange,
}) {
  return (
    <Box>
      <Typography variant="h6" gutterBottom>
        Supply Categories
      </Typography>
      <Box sx={{ display: "flex", flexWrap: "wrap", gap: 1 }}>
        <Chip
          label="All"
          onClick={() => onCategoryChange(null)}
          variant={selectedCategory === null ? "filled" : "outlined"}
          sx={{
            bgcolor: selectedCategory === null ? "primary.main" : "transparent",
            color: selectedCategory === null ? "white" : "inherit",
          }}
        />
        {categories.map((category) => (
          <Chip
            key={category.value}
            label={category.label}
            onClick={() => onCategoryChange(category.value)}
            variant={
              selectedCategory === category.value ? "filled" : "outlined"
            }
            sx={{
              bgcolor:
                selectedCategory === category.value
                  ? category.color
                  : "transparent",
              color: selectedCategory === category.value ? "white" : "inherit",
              "&:hover": {
                bgcolor:
                  selectedCategory === category.value
                    ? category.color
                    : `${category.color}33`, // 20% opacity
              },
            }}
          />
        ))}
      </Box>
    </Box>
  );
}
