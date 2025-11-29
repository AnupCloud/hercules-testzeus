"""
Planning Log Parser

Extracts intended step-by-step actions from Hercules planning logs.
"""

import json
from pathlib import Path
from typing import List, Dict, Any


class PlanningLogParser:
    """Parses Hercules planning logs to extract planned steps"""
    
    def __init__(self, log_path: str):
        self.log_path = Path(log_path)
        self.data = self._load_log()
    
    def _load_log(self) -> Dict[str, Any]:
        """Load the planning log JSON file"""
        with open(self.log_path, 'r') as f:
            return json.load(f)
    
    def extract_steps(self) -> List[Dict[str, Any]]:
        """
        Extract planned steps from the log.
        
        Returns:
            List of dictionaries containing:
            - step_number: int
            - description: str
            - action_type: str (navigate, click, enter_text, filter, assert, etc.)
            - target: str (element or URL)
            - expected_outcome: str
        """
        steps = []
        step_number = 1
        
        # Extract from planner_agent messages
        if 'planner_agent' in self.data:
            for message in self.data['planner_agent']:
                if message.get('role') == 'assistant' and 'content' in message:
                    content = message['content']
                    
                    # Extract the plan if available
                    if isinstance(content, dict) and 'plan' in content:
                        plan_text = content['plan']
                        # Parse plan into individual steps
                        for line in plan_text.split('\\n'):
                            line = line.strip()
                            if line and (line[0].isdigit() or line.startswith('-')):
                                # Remove numbering
                                cleaned_line = line.lstrip('0123456789.-) ').strip()
                                if cleaned_line:
                                    step = self._parse_step_description(cleaned_line, step_number)
                                    steps.append(step)
                                    step_number += 1
                    
                    # Also extract detailed next_step
                    if isinstance(content, dict) and 'next_step' in content:
                        next_step = content['next_step']
                        if next_step:
                            step = self._parse_step_description(next_step, step_number)
                            step['is_next_action'] = True
                            steps.append(step)
                            step_number += 1
        
        return steps
    
    def _parse_step_description(self, description: str, step_number: int) -> Dict[str, Any]:
        """Parse a step description to extract action details"""
        description_lower = description.lower()
        
        # Determine action type
        action_type = 'unknown'
        target = ''
        
        if 'navigate' in description_lower or 'go to' in description_lower or 'open' in description_lower:
            action_type = 'navigate'
            # Extract URL if present
            import re
            url_match = re.search(r'https?://[^\s]+', description)
            if url_match:
                target = url_match.group(0)
        
        elif 'click' in description_lower:
            action_type = 'click'
            # Extract element description
            if 'search icon' in description_lower:
                target = 'Search icon'
            elif 'button' in description_lower:
                target = 'button'
        
        elif 'enter' in description_lower or 'type' in description_lower or 'input' in description_lower:
            action_type = 'enter_text'
            # Extract the text to be entered
            import re
            quote_match = re.search(r'"([^"]+)"|\'([^\']+)\'', description)
            if quote_match:
                target = quote_match.group(1) or quote_match.group(2)
        
        elif 'filter' in description_lower or 'select' in description_lower:
            action_type = 'filter'
            import re
            quote_match = re.search(r'"([^"]+)"|\'([^\']+)\'', description)
            if quote_match:
                target = quote_match.group(1) or quote_match.group(2)
        
        elif 'assert' in description_lower or 'verify' in description_lower or 'confirm' in description_lower or 'should see' in description_lower:
            action_type = 'assert'
        
        return {
            'step_number': step_number,
            'description': description,
            'action_type': action_type,
            'target': target,
            'expected_outcome': '',
            'is_next_action': False
        }
