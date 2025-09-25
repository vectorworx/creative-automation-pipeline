"""
Campaign Processor with Compliance Integration
Orchestrates end-to-end campaign processing with brand compliance validation
"""

import logging
import time
import uuid
from pathlib import Path
from typing import Dict, List, Any, Optional
import json

from src.asset_generator import AssetGenerator
from src.compliance_checker import BrandComplianceChecker

class CampaignProcessor:
    """Enterprise campaign processing orchestrator"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Initialize components
        self.asset_generator = AssetGenerator(config)
        self.compliance_checker = BrandComplianceChecker(config)
        
        # Processing metrics
        self.processing_metrics = {
            "campaigns_processed": 0,
            "total_assets_generated": 0,
            "compliance_failures": 0,
            "average_processing_time": 0.0
        }
    
    def process_campaign(self, campaign_brief: Dict[str, Any], correlation_id: Optional[str] = None) -> Dict[str, Any]:
        """Process complete campaign with compliance validation"""
        
        if not correlation_id:
            correlation_id = f"cam_{uuid.uuid4().hex[:8]}"
        
        start_time = time.time()
        
        # Initialize campaign processing result
        campaign_result = {
            "correlation_id": correlation_id,
            "campaign_name": campaign_brief.get("campaign_name", "Unknown"),
            "processing_status": "in_progress",
            "start_time": time.strftime("%Y-%m-%d %H:%M:%S"),
            "assets": {},
            "compliance_results": {},
            "summary": {
                "total_assets_requested": 0,
                "assets_generated": 0,
                "assets_failed": 0,
                "compliance_passed": 0,
                "compliance_failed": 0,
                "overall_compliance_score": 0.0
            },
            "recommendations": [],
            "processing_time": 0.0
        }
        
        self.logger.info(f"Starting campaign processing: {campaign_brief.get('campaign_name')} [{correlation_id}]")
        
        try:
            # Validate campaign brief
            validation_result = self._validate_campaign_brief(campaign_brief)
            if not validation_result["valid"]:
                campaign_result["processing_status"] = "failed"
                campaign_result["error"] = f"Campaign brief validation failed: {validation_result['error']}"
                return campaign_result
            
            # Pre-process campaign brief (cultural adaptations, etc.)
            processed_brief = self._preprocess_campaign_brief(campaign_brief)
            
            # Generate assets
            self.logger.info(f"Generating assets for {len(processed_brief['products'])} products [{correlation_id}]")
            generation_result = self.asset_generator.generate_campaign_assets(processed_brief)
            
            # Process each generated asset
            compliance_scores = []
            
            for product_name, product_assets in generation_result["assets"].items():
                campaign_result["assets"][product_name] = {}
                campaign_result["compliance_results"][product_name] = {}
                
                product = next((p for p in processed_brief["products"] if p["name"] == product_name), {})
                
                for aspect_ratio, asset_info in product_assets.items():
                    campaign_result["summary"]["total_assets_requested"] += 1
                    
                    if asset_info["status"] == "success" and asset_info.get("path"):
                        # Asset generated successfully
                        campaign_result["assets"][product_name][aspect_ratio] = asset_info
                        campaign_result["summary"]["assets_generated"] += 1
                        
                        # Run compliance check
                        compliance_result = self.compliance_checker.check_asset_compliance(
                            asset_info["path"], processed_brief, product
                        )
                        
                        campaign_result["compliance_results"][product_name][aspect_ratio] = compliance_result
                        compliance_scores.append(compliance_result["overall_score"])
                        
                        if compliance_result["passed"]:
                            campaign_result["summary"]["compliance_passed"] += 1
                            self.logger.info(f"Compliance passed: {product_name}_{aspect_ratio} (Score: {compliance_result['overall_score']}) [{correlation_id}]")
                        else:
                            campaign_result["summary"]["compliance_failed"] += 1
                            self.logger.warning(f"Compliance failed: {product_name}_{aspect_ratio} (Score: {compliance_result['overall_score']}) [{correlation_id}]")
                        
                        # Collect recommendations
                        campaign_result["recommendations"].extend(compliance_result.get("recommendations", []))
                        
                    else:
                        # Asset generation failed
                        campaign_result["assets"][product_name][aspect_ratio] = asset_info
                        campaign_result["summary"]["assets_failed"] += 1
                        self.logger.error(f"Asset generation failed: {product_name}_{aspect_ratio} - {asset_info.get('error')} [{correlation_id}]")
            
            # Calculate overall compliance score
            if compliance_scores:
                campaign_result["summary"]["overall_compliance_score"] = round(sum(compliance_scores) / len(compliance_scores), 1)
            
            # Determine processing status
            if campaign_result["summary"]["assets_generated"] == 0:
                campaign_result["processing_status"] = "failed"
                campaign_result["error"] = "No assets were generated successfully"
            elif campaign_result["summary"]["compliance_failed"] > campaign_result["summary"]["compliance_passed"]:
                campaign_result["processing_status"] = "completed_with_issues"
            else:
                campaign_result["processing_status"] = "completed_successfully"
            
            # Generate strategic recommendations
            campaign_result["strategic_recommendations"] = self._generate_strategic_recommendations(campaign_result, processed_brief)
            
        except Exception as e:
            self.logger.error(f"Campaign processing failed: {str(e)} [{correlation_id}]")
            campaign_result["processing_status"] = "failed"
            campaign_result["error"] = str(e)
        
        # Calculate processing time and update metrics
        processing_time = time.time() - start_time
        campaign_result["processing_time"] = round(processing_time, 2)
        campaign_result["end_time"] = time.strftime("%Y-%m-%d %H:%M:%S")
        
        self._update_processing_metrics(campaign_result, processing_time)
        
        self.logger.info(f"Campaign processing completed: {campaign_result['processing_status']} in {processing_time:.2f}s [{correlation_id}]")
        
        return campaign_result
    
    def _validate_campaign_brief(self, campaign_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Validate campaign brief structure and content"""
        
        required_fields = ["campaign_name", "products", "target_region", "target_audience", "campaign_message"]
        
        for field in required_fields:
            if field not in campaign_brief or not campaign_brief[field]:
                return {"valid": False, "error": f"Missing required field: {field}"}
        
        # Validate products
        if not isinstance(campaign_brief["products"], list) or len(campaign_brief["products"]) == 0:
            return {"valid": False, "error": "Campaign must include at least one product"}
        
        for i, product in enumerate(campaign_brief["products"]):
            if not isinstance(product, dict) or "name" not in product:
                return {"valid": False, "error": f"Product {i+1} must have a 'name' field"}
        
        return {"valid": True}
    
    def _preprocess_campaign_brief(self, campaign_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Preprocess campaign brief with cultural adaptations"""
        
        processed_brief = campaign_brief.copy()
        
        # Apply cultural adaptations based on target region
        target_region = campaign_brief.get("target_region", "").lower().replace(" ", "_")
        
        if target_region in self.config.get("cultural_adaptation", {}).get("regions", {}):
            region_config = self.config["cultural_adaptation"]["regions"][target_region]
            
            # Add cultural context to brand guidelines
            if "brand_guidelines" not in processed_brief:
                processed_brief["brand_guidelines"] = {}
            
            processed_brief["brand_guidelines"]["cultural_adaptation"] = {
                "region": target_region,
                "cultural_keywords": region_config.get("cultural_keywords", []),
                "language": region_config.get("language", "en"),
                "text_direction": region_config.get("text_direction", "ltr")
            }
            
            self.logger.info(f"Applied cultural adaptation for {target_region}")
        
        # Enhance campaign message if too generic
        message = processed_brief.get("campaign_message", "")
        if len(message.split()) < 3:
            enhanced_message = self._enhance_campaign_message(message, processed_brief)
            if enhanced_message != message:
                processed_brief["campaign_message"] = enhanced_message
                self.logger.info(f"Enhanced campaign message: {enhanced_message}")
        
        return processed_brief
    
    def _enhance_campaign_message(self, original_message: str, campaign_brief: Dict[str, Any]) -> str:
        """Enhance generic campaign messages"""
        
        target_audience = campaign_brief.get("target_audience", "").lower()
        target_region = campaign_brief.get("target_region", "").lower()
        
        # Add audience-specific enhancements
        enhancements = {
            "young professionals": "Elevate your professional life",
            "families": "Perfect for the whole family",
            "students": "Smart choice for students", 
            "seniors": "Trusted quality for life's experiences"
        }
        
        for audience, enhancement in enhancements.items():
            if audience in target_audience:
                return f"{original_message} - {enhancement}"
        
        return original_message
    
    def _generate_strategic_recommendations(self, campaign_result: Dict[str, Any], 
                                          campaign_brief: Dict[str, Any]) -> List[str]:
        """Generate strategic recommendations based on campaign results"""
        
        recommendations = []
        summary = campaign_result["summary"]
        
        # Performance recommendations
        success_rate = (summary["assets_generated"] / max(summary["total_assets_requested"], 1)) * 100
        if success_rate < 90:
            recommendations.append(f"Asset generation success rate ({success_rate:.1f}%) below optimal. Consider API reliability improvements.")
        
        # Compliance recommendations
        compliance_rate = (summary["compliance_passed"] / max(summary["assets_generated"], 1)) * 100
        if compliance_rate < 95:
            recommendations.append(f"Brand compliance rate ({compliance_rate:.1f}%) needs improvement. Review brand guidelines integration.")
        
        # Regional optimization recommendations
        target_region = campaign_brief.get("target_region", "")
        if target_region.lower() in ["japan", "middle east", "india"]:
            if summary["overall_compliance_score"] < 90:
                recommendations.append(f"Consider specialized cultural adaptation for {target_region} market requirements.")
        
        # Asset optimization recommendations
        if summary["assets_generated"] >= 6:  # Multiple products and ratios
            recommendations.append("Consider A/B testing different creative variations for optimal performance.")
        
        # Efficiency recommendations
        if campaign_result["processing_time"] > 120:  # 2 minutes
            recommendations.append("Processing time suggests potential for optimization. Consider caching strategies.")
        
        return recommendations[:5]  # Limit to top 5 recommendations
    
    def _update_processing_metrics(self, campaign_result: Dict[str, Any], processing_time: float):
        """Update overall processing metrics"""
        
        self.processing_metrics["campaigns_processed"] += 1
        self.processing_metrics["total_assets_generated"] += campaign_result["summary"]["assets_generated"]
        self.processing_metrics["compliance_failures"] += campaign_result["summary"]["compliance_failed"]
        
        # Update average processing time
        current_avg = self.processing_metrics["average_processing_time"]
        campaign_count = self.processing_metrics["campaigns_processed"]
        new_avg = ((current_avg * (campaign_count - 1)) + processing_time) / campaign_count
        self.processing_metrics["average_processing_time"] = round(new_avg, 2)
    
    def generate_campaign_report(self, campaign_result: Dict[str, Any]) -> str:
        """Generate human-readable campaign report"""
        
        report_lines = [
            "="*60,
            "ENTERPRISE CAMPAIGN PROCESSING REPORT",
            "="*60,
            f"Campaign: {campaign_result['campaign_name']}",
            f"Correlation ID: {campaign_result['correlation_id']}",
            f"Status: {campaign_result['processing_status'].replace('_', ' ').upper()}",
            f"Processing Time: {campaign_result['processing_time']}s",
            ""
        ]
        
        # Asset Generation Summary
        summary = campaign_result["summary"]
        report_lines.extend([
            "ASSET GENERATION SUMMARY:",
            f"  Total Requested: {summary['total_assets_requested']}",
            f"  Successfully Generated: {summary['assets_generated']}",
            f"  Failed: {summary['assets_failed']}",
            f"  Success Rate: {(summary['assets_generated']/max(summary['total_assets_requested'],1)*100):.1f}%",
            ""
        ])
        
        # Compliance Summary
        if summary['assets_generated'] > 0:
            report_lines.extend([
                "BRAND COMPLIANCE SUMMARY:",
                f"  Compliance Passed: {summary['compliance_passed']}",
                f"  Compliance Failed: {summary['compliance_failed']}",
                f"  Overall Compliance Score: {summary['overall_compliance_score']}/100",
                f"  Compliance Rate: {(summary['compliance_passed']/max(summary['assets_generated'],1)*100):.1f}%",
                ""
            ])
        
        # Strategic Recommendations
        if campaign_result.get("strategic_recommendations"):
            report_lines.extend([
                "STRATEGIC RECOMMENDATIONS:",
            ])
            for i, rec in enumerate(campaign_result["strategic_recommendations"], 1):
                report_lines.append(f"  {i}. {rec}")
            report_lines.append("")
        
        # Asset Details
        report_lines.append("GENERATED ASSETS:")
        for product_name, product_assets in campaign_result["assets"].items():
            report_lines.append(f"  {product_name}:")
            for aspect_ratio, asset_info in product_assets.items():
                status_icon = "✅" if asset_info["status"] == "success" else "❌"
                report_lines.append(f"    {status_icon} {aspect_ratio}: {asset_info.get('path', 'Failed')}")
        
        return "\n".join(report_lines)
    
    def get_processing_metrics(self) -> Dict[str, Any]:
        """Get overall processing performance metrics"""
        
        metrics = self.processing_metrics.copy()
        
        # Add calculated metrics
        if metrics["campaigns_processed"] > 0:
            metrics["average_assets_per_campaign"] = round(
                metrics["total_assets_generated"] / metrics["campaigns_processed"], 1
            )
            metrics["compliance_failure_rate"] = round(
                (metrics["compliance_failures"] / max(metrics["total_assets_generated"], 1)) * 100, 1
            )
        
        return metrics