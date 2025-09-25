#!/usr/bin/env bash
set -euo pipefail

echo "==> Init git"
git init
git branch -m main

echo "==> Python 3.13 venv"
python -m venv .venv
source .venv/Scripts/activate

echo "==> Upgrade pip"
python -m pip install --upgrade pip

echo "==> Make dirs"
mkdir -p src/{pipeline,adapters,compliance,localization,utils} \
         assets/{fonts,templates} briefs outputs diagrams tests .vscode

echo "==> Write starter files"

cat > README.md << 'R'
# Creative Automation Pipeline

Enterprise-grade pipeline for brand-compliant social creative at scale.
R

cat > requirements.txt << 'R'
openai>=1.40.0
Pillow>=10.4.0
PyYAML>=6.0.2
python-dotenv>=1.0.1
loguru>=0.7.2
redis>=5.0.7
tenacity>=8.5.0
pydantic>=2.8.2
# Optional fallback provider:
# stability-sdk
R

cat > .env.example << 'R'
OPENAI_API_KEY=sk-...
STABILITY_API_KEY=...
ASSET_BUCKET_URI=s3://your-bucket/prefix
DEFAULT_FONT_PATH=./assets/fonts/Inter-Regular.ttf
R

cat > .gitignore << 'R'
.venv/
__pycache__/
*.py[cod]
.env
.vscode/
.idea/
R

cat > src/main.py << 'R'
def main():
    print("Creative Automation Pipeline - skeleton ready")

if __name__ == "__main__":
    main()
R

cat > briefs/sample_campaign.yaml << 'R'
campaign:
  name: "Global Sparkle Refresh Q4"
  start_date: 2025-10-01
  regions: ["US", "JP", "DE", "AE"]
  objectives:
    - brand_awareness
    - product_launch
products:
  - id: "sparkle-zero"
    name: "Sparkle Zero"
    key_messages:
      en: "Zero sugar. 100% sparkle."
      de: "Null Zucker. 100% Sprudel."
      ja: "砂糖ゼロ。100%スパークル。"
      ar: "بدون سكر. تألق ١٠٠٪."
    brand_colors: ["#E4002B", "#FFFFFF", "#000000"]
    logo_path: "assets/templates/sparkle-logo.png"
    fallback_images:
      - "assets/templates/sparkle-fallback-1.jpg"
      - "assets/templates/sparkle-fallback-2.jpg"
audiences:
  primary:
    - "Gen Z beverage explorers"
    - "Fitness-minded adults"
formats:
  - ratio: "1:1"
  - ratio: "9:16"
  - ratio: "16:9"
R

cat > .vscode/settings.json << 'R'
{
  "python.defaultInterpreterPath": "${workspaceFolder}/.venv/Scripts/python.exe",
  "terminal.integrated.defaultProfile.windows": "Git Bash",
  "editor.formatOnSave": true,
  "files.eol": "\n"
}
R

echo "==> Install deps"
pip install -r requirements.txt

echo "==> First commit"
git add .
git commit -m "chore: scaffold repo (py3.13), venv, requirements, sample brief"
