"""
HTML Report Generator for Credit Portfolio Analysis
Generates professional HTML reports with interactive charts and visualizations.
"""

import os
from pathlib import Path
from typing import Dict, Any, List, Optional
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import jinja2


class HTMLReportGenerator:
    """Generates professional HTML reports with interactive charts."""
    
    def __init__(self):
        """Initialize the report generator."""
        self.template_dir = Path(__file__).parent / "templates"
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(str(self.template_dir)),
            autoescape=True
        )
    
    def generate_combined_report(self, data: Dict[str, Any], output_path: str) -> None:
        """
        Generate a combined HTML report with both Part 1 and Part 2 analysis.
        
        Args:
            data: Dictionary containing both Part 1 and Part 2 data
            output_path: Path to save the HTML report
        """
        # Extract data
        part1_data = data['part1_data']
        part2_data = data['part2_data']
        part1_charts = data['part1_charts']
        part2_charts = data['part2_charts']
        report_date = data.get('report_date', 'Unknown')
        
        # Get portfolio-wide rates instead of latest month
        portfolio_wide_rates = part1_data.get('portfolio_wide_rates', {})
        if not portfolio_wide_rates and part1_data.get('portfolio_metrics'):
            # Fallback to latest month if portfolio-wide rates not available
            portfolio_wide_rates = part1_data['portfolio_metrics'][0] if part1_data['portfolio_metrics'] else {}
        
        # Prepare template data
        template_data = {
            'report_date': report_date,
            'portfolio_wide_rates': portfolio_wide_rates,
            'yield_metrics': part1_data.get('yield_metrics', {}),
            'business_metrics': part1_data.get('business_metrics', pd.DataFrame()),
            'insights': part1_data.get('insights', {}),
            'summary_stats': part2_data.get('summary_stats', {}),
            'lifetime_value': part2_data.get('lifetime_value', {}),
            'average_order_value': part2_data.get('average_order_value', {}),
            'customer_acquisition_cost': part2_data.get('customer_acquisition_cost', {}),
            'cohort_metrics': part2_data.get('cohort_metrics', pd.DataFrame()),
            'part2_insights': part2_data.get('insights', {}),
            'portfolio_chart': part1_charts.get('portfolio_metrics', {}),
            'yield_chart': part1_charts.get('yield_metrics', {}),
            'ltv_chart': part2_charts.get('ltv_by_cohort', {}),
            'aov_chart': part2_charts.get('aov_by_cohort', {}),
            'account_type_heatmap': part1_charts.get('account_type_heatmap', {})
        }
        
        # Render template
        template = self.env.get_template('combined_report_template.html.j2')
        html_content = template.render(**template_data)
        
        # Save report
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(html_content)
    
    def _create_portfolio_metrics_chart(self, portfolio_metrics: List[Dict]) -> Dict:
        """Create a bar chart showing portfolio metrics."""
        if not portfolio_metrics:
            return {}
        
        # Since portfolio metrics don't have time series data, create a bar chart
        df = pd.DataFrame(portfolio_metrics)
        
        # Get the latest metrics (first row)
        if len(df) == 0:
            return {}
            
        latest_metrics = df.iloc[0]
        
        # Create bar chart for key metrics
        metrics = ['delinquency_rate', 'default_rate', 'charge_off_rate']
        metric_names = ['Delinquency Rate', 'Default Rate', 'Charge-off Rate']
        values = []
        
        for metric in metrics:
            if metric in latest_metrics:
                values.append(latest_metrics[metric] * 100)  # Convert to percentage
            else:
                values.append(0)
        
        fig = go.Figure(data=[
            go.Bar(
                x=metric_names,
                y=values,
                marker_color=['#667eea', '#764ba2', '#f093fb'],
                text=[f'{v:.2f}%' for v in values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Portfolio Risk Metrics",
            xaxis_title="Risk Metric",
            yaxis_title="Rate (%)",
            template="plotly_white",
            height=500,
            showlegend=False
        )
        
        return fig.to_dict()
    
    def _create_yield_metrics_chart(self, yield_metrics: Dict) -> Dict:
        """Create a bar chart comparing different yield metrics."""
        if not yield_metrics:
            return {}
        
        # Extract yield values
        metrics = []
        values = []
        colors = []
        
        for metric_name, metric_data in yield_metrics.items():
            if isinstance(metric_data, dict) and metric_name in metric_data:
                metrics.append(metric_name.replace('_', ' ').title())
                values.append(metric_data[metric_name] * 100)  # Convert to percentage
                colors.append('#667eea')
        
        if not metrics:
            return {}
        
        fig = go.Figure(data=[
            go.Bar(
                x=metrics,
                y=values,
                marker_color=colors,
                text=[f'{v:.2f}%' for v in values],
                textposition='auto'
            )
        ])
        
        fig.update_layout(
            title="Portfolio Yield Metrics Comparison",
            xaxis_title="Yield Metric",
            yaxis_title="Annualized Yield (%)",
            template="plotly_white",
            height=500,
            showlegend=False
        )
        
        return fig.to_dict()
    
    def _create_ltv_by_cohort_chart(self, cohort_analysis: Dict) -> Dict:
        """Create a line chart showing LTV by cohort."""
        if not cohort_analysis or 'by_cohort' not in cohort_analysis:
            return {}
        
        ltv_data = cohort_analysis['by_cohort']
        if not ltv_data:
            return {}
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(ltv_data)
        df['cohort_date'] = pd.to_datetime(df['cohort_month'].astype(str))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['cohort_date'],
            y=df['ltv'],
            mode='lines+markers',
            name='Lifetime Value',
            line=dict(color='#667eea', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Customer Lifetime Value by Cohort",
            xaxis_title="Cohort Date",
            yaxis_title="Lifetime Value ($)",
            template="plotly_white",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig.to_dict()
    
    def _create_aov_by_cohort_chart(self, cohort_analysis: Dict) -> Dict:
        """Create a line chart showing AOV by cohort."""
        if not cohort_analysis or 'by_cohort' not in cohort_analysis:
            return {}
        
        aov_data = cohort_analysis['by_cohort']
        if not aov_data:
            return {}
        
        # Convert to DataFrame for easier manipulation
        df = pd.DataFrame(aov_data)
        df['cohort_date'] = pd.to_datetime(df['cohort_month'].astype(str))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatter(
            x=df['cohort_date'],
            y=df['aov'],
            mode='lines+markers',
            name='Average Order Value',
            line=dict(color='#764ba2', width=3),
            marker=dict(size=8)
        ))
        
        fig.update_layout(
            title="Average Order Value by Cohort",
            xaxis_title="Cohort Date",
            yaxis_title="Average Order Value ($)",
            template="plotly_white",
            height=500,
            showlegend=True,
            hovermode='x unified'
        )
        
        return fig.to_dict()
    
    def _create_revenue_gauge_chart(self, summary_stats: Dict) -> Dict:
        """Create a gauge chart showing revenue metrics."""
        if not summary_stats:
            return {}
        
        # Calculate revenue efficiency
        gross_revenue = summary_stats.get('gross_revenue', 0)
        net_revenue = summary_stats.get('net_revenue', 0)
        
        if gross_revenue > 0:
            efficiency = (net_revenue / gross_revenue) * 100
        else:
            efficiency = 0
        
        fig = go.Figure(go.Indicator(
            mode="gauge+number+delta",
            value=efficiency,
            domain={'x': [0, 1], 'y': [0, 1]},
            title={'text': "Revenue Efficiency (%)"},
            delta={'reference': 80},
            gauge={
                'axis': {'range': [None, 100]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [0, 50], 'color': "lightgray"},
                    {'range': [50, 80], 'color': "gray"},
                    {'range': [80, 100], 'color': "darkgray"}
                ],
                'threshold': {
                    'line': {'color': "red", 'width': 4},
                    'thickness': 0.75,
                    'value': 90
                }
            }
        ))
        
        fig.update_layout(
            height=400,
            template="plotly_white"
        )
        
        return fig.to_dict() 

    def _create_account_type_heatmap(self, business_metrics: pd.DataFrame) -> Dict:
        """
        Create an interactive heatmap for account type distribution.
        
        Args:
            business_metrics: Business metrics DataFrame
            
        Returns:
            Dictionary with heatmap data
        """
        if business_metrics.empty:
            return {}
        
        try:
            # Parse account types from the accountTypes column
            account_types_list = []
            for account_types_str in business_metrics['accountTypes']:
                if pd.notna(account_types_str) and isinstance(account_types_str, str):
                    types = [t.strip() for t in account_types_str.split(',')]
                    account_types_list.extend(types)
            
            if not account_types_list:
                return {}
            
            # Count account types
            account_type_counts = pd.Series(account_types_list).value_counts()
            
            # Create heatmap using plotly.graph_objects
            fig = go.Figure(data=go.Heatmap(
                z=[[int(v) for v in account_type_counts.values]],
                x=['Account Types'],
                y=[str(k) for k in account_type_counts.index],
                colorscale='Viridis',
                showscale=True,
                text=[[str(int(val)) for val in account_type_counts.values]],
                texttemplate='%{text}',
                textfont={'size': 12}
            ))
            
            fig.update_layout(
                title='Account Type Distribution Heatmap',
                xaxis_title='Categories',
                yaxis_title='Account Types',
                height=400,
                margin={'l': 100, 'r': 50, 't': 50, 'b': 50}
            )
            
            return fig.to_dict()
        except Exception as e:
            print(f"Error creating account type heatmap: {e}")
            return {} 