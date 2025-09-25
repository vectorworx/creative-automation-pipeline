"""
Brand Compliance Checker
Validates generated assets against brand guidelines and cultural requirements
"""

import logging
from pathlib import Path
from PIL import Image, ImageStat
from typing import Dict, List, Any, Optional
import re

class BrandComplianceChecker:
    """Enterprise brand compliance validation system"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.compliance_config = config.get("brand_compliance", {})
        self.cultural_config = config.get("cultural_adaptation", {})
        
        # Load prohibited content patterns
        self.prohibited_patterns = [
            r'\b(free|buy now|limited time|click here)\b',  # Aggressive marketing
            r'\b(guaranteed|miracle|instant)\b',           # Exaggerated claims
            r'\b(lose weight|diet pill|supplement)\b'      # Health claims
        ]
        
        # Cultural sensitivity patterns by region
        self.cultural_restrictions = {
            "middle_east": [
                r'\b(alcohol|beer|wine|party)\b',
                r'\b(revealing|bikini|shorts)\b'
            ],
            "japan": [
                r'\b(aggressive|loud|pushy)\b',
                r'\b(individual|personal|me)\b'  # Collectivist culture preference
            ],
            "india": [
                r'\b(beef|cow|leather)\b',
                r'\b(left hand|unclean)\b'
            ]
        }
    
    def check_asset_compliance(self, asset_path: str, campaign_brief: Dict[str, Any], 
                              product: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive compliance check for generated asset"""
        
        compliance_result = {
            "overall_score": 0,
            "passed": False,
            "checks": {
                "visual_compliance": {},
                "content_compliance": {},
                "cultural_compliance": {},
                "technical_compliance": {}
            },
            "issues": [],
            "recommendations": []
        }
        
        try:
            # Visual compliance checks
            visual_score = self._check_visual_compliance(asset_path, campaign_brief)
            compliance_result["checks"]["visual_compliance"] = visual_score
            
            # Content compliance checks
            content_score = self._check_content_compliance(campaign_brief, product)
            compliance_result["checks"]["content_compliance"] = content_score
            
            # Cultural compliance checks
            cultural_score = self._check_cultural_compliance(campaign_brief)
            compliance_result["checks"]["cultural_compliance"] = cultural_score
            
            # Technical compliance checks
            technical_score = self._check_technical_compliance(asset_path)
            compliance_result["checks"]["technical_compliance"] = technical_score
            
            # Calculate overall score (weighted average)
            weights = {"visual": 0.3, "content": 0.3, "cultural": 0.25, "technical": 0.15}
            overall_score = (
                visual_score["score"] * weights["visual"] +
                content_score["score"] * weights["content"] +
                cultural_score["score"] * weights["cultural"] +
                technical_score["score"] * weights["technical"]
            )
            
            compliance_result["overall_score"] = round(overall_score, 1)
            compliance_result["passed"] = overall_score >= self.compliance_config.get("minimum_score", 85)
            
            # Collect issues and recommendations
            for check_type, results in compliance_result["checks"].items():
                compliance_result["issues"].extend(results.get("issues", []))
                compliance_result["recommendations"].extend(results.get("recommendations", []))
            
            self.logger.info(f"Compliance check completed: {overall_score}/100")
            
        except Exception as e:
            self.logger.error(f"Compliance check failed: {e}")
            compliance_result["overall_score"] = 0
            compliance_result["issues"].append(f"Compliance check system error: {str(e)}")
        
        return compliance_result
    
    def _check_visual_compliance(self, asset_path: str, campaign_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Check visual brand compliance"""
        
        result = {
            "score": 85,  # Default score
            "issues": [],
            "recommendations": [],
            "checks_performed": []
        }
        
        try:
            if not Path(asset_path).exists():
                result["score"] = 0
                result["issues"].append("Asset file not found")
                return result
            
            image = Image.open(asset_path)
            
            # Image quality checks
            if image.width < 800 or image.height < 600:
                result["score"] -= 10
                result["issues"].append("Image resolution below recommended minimum")
                result["recommendations"].append("Use higher resolution images for better quality")
            else:
                result["checks_performed"].append("Resolution check passed")
            
            # Color analysis (basic)
            colors = self._analyze_dominant_colors(image)
            brand_colors = campaign_brief.get("brand_guidelines", {}).get("color_palette", [])
            
            if brand_colors and not self._colors_compatible(colors, brand_colors):
                result["score"] -= 15
                result["issues"].append("Generated colors don't align with brand palette")
                result["recommendations"].append("Adjust prompt to specify brand colors")
            else:
                result["checks_performed"].append("Color alignment acceptable")
            
            # Aspect ratio validation
            expected_ratios = {"square": 1.0, "story": 0.5625, "landscape": 1.777}
            actual_ratio = image.width / image.height
            
            # Check if close to any expected ratio (within 5% tolerance)
            ratio_match = False
            for ratio_name, expected_ratio in expected_ratios.items():
                if abs(actual_ratio - expected_ratio) / expected_ratio <= 0.05:
                    ratio_match = True
                    result["checks_performed"].append(f"Aspect ratio matches {ratio_name}")
                    break
            
            if not ratio_match:
                result["score"] -= 10
                result["issues"].append(f"Aspect ratio {actual_ratio:.3f} doesn't match standard formats")
            
        except Exception as e:
            result["score"] = 50
            result["issues"].append(f"Visual analysis failed: {str(e)}")
        
        return result
    
    def _check_content_compliance(self, campaign_brief: Dict[str, Any], 
                                 product: Dict[str, Any]) -> Dict[str, Any]:
        """Check content and messaging compliance"""
        
        result = {
            "score": 90,  # Start high, deduct for issues
            "issues": [],
            "recommendations": [],
            "checks_performed": []
        }
        
        message = campaign_brief.get("campaign_message", "").lower()
        
        # Check for prohibited content patterns
        for pattern in self.prohibited_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                result["score"] -= 20
                result["issues"].append(f"Prohibited content detected: {pattern}")
                result["recommendations"].append("Remove prohibited marketing language")
        
        if not result["issues"]:
            result["checks_performed"].append("Content screening passed")
        
        # Message length validation
        if len(message) > 100:
            result["score"] -= 5
            result["issues"].append("Campaign message may be too long for social media")
            result["recommendations"].append("Consider shortening message for better engagement")
        elif len(message) < 10:
            result["score"] -= 10
            result["issues"].append("Campaign message is too short")
            result["recommendations"].append("Provide more descriptive campaign message")
        else:
            result["checks_performed"].append("Message length appropriate")
        
        # Brand name consistency
        product_name = product.get("name", "").lower()
        if product_name and product_name not in message:
            result["score"] -= 5
            result["recommendations"].append(f"Consider mentioning '{product['name']}' in campaign message")
        
        return result
    
    def _check_cultural_compliance(self, campaign_brief: Dict[str, Any]) -> Dict[str, Any]:
        """Check cultural sensitivity and regional compliance"""
        
        result = {
            "score": 95,  # Start very high, deduct for cultural issues
            "issues": [],
            "recommendations": [],
            "checks_performed": []
        }
        
        target_region = campaign_brief.get("target_region", "").lower().replace(" ", "_")
        message = campaign_brief.get("campaign_message", "").lower()
        
        # Check region-specific restrictions
        if target_region in self.cultural_restrictions:
            restrictions = self.cultural_restrictions[target_region]
            
            for pattern in restrictions:
                if re.search(pattern, message, re.IGNORECASE):
                    result["score"] -= 25
                    result["issues"].append(f"Culturally inappropriate content for {target_region}: {pattern}")
                    result["recommendations"].append(f"Adapt messaging for {target_region} cultural norms")
        
        # General cultural sensitivity checks
        cultural_red_flags = [
            r'\b(exotic|primitive|backwards)\b',     # Potentially offensive descriptors
            r'\b(crazy|insane|mad)\b',               # Mental health sensitivity
            r'\b(disabled|handicapped|lame)\b'       # Disability sensitivity
        ]
        
        for pattern in cultural_red_flags:
            if re.search(pattern, message, re.IGNORECASE):
                result["score"] -= 15
                result["issues"].append(f"Potentially insensitive language detected: {pattern}")
                result["recommendations"].append("Use more inclusive language")
        
        if not result["issues"]:
            result["checks_performed"].append("Cultural sensitivity screening passed")
        
        # Regional adaptation recommendations
        if target_region in self.cultural_config.get("regions", {}):
            region_config = self.cultural_config["regions"][target_region]
            cultural_keywords = region_config.get("cultural_keywords", [])
            
            keyword_matches = sum(1 for keyword in cultural_keywords if keyword in message)
            if keyword_matches == 0:
                result["recommendations"].append(
                    f"Consider incorporating {target_region} cultural elements: {', '.join(cultural_keywords[:3])}"
                )
        
        return result
    
    def _check_technical_compliance(self, asset_path: str) -> Dict[str, Any]:
        """Check technical requirements and specifications"""
        
        result = {
            "score": 100,  # Start perfect, deduct for technical issues
            "issues": [],
            "recommendations": [],
            "checks_performed": []
        }
        
        try:
            if not Path(asset_path).exists():
                result["score"] = 0
                result["issues"].append("Asset file does not exist")
                return result
            
            # File size check
            file_size_mb = Path(asset_path).stat().st_size / (1024 * 1024)
            if file_size_mb > 5.0:
                result["score"] -= 10
                result["issues"].append(f"File size ({file_size_mb:.1f}MB) exceeds social media limits")
                result["recommendations"].append("Optimize image compression")
            else:
                result["checks_performed"].append("File size appropriate")
            
            # Image format validation
            image = Image.open(asset_path)
            if image.format not in ['PNG', 'JPEG', 'JPG']:
                result["score"] -= 5
                result["issues"].append(f"Image format {image.format} not optimal for web")
                result["recommendations"].append("Use PNG or JPEG format")
            else:
                result["checks_performed"].append("Image format acceptable")
            
            # Color mode validation
            if image.mode not in ['RGB', 'RGBA']:
                result["score"] -= 10
                result["issues"].append(f"Color mode {image.mode} not suitable for digital display")
                result["recommendations"].append("Convert to RGB color mode")
            else:
                result["checks_performed"].append("Color mode appropriate")
            
        except Exception as e:
            result["score"] = 50
            result["issues"].append(f"Technical validation failed: {str(e)}")
        
        return result
    
    def _analyze_dominant_colors(self, image: Image.Image) -> List[tuple]:
        """Extract dominant colors from image (simplified)"""
        
        try:
            # Convert to RGB if necessary
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # Get color statistics
            colors = image.getcolors(maxcolors=256*256*256)
            if colors:
                # Sort by frequency and get top 3
                colors.sort(key=lambda x: x[0], reverse=True)
                return [color[1] for color in colors[:3]]
            else:
                # Fallback: get average color
                stat = ImageStat.Stat(image)
                return [tuple(stat.mean)]
                
        except Exception:
            return [(128, 128, 128)]  # Default gray
    
    def _colors_compatible(self, image_colors: List[tuple], brand_colors: List[str]) -> bool:
        """Check if image colors are compatible with brand palette (simplified)"""
        
        # Convert brand colors from hex to RGB (simplified)
        brand_rgb = []
        for color in brand_colors:
            if color.startswith('#') and len(color) == 7:
                try:
                    r = int(color[1:3], 16)
                    g = int(color[3:5], 16)
                    b = int(color[5:7], 16)
                    brand_rgb.append((r, g, b))
                except ValueError:
                    continue
        
        if not brand_rgb:
            return True  # No brand colors defined, assume compatible
        
        # Simple compatibility check: see if any image color is close to brand colors
        for img_color in image_colors:
            for brand_color in brand_rgb:
                # Calculate color distance (simplified)
                distance = sum(abs(a - b) for a, b in zip(img_color, brand_color))
                if distance < 100:  # Threshold for "similar"
                    return True
        
        return False
    
    def generate_compliance_report(self, results: Dict[str, Any]) -> str:
        """Generate human-readable compliance report"""
        
        report_lines = [
            "=== BRAND COMPLIANCE REPORT ===",
            f"Overall Score: {results['overall_score']}/100",
            f"Status: {'✅ PASSED' if results['passed'] else '❌ FAILED'}",
            ""
        ]
        
        # Add check results
        for check_type, check_results in results["checks"].items():
            check_name = check_type.replace('_', ' ').title()
            report_lines.append(f"{check_name}: {check_results['score']}/100")
            
            if check_results.get("checks_performed"):
                for check in check_results["checks_performed"]:
                    report_lines.append(f"  ✅ {check}")
        
        # Add issues
        if results["issues"]:
            report_lines.extend(["", "Issues Found:"])
            for issue in results["issues"]:
                report_lines.append(f"  ⚠️  {issue}")
        
        # Add recommendations
        if results["recommendations"]:
            report_lines.extend(["", "Recommendations:"])
            for rec in results["recommendations"]:
                report_lines.append(f"  💡 {rec}")
        
        return "\n".join(report_lines)