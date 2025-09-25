#!/usr/bin/env python3
"""
Creative Automation Pipeline - Enhanced Main Entry Point
Adobe FDE Take-Home Exercise

Enterprise campaign processing with brand compliance validation
"""

import os
import sys
import yaml
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from src.campaign_processor import CampaignProcessor

def setup_logging():
    """Setup enterprise logging"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)

def load_config(config_path="config.yml"):
    """Load configuration with environment variable substitution"""
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Substitute environment variables
    def substitute_env_vars(obj):
        if isinstance(obj, dict):
            return {key: substitute_env_vars(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [substitute_env_vars(item) for item in obj]
        elif isinstance(obj, str) and obj.startswith("${") and obj.endswith("}"):
            env_var = obj[2:-1]
            return os.getenv(env_var, obj)
        else:
            return obj
    
    return substitute_env_vars(config)

def load_campaign_brief(brief_path):
    """Load campaign brief from YAML file with UTF-8 encoding"""
    
    if not Path(brief_path).exists():
        raise FileNotFoundError(f"Campaign brief not found: {brief_path}")
    
    # Explicitly use UTF-8 encoding to handle international characters
    with open(brief_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)

def main():
    """Enhanced main execution function"""
    
    logger = setup_logging()
    
    # Handle command line arguments
    if len(sys.argv) < 2:
        print("Usage: python main.py <campaign_brief.yml>")
        print("\nAvailable enterprise campaigns:")
        sample_dir = Path("data/sample_campaigns")
        if sample_dir.exists():
            for yaml_file in sample_dir.glob("*.yml"):
                print(f"  - {yaml_file}")
        else:
            print("  - No sample campaigns found")
        sys.exit(1)
    
    campaign_brief_path = sys.argv[1]
    
    try:
        # Load configuration
        config = load_config()
        logger.info("Enterprise configuration loaded successfully")
        
        # Load campaign brief - ADD UTF-8 ENCODING HERE
        with open(campaign_brief_path, 'r', encoding='utf-8') as f:
            campaign_brief = yaml.safe_load(f)
        logger.info(f"Campaign brief loaded: {campaign_brief.get('campaign_name', 'Unknown')}")
        
        # Initialize enterprise campaign processor
        processor = CampaignProcessor(config)
        
        # Display campaign overview - REMOVE EMOJIS
        print("\n" + "="*70)
        print("ENTERPRISE CREATIVE AUTOMATION PIPELINE")
        print("="*70)
        print(f"Campaign: {campaign_brief.get('campaign_name', 'Unknown')}")
        print(f"Products: {', '.join([p['name'] for p in campaign_brief.get('products', [])])}")
        print(f"Region: {campaign_brief.get('target_region', 'Unknown')}")
        print(f"Audience: {campaign_brief.get('target_audience', 'Unknown')}")
        print(f"Message: {campaign_brief.get('campaign_message', 'No message')}")
        
        if campaign_brief.get("cultural_requirements"):
            print(f"Cultural Requirements: {len(campaign_brief['cultural_requirements'])} specified")
        if campaign_brief.get("brand_guidelines"):
            print("Brand Guidelines: Specified")
        
        print("\nStarting enterprise campaign processing...")
        print("="*70)
        
        # Process campaign with full compliance checking
        campaign_result = processor.process_campaign(campaign_brief)
        
        # Generate and display comprehensive report
        report = processor.generate_campaign_report(campaign_result)
        print(report)
        
        # Save detailed results
        results_dir = Path(config["directories"]["output"]) / campaign_result["campaign_name"]
        results_dir.mkdir(parents=True, exist_ok=True)
        
        results_file = results_dir / "campaign_results.json"
        with open(results_file, 'w', encoding='utf-8') as f:  # ADD UTF-8 HERE TOO
            json.dump(campaign_result, f, indent=2, ensure_ascii=False)
        
        print(f"\nDetailed results saved to: {results_dir}")
        
        # Display processing metrics
        metrics = processor.get_processing_metrics()
        print(f"\nSYSTEM PERFORMANCE METRICS:")
        print(f"Campaigns Processed: {metrics['campaigns_processed']}")
        print(f"Average Processing Time: {metrics['average_processing_time']}s")
        
        # Final status - REMOVE EMOJIS
        if campaign_result["processing_status"] == "completed_successfully":
            print(f"\nCampaign completed successfully!")
        elif campaign_result["processing_status"] == "completed_with_issues":
            print(f"\nCampaign completed with compliance issues. Review recommendations.")
        else:
            print(f"\nCampaign processing failed: {campaign_result.get('error')}")
            sys.exit(1)
        
    except Exception as e:
        logger.error(f"Enterprise campaign processing failed: {e}")
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()