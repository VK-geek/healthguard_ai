import pathway as pw
from pathway.xpacks.llm import LLMPack, OpenAIChatModel
from pathway.xpacks.llm.embedders import OpenAIEmbedder
import os
from dotenv import load_dotenv
from typing import Dict, Any
import json

# Load environment variables
load_dotenv()

class HealthRAGPipeline:
    def __init__(self):
        self.llm_pack = LLMPack(
            embedder=OpenAIEmbedder(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="text-embedding-ada-002"
            ),
            model=OpenAIChatModel(
                api_key=os.getenv("OPENAI_API_KEY"),
                model="gpt-3.5-turbo"
            )
        )
        
        # Load and embed health guidelines
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> pw.Table:
        """Load health guidelines and create embeddings."""
        guidelines_path = os.path.join(
            os.path.dirname(__file__), 
            "..", "..", "data", "knowledge_base", "health_guidelines.txt"
        )
        
        with open(guidelines_path, 'r') as f:
            guidelines = f.read().split('\n\n')  # Split by double newline
        
        # Create a Pathway table with the guidelines
        return pw.debug.table_from_markdown(
            '''
            | id | content |
            | -- | ------- |
            ''' + '\n'.join([
                f'| {i} | {g.replace("|", "\\|")} |' 
                for i, g in enumerate(guidelines) if g.strip()
            ])
        )
    
    def _analyze_metrics(self, metrics: Dict[str, Any]) -> Dict[str, Dict[str, str]]:
        """Analyze health metrics and determine status."""
        status = {}
        
        # Heart Rate Analysis
        hr = metrics['heart_rate']
        if hr < 60:
            status['heart_rate'] = {
                'status': 'low',
                'message': 'Your heart rate is below normal range. Take it easy and monitor how you feel.'
            }
        elif hr > 100:
            status['heart_rate'] = {
                'status': 'high',
                'message': 'Your heart rate is elevated. Consider taking a break and practicing deep breathing.'
            }
        else:
            status['heart_rate'] = {
                'status': 'normal',
                'message': 'Your heart rate is within a healthy range.'
            }
        
        # SpO2 Analysis
        spo2 = metrics['spo2']
        if spo2 < 95:
            status['spo2'] = {
                'status': 'low',
                'message': 'Your blood oxygen level is lower than optimal. Try taking deep breaths.'
            }
        else:
            status['spo2'] = {
                'status': 'normal',
                'message': 'Your blood oxygen level is good.'
            }
        
        # Steps Analysis
        steps = metrics['steps']
        if steps >= 10000:
            status['steps'] = {
                'status': 'excellent',
                'message': 'Great job! You’ve reached your daily step goal!'
            }
        elif steps >= 7500:
            status['steps'] = {
                'status': 'good',
                'message': 'You’re making good progress on your steps today.'
            }
        elif steps >= 5000:
            status['steps'] = {
                'status': 'fair',
                'message': 'You’re halfway to your daily step goal.'
            }
        else:
            status['steps'] = {
                'status': 'low',
                'message': 'Try to move a bit more today to reach your step goal.'
            }
        
        return status
    
    def generate_insights(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Generate personalized health insights using RAG."""
        # Create context from metrics
        context = (
            f"Current Metrics:\n"
            f"- Heart Rate: {metrics['heart_rate']} bpm\n"
            f"- Blood Oxygen: {metrics['spo2']}%\n"
            f"- Steps Today: {metrics['steps']}\n\n"
        )
        
        # Analyze metrics
        status = self._analyze_metrics(metrics)
        
        # Create query based on metrics and status
        query = self._create_query(metrics, status)
        
        # Get relevant guidelines using RAG
        relevant_docs = self.llm_pack.retrieve(
            self.knowledge_base,
            query=query,
            content_column="content",
            n_results=3
        )
        
        # Generate personalized analysis
        prompt = f"""
        Based on the following health metrics and relevant health guidelines, 
        provide a brief, friendly analysis and personalized recommendations.
        
        {context}
        
        Relevant Health Guidelines:
        {relevant_docs.select('content').collect()[0]}
        
        Keep the response conversational and encouraging. Focus on actionable advice.
        """
        
        analysis = self.llm_pack.generate(prompt).collect()[0]
        
        return {
            "status": status,
            "analysis": analysis,
            "relevant_guidelines": relevant_docs.select("content").collect()
        }
    
    def _create_query(self, metrics: Dict[str, Any], status: Dict[str, Dict[str, str]]) -> str:
        """Create a relevant query based on metrics and their status."""
        queries = []
        
        # Add queries based on status
        for metric, info in status.items():
            if info['status'] != 'normal':
                if metric == 'heart_rate':
                    queries.append(f"{info['status']} heart rate guidelines")
                elif metric == 'spo2':
                    queries.append(f"blood oxygen {info['status']} recommendations")
                elif metric == 'steps':
                    queries.append("physical activity guidelines")
        
        # If everything is normal, ask for general wellness tips
        if not queries:
            queries.append("maintaining healthy metrics guidelines")
        
        return " AND ".join(queries)

    @pw.serve_pathway_api()
    def serve_callable(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Serve the RAG pipeline as a callable API endpoint."""
        return self.generate_insights(metrics)
