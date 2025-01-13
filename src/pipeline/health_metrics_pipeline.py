import pathway as pw
from pathway.stdlib.utils.col import unpack_col
import json
from datetime import datetime

class HealthMetricsProcessor:
    def __init__(self):
        self.schema = {
            "heart_rate": pw.column_definition(int),
            "spo2": pw.column_definition(int),
            "steps": pw.column_definition(int),
            "timestamp": pw.column_definition(str)
        }

    def process_metrics(self, input_stream):
        """Process real-time health metrics stream."""
        return input_stream.select(
            pw.this.data.map(json.loads)
        ).select(
            unpack_col("data", self.schema)
        ).select(
            heart_rate=pw.this.heart_rate,
            spo2=pw.this.spo2,
            steps=pw.this.steps,
            timestamp=pw.this.timestamp,
            # Add computed metrics
            heart_rate_status=pw.case(
                (pw.this.heart_rate < 60, "Low"),
                (pw.this.heart_rate > 100, "High"),
                default="Normal"
            ),
            spo2_status=pw.case(
                (pw.this.spo2 < 95, "Low"),
                default="Normal"
            ),
            activity_level=pw.case(
                (pw.this.steps < 5000, "Low"),
                (pw.this.steps < 10000, "Moderate"),
                default="High"
            )
        )

    def compute_trends(self, metrics_table, window_size="1h"):
        """Compute health metric trends over time."""
        return metrics_table.groupby(
            pw.tumbling_window(pw.this.timestamp, window_size)
        ).reduce(
            window_start=pw.reducers.min(pw.this.timestamp),
            window_end=pw.reducers.max(pw.this.timestamp),
            avg_heart_rate=pw.reducers.avg(pw.this.heart_rate),
            min_heart_rate=pw.reducers.min(pw.this.heart_rate),
            max_heart_rate=pw.reducers.max(pw.this.heart_rate),
            avg_spo2=pw.reducers.avg(pw.this.spo2),
            min_spo2=pw.reducers.min(pw.this.spo2),
            total_steps=pw.reducers.sum(pw.this.steps)
        )

def run_pipeline():
    """Initialize and run the health metrics pipeline."""
    # Initialize processor
    processor = HealthMetricsProcessor()
    
    # Set up input stream from REST API
    input_stream = pw.io.http.rest_connector(
        host="0.0.0.0",
        port=8000,
        endpoint="/metrics",
        method="POST"
    )
    
    # Process real-time metrics
    metrics = processor.process_metrics(input_stream)
    
    # Compute trends
    hourly_trends = processor.compute_trends(metrics, "1h")
    daily_trends = processor.compute_trends(metrics, "24h")
    
    # Output processed metrics and trends
    metrics.output(
        pw.io.http.response_stream(),
        host="0.0.0.0",
        port=8001,
        endpoint="/processed_metrics"
    )
    
    hourly_trends.output(
        pw.io.http.response_stream(),
        host="0.0.0.0",
        port=8001,
        endpoint="/hourly_trends"
    )
    
    daily_trends.output(
        pw.io.http.response_stream(),
        host="0.0.0.0",
        port=8001,
        endpoint="/daily_trends"
    )
    
    # Run the pipeline
    pw.run()

if __name__ == "__main__":
    run_pipeline()
