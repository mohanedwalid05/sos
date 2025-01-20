const https = require("https");
const fs = require("fs");
const path = require("path");

const ICON_URLS = {
  "marker-icon.png":
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  "marker-icon-2x.png":
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-blue.png",
  "marker-shadow.png":
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-shadow.png",
  "crisis-marker.png":
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  "crisis-marker-2x.png":
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-red.png",
  "ngo-marker.png":
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
  "ngo-marker-2x.png":
    "https://raw.githubusercontent.com/pointhi/leaflet-color-markers/master/img/marker-icon-2x-green.png",
};

const ICONS_DIR = path.join(__dirname, "..", "public", "icons");

// Create icons directory if it doesn't exist
if (!fs.existsSync(ICONS_DIR)) {
  fs.mkdirSync(ICONS_DIR, { recursive: true });
}

// Download each icon
Object.entries(ICON_URLS).forEach(([filename, url]) => {
  const filepath = path.join(ICONS_DIR, filename);
  const file = fs.createWriteStream(filepath);

  https
    .get(url, (response) => {
      response.pipe(file);
      file.on("finish", () => {
        file.close();
        console.log(`Downloaded ${filename}`);
      });
    })
    .on("error", (err) => {
      fs.unlink(filepath, () => {});
      console.error(`Error downloading ${filename}:`, err.message);
    });
});
