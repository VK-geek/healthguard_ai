import pathway as pw
from typing import Dict, Any
import json
from datetime import datetime
from .health_rag import HealthRAGPipeline

class HealthMetricsPipeline:
    def __init__(self):
        self.rag_pipeline = HealthRAGPipeline()
    
    def process_metrics(self, metrics: Dict[str, Any]) -> pw.Table:
        """Process incoming health metrics in real-time."""
        # Convert metrics to Pathway table
        metrics_table = pw.debug.table_from_markdown(
            '''
            | timestamp | heart_rate | spo2 | steps |
            | --------- | ---------- | ---- | ----- |
            ''' + f'''
            | {datetime.now().isoformat()} | {metrics['heart_rate']} | {metrics['spo2']} | {metrics['steps']} |
            '''
        )
        
        # Apply transformations
        processed = metrics_table.select(
            timestamp=pw.this.timestamp,
            heart_rate=pw.this.heart_rate,
            spo2=pw.this.spo2,
            steps=pw.this.steps,
            # Add computed metrics
            heart_rate_status=pw.case(
                pw.this.heart_rate < 60, "low",
                pw.this.heart_rate > 100, "high",
                default="normal"
            ),
            spo2_status=pw.case(
                pw.this.spo2 < 95, "low",
                default="normal"
            ),
            steps_status=pw.case(
                pw.this.steps >= 10000, "excellent",
                pw.this.steps >= 7500, "good",
                pw.this.steps >= 5000, "fair",
                default="low"
            )
        )
        
        return processed
    
    @pw.serve_pathway_api()
    def serve_callable(self, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """Process metrics and generate insights using the RAG pipeline."""
        # Process metrics
        processed_metrics = self.process_metrics(metrics)
        
        # Generate insights using RAG
        insights = self.rag_pipeline.generate_insights(metrics)
        
        # Combine processed metrics with insights
        return {
            "processed_metrics": processed_metrics.collect()[0],
            "insights": insights
        }
