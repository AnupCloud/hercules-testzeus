"""
Deviation Reporter

Generates deviation reports comparing planned vs observed actions.
Uses LangGraph for intelligent analysis and decision-making.
"""

from typing import List, Dict, Any, TypedDict, Annotated
from langgraph.graph import StateGraph, END
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import HumanMessage, SystemMessage
import operator


class AnalysisState(TypedDict):
    """State for the analysis workflow"""
    planned_steps: List[Dict[str, Any]]
    video_events: List[Dict[str, Any]]
    test_result: Dict[str, Any]
    current_step_index: int
    deviations: Annotated[List[Dict[str, Any]], operator.add]
    observations: Annotated[List[Dict[str, Any]], operator.add]
    summary: Dict[str, Any]


class DeviationReporter:
    """Generates deviation reports using LangGraph workflow"""
    
    def __init__(self, planned_steps: List[Dict], video_analysis: Dict, test_result: Dict, api_key: str = None):
        self.planned_steps = planned_steps
        self.video_analysis = video_analysis
        self.test_result = test_result
        self.api_key = api_key
        
        # Initialize LLM
        self.llm = ChatAnthropic(
            model="claude-3-haiku-20240307",
            api_key=api_key
        ) if api_key else None
        
        # Build the analysis graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow"""
        workflow = StateGraph(AnalysisState)
        
        # Add nodes
        workflow.add_node("initialize", self._initialize_analysis)
        workflow.add_node("analyze_step", self._analyze_step)
        workflow.add_node("compare_with_video", self._compare_with_video)
        workflow.add_node("determine_deviation", self._determine_deviation)
        workflow.add_node("finalize_report", self._finalize_report)
        
        # Add edges
        workflow.set_entry_point("initialize")
        workflow.add_edge("initialize", "analyze_step")
        workflow.add_conditional_edges(
            "analyze_step",
            self._should_continue_analysis,
            {
                "compare": "compare_with_video",
                "finalize": "finalize_report"
            }
        )
        workflow.add_edge("compare_with_video", "determine_deviation")
        workflow.add_edge("determine_deviation", "analyze_step")
        workflow.add_edge("finalize_report", END)
        
        return workflow.compile()
    
    def _initialize_analysis(self, state: AnalysisState) -> Dict:
        """Initialize the analysis state"""
        return {
            "planned_steps": self.planned_steps,
            "video_events": self.video_analysis.get('detected_events', []),
            "test_result": self.test_result,
            "current_step_index": 0,
            "deviations": [],
            "observations": [],
            "summary": {}
        }
    
    def _analyze_step(self, state: AnalysisState) -> Dict:
        """Analyze the current step"""
        idx = state["current_step_index"]
        if idx >= len(state["planned_steps"]):
            return state
        
        current_step = state["planned_steps"][idx]
        
        # Use LLM to understand the step if available
        if self.llm:
            step_analysis = self._llm_analyze_step(current_step)
            current_step['llm_analysis'] = step_analysis
        
        return {"current_step_index": idx}
    
    def _compare_with_video(self, state: AnalysisState) -> Dict:
        """Compare planned step with video evidence"""
        idx = state["current_step_index"]
        current_step = state["planned_steps"][idx]
        video_events = state["video_events"]
        
        # Find relevant video events (simplified matching)
        relevant_events = self._find_relevant_events(current_step, video_events)
        
        observation = {
            "step_number": current_step["step_number"],
            "description": current_step["description"],
            "relevant_events": relevant_events,
            "event_count": len(relevant_events)
        }
        
        return {"observations": [observation]}
    
    def _determine_deviation(self, state: AnalysisState) -> Dict:
        """Determine if there's a deviation"""
        idx = state["current_step_index"]
        current_step = state["planned_steps"][idx]
        latest_observation = state["observations"][-1] if state["observations"] else None
        
        if not latest_observation or latest_observation["event_count"] == 0:
            # No evidence found - potential deviation
            deviation = {
                "step_number": current_step["step_number"],
                "description": current_step["description"],
                "result": "❌ Deviation",
                "notes": "Step not visibly executed in video",
                "confidence": 0.8
            }
            deviations = [deviation]
        else:
            # Evidence found
            deviation = {
                "step_number": current_step["step_number"],
                "description": current_step["description"],
                "result": "✅ Observed",
                "notes": f"Detected {latest_observation['event_count']} relevant event(s)",
                "confidence": 0.7
            }
            deviations = []
        
        # Increment step index
        return {
            "deviations": deviations,
            "current_step_index": idx + 1
        }
    
    def _should_continue_analysis(self, state: AnalysisState) -> str:
        """Decide whether to continue analyzing steps"""
        if state["current_step_index"] >= len(state["planned_steps"]):
            return "finalize"
        return "compare"
    
    def _finalize_report(self, state: AnalysisState) -> Dict:
        """Finalize the deviation report"""
        total_steps = len(state["planned_steps"])
        deviation_count = len([d for d in state["deviations"]])
        observed_steps = total_steps - deviation_count
        
        summary = {
            "total_steps": total_steps,
            "observed_steps": observed_steps,
            "deviation_count": deviation_count,
            "status": "No deviations detected" if deviation_count == 0 else f"{deviation_count} deviation(s) found"
        }
        
        return {"summary": summary}
    
    def _find_relevant_events(self, step: Dict, events: List[Dict]) -> List[Dict]:
        """Find video events relevant to the step (simplified)"""
        # In a real implementation, this would use more sophisticated matching
        # For now, we'll use basic heuristics
        relevant = []
        
        action_type = step.get('action_type', 'unknown')
        
        for event in events:
            # Match based on timing and event type
            if event.get('type') == 'scene_change':
                relevant.append(event)
        
        return relevant[:2]  # Return top 2 most relevant
    
    def _llm_analyze_step(self, step: Dict) -> str:
        """Use LLM to analyze a step"""
        if not self.llm:
            return ""
        
        prompt = f"""Analyze this test step and describe what should be visible in a video recording:

Step: {step['description']}
Action Type: {step['action_type']}
Target: {step.get('target', 'N/A')}

Describe in 1-2 sentences what visual cues would confirm this step was executed."""
        
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            return response.content
        except:
            return ""
    
    def generate_report(self) -> Dict[str, Any]:
        """Generate the deviation report"""
        # Run the graph with increased recursion limit
        config = {"recursion_limit": 100}
        final_state = self.graph.invoke({
            "planned_steps": self.planned_steps,
            "video_events": self.video_analysis.get('detected_events', []),
            "test_result": self.test_result,
            "current_step_index": 0,
            "deviations": [],
            "observations": [],
            "summary": {}
        }, config=config)
        
        # Build comprehensive report
        all_results = []
        for step in self.planned_steps:
            matching_dev = next((d for d in final_state["deviations"] if d["step_number"] == step["step_number"]), None)
            if matching_dev:
                all_results.append(matching_dev)
            else:
                all_results.append({
                    "step_number": step["step_number"],
                    "description": step["description"],
                    "result": "✅ Observed",
                    "notes": "Evidence found in video",
                    "confidence": 0.7
                })
        
        return {
            "summary": final_state["summary"],
            "steps": all_results,
            "test_result": self.test_result,
            "video_analysis": {
                "video_count": self.video_analysis.get('video_count', 0),
                "total_events": self.video_analysis.get('total_events', 0)
            }
        }
    
    def format_markdown(self) -> str:
        """Format report as markdown"""
        report = self.generate_report()
        
        md = "# Test Execution Deviation Report\n\n"
        md += "## Summary\n\n"
        md += f"- **Total Steps**: {report['summary']['total_steps']}\n"
        md += f"- **Observed Steps**: {report['summary']['observed_steps']}\n"
        md += f"- **Deviations**: {report['summary']['deviation_count']}\n"
        md += f"- **Status**: {report['summary']['status']}\n\n"
        
        md += "## Detailed Results\n\n"
        md += "_Confidence Legend: 🟢 High (≥80%) | 🟡 Medium (60-79%) | 🔴 Low (<60%) | ⚪ N/A_\n\n"
        md += "| Step | Description | Result | Confidence | Notes |\n"
        md += "|------|-------------|--------|------------|-------|\n"

        for step in report['steps']:
            # Replace newlines with spaces for proper table formatting
            description = step['description'].replace('\n', ' ').replace('\r', ' ')[:50]
            confidence = step.get('confidence', 0.0)
            confidence_str = f"{confidence:.0%}" if confidence > 0 else "N/A"
            # Add visual confidence indicator
            if confidence >= 0.8:
                confidence_display = f"🟢 {confidence_str}"
            elif confidence >= 0.6:
                confidence_display = f"🟡 {confidence_str}"
            elif confidence > 0:
                confidence_display = f"🔴 {confidence_str}"
            else:
                confidence_display = "⚪ N/A"
            md += f"| {step['step_number']} | {description}... | {step['result']} | {confidence_display} | {step['notes']} |\n"
        
        md += "\n## Test Output\n\n"
        md += f"- **Status**: {report['test_result'].get('status', 'unknown')}\n"
        
        md += "\n## Video Analysis\n\n"
        md += f"- **Videos Analyzed**: {report['video_analysis']['video_count']}\n"
        md += f"- **Events Detected**: {report['video_analysis']['total_events']}\n"
        
        return md
