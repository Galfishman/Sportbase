import xml.etree.ElementTree as ET
from typing import Dict, List, Optional
import json
import csv
import pandas as pd

class InstatEventParser:
    def __init__(self, xml_file_path: str):
        self.xml_file_path = xml_file_path
        self.tree = None
        self.root = None
        self.events = []
        
    def parse_xml(self):
        """Parse the XML file and extract all events"""
        try:
            self.tree = ET.parse(self.xml_file_path)
            self.root = self.tree.getroot()
            print(f"Successfully loaded XML file: {self.xml_file_path}")
            return True
        except ET.ParseError as e:
            print(f"Error parsing XML: {e}")
            return False
        except FileNotFoundError:
            print(f"File not found: {self.xml_file_path}")
            return False
    
    def extract_events(self):
        """Extract all event instances from the XML"""
        if not self.root:
            print("XML not loaded. Call parse_xml() first.")
            return
        
        instances = self.root.find('.//ALL_INSTANCES')
        if instances is None:
            print("No ALL_INSTANCES found in XML")
            return
        
        self.events = []
        for instance in instances.findall('instance'):
            event = self._parse_instance(instance)
            if event:
                self.events.append(event)
        
        print(f"Extracted {len(self.events)} events")
        return self.events
    
    def _parse_instance(self, instance) -> Optional[Dict]:
        """Parse a single event instance"""
        event = {}
        
        # Extract basic info
        id_elem = instance.find('ID')
        start_elem = instance.find('start')
        end_elem = instance.find('end')
        code_elem = instance.find('code')
        
        if id_elem is not None:
            event['id'] = int(id_elem.text)
        if start_elem is not None:
            event['start_time'] = float(start_elem.text)
        if end_elem is not None:
            event['end_time'] = float(end_elem.text)
        if code_elem is not None:
            event['code'] = code_elem.text
        
        # Extract labels
        labels = {}
        for label in instance.findall('label'):
            group_elem = label.find('group')
            text_elem = label.find('text')
            if group_elem is not None and text_elem is not None:
                group = group_elem.text
                text = text_elem.text
                labels[group] = text
        
        event['labels'] = labels
        return event
    
    def get_events_by_action(self, action_type: str) -> List[Dict]:
        """Get all events of a specific action type"""
        return [event for event in self.events 
                if event.get('labels', {}).get('Action') == action_type]
    
    def get_events_by_team(self, team_name: str) -> List[Dict]:
        """Get all events for a specific team"""
        return [event for event in self.events 
                if team_name in event.get('labels', {}).get('Team', '')]
    
    def get_events_by_half(self, half: str) -> List[Dict]:
        """Get all events from a specific half"""
        return [event for event in self.events 
                if event.get('labels', {}).get('Half') == half]
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics of the match"""
        if not self.events:
            return {}
        
        stats = {
            'total_events': len(self.events),
            'teams': set(),
            'actions': {},
            'halves': {},
            'time_range': {'start': float('inf'), 'end': 0}
        }
        
        for event in self.events:
            labels = event.get('labels', {})
            
            # Collect teams
            team = labels.get('Team')
            if team and team != 'None':
                stats['teams'].add(team)
            
            # Count actions
            action = labels.get('Action')
            if action:
                stats['actions'][action] = stats['actions'].get(action, 0) + 1
            
            # Count by half
            half = labels.get('Half')
            if half:
                stats['halves'][half] = stats['halves'].get(half, 0) + 1
            
            # Track time range
            if 'start_time' in event:
                stats['time_range']['start'] = min(stats['time_range']['start'], event['start_time'])
                stats['time_range']['end'] = max(stats['time_range']['end'], event['end_time'])
        
        stats['teams'] = list(stats['teams'])
        return stats
    
    def export_to_json(self, output_file: str):
        """Export parsed events to JSON file"""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(self.events, f, indent=2, ensure_ascii=False)
            print(f"Events exported to {output_file}")
        except Exception as e:
            print(f"Error exporting to JSON: {e}")
    
    def export_to_csv(self, output_file: str):
        """Export parsed events to CSV file"""
        try:
            if not self.events:
                print("No events to export")
                return
            
            # Flatten the nested structure for CSV
            flattened_data = []
            for event in self.events:
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
            
            # Create DataFrame and export to CSV
            df = pd.DataFrame(flattened_data)
            df.to_csv(output_file, index=False, encoding='utf-8')
            print(f"Events exported to {output_file}")
            print(f"CSV contains {len(df)} rows and {len(df.columns)} columns")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def export_to_simple_csv(self, output_file: str):
        """Export parsed events to a simple CSV file without pandas"""
        try:
            if not self.events:
                print("No events to export")
                return
            
            # Get all unique label keys to create headers
            all_label_keys = set()
            for event in self.events:
                labels = event.get('labels', {})
                all_label_keys.update(labels.keys())
            
            # Create headers
            headers = ['id', 'start_time', 'end_time', 'code']
            label_headers = [f'label_{key.lower()}' for key in sorted(all_label_keys)]
            headers.extend(label_headers)
            
            with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)
                
                for event in self.events:
                    row = [
                        event.get('id', ''),
                        event.get('start_time', ''),
                        event.get('end_time', ''),
                        event.get('code', '')
                    ]
                    
                    labels = event.get('labels', {})
                    for key in sorted(all_label_keys):
                        row.append(labels.get(key, ''))
                    
                    writer.writerow(row)
            
            print(f"Events exported to {output_file}")
            print(f"CSV contains {len(self.events)} rows and {len(headers)} columns")
            
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
    
    def print_sample_events(self, count: int = 5):
        """Print a sample of events for inspection"""
        print(f"\nFirst {count} events:")
        for i, event in enumerate(self.events[:count]):
            print(f"\nEvent {i+1}:")
            print(f"  ID: {event.get('id')}")
            print(f"  Time: {event.get('start_time')}-{event.get('end_time')}")
            print(f"  Code: {event.get('code')}")
            print("  Labels:")
            for key, value in event.get('labels', {}).items():
                print(f"    {key}: {value}")

# Main execution
if __name__ == "__main__":
    xml_file = "Bnei Yehuda Tel-Aviv 2-3 Hapoel Kfar Shalem 31.08.2025, Full match.xml"
    
    parser = InstatEventParser(xml_file)
    
    if parser.parse_xml():
        parser.extract_events()
        
        # Display summary stats
        stats = parser.get_summary_stats()
        print("\n" + "="*50)
        print("MATCH SUMMARY")
        print("="*50)
        print(f"Total Events: {stats['total_events']}")
        print(f"Teams: {', '.join(stats['teams'])}")
        print(f"Time Range: {stats['time_range']['start']:.2f} - {stats['time_range']['end']:.2f}")
        
        print(f"\nEvents by Half:")
        for half, count in stats['halves'].items():
            print(f"  Half {half}: {count} events")
        
        print(f"\nTop 10 Actions:")
        sorted_actions = sorted(stats['actions'].items(), key=lambda x: x[1], reverse=True)
        for action, count in sorted_actions[:10]:
            print(f"  {action}: {count}")
        
        # Show sample events
        parser.print_sample_events()
        
        # Export to JSON and CSV
        parser.export_to_json("match_events.json")
        parser.export_to_simple_csv("match_events.csv")
        
        print(f"\n" + "="*50)
        print("Files created:")
        print("- match_events.json (structured data)")
        print("- match_events.csv (tabular data)")
        print("\nParser ready! You can now use methods like:")
        print("- parser.get_events_by_action('Passes accurate')")
        print("- parser.get_events_by_team('Bnei Yehuda Tel-Aviv')")
        print("- parser.get_events_by_half('1')")