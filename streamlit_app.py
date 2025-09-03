import streamlit as st
import pandas as pd
import xml.etree.ElementTree as ET
import tempfile
import os
import io
from player_report import PlayerReport
from instat_parser import InstatEventParser

# Set page config
st.set_page_config(
    page_title="SportBase - Player Performance Reports",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        font-weight: bold;
        text-align: center;
        color: #2E7D32;
        margin-bottom: 2rem;
    }
    .step-header {
        font-size: 1.5rem;
        font-weight: bold;
        color: #1976D2;
        margin: 1rem 0;
    }
    .info-box {
        background-color: #E3F2FD;
        border-left: 5px solid #2196F3;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .success-box {
        background-color: #E8F5E8;
        border-left: 5px solid #4CAF50;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
    .error-box {
        background-color: #FFEBEE;
        border-left: 5px solid #F44336;
        padding: 1rem;
        margin: 1rem 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

def parse_uploaded_xml(uploaded_file):
    """Parse uploaded XML file and return CSV data"""
    try:
        # Save uploaded file to temporary location
        with tempfile.NamedTemporaryFile(delete=False, suffix='.xml') as tmp_file:
            tmp_file.write(uploaded_file.getvalue())
            tmp_xml_path = tmp_file.name
        
        # Parse XML using existing parser
        parser = InstatEventParser(tmp_xml_path)
        if parser.parse_xml():
            events = parser.extract_events()
            
            # Convert to DataFrame
            flattened_data = []
            for event in events:
                row = {
                    'id': event.get('id'),
                    'start_time': event.get('start_time'),
                    'end_time': event.get('end_time'),
                    'code': event.get('code')
                }
                
                # Add all labels as separate columns
                labels = event.get('labels', {})
                for key, value in labels.items():
                    row[f'label_{key.lower()}'] = value
                
                flattened_data.append(row)
            
            df = pd.DataFrame(flattened_data)
            
            # Clean up temp file
            os.unlink(tmp_xml_path)
            
            return df, len(events)
        else:
            # Clean up temp file
            os.unlink(tmp_xml_path)
            return None, 0
            
    except Exception as e:
        st.error(f"Error parsing XML file: {str(e)}")
        return None, 0

def get_player_list_from_df(df):
    """Extract player list from DataFrame"""
    players = set()
    for code in df['code'].dropna():
        if ' - ' in code and '.' in code and '(' in code:
            player_part = code.split(' - ')[0]
            player_name = player_part.split('.', 1)[1].split('(')[0].strip()
            if player_name and player_name != 'None':
                players.add(player_name)
    
    return sorted(list(players))

def get_match_info(df):
    """Extract match information from DataFrame"""
    teams = set()
    for team in df['label_team'].dropna():
        if team != 'None':
            teams.add(team)
    
    # Get match duration
    max_time = df['start_time'].max() / 60  # Convert to minutes
    
    return list(teams), max_time

def main():
    # Main header
    st.markdown('<h1 class="main-header">⚽ SportBase - Player Performance Reports</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("📊 Navigation")
    st.sidebar.markdown("---")
    
    # Step 1: File Upload
    st.markdown('<div class="step-header">Step 1: Upload Instat XML File</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        "Choose an Instat XML file",
        type=['xml'],
        help="Upload your Instat event data XML file to generate player performance reports"
    )
    
    if uploaded_file is not None:
        st.markdown('<div class="info-box">📁 File uploaded successfully! Processing...</div>', unsafe_allow_html=True)
        
        # Parse the uploaded file
        with st.spinner('Parsing XML file...'):
            df, event_count = parse_uploaded_xml(uploaded_file)
        
        if df is not None and len(df) > 0:
            # Store data in session state
            st.session_state.match_data = df
            st.session_state.event_count = event_count
            
            # Get match information
            teams, match_duration = get_match_info(df)
            players = get_player_list_from_df(df)
            
            st.markdown('<div class="success-box">✅ XML file parsed successfully!</div>', unsafe_allow_html=True)
            
            # Display match information
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("📊 Total Events", f"{event_count:,}")
            with col2:
                st.metric("👥 Players Found", len(players))
            with col3:
                st.metric("⏱️ Match Duration", f"{match_duration:.0f} min")
            
            # Display teams
            st.markdown("**Teams:**")
            for i, team in enumerate(teams):
                st.markdown(f"• {team}")
            
            st.markdown("---")
            
            # Step 2: Player Selection
            st.markdown('<div class="step-header">Step 2: Select Players for Reports</div>', unsafe_allow_html=True)
            
            # Player selection options
            selection_method = st.radio(
                "How would you like to select players?",
                ["Select individual players", "Select all players", "Select by team"],
                horizontal=True
            )
            
            selected_players = []
            
            if selection_method == "Select individual players":
                selected_players = st.multiselect(
                    "Choose players:",
                    players,
                    help="Select one or more players to generate reports for"
                )
                
            elif selection_method == "Select all players":
                if st.checkbox("Generate reports for all players"):
                    selected_players = players
                    st.info(f"Selected all {len(players)} players")
                    
            elif selection_method == "Select by team":
                # Create team-based selection
                team_players = {}
                for player in players:
                    # Get player's team from data
                    player_events = df[df['code'].str.contains(f' {player} ', na=False)]
                    if len(player_events) > 0:
                        team = player_events['label_team'].iloc[0]
                        if team not in team_players:
                            team_players[team] = []
                        team_players[team].append(player)
                
                selected_team = st.selectbox("Select team:", list(team_players.keys()))
                if selected_team:
                    team_player_list = team_players[selected_team]
                    selected_players = st.multiselect(
                        f"Players from {selected_team}:",
                        team_player_list,
                        default=team_player_list
                    )
            
            # Step 3: Generate Reports
            if selected_players:
                st.markdown("---")
                st.markdown('<div class="step-header">Step 3: Generate Player Reports</div>', unsafe_allow_html=True)
                
                st.info(f"Ready to generate reports for {len(selected_players)} player(s)")
                
                if st.button("🚀 Generate Reports", type="primary"):
                    # Create temporary CSV file for the report generator
                    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as tmp_csv:
                        df.to_csv(tmp_csv.name, index=False)
                        tmp_csv_path = tmp_csv.name
                    
                    try:
                        # Initialize report generator
                        report_generator = PlayerReport(tmp_csv_path)
                        
                        # Progress bar
                        progress_bar = st.progress(0)
                        status_text = st.empty()
                        
                        generated_reports = []
                        
                        for i, player in enumerate(selected_players):
                            status_text.text(f'Generating report for {player}...')
                            progress_bar.progress((i + 1) / len(selected_players))
                            
                            try:
                                # Generate report
                                output_file = f"{player.replace(' ', '_')}_report.png"
                                report_path = report_generator.generate_complete_report(player, output_file)
                                
                                if os.path.exists(report_path):
                                    generated_reports.append((player, report_path))
                                    
                            except Exception as e:
                                st.error(f"Error generating report for {player}: {str(e)}")
                        
                        status_text.text('Reports generated successfully!')
                        
                        # Clean up temp CSV
                        os.unlink(tmp_csv_path)
                        
                        if generated_reports:
                            st.markdown("---")
                            st.markdown('<div class="step-header">Step 4: Download Reports</div>', unsafe_allow_html=True)
                            
                            st.success(f"✅ Generated {len(generated_reports)} report(s) successfully!")
                            
                            # Display and provide download for each report
                            for player, report_path in generated_reports:
                                st.markdown(f"### 📊 {player}")
                                
                                col1, col2 = st.columns([3, 1])
                                
                                with col1:
                                    # Display the report image
                                    st.image(report_path, caption=f"{player} - Performance Report")
                                
                                with col2:
                                    # Provide download button
                                    with open(report_path, "rb") as file:
                                        st.download_button(
                                            label=f"📥 Download {player} Report",
                                            data=file.read(),
                                            file_name=f"{player.replace(' ', '_')}_performance_report.png",
                                            mime="image/png",
                                            key=f"download_{player}"
                                        )
                                
                                st.markdown("---")
                            
                            # Cleanup generated files
                            for _, report_path in generated_reports:
                                if os.path.exists(report_path):
                                    os.unlink(report_path)
                    
                    except Exception as e:
                        st.error(f"Error in report generation process: {str(e)}")
                        # Clean up temp CSV
                        if os.path.exists(tmp_csv_path):
                            os.unlink(tmp_csv_path)
        else:
            st.markdown('<div class="error-box">❌ Error parsing XML file. Please check the file format.</div>', unsafe_allow_html=True)
    
    else:
        # Instructions when no file is uploaded
        st.markdown('<div class="info-box">', unsafe_allow_html=True)
        st.markdown("""
        **How to use SportBase:**
        
        1. **Upload** your Instat XML match data file
        2. **Select** players you want to generate reports for  
        3. **Generate** comprehensive performance reports
        4. **Download** the reports as high-quality PNG files
        
        **Report Features:**
        - ✅ Passes map with accurate positioning
        - ✅ Dribbles and shooting analysis  
        - ✅ Defensive actions breakdown
        - ✅ Activity heatmap
        - ✅ Performance timeline (5-minute intervals)
        - ✅ Comprehensive statistics summary
        """)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Footer
    st.markdown("---")
    st.markdown("**SportBase** - Advanced Football Analytics Platform | Built with ❤️ using Streamlit")

if __name__ == "__main__":
    main()