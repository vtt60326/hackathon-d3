# Device Analytics Dashboard - Pure JavaScript UI

## Overview

A modern, modular web dashboard built with **pure JavaScript** and **D3.js** for visualizing device analytics, customer data, and Next Best Action recommendations.

## Architecture

### Folder Structure

```
UI/
├── index.html          # Main HTML entry point
├── css/
│   ├── styles.css      # Global styles and layout
│   └── components.css  # Component-specific styles
└── js/
    ├── data-loader.js  # CSV data loading module
    ├── charts.js       # D3.js chart rendering
    ├── dashboard.js    # Device overview logic
    ├── nba.js          # Next Best Action logic
    └── app.js          # Main application controller
```

## Features

### 📊 Device Overview Tab
- **Interactive threshold slider** (7-90 days)
- **Real-time statistics cards** with color-coded metrics
- **Tree visualization** showing device hierarchy
- **D3.js pie charts** for Frontier vs Non-Frontier distribution
- **Target group highlighting** (Frontier + Active devices)

### 👥 Customer Analysis Tab
- Placeholder for future customer analytics
- Ready for expansion

### 🔍 Device Details Tab
- Placeholder for detailed device metrics
- Ready for expansion

### 🎯 Next Best Action Tab
- **AI-driven recommendations** based on business rules:
  - Ship new device (urgent - at-risk customers)
  - Speed upgrade + new device (high-value opportunities)
  - Speed upgrade only (cost-effective enhancements)
  - Keep as is (satisfied stable customers)
  - No action recommended (requires review)
- **Action filter dropdown** for targeted views
- **Customer ID search** functionality
- **Interactive bar chart** showing action distribution
- **Sortable data table** with color-coded badges
- **CSV export** with timestamped filenames

## Technology Stack

- **Frontend**: Pure JavaScript (ES6+), HTML5, CSS3
- **Visualization**: D3.js v7
- **Data Format**: CSV files loaded via Fetch API
- **Server**: Python HTTP Server (simple file serving)

## Quick Start

### Option 1: Using Batch File (Windows - Easiest)

Simply **double-click** `run_ui_dashboard.bat` in the project root!

### Option 2: Using Python

```bash
# From project root
python server.py
```

The dashboard will automatically open at: `http://localhost:8000/index.html`

### Option 3: Manual Server

```bash
# From project root
python -m http.server 8000

# Then navigate to:
# http://localhost:8000/UI/index.html
```

## Data Requirements

The dashboard requires three CSV files in `Data/Data Output/`:

1. **customer_data.csv** - Customer information
   - customer_id, clv_decile, churn_risk, customer_segment, etc.

2. **device_data.csv** - Device information
   - customer_id, serial_number, device_model, isp, last_alive_date, etc.

3. **nba_data.csv** - Next Best Action recommendations
   - Merged customer + device data with next_best_action field

### Generating NBA Data

If `nba_data.csv` doesn't exist:

```bash
python generate_nba_data.py
```

## Module Documentation

### data-loader.js

Handles all data loading operations:
- `loadAllData()` - Loads all CSV files in parallel
- `loadCSV(url)` - Loads a single CSV file
- `parseDeviceData()` - Parses and converts date fields
- `getMergedData()` - Merges customer and device data

### charts.js

D3.js visualization functions:
- `drawPieChart()` - Creates interactive pie charts
- `drawBarChart()` - Creates horizontal bar charts
- `drawVerticalBarChart()` - Creates vertical bar charts

### dashboard.js

Device overview dashboard logic:
- `init()` - Initializes the dashboard
- `calculateStats()` - Computes device statistics
- `updateDashboard()` - Refreshes all visualizations
- `updateCharts()` - Updates D3.js charts

### nba.js

Next Best Action module:
- `init()` - Initializes NBA features
- `filterData()` - Filters by action type
- `updateNBAView()` - Updates all NBA visualizations
- `downloadCSV()` - Exports filtered data

### app.js

Main application controller:
- `init()` - Initializes the entire application
- `loadData()` - Loads all required data
- `setupTabs()` - Configures tab navigation
- `initializeModules()` - Initializes all dashboard modules

## Customization

### Changing Colors

Edit `UI/css/styles.css`:

```css
/* Main gradient */
body {
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

/* Target card */
.stat-card.target {
    background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
}
```

### Changing Port

Edit `server.py`:

```python
PORT = 8000  # Change to your preferred port
```

### Adding New Visualizations

1. Create new functions in `charts.js`
2. Call them from `dashboard.js` or `nba.js`
3. Add HTML containers in `index.html`

### Adding New Tabs

1. Add tab button in `index.html`:
   ```html
   <button class="tab" data-tab="mytab">My Tab</button>
   ```

2. Add tab content:
   ```html
   <div id="mytab-content" class="tab-content">
       <!-- Your content -->
   </div>
   ```

3. Handle in `app.js` `onTabChange()` if needed

## Browser Compatibility

✅ **Tested on:**
- Chrome 90+
- Firefox 88+
- Edge 90+
- Safari 14+

⚠️ **Requirements:**
- Modern browser with ES6+ support
- JavaScript enabled
- Fetch API support

## Performance

- **Fast Loading**: Handles 300K+ device records
- **Real-time Updates**: Instant response to filters
- **Smooth Animations**: 60 FPS D3.js transitions
- **Efficient Rendering**: Virtual scrolling for large tables (first 100 shown)

## Troubleshooting

### Dashboard shows "Loading data..." forever

**Cause**: Server not running or data files missing

**Solution**:
```bash
# Make sure server is running
python server.py

# Check data files exist in Data/Data Output/
```

### Error: Cannot load CSV files

**Cause**: CORS policy or incorrect file paths

**Solution**:
- Always use the server (don't open HTML directly)
- Check file paths in `data-loader.js`
- Verify CSV files exist

### Port already in use

**Solution**: Change port in `server.py` or kill existing process

```bash
# Windows
netstat -ano | findstr :8000
taskkill /PID <pid> /F

# Linux/Mac
lsof -ti:8000 | xargs kill
```

### Browser shows old data

**Solution**: Hard refresh
- **Windows**: Ctrl + Shift + R
- **Mac**: Cmd + Shift + R

## Development

### Adding New Features

1. Create new module in `js/` folder
2. Import in `index.html` before `app.js`
3. Initialize in `app.js`
4. Add styles in `css/` as needed

### Debugging

Open browser console (F12) to see:
- Data loading progress
- Module initialization logs
- Error messages

## API Documentation

### DataLoader API

```javascript
// Load all data
const data = await DataLoader.loadAllData();

// Access loaded data
const customers = DataLoader.customerData;
const devices = DataLoader.deviceData;
const nba = DataLoader.nbaData;

// Get merged data
const merged = DataLoader.getMergedData();
```

### Charts API

```javascript
// Draw pie chart
Charts.drawPieChart('container-id', data, colors);

// Draw bar chart
Charts.drawBarChart('container-id', data, colorMap);
```

### Dashboard API

```javascript
// Initialize
Dashboard.init(deviceData);

// Update threshold
Dashboard.activeThreshold = 60;
Dashboard.updateDashboard();
```

### NBA API

```javascript
// Initialize
NBA.init(nbaData);

// Filter data
NBA.currentFilter = 'Ship new device';
NBA.filterData();
NBA.updateNBAView();

// Download CSV
NBA.downloadCSV();
```

## Contributing

To add new features:

1. Follow the modular structure
2. Keep modules independent
3. Use global `window` object for exports
4. Document public APIs
5. Test in multiple browsers

## License

Part of the Hackathon project. Modify and use as needed!

## Support

For issues:

1. Check browser console (F12) for errors
2. Verify data files exist
3. Ensure server is running
4. Check file paths are correct
5. Try a different port if needed

---

**Built with ❤️ using Pure JavaScript and D3.js**

