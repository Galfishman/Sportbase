# ⚽ SportBase - Player Performance Reports

A comprehensive web application for generating detailed football player performance reports from Instat XML data.

## 🌟 Features

### 📊 **Complete Analysis Suite**
- **Passes Map**: Accurate positioning with progressive/successful/unsuccessful categorization
- **Dribbles Analysis**: Success/failure rates with field positioning
- **Defensive Actions**: Detailed breakdown by action type with color coding
- **Shot Map**: Goals (stars), shots on target (dots), shots off target (X)
- **Activity Heatmap**: Movement patterns with Gaussian filtering
- **Performance Timeline**: 5-minute interval analysis vs team average

### 🎯 **Key Metrics**
- Pass accuracy and progressive passes
- Shooting efficiency and goal conversion
- Defensive contributions by category
- Effective playing time calculation
- Comparative team analysis

### 💻 **User-Friendly Interface**
- Drag-and-drop XML file upload
- Multiple player selection methods
- Real-time report generation
- High-quality PNG downloads
- Professional report layouts

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Installation

1. **Clone or download the SportBase folder**
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application:**
   ```bash
   python run_app.py
   ```
   
   Or manually:
   ```bash
   streamlit run streamlit_app.py
   ```

4. **Open your browser** to `http://localhost:8501`

## 📖 How to Use

### Step 1: Upload XML File
- Click "Choose an Instat XML file" 
- Upload your match data XML file
- Wait for parsing confirmation

### Step 2: Select Players
Choose from three selection methods:
- **Individual Selection**: Pick specific players
- **All Players**: Generate reports for entire match
- **Team Selection**: Choose players by team

### Step 3: Generate Reports
- Click "🚀 Generate Reports"
- Wait for processing (progress bar shown)
- Review generated reports

### Step 4: Download
- Preview reports in the browser
- Download high-quality PNG files
- Reports saved with player names

## 📁 Project Structure

```
SportBase/
├── streamlit_app.py          # Main web application
├── player_report.py          # Report generation engine  
├── instat_parser.py          # XML parsing utilities
├── run_app.py               # Launch script
├── requirements.txt         # Python dependencies
├── match_events.csv         # Sample parsed data
├── sample_player_report.png # Example output
└── README.md               # This file
```

## 🔧 Technical Details

### Report Generation Process
1. **XML Parsing**: Instat event data → structured DataFrame
2. **Player Analysis**: Extract individual player actions
3. **Visualization**: Generate pitch maps using mplsoccer
4. **Statistics**: Calculate comprehensive performance metrics
5. **Export**: High-resolution PNG reports (300 DPI)

### Performance Features
- **Accurate Positioning**: No misleading trajectory arrows
- **Smart Filtering**: Removes duplicate goal/shot events
- **Effective Time**: Calculates actual playing time
- **Team Comparison**: Player vs team average metrics
- **Professional Styling**: Clean, readable layouts

## 📊 Sample Output

Reports include:
- **Six visualization panels** in professional layout
- **Comprehensive statistics** with pass accuracy, shooting stats
- **Defensive contributions** broken down by action type  
- **Activity patterns** with heatmap visualization
- **Performance timeline** showing consistency over time

## 🛠️ Dependencies

- **streamlit**: Web application framework
- **pandas**: Data manipulation and analysis
- **matplotlib**: Plotting and visualization
- **mplsoccer**: Football pitch visualization
- **numpy**: Numerical computing
- **scipy**: Scientific computing (Gaussian filtering)

## 💡 Tips for Best Results

1. **File Format**: Ensure XML files are valid Instat event data
2. **Player Selection**: Preview player lists before generating all reports
3. **Performance**: Large files may take longer to process
4. **Download**: Reports are temporarily stored and cleaned up automatically

## 🚨 Troubleshooting

### Common Issues
- **Import Error**: Run `pip install -r requirements.txt`
- **XML Parse Error**: Check file format and validity
- **Memory Issues**: Try selecting fewer players at once
- **Display Issues**: Ensure browser supports modern web standards

### Error Messages
- "Error parsing XML": File format issue - check XML structure
- "Player not found": Name mismatch - verify player selection
- "No data available": Insufficient events for selected player

## 🎯 Use Cases

- **Match Analysis**: Post-game player performance review
- **Scouting Reports**: Comprehensive player evaluation
- **Team Meetings**: Visual performance presentations  
- **Player Development**: Track individual progress over time
- **Recruitment**: Data-driven player assessment

## 🔄 Updates

The application automatically handles:
- ✅ Duplicate shot/goal event filtering
- ✅ Coordinate system normalization  
- ✅ Team-based player categorization
- ✅ Effective playing time calculation
- ✅ Professional report formatting

---

**SportBase** - Advanced Football Analytics Platform | Built with ❤️ using Python & Streamlit