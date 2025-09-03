import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Circle
from matplotlib.colors import LinearSegmentedColormap
import numpy as np
from mplsoccer import Pitch
from scipy.ndimage import gaussian_filter

class PlayerReport:
    def __init__(self, csv_file_path: str):
        """Initialize the corrected player report generator with match data"""
        self.csv_file = csv_file_path
        self.df = None
        self.load_data()
        
        # Action mappings for different categories
        self.pass_actions = [
            'Passes accurate', 'Passes forward accurate', 'Progressive passes accurate',
            'Inaccurate passes', 'Incomplete passes forward', 'Passes inaccurate',
            'Long passes accurate', 'Long passes inaccurate', 'Key passes'
        ]
        
        self.dribble_actions = [
            'Dribbling successful', 'Dribbling unsuccessful', 'Take on successful',
            'Take on unsuccessful', 'Dribbles', 'Dribbling'
        ]
        
        self.defensive_actions = [
            'Challenges won', 'Challenges unsuccessful', 'Interceptions',
            'Tackles successful', 'Tackles unsuccessful', 'Clearances',
            'Blocks', 'Ball recoveries', 'Duels won', 'Duels lost'
        ]
        
        self.shooting_actions = [
            'Goals', 'Shots on target', 'Shots off target', 'Shots blocked',
            'Participation in positional attacks with shots',
            'Participation in set-pieces with shots',
            'Participation in counterattacks with shots'
        ]
        
    def load_data(self):
        """Load and prepare the CSV data"""
        try:
            self.df = pd.read_csv(self.csv_file)
            print(f"Loaded {len(self.df)} events from {self.csv_file}")
            
            # Clean and prepare data
            self.df['label_pos_x'] = pd.to_numeric(self.df['label_pos_x'], errors='coerce')
            self.df['label_pos_y'] = pd.to_numeric(self.df['label_pos_y'], errors='coerce')
            self.df['start_time'] = pd.to_numeric(self.df['start_time'], errors='coerce')
            
            # Remove rows with invalid coordinates
            self.df = self.df.dropna(subset=['label_pos_x', 'label_pos_y'])
            
        except Exception as e:
            print(f"Error loading data: {e}")
            
    def get_player_list(self, team_name=None):
        """Get list of all players, optionally filtered by team"""
        if team_name:
            team_df = self.df[self.df['label_team'].str.contains(team_name, na=False)]
        else:
            team_df = self.df
            
        # Extract player names from the code column
        players = set()
        for code in team_df['code'].dropna():
            if ' - ' in code and '.' in code and '(' in code:
                player_part = code.split(' - ')[0]
                player_name = player_part.split('.', 1)[1].split('(')[0].strip()
                if player_name and player_name != 'None':
                    players.add(player_name)
        
        return sorted(list(players))
    
    def get_player_events(self, player_name: str):
        """Get all events for a specific player"""
        player_events = self.df[self.df['code'].str.contains(f' {player_name} ', na=False)]
        return player_events
    
    def create_passes_dots_map(self, player_name: str, ax, title_suffix=""):
        """Create passes map with ONLY dots (no misleading arrows)"""
        pitch = Pitch(pitch_color='white', line_color='black', linewidth=2, pitch_length=105, pitch_width=68)
        pitch.draw(ax=ax)
        
        player_events = self.get_player_events(player_name)
        pass_events = player_events[player_events['label_action'].isin(self.pass_actions)]
        
        # Categorize passes
        progressive_passes = pass_events[pass_events['label_action'] == 'Progressive passes accurate']
        successful_passes = pass_events[
            (pass_events['label_action'] == 'Passes accurate') |
            (pass_events['label_action'] == 'Passes forward accurate')
        ]
        unsuccessful_passes = pass_events[
            (pass_events['label_action'] == 'Inaccurate passes') |
            (pass_events['label_action'] == 'Incomplete passes forward') |
            (pass_events['label_action'] == 'Passes inaccurate')
        ]
        
        # Draw dots only - no arrows!
        # Unsuccessful passes (lowest layer)
        for _, event in unsuccessful_passes.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='grey', s=100, alpha=0.4, marker='o', zorder=1, 
                      edgecolors='black', linewidths=1)
            
        # Successful passes
        for _, event in successful_passes.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='#4444FF', s=100, alpha=0.7, marker='o', zorder=2, 
                      edgecolors='black', linewidths=1)
            
        # Progressive passes (highest layer)
        for _, event in progressive_passes.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='yellow', s=100, alpha=0.8, marker='o', zorder=3, 
                      edgecolors='black', linewidths=1)
        
        ax.set_title(f'{player_name} - Passes Map{title_suffix}', 
                    fontsize=12, fontweight='bold', color='black', pad=15)
        
        # Enhanced legend
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='yellow', 
                      markersize=7, alpha=0.8, label=f'Progressive ({len(progressive_passes)})'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4444FF', 
                      markersize=7, alpha=0.7, label=f'Successful ({len(successful_passes)})'),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='grey', 
                      markersize=7, alpha=0.4, label=f'Unsuccessful ({len(unsuccessful_passes)})')
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        return len(successful_passes), len(unsuccessful_passes), len(progressive_passes)
    
    def create_dribbles_dots_map(self, player_name: str, ax, title_suffix=""):
        """Create dribbles map with dots"""
        pitch = Pitch(pitch_color='white', line_color='black', linewidth=2, pitch_length=105, pitch_width=68)
        pitch.draw(ax=ax)
        
        player_events = self.get_player_events(player_name)
        dribble_events = player_events[player_events['label_action'].isin(self.dribble_actions)]
        
        successful_dribbles = dribble_events[
            (dribble_events['label_action'] == 'Dribbling successful') |
            (dribble_events['label_action'] == 'Take on successful')
        ]
        
        unsuccessful_dribbles = dribble_events[
            (dribble_events['label_action'] == 'Dribbling unsuccessful') |
            (dribble_events['label_action'] == 'Take on unsuccessful')
        ]
        
        # Draw dots for dribbles with consistent size
        for _, event in unsuccessful_dribbles.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='#FF4444', s=100, alpha=0.7, marker='x', 
                      linewidths=3, zorder=2, edgecolors='black')
            
        for _, event in successful_dribbles.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='#4444FF', s=100, alpha=1.0, marker='o', 
                      zorder=3, edgecolors='black', linewidths=2)
        
        ax.set_title(f'{player_name} - Dribbles Map{title_suffix}', 
                    fontsize=12, fontweight='bold', color='black', pad=15)
        
        legend_elements = [
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4444FF', 
                      markersize=10, alpha=0.8, label=f'Successful ({len(successful_dribbles)})',
                      markeredgecolor='darkblue', markeredgewidth=2),
            plt.Line2D([0], [0], marker='x', color='#FF4444', markersize=10, 
                      alpha=0.7, label=f'Unsuccessful ({len(unsuccessful_dribbles)})', 
                      linestyle='None', markeredgewidth=3)
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        return len(successful_dribbles), len(unsuccessful_dribbles)
    
    def create_defensive_dots_map(self, player_name: str, ax, title_suffix=""):
        """Create defensive actions map with separated legend for each action type"""
        pitch = Pitch(pitch_color='white', line_color='black', linewidth=2, pitch_length=105, pitch_width=68)
        pitch.draw(ax=ax)
        
        player_events = self.get_player_events(player_name)
        defensive_events = player_events[player_events['label_action'].isin(self.defensive_actions)]
        
        # Separate by action type
        interceptions = defensive_events[defensive_events['label_action'] == 'Interceptions']
        ball_recoveries = defensive_events[defensive_events['label_action'] == 'Ball recoveries']
        tackles_successful = defensive_events[defensive_events['label_action'] == 'Tackles successful']
        challenges_won = defensive_events[defensive_events['label_action'] == 'Challenges won']
        clearances = defensive_events[defensive_events['label_action'] == 'Clearances']
        
        # Draw different colored dots for each action type
        colors = ['red', 'green', 'orange', 'blue', 'purple']
        action_types = [
            (interceptions, 'Interceptions', 'red'),
            (ball_recoveries, 'Ball Recovery', 'green'), 
            (tackles_successful, 'Tackles', 'orange'),
            (challenges_won, 'Challenges', 'blue'),
            (clearances, 'Clearances', 'purple')
        ]
        
        legend_elements = []
        
        for events, label, color in action_types:
            if len(events) > 0:
                for _, event in events.iterrows():
                    x, y = event['label_pos_x'], event['label_pos_y']
                    ax.scatter(x, y, c=color, s=100, alpha=0.8, marker='o', 
                              zorder=3, edgecolors='black', linewidths=1)
                
                legend_elements.append(
                    plt.Line2D([0], [0], marker='o', color='w', markerfacecolor=color, 
                              markersize=8, alpha=0.8, label=label,
                              markeredgecolor='black', markeredgewidth=1)
                )
        
        ax.set_title('Defensive Actions', fontsize=12, fontweight='bold', color='black', pad=15)
        
        if legend_elements:
            ax.legend(handles=legend_elements, loc='upper right', fontsize=9)
        
        return len(defensive_events)
    
    def create_shot_map(self, player_name: str, ax, title_suffix=""):
        """Create shot map with stars for goals, X for off-target, dots for on-target"""
        pitch = Pitch(pitch_color='white', line_color='black', linewidth=2, pitch_length=105, pitch_width=68)
        pitch.draw(ax=ax)
        
        player_events = self.get_player_events(player_name)
        
        # Get shooting events
        goals = player_events[player_events['label_action'] == 'Goals']
        all_shots_on_target = player_events[player_events['label_action'] == 'Shots on target']
        shots_off_target = player_events[player_events['label_action'] == 'Shots off target']
        
        # Remove shots on target that are also goals (same time and position)
        shots_on_target = []
        for _, shot in all_shots_on_target.iterrows():
            is_also_goal = False
            for _, goal in goals.iterrows():
                if (abs(shot['start_time'] - goal['start_time']) < 1 and 
                    abs(shot['label_pos_x'] - goal['label_pos_x']) < 0.1 and 
                    abs(shot['label_pos_y'] - goal['label_pos_y']) < 0.1):
                    is_also_goal = True
                    break
            if not is_also_goal:
                shots_on_target.append(shot)
        
        # Convert back to DataFrame-like structure for iteration
        import pandas as pd
        if shots_on_target:
            shots_on_target = pd.DataFrame(shots_on_target)
        else:
            shots_on_target = pd.DataFrame()  # Empty DataFrame
        
        # Draw shots off target (X markers) - keep scatter for X shape
        for _, event in shots_off_target.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='#FF4444', s=120, alpha=0.8, marker='x', 
                      linewidths=4, zorder=2, edgecolors='black')
        
        # Draw shots on target (dots) - use consistent size
        for _, event in shots_on_target.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='#4444FF', s=100, alpha=0.8, marker='o', 
                      zorder=3, edgecolors='black', linewidths=2)
        
        # Draw goals (stars) - keep scatter for star shape
        for _, event in goals.iterrows():
            x, y = event['label_pos_x'], event['label_pos_y']
            ax.scatter(x, y, c='gold', s=200, alpha=1.0, marker='*', 
                      zorder=4, edgecolors='black', linewidths=2)
        
        ax.set_title(f'{player_name} - Shot Map{title_suffix}', 
                    fontsize=12, fontweight='bold', color='black', pad=15)
        
        legend_elements = [
            plt.Line2D([0], [0], marker='*', color='w', markerfacecolor='gold', 
                      markersize=15, alpha=1.0, label=f'Goals ({len(goals)})',
                      markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='o', color='w', markerfacecolor='#4444FF', 
                      markersize=10, alpha=0.8, label=f'On Target ({len(shots_on_target)})',
                      markeredgecolor='black', markeredgewidth=2),
            plt.Line2D([0], [0], marker='x', color='#FF4444', markersize=12, 
                      alpha=0.8, label=f'Off Target ({len(shots_off_target)})', 
                      linestyle='None', markeredgewidth=4)
        ]
        ax.legend(handles=legend_elements, loc='upper left', fontsize=9)
        
        return len(goals), len(shots_on_target), len(shots_off_target)
    
    def create_heatmap(self, player_name: str, ax, title_suffix=""):
        """Create activity heatmap with gaussian filter and white-to-blue design"""
        # Keep regular pitch format but use your heatmap design
        pitch_heat = Pitch(pitch_color='white', line_color='black', linewidth=2, pitch_length=105, pitch_width=68, line_zorder=2)
        pitch_heat.draw(ax=ax)
        
        player_events = self.get_player_events(player_name)
        
        if len(player_events) < 5:  # Not enough data for heatmap
            ax.text(52.5, 34, 'Insufficient data\nfor heatmap', 
                   ha='center', va='center', fontsize=12, color='black',
                   bbox=dict(boxstyle="round,pad=0.5", facecolor='lightgray'))
            ax.set_title('Heatmap', fontsize=16, color='black')
            return
        
        # Get positions (keep original coordinate system)
        x_coords = player_events['label_pos_x'].values
        y_coords = player_events['label_pos_y'].values
        
        # Create white to darkblue colormap exactly like your example
        cmap_heat = LinearSegmentedColormap.from_list("white_to_darkblue", ["white", "blue"])
        
        # Create bin statistic with same parameters as your example
        bin_stat = pitch_heat.bin_statistic(x_coords, y_coords, statistic='count', bins=(20, 20))
        
        # Apply Gaussian filter exactly like your example
        bin_stat['statistic'] = gaussian_filter(bin_stat['statistic'], 1)
        
        # Create heatmap with white edges exactly like your example
        pitch_heat.heatmap(bin_stat, ax=ax, cmap=cmap_heat, edgecolors='white')
        
        # Set title exactly like your example
        ax.set_title('Heatmap', fontsize=16, color='black')
        
        return len(player_events)
    
    def create_involvement_line_chart(self, player_name: str, ax, title_suffix=""):
        """Create player involvement line chart with 5-minute intervals"""
        player_events = self.get_player_events(player_name)
        if len(player_events) == 0:
            ax.text(0.5, 0.5, 'No data available for this player', 
                   transform=ax.transAxes, ha='center', va='center', fontsize=12)
            return [], []
            
        player_team = player_events['label_team'].iloc[0]
        team_events = self.df[self.df['label_team'] == player_team]
        
        # Get unique players in the team
        team_players = set()
        for code in team_events['code'].dropna():
            if ' - ' in code and '.' in code and '(' in code:
                player_part = code.split(' - ')[0]
                player_name_extracted = player_part.split('.', 1)[1].split('(')[0].strip()
                if player_name_extracted and player_name_extracted != 'None':
                    team_players.add(player_name_extracted)
        
        # Calculate actions per 5-minute intervals
        max_time = max(self.df['start_time'].max(), 5400)  # At least 90 minutes
        intervals = [(i, i+300) for i in range(0, int(max_time), 300)]  # 5-minute intervals
        interval_labels = [f'{i//60}' for i in range(0, int(max_time), 300)]
        
        player_actions = []
        team_avg_actions = []
        
        for start, end in intervals:
            # Player actions in this interval
            player_interval = player_events[
                (player_events['start_time'] >= start) & 
                (player_events['start_time'] < end)
            ]
            player_count = len(player_interval)
            player_actions.append(player_count)
            
            # Team average actions in this interval
            team_interval = team_events[
                (team_events['start_time'] >= start) & 
                (team_events['start_time'] < end)
            ]
            team_avg = len(team_interval) / len(team_players) if team_players else 0
            team_avg_actions.append(team_avg)
        
        x = np.arange(len(interval_labels))
        
        # Create line chart with dots - black and blue lines
        ax.plot(x, player_actions, 'o-', color='black', linewidth=2, markersize=6, 
                label=player_name, alpha=0.8)
        ax.plot(x, team_avg_actions, 'o-', color='blue', linewidth=2, markersize=6, 
                label='Team Average', alpha=0.8)
        
        ax.set_xlabel('Minutes', fontweight='bold', color='black', fontsize=11)
        ax.set_ylabel('Number of Actions', fontweight='bold', color='black', fontsize=11)
        ax.set_title(f'{player_name} - Player Involvement (Actions per 5 Minutes){title_suffix}', 
                    fontsize=12, fontweight='bold', color='black', pad=15)
        ax.set_xticks(x[::2])  # Show every other label to avoid crowding
        ax.set_xticklabels(interval_labels[::2])
        ax.legend(fontsize=10)
        ax.grid(True, alpha=0.3, linestyle='--')
        
        # Enhanced styling
        ax.set_facecolor('white')
        ax.spines['top'].set_visible(False)
        ax.spines['right'].set_visible(False)
        
        return player_actions, team_avg_actions
    
    def generate_complete_report(self, player_name: str, output_file: str = None):
        """Generate complete corrected player report with performance summary"""
        if output_file is None:
            output_file = f"{player_name.replace(' ', '_')}_corrected_report.png"
        
        # Create figure with enhanced layout
        plt.style.use('default')
        fig = plt.figure(figsize=(24, 18))
        fig.patch.set_facecolor('white')
        
        # Create 3x2 grid layout + smaller summary area with minimal spacing
        gs = fig.add_gridspec(4, 3, height_ratios=[1.2, 1.2, 1.2, 0.4], width_ratios=[1, 1, 1],
                             hspace=0.25, wspace=0.25)
        
        # Create subplots
        ax1 = fig.add_subplot(gs[0, 0])  # Passes map
        ax2 = fig.add_subplot(gs[0, 1])  # Dribbles map  
        ax3 = fig.add_subplot(gs[0, 2])  # Defensive actions map
        ax4 = fig.add_subplot(gs[1, 0])  # Shot map
        ax5 = fig.add_subplot(gs[1, 1])  # Heatmap
        ax6 = fig.add_subplot(gs[1, 2])  # Player involvement line chart
        
        # Calculate effective time first
        player_events = self.get_player_events(player_name)
        if len(player_events) > 0:
            first_action_time = player_events['start_time'].min()
            last_action_time = player_events['start_time'].max()
            start_time = 0 if first_action_time <= 600 else first_action_time
            effective_time = int((last_action_time - start_time) / 60)
        else:
            effective_time = 0
        
        # Generate all visualizations
        pass_stats = self.create_passes_dots_map(player_name, ax1)
        dribble_stats = self.create_dribbles_dots_map(player_name, ax2)
        defensive_count = self.create_defensive_dots_map(player_name, ax3)
        shot_stats = self.create_shot_map(player_name, ax4)
        self.create_heatmap(player_name, ax5)
        self.create_involvement_line_chart(player_name, ax6)
        
        # Add main title with effective time - move higher for more space
        fig.suptitle(f'{player_name.upper()} - REPORT\nEffective Time - {effective_time} Minutes', 
                    fontsize=24, fontweight='bold', color='black', y=0.97)
        
        # Create Performance Summary panel (spans full width)
        summary_ax = fig.add_subplot(gs[2:, :])
        summary_ax.axis('off')
        
        # We already calculated effective_time above, so just get player_events for other calculations
        # (removed duplicate calculation)
        
        # Create detailed performance summary with better formatting
        # Calculate additional stats for new format
        total_passes = pass_stats[0] + pass_stats[1]  # successful + unsuccessful
        total_shots = shot_stats[0] + shot_stats[1] + shot_stats[2]  # goals + on target + off target
        total_dribbles = dribble_stats[0] + dribble_stats[1]  # successful + unsuccessful
        
        # Get specific defensive actions for new breakdown
        player_events = self.get_player_events(player_name)
        challenges = player_events[player_events['label_action'].isin(['Challenges won', 'Challenges unsuccessful'])]
        challenges_won = len(player_events[player_events['label_action'] == 'Challenges won'])
        ball_recoveries = len(player_events[player_events['label_action'] == 'Ball recoveries'])
        
        # Calculate ball recoveries in opponent half (assuming x > 50 is opponent half)
        ball_recoveries_opp_half = len(player_events[
            (player_events['label_action'] == 'Ball recoveries') & 
            (player_events['label_pos_x'] > 50)
        ])
        
        performance_text = f"""COMPREHENSIVE PERFORMANCE SUMMARY
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

PASSING                          ATTACKING                        DEFENDING
Total Passes             {total_passes:>3}     Total Shots          {total_shots:>3}     Total Defensive Actions  {defensive_count:>3}
Accurate Passes          {pass_stats[0]:>3}     Shots on Target      {shot_stats[1]:>3}     Challenges               {len(challenges):>3}
Success Rate         {(pass_stats[0]/(max(total_passes, 1))*100):>6.1f}%     Shot Rate %      {(shot_stats[1]/(max(total_shots, 1))*100):>6.1f}%     Success Rate         {(challenges_won/(max(len(challenges), 1))*100):>6.1f}%
Progressive Passes       {pass_stats[2]:>3}     Dribbles             {total_dribbles:>3}     Ball Recoveries          {ball_recoveries:>3}
                                 Successful Dribbles  {dribble_stats[0]:>3}     Ball Recoveries Opp Half {ball_recoveries_opp_half:>3}
Success Rate %   {(dribble_stats[0]/(max(total_dribbles, 1))*100):>6.1f}%

KEY INSIGHTS
• Position maps show actual event locations with accurate visualization
• Heatmap reveals movement patterns and field positioning
• Performance tracked in 5-minute intervals for detailed analysis"""
        
        summary_ax.text(0.5, 0.5, performance_text, fontsize=11, color='black', 
                       ha='center', va='center', 
                       bbox=dict(boxstyle="round,pad=1.2", facecolor='#f8f9fa', 
                                edgecolor='#dee2e6', linewidth=2),
                       family='monospace')
        
        plt.tight_layout()
        plt.savefig(output_file, dpi=300, bbox_inches='tight', facecolor='white')
        # plt.show()
        
        print(f"Corrected player report saved as: {output_file}")
        return output_file

# Main execution
if __name__ == "__main__":
    import sys
    
    generator = PlayerReport("match_events.csv")
    
    if len(sys.argv) > 1:
        # Player name provided as argument
        player_name = sys.argv[1]
        available_players = generator.get_player_list()
        if player_name in available_players:
            print(f"Generating report for: {player_name}")
            generator.generate_complete_report(player_name)
        else:
            print(f"Player '{player_name}' not found.")
            print("Available players:", ", ".join(available_players))
    else:
        # Show available players and generate sample
        print("PLAYER REPORT GENERATOR")
        print("="*40)
        print("\nAvailable players:")
        
        all_players = generator.get_player_list()
        for i, player in enumerate(all_players):
            print(f"{i+1:2d}. {player}")
        
        if all_players:
            selected_player = "Avihai Wodaje"  # Default sample
            print(f"\nGenerating sample report for: {selected_player}")
            print(f"Usage: python player_report.py \"Player Name\"")
            generator.generate_complete_report(selected_player)