"""
Output Comparator

Parses and compares test output files (XML/HTML) with expected results.
"""

import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Dict, Any
from bs4 import BeautifulSoup


class OutputComparator:
    """Compares test output with expected results"""
    
    def __init__(self, output_path: str):
        self.output_path = Path(output_path)
        self.result = self._parse_output()
    
    def _parse_output(self) -> Dict[str, Any]:
        """Parse the test output file"""
        if self.output_path.suffix == '.xml':
            return self._parse_xml()
        elif self.output_path.suffix == '.html':
            return self._parse_html()
        else:
            return {'status': 'unknown', 'message': 'Unsupported format'}
    
    def _parse_xml(self) -> Dict[str, Any]:
        """Parse JUnit XML output"""
        try:
            tree = ET.parse(self.output_path)
            root = tree.getroot()
            
            # Extract test case info
            testcase = root.find('.//testcase')
            if testcase is not None:
                status = 'passed'
                message = ''
                
                # Check for failure
                failure = testcase.find('failure')
                if failure is not None:
                    status = 'failed'
                    message = failure.get('message', '')
                
                return {
                    'status': status,
                    'name': testcase.get('name', ''),
                    'time': testcase.get('time', ''),
                    'message': message
                }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
        
        return {'status': 'unknown'}
    
    def _parse_html(self) -> Dict[str, Any]:
        """Parse HTML test report"""
        try:
            with open(self.output_path, 'r') as f:
                soup = BeautifulSoup(f.read(), 'html.parser')
            
            # Look for pass/fail indicators
            if soup.find(string=lambda text: 'FAILED' in text if text else False):
                status = 'failed'
            elif soup.find(string=lambda text: 'PASSED' in text if text else False):
                status = 'passed'
            else:
                status = 'unknown'
            
            return {
                'status': status,
                'source': 'html'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def get_result(self) -> Dict[str, Any]:
        """Get the parsed result"""
        return self.result
