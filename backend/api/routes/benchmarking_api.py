"""
Supply Chain Benchmarking API Routes
===================================

Professional benchmarking API that transforms DSP Eco Tracker from 
"carbon tracking" to "competitive intelligence platform."

Features:
- Industry peer comparison
- Percentile rankings
- Competitive positioning
- Market leader identification
- Improvement opportunity quantification

Business Impact:
- C-suite competitive intelligence
- Data-driven sustainability strategy
- Procurement decision support
- ESG competitive advantage
"""

from flask import Blueprint, jsonify, request
from datetime import datetime
import sys
import os

# Add services path
sys.path.append('/Users/jamie/Documents/University/dsp_eco_tracker/backend/services')

try:
    from supply_chain_benchmarking import SupplyChainBenchmarkingEngine
    benchmarking_engine = SupplyChainBenchmarkingEngine()
    BENCHMARKING_AVAILABLE = True
    print("✅ Supply Chain Benchmarking Engine loaded successfully")
except ImportError as e:
    print(f"⚠️ Benchmarking engine not available: {e}")
    BENCHMARKING_AVAILABLE = False

# Blueprint for benchmarking API routes
benchmarking_bp = Blueprint('benchmarking', __name__, url_prefix='/api/benchmarking')

@benchmarking_bp.route('/health', methods=['GET'])
def benchmarking_health_check():
    """Health check for benchmarking service."""
    return jsonify({
        'status': 'healthy' if BENCHMARKING_AVAILABLE else 'unavailable',
        'service': 'Supply Chain Benchmarking Engine',
        'timestamp': datetime.now().isoformat(),
        'features': {
            'industry_comparison': BENCHMARKING_AVAILABLE,
            'percentile_rankings': BENCHMARKING_AVAILABLE,
            'competitive_analysis': BENCHMARKING_AVAILABLE
        }
    })

@benchmarking_bp.route('/company/analyze', methods=['POST'])
def analyze_company_benchmarks():
    """
    Analyze a company's sustainability performance against industry benchmarks.
    
    Expected payload:
    {
        "company_name": "Apple Inc.",
        "products": [
            {
                "category": "smartphones",
                "carbon_kg": 70.2,
                "recyclability": "High",
                "weight": 0.8,
                "title": "iPhone 15 Pro"
            }
        ]
    }
    """
    if not BENCHMARKING_AVAILABLE:
        return jsonify({
            'error': 'Benchmarking service unavailable',
            'status': 'error'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'company_name' not in data or 'products' not in data:
            return jsonify({
                'error': 'Missing required fields: company_name and products',
                'status': 'error'
            }), 400
        
        # Analyze company portfolio
        benchmark_result = benchmarking_engine.analyze_company_portfolio(data)
        
        # Format response for frontend
        response_data = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'company_analysis': {
                'company_name': benchmark_result.company_name,
                'industry': benchmark_result.industry,
                'overall_sustainability_score': round(benchmark_result.overall_score, 1),
                'market_position': _get_market_position(benchmark_result.overall_score),
                'metrics': {
                    metric_name: {
                        'value': round(metric.value, 2),
                        'industry_average': round(metric.industry_average, 2),
                        'percentile_rank': round(metric.percentile_rank, 1),
                        'peer_position': metric.peer_position,
                        'improvement_potential': round(metric.improvement_potential, 2),
                        'best_in_class_target': round(metric.best_in_class, 2),
                        'performance_gap': round(metric.value - metric.best_in_class, 2) if metric_name == 'carbon_footprint' else round(metric.best_in_class - metric.value, 2)
                    }
                    for metric_name, metric in benchmark_result.metrics.items()
                },
                'competitive_insights': benchmark_result.competitive_insights,
                'improvement_opportunities': benchmark_result.improvement_opportunities,
                'peer_comparison': benchmark_result.peer_comparison
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Benchmarking analysis failed: {str(e)}',
            'status': 'error'
        }), 500

@benchmarking_bp.route('/industry/<industry_name>/report', methods=['GET'])
def get_industry_benchmark_report(industry_name):
    """
    Get comprehensive industry benchmarking report.
    
    Available industries:
    - Technology & Electronics
    - Fashion & Apparel  
    - Home & Garden
    - Health & Beauty
    - Automotive & Transportation
    - Food & Beverage
    - Industrial & B2B
    - Sports & Recreation
    """
    if not BENCHMARKING_AVAILABLE:
        return jsonify({
            'error': 'Benchmarking service unavailable',
            'status': 'error'
        }), 503
    
    try:
        # Decode URL-encoded industry name
        industry_name = industry_name.replace('%20', ' ').replace('+', ' ')
        
        report = benchmarking_engine.get_industry_report(industry_name)
        
        if 'error' in report:
            return jsonify({
                'error': report['error'],
                'available_industries': report.get('available_industries', []),
                'status': 'error'
            }), 404
        
        # Format for frontend visualization
        formatted_report = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'industry_report': {
                'industry_name': report['industry'],
                'sample_size': report['sample_size'],
                'carbon_benchmarks': {
                    'industry_average': round(report['carbon_benchmarks'].get('mean', 0), 2),
                    'industry_median': round(report['carbon_benchmarks'].get('median', 0), 2),
                    'top_10_percent': round(report['carbon_benchmarks'].get('percentiles', {}).get('10', 0), 2),
                    'top_25_percent': round(report['carbon_benchmarks'].get('percentiles', {}).get('25', 0), 2),
                    'bottom_25_percent': round(report['carbon_benchmarks'].get('percentiles', {}).get('75', 0), 2),
                    'bottom_10_percent': round(report['carbon_benchmarks'].get('percentiles', {}).get('90', 0), 2)
                },
                'recyclability_benchmarks': {
                    'high_recyclability_average': round(report['recyclability_benchmarks'].get('high_percentage', 0), 1),
                    'medium_recyclability_average': round(report['recyclability_benchmarks'].get('medium_percentage', 0), 1),
                    'low_recyclability_average': round(report['recyclability_benchmarks'].get('low_percentage', 0), 1)
                },
                'top_performers': report.get('top_performers', []),
                'industry_trends': report.get('industry_trends', {}),
                'benchmarking_insights': _generate_industry_insights(report)
            }
        }
        
        return jsonify(formatted_report)
        
    except Exception as e:
        return jsonify({
            'error': f'Industry report generation failed: {str(e)}',
            'status': 'error'
        }), 500

@benchmarking_bp.route('/competitor/compare', methods=['POST'])
def compare_competitors():
    """
    Direct competitor comparison analysis.
    
    Expected payload:
    {
        "company_a": {
            "name": "Apple Inc.",
            "products": [...]
        },
        "company_b": {
            "name": "Samsung Electronics",
            "products": [...]
        }
    }
    """
    if not BENCHMARKING_AVAILABLE:
        return jsonify({
            'error': 'Benchmarking service unavailable',
            'status': 'error'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'company_a' not in data or 'company_b' not in data:
            return jsonify({
                'error': 'Missing required fields: company_a and company_b',
                'status': 'error'
            }), 400
        
        company_a_data = data['company_a']
        company_b_data = data['company_b']
        
        # Perform competitor analysis
        comparison = benchmarking_engine.benchmark_competitor_analysis(
            company_a_data['name'],
            company_b_data['name'],
            company_a_data['products'],
            company_b_data['products']
        )
        
        # Format response
        response_data = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'competitor_comparison': {
                'comparison_summary': {
                    'winner': comparison['competitive_advantage'],
                    'key_differentiators': comparison['key_differentiators']
                },
                'company_a': {
                    'name': comparison['company_a']['name'],
                    'overall_score': round(comparison['company_a']['overall_score'], 1),
                    'carbon_percentile': round(comparison['company_a']['carbon_percentile'], 1),
                    'recyclability_percentile': round(comparison['company_a']['recyclability_percentile'], 1),
                    'market_position': _get_market_position(comparison['company_a']['overall_score'])
                },
                'company_b': {
                    'name': comparison['company_b']['name'],
                    'overall_score': round(comparison['company_b']['overall_score'], 1),
                    'carbon_percentile': round(comparison['company_b']['carbon_percentile'], 1),
                    'recyclability_percentile': round(comparison['company_b']['recyclability_percentile'], 1),
                    'market_position': _get_market_position(comparison['company_b']['overall_score'])
                },
                'competitive_insights': _generate_competitive_insights(comparison)
            }
        }
        
        return jsonify(response_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Competitor comparison failed: {str(e)}',
            'status': 'error'
        }), 500

@benchmarking_bp.route('/rankings/industry/<industry_name>', methods=['GET'])
def get_industry_rankings(industry_name):
    """
    Get industry sustainability rankings and leaderboards.
    
    Query parameters:
    - metric: carbon_footprint, recyclability, overall (default: overall)
    - limit: number of results (default: 10)
    """
    if not BENCHMARKING_AVAILABLE:
        return jsonify({
            'error': 'Benchmarking service unavailable',
            'status': 'error'
        }), 503
    
    try:
        # Get query parameters
        metric = request.args.get('metric', 'overall')
        limit = int(request.args.get('limit', 10))
        
        # Decode industry name
        industry_name = industry_name.replace('%20', ' ').replace('+', ' ')
        
        # Get industry report for base data
        report = benchmarking_engine.get_industry_report(industry_name)
        
        if 'error' in report:
            return jsonify({
                'error': report['error'],
                'status': 'error'
            }), 404
        
        # Generate rankings based on top performers
        top_performers = report.get('top_performers', [])
        
        rankings_data = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'industry_rankings': {
                'industry': industry_name,
                'ranking_metric': metric,
                'sample_size': report['sample_size'],
                'top_performers': [
                    {
                        'rank': idx + 1,
                        'product': performer.get('title', 'Unknown Product'),
                        'origin': performer.get('origin', 'Unknown'),
                        'carbon_footprint': round(performer.get('co2_emissions', 0), 2),
                        'sustainability_grade': _calculate_sustainability_grade(performer.get('co2_emissions', 0))
                    }
                    for idx, performer in enumerate(top_performers[:limit])
                ],
                'benchmarking_thresholds': {
                    'excellent': round(report['carbon_benchmarks'].get('percentiles', {}).get('10', 0), 2),
                    'good': round(report['carbon_benchmarks'].get('percentiles', {}).get('25', 0), 2),
                    'average': round(report['carbon_benchmarks'].get('mean', 0), 2),
                    'below_average': round(report['carbon_benchmarks'].get('percentiles', {}).get('75', 0), 2)
                }
            }
        }
        
        return jsonify(rankings_data)
        
    except Exception as e:
        return jsonify({
            'error': f'Industry rankings generation failed: {str(e)}',
            'status': 'error'
        }), 500

@benchmarking_bp.route('/insights/market-position', methods=['POST'])
def get_market_positioning_insights():
    """
    Get strategic market positioning insights based on sustainability metrics.
    
    Expected payload:
    {
        "company_name": "Tesla Inc.",
        "current_metrics": {
            "carbon_footprint": 45.2,
            "recyclability_score": 67.5,
            "weight_efficiency": 2.1
        },
        "target_industry": "Automotive & Transportation"
    }
    """
    if not BENCHMARKING_AVAILABLE:
        return jsonify({
            'error': 'Benchmarking service unavailable',
            'status': 'error'
        }), 503
    
    try:
        data = request.get_json()
        
        if not data or 'company_name' not in data or 'current_metrics' not in data:
            return jsonify({
                'error': 'Missing required fields: company_name and current_metrics',
                'status': 'error'
            }), 400
        
        company_name = data['company_name']
        metrics = data['current_metrics']
        target_industry = data.get('target_industry', 'General Commerce')
        
        # Get industry benchmarks
        industry_report = benchmarking_engine.get_industry_report(target_industry)
        
        if 'error' in industry_report:
            return jsonify({
                'error': f'Industry "{target_industry}" not available for benchmarking',
                'status': 'error'
            }), 404
        
        # Calculate positioning insights
        carbon_footprint = metrics.get('carbon_footprint', 0)
        recyclability_score = metrics.get('recyclability_score', 0)
        
        carbon_benchmarks = industry_report.get('carbon_benchmarks', {})
        recyclability_benchmarks = industry_report.get('recyclability_benchmarks', {})
        
        # Calculate market position
        carbon_percentile = _calculate_carbon_percentile(carbon_footprint, carbon_benchmarks)
        recyclability_percentile = _calculate_recyclability_percentile(recyclability_score, recyclability_benchmarks)
        
        overall_position_score = (carbon_percentile + recyclability_percentile) / 2
        
        positioning_insights = {
            'status': 'success',
            'timestamp': datetime.now().isoformat(),
            'market_positioning': {
                'company_name': company_name,
                'target_industry': target_industry,
                'overall_market_position': _get_market_position(overall_position_score),
                'position_score': round(overall_position_score, 1),
                'competitive_analysis': {
                    'carbon_performance': {
                        'percentile_rank': round(carbon_percentile, 1),
                        'vs_industry_average': round(carbon_footprint - carbon_benchmarks.get('mean', 0), 2),
                        'position': _get_carbon_position(carbon_percentile)
                    },
                    'recyclability_performance': {
                        'percentile_rank': round(recyclability_percentile, 1),
                        'vs_industry_average': round(recyclability_score - recyclability_benchmarks.get('high_percentage', 0), 1),
                        'position': _get_recyclability_position(recyclability_percentile)
                    }
                },
                'strategic_recommendations': _generate_strategic_recommendations(
                    carbon_percentile, recyclability_percentile, company_name
                ),
                'competitive_opportunities': _identify_competitive_opportunities(
                    carbon_footprint, recyclability_score, carbon_benchmarks, recyclability_benchmarks
                )
            }
        }
        
        return jsonify(positioning_insights)
        
    except Exception as e:
        return jsonify({
            'error': f'Market positioning analysis failed: {str(e)}',
            'status': 'error'
        }), 500

# Helper functions
def _get_market_position(score):
    """Convert overall score to market position description."""
    if score >= 80:
        return "Market Leader"
    elif score >= 60:
        return "Above Average Performer"
    elif score >= 40:
        return "Average Performer"
    elif score >= 20:
        return "Below Average Performer"
    else:
        return "Significant Improvement Needed"

def _generate_industry_insights(report):
    """Generate insights from industry report data."""
    insights = []
    
    carbon_data = report.get('carbon_benchmarks', {})
    recyclability_data = report.get('recyclability_benchmarks', {})
    
    # Carbon insights
    avg_carbon = carbon_data.get('mean', 0)
    if avg_carbon > 50:
        insights.append(f"Industry has high carbon intensity - significant sustainability improvement opportunities")
    elif avg_carbon < 20:
        insights.append(f"Industry shows strong carbon performance - competitive advantage through efficiency")
    
    # Recyclability insights
    high_recyclability = recyclability_data.get('high_percentage', 0)
    if high_recyclability > 60:
        insights.append(f"Industry demonstrates strong circular economy adoption")
    elif high_recyclability < 30:
        insights.append(f"Major opportunity for circular economy leadership in this industry")
    
    return insights

def _generate_competitive_insights(comparison):
    """Generate competitive insights from comparison data."""
    insights = []
    
    company_a = comparison['company_a']
    company_b = comparison['company_b']
    
    # Overall performance comparison
    score_diff = abs(company_a['overall_score'] - company_b['overall_score'])
    
    if score_diff > 20:
        leader = company_a['name'] if company_a['overall_score'] > company_b['overall_score'] else company_b['name']
        insights.append(f"{leader} has significant overall sustainability advantage")
    
    # Carbon performance comparison
    carbon_diff = abs(company_a['carbon_percentile'] - company_b['carbon_percentile'])
    if carbon_diff > 25:
        leader = company_a['name'] if company_a['carbon_percentile'] > company_b['carbon_percentile'] else company_b['name']
        insights.append(f"{leader} demonstrates superior carbon management")
    
    # Recyclability comparison
    recyclability_diff = abs(company_a['recyclability_percentile'] - company_b['recyclability_percentile'])
    if recyclability_diff > 25:
        leader = company_a['name'] if company_a['recyclability_percentile'] > company_b['recyclability_percentile'] else company_b['name']
        insights.append(f"{leader} leads in circular economy practices")
    
    return insights

def _calculate_sustainability_grade(carbon_emissions):
    """Calculate sustainability grade based on carbon emissions."""
    if carbon_emissions <= 10:
        return "A+"
    elif carbon_emissions <= 20:
        return "A"
    elif carbon_emissions <= 35:
        return "B+"
    elif carbon_emissions <= 50:
        return "B"
    elif carbon_emissions <= 75:
        return "C"
    else:
        return "D"

def _calculate_carbon_percentile(value, benchmarks):
    """Calculate carbon footprint percentile (lower is better)."""
    percentiles = benchmarks.get('percentiles', {})
    
    if value <= percentiles.get('10', float('inf')):
        return 90
    elif value <= percentiles.get('25', float('inf')):
        return 75
    elif value <= benchmarks.get('median', float('inf')):
        return 50
    elif value <= percentiles.get('75', float('inf')):
        return 25
    else:
        return 10

def _calculate_recyclability_percentile(value, benchmarks):
    """Calculate recyclability percentile (higher is better)."""
    industry_avg = benchmarks.get('high_percentage', 30)
    
    if value >= industry_avg * 1.5:
        return 90
    elif value >= industry_avg * 1.2:
        return 75
    elif value >= industry_avg:
        return 50
    elif value >= industry_avg * 0.8:
        return 25
    else:
        return 10

def _get_carbon_position(percentile):
    """Get carbon performance position description."""
    if percentile >= 75:
        return "Low Carbon Leader"
    elif percentile >= 50:
        return "Above Average Carbon Performance"
    elif percentile >= 25:
        return "Below Average Carbon Performance"
    else:
        return "High Carbon Intensity"

def _get_recyclability_position(percentile):
    """Get recyclability position description."""
    if percentile >= 75:
        return "Circular Economy Leader"
    elif percentile >= 50:
        return "Above Average Recyclability"
    elif percentile >= 25:
        return "Below Average Recyclability"
    else:
        return "Limited Circular Economy Adoption"

def _generate_strategic_recommendations(carbon_percentile, recyclability_percentile, company_name):
    """Generate strategic recommendations based on performance."""
    recommendations = []
    
    if carbon_percentile < 50:
        recommendations.append({
            'priority': 'High',
            'category': 'Carbon Reduction',
            'recommendation': 'Implement aggressive carbon reduction strategy to reach industry top 25%',
            'business_impact': 'ESG rating improvement, regulatory compliance, cost savings'
        })
    
    if recyclability_percentile < 50:
        recommendations.append({
            'priority': 'Medium',
            'category': 'Circular Economy',
            'recommendation': 'Increase focus on product design for recyclability and circular business models',
            'business_impact': 'Brand differentiation, regulatory future-proofing, new revenue streams'
        })
    
    if carbon_percentile >= 75 and recyclability_percentile >= 75:
        recommendations.append({
            'priority': 'Strategic',
            'category': 'Market Leadership',
            'recommendation': 'Leverage sustainability leadership for premium positioning and market expansion',
            'business_impact': 'Premium pricing, market share growth, brand value enhancement'
        })
    
    return recommendations

def _identify_competitive_opportunities(carbon_footprint, recyclability_score, carbon_benchmarks, recyclability_benchmarks):
    """Identify specific competitive opportunities."""
    opportunities = []
    
    # Carbon opportunity
    top_25_carbon = carbon_benchmarks.get('percentiles', {}).get('25', 0)
    if carbon_footprint > top_25_carbon:
        potential_reduction = carbon_footprint - top_25_carbon
        opportunities.append({
            'type': 'Carbon Leadership',
            'description': f'Reduce carbon footprint by {potential_reduction:.1f} kg CO₂ to reach top 25%',
            'competitive_advantage': 'Position as low-carbon alternative to competitors',
            'market_impact': 'Access to green procurement contracts, ESG-focused customers'
        })
    
    # Recyclability opportunity
    industry_high = recyclability_benchmarks.get('high_percentage', 30)
    if recyclability_score < industry_high * 1.2:
        opportunities.append({
            'type': 'Circular Economy Leadership',
            'description': f'Increase recyclable products to {industry_high * 1.2:.1f}% for market leadership',
            'competitive_advantage': 'First-mover advantage in circular economy transition',
            'market_impact': 'Regulatory compliance advantage, appeal to sustainability-conscious consumers'
        })
    
    return opportunities