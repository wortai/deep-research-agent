"""
Utility functions for Gap Question Generator.
"""

import json
import os
from datetime import datetime
from urllib.parse import urlparse


def analyze_logs(session_id: str, log_dir: str = "gap_generator_logs"):
    """Analyze and display insights from logged data"""
    print(f"\n📈 Analyzing logs for session: {session_id}")
    
    try:
        # Load detailed log
        json_file = os.path.join(log_dir, f"{session_id}_detailed_log.json")
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        print("\n🔍 Analysis Results:")
        print(f"Total URLs accessed: {len(data['all_urls_accessed'])}")
        print(f"Total vector queries: {len(data['all_vector_queries'])}")
        print(f"LLM interactions: {len(data['llm_interactions'])}")
        
        # URL domain analysis
        domains = {}
        for url in data['all_urls_accessed']:
            domain = urlparse(url).netloc
            domains[domain] = domains.get(domain, 0) + 1
        
        print("\n📊 Top domains accessed:")
        for domain, count in sorted(domains.items(), key=lambda x: x[1], reverse=True)[:5]:
            print(f"  • {domain}: {count} times")
        
        # Query complexity
        print("\n📝 Query processing complexity:")
        for i, query in enumerate(data['detailed_queries'], 1):
            print(f"\nQuery {i}: {query['gap_query']}")
            print(f"  - Vector queries: {len(query['vector_queries'])}")
            print(f"  - URLs accessed: {len(query['urls_accessed'])}")
            print(f"  - Content items: {len(query['content_from_urls'])}")
            print(f"  - Insights extracted: {len(query['insights_extracted'])}")
        
        # LLM usage patterns
        print("\n🤖 LLM Usage Patterns:")
        total_prompt_chars = sum(i['prompt_length'] for i in data['llm_interactions'])
        total_response_chars = sum(i['response_length'] for i in data['llm_interactions'])
        print(f"  - Total prompt characters: {total_prompt_chars:,}")
        print(f"  - Total response characters: {total_response_chars:,}")
        print(f"  - Average response length: {total_response_chars // len(data['llm_interactions']):,} chars")
        
        # Context distribution
        context_counts = {}
        for interaction in data['llm_interactions']:
            ctx = interaction['context']
            context_counts[ctx] = context_counts.get(ctx, 0) + 1
        
        print("\n🎯 LLM Context Distribution:")
        for context, count in context_counts.items():
            print(f"  - {context}: {count} calls")
        
        return data
        
    except Exception as e:
        print(f"❌ Error analyzing logs: {e}")
        return None


def create_visualization_report(session_id: str, log_dir: str = "gap_generator_logs") -> str:
    """Create an HTML visualization report"""
    try:
        json_file = os.path.join(log_dir, f"{session_id}_detailed_log.json")
        with open(json_file, 'r') as f:
            data = json.load(f)
        
        # Calculate metrics
        domains = {}
        for url in data['all_urls_accessed']:
            domain = urlparse(url).netloc
            domains[domain] = domains.get(domain, 0) + 1
        
        # Generate HTML report
        html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Gap Generator Report - {session_id}</title>
    <script src="https://cdn.plot.ly/plotly-latest.min.js"></script>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 20px; background: #f5f5f5; }}
        .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 20px; box-shadow: 0 0 10px rgba(0,0,0,0.1); }}
        h1, h2, h3 {{ color: #333; }}
        .metric {{ display: inline-block; margin: 10px; padding: 15px; background: #e3f2fd; border-radius: 5px; }}
        .metric-value {{ font-size: 24px; font-weight: bold; color: #1976d2; }}
        .metric-label {{ font-size: 14px; color: #666; }}
        .query-box {{ background: #f9f9f9; padding: 15px; margin: 10px 0; border-left: 4px solid #2196f3; }}
        .url-list {{ max-height: 300px; overflow-y: auto; background: #fafafa; padding: 10px; }}
        table {{ width: 100%; border-collapse: collapse; margin: 20px 0; }}
        th, td {{ padding: 10px; text-align: left; border-bottom: 1px solid #ddd; }}
        th {{ background: #e3f2fd; font-weight: bold; }}
        .insight {{ background: #e8f5e9; padding: 8px; margin: 5px 0; border-radius: 3px; }}
        .chart {{ margin: 20px 0; }}
    </style>
</head>
<body>
    <div class="container">
        <h1>Gap Question Generator Analysis Report</h1>
        <p>Session: {session_id}</p>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        
        <h2>Performance Metrics</h2>
        <div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['queries_processed']}</div>
                <div class="metric-label">Queries Processed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['sources_processed']}</div>
                <div class="metric-label">Sources Processed</div>
            </div>
            <div class="metric">
                <div class="metric-value">{len(data['all_urls_accessed'])}</div>
                <div class="metric-label">Unique URLs</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['content_items_added']}</div>
                <div class="metric-label">Content Items</div>
            </div>
            <div class="metric">
                <div class="metric-value">{data['execution_results']['final_confidence']:.2%}</div>
                <div class="metric-label">Final Confidence</div>
            </div>
        </div>
        
        <h2>Processing Timeline</h2>
        <div id="timeline-chart" class="chart"></div>
        
        <h2>URL Domain Distribution</h2>
        <div id="domain-chart" class="chart"></div>
        
        <h2>Processing Steps Status</h2>
        <div id="steps-chart" class="chart"></div>
        
        <h2>Query Details</h2>
        <div id="query-details">
            <!-- Query details will be added by JavaScript -->
        </div>
    </div>
    
    <script>
        // Data preparation
        const data = {json.dumps(data)};
        
        // Timeline chart
        const timelineData = [];
        const timelineLayout = {{
            title: 'Processing Step Durations',
            xaxis: {{ title: 'Duration (ms)' }},
            yaxis: {{ title: 'Step Name' }},
            margin: {{ l: 150 }}
        }};
        
        data.processing_steps.forEach(step => {{
            if (step.status === 'completed' && step.duration_ms) {{
                timelineData.push({{
                    x: [step.duration_ms],
                    y: [step.step_name],
                    type: 'bar',
                    orientation: 'h',
                    name: step.step_name
                }});
            }}
        }});
        
        Plotly.newPlot('timeline-chart', timelineData, timelineLayout);
        
        // Domain distribution
        const domains = {json.dumps(domains)};
        const domainData = [{{
            labels: Object.keys(domains),
            values: Object.values(domains),
            type: 'pie'
        }}];
        
        Plotly.newPlot('domain-chart', domainData, {{
            title: 'URL Domain Distribution'
        }});
        
        // Step status distribution
        const statusCounts = {{ completed: 0, started: 0, error: 0 }};
        data.processing_steps.forEach(step => {{
            if (statusCounts.hasOwnProperty(step.status)) {{
                statusCounts[step.status]++;
            }}
        }});
        
        const stepsData = [{{
            x: Object.keys(statusCounts),
            y: Object.values(statusCounts),
            type: 'bar',
            marker: {{ color: ['#4caf50', '#ff9800', '#f44336'] }}
        }}];
        
        Plotly.newPlot('steps-chart', stepsData, {{
            title: 'Processing Step Status Distribution'
        }});
        
        // Query details
        const queryDetailsDiv = document.getElementById('query-details');
        data.detailed_queries.forEach((query, index) => {{
            const queryBox = document.createElement('div');
            queryBox.className = 'query-box';
            queryBox.innerHTML = `
                <h3>Gap Query ${{index + 1}}: ${{query.gap_query}}</h3>
                <p><strong>Vector Queries:</strong> ${{query.vector_queries.length}}</p>
                <p><strong>URLs Accessed:</strong> ${{query.urls_accessed.length}}</p>
                <p><strong>Insights Extracted:</strong> ${{query.insights_extracted.length}}</p>
            `;
            queryDetailsDiv.appendChild(queryBox);
        }});
    </script>
</body>
</html>
"""
        
        # Save HTML file
        html_file = os.path.join(log_dir, f"{session_id}_visualization.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)
        
        print(f"✅ Visualization report created: {html_file}")
        return html_file
        
    except Exception as e:
        print(f"❌ Error creating visualization: {e}")
        return None