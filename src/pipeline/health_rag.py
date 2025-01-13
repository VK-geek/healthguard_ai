import pathway as pw
from sentence_transformers import SentenceTransformer
import openai
from typing import Dict, List, Optional
import os
from dotenv import load_dotenv
import json
from pathlib import Path

# Load environment variables
load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")

class HealthRAGPipeline:
    def __init__(self):
        self.embedder = SentenceTransformer('all-MiniLM-L6-v2')
        self.knowledge_base = self._load_knowledge_base()
        
    def _load_knowledge_base(self) -> List[Dict]:
        """Load and embed health guidelines."""
        base_path = Path(__file__).parent.parent.parent
        guidelines_path = base_path / 'data' / 'knowledge_base' / 'health_guidelines.txt'
        
        with open(guidelines_path, 'r') as f:
            guidelines = f.readlines()
        
        # Clean and filter guidelines
        guidelines = [g.strip() for g in guidelines if g.strip()]
        
        # Embed guidelines
        embeddings = self.embedder.encode(guidelines)
        return [
            {"text": text, "embedding": emb} 
            for text, emb in zip(guidelines, embeddings)
        ]
    
    def get_relevant_guidelines(self, metrics: Dict) -> List[str]:
        """Get relevant health guidelines based on current metrics."""
        query = self._metrics_to_query(metrics)
        query_embedding = self.embedder.encode(query)
        
        # Find most relevant guidelines using cosine similarity
        similarities = [
            pw.cosine_similarity(query_embedding, item["embedding"])
            for item in self.knowledge_base
        ]
        
        # Get top 3 most relevant guidelines
        top_indices = sorted(range(len(similarities)), 
                           key=lambda i: similarities[i], 
                           reverse=True)[:3]
        return [self.knowledge_base[i]["text"] for i in top_indices]
    
    def _metrics_to_query(self, metrics: Dict) -> str:
        """Convert metrics to a natural language query."""
        return f"""
        What health advice is relevant for someone with:
        - Heart rate: {metrics.get('heart_rate', 'N/A')} bpm
        - SpO2: {metrics.get('spo2', 'N/A')}%
        - Steps: {metrics.get('steps', 'N/A')} steps
        """
    
    def generate_insights(self, metrics: Dict) -> Dict:
        """Generate health insights using RAG."""
        # Get relevant guidelines
        guidelines = self.get_relevant_guidelines(metrics)
        
        # Prepare prompt with metrics and guidelines
        prompt = f"""
        Based on the following health metrics and relevant guidelines, provide personalized health insights and recommendations.

        Current Metrics:
        - Heart Rate: {metrics.get('heart_rate', 'N/A')} bpm
        - SpO2: {metrics.get('spo2', 'N/A')}%
        - Steps: {metrics.get('steps', 'N/A')} steps

        Relevant Health Guidelines:
        {chr(10).join(f'- {g}' for g in guidelines)}

        Please provide:
        1. A brief analysis of the metrics
        2. Health status assessment
        3. Personalized recommendations
        """

        # Generate insights using OpenAI
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a health monitoring AI assistant providing personalized insights based on real-time health metrics."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        
        return {
            "analysis": response.choices[0].message.content,
            "relevant_guidelines": guidelines,
            "metrics_summary": metrics
        }

def run_pipeline():
    """Initialize and run the health RAG pipeline."""
    # Initialize pipeline
    pipeline = HealthRAGPipeline()
    
    # Set up document input
    docs = pw.io.fs.read(
        "data/knowledge_base/*.txt",
        format="text",
        with_metadata=True
    )
    
    # Process documents
    embedded_chunks = pipeline.process_documents(docs)
    
    # Set up query handling
    queries = pw.io.http.rest_connector(
        host="0.0.0.0",
        port=8080,
        endpoint="/query"
    )
    
    # Process queries and generate responses
    responses = pipeline.process_health_query(queries, embedded_chunks)
    
    # Output responses
    responses.output(pw.io.http.response_stream())
    
    # Run the pipeline
    pw.run()

if __name__ == "__main__":
    run_pipeline()
