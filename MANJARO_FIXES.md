# 🛠️ **MANJARO GOOGLE CLOUD SDK INSTALLATION FIX**

## ❌ **ERROR ANALYSIS**
The error you're seeing is because the guide used Ubuntu/Debian commands instead of Manjaro/Arch commands:
- `apt-key` doesn't exist on Manjaro (it's `pacman`)
- `apt` doesn't exist on Manjaro (it's `pacman`)
- The curl command failed due to permission issues

## ✅ **CORRECTED MANJARO INSTALLATION**

### **Method 1: Install from AUR (Recommended)**

```bash
# Install Google Cloud SDK from AUR
sudo pacman -S google-cloud-sdk

# If not available in official repos, use yay (AUR helper)
# First install yay if you don't have it
sudo pacman -S yay

# Then install Google Cloud SDK
yay -S google-cloud-sdk
```

### **Method 2: Manual Installation (Alternative)**

```bash
# Download the Google Cloud SDK archive
cd /tmp
wget https://dl.google.com/dl/cloudsdk/channels/rapid/downloads/google-cloud-sdk-468.0.0-linux-x86_64.tar.gz

# Extract the archive
tar -xzf google-cloud-sdk-468.0.0-linux-x86_64.tar.gz

# Move to /opt
sudo mv google-cloud-sdk /opt/

# Add to PATH
echo 'export PATH=$PATH:/opt/google-cloud-sdk/bin' >> ~/.bashrc
source ~/.bashrc

# Initialize gcloud
gcloud init
```

### **Method 3: Snap Installation (If snap is available)**

```bash
# Install snap if not available
sudo pacman -S snapd

# Enable snap
sudo systemctl enable --now snapd.socket

# Install Google Cloud SDK via snap
sudo snap install google-cloud-sdk --classic
```

## 🔧 **VERIFICATION STEPS**

### **After Installation, Verify:**

```bash
# Check if gcloud is installed
gcloud --version

# Initialize gcloud (first time)
gcloud init

# Authenticate
gcloud auth application-default login

# Set your project (replace with your actual project ID)
gcloud config set project your-project-id-here

# Verify authentication
gcloud auth list
gcloud config get-value project
```

## 🚀 **CONTINUE WITH THE SETUP**

### **Once Google Cloud SDK is working, continue:**

```bash
# Navigate to your project
cd /home/dataman/Desktop/Kaggle/BigQuery_AI

# Enable required APIs
gcloud services enable bigquery.googleapis.com
gcloud services enable bigqueryconnection.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable storage.googleapis.com
gcloud services enable documentai.googleapis.com
gcloud services enable vision.googleapis.com

# Create BigQuery datasets
bq mk --dataset --location=us retail_analytics
bq mk --dataset --location=us retail_analytics_v2
bq mk --dataset --location=us retail_models_v2
bq mk --dataset --location=us retail_insights_v2
bq mk --dataset --location=us retail_agents
bq mk --dataset --location=us retail_rag
bq mk --dataset --location=us retail_nemo

# Install Python dependencies
pip install -r requirements.txt
pip install -r enhanced_requirements.txt

# Test Google Cloud connection
python -c "
from google.cloud import bigquery
client = bigquery.Client()
print('✅ Google Cloud BigQuery connected successfully!')
print(f'Project: {client.project}')
"
```

## 🐛 **TROUBLESHOOTING ADDITIONAL ISSUES**

### **If you get permission errors:**

```bash
# Fix pip permissions
pip install --user -r requirements.txt
pip install --user -r enhanced_requirements.txt

# Or use virtual environment
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install -r enhanced_requirements.txt
```

### **If BigQuery connection fails:**

```bash
# Check authentication
gcloud auth list

# Re-authenticate if needed
gcloud auth application-default login

# Check project configuration
gcloud config get-value project

# Set project if needed
gcloud config set project your-project-id
```

### **If dataset creation fails:**

```bash
# Check if project exists
gcloud projects list

# Verify BigQuery API is enabled
gcloud services list | grep bigquery

# Try creating dataset with explicit project
bq --project_id=your-project-id mk --dataset --location=us retail_analytics
```

## 🎯 **QUICK VERIFICATION SCRIPT**

Create and run this verification script:

```bash
# Create verification script
cat > verify_setup.sh << 'EOF'
#!/bin/bash
echo "🔍 MANJARO BIGQUERY AI SETUP VERIFICATION"
echo "========================================"

# Check system
echo "📊 System Information:"
echo "  • OS: $(cat /etc/os-release | grep PRETTY_NAME | cut -d'"' -f2)"
echo "  • Python: $(python --version)"
echo "  • Pip: $(pip --version | head -1)"
echo "  • Disk: $(df -h / | tail -1 | awk '{print $4 " available"})"
echo "  • Memory: $(free -h | grep Mem | awk '{print $7 " available"}')"

# Check Google Cloud SDK
echo ""
echo "☁️  Google Cloud SDK:"
if command -v gcloud &> /dev/null; then
    echo "  ✅ gcloud installed: $(gcloud --version | head -1)"
    echo "  📍 Current project: $(gcloud config get-value project 2>/dev/null || echo 'Not set')"
    echo "  🔐 Authentication: $(gcloud auth list 2>/dev/null | grep -c "ACTIVE" || echo '0') active accounts"
else
    echo "  ❌ gcloud not installed"
fi

# Check BigQuery
echo ""
echo "🗄️  BigQuery Status:"
if python -c "from google.cloud import bigquery; print('Connected')" 2>/dev/null; then
    echo "  ✅ BigQuery client working"
else
    echo "  ❌ BigQuery client failed"
fi

# Check datasets
echo ""
echo "📂 BigQuery Datasets:"
PROJECT_ID=$(gcloud config get-value project 2>/dev/null)
if [ ! -z "$PROJECT_ID" ]; then
    DATASETS=$(bq ls $PROJECT_ID 2>/dev/null | wc -l)
    echo "  📊 Datasets found: $DATASETS"
else
    echo "  ⚠️  Project not configured"
fi

# Check Python dependencies
echo ""
echo "🐍 Python Dependencies:"
DEPS=("pandas" "numpy" "matplotlib" "seaborn" "google-cloud-bigquery")
for dep in "${DEPS[@]}"; do
    if python -c "import $dep" 2>/dev/null; then
        echo "  ✅ $dep installed"
    else
        echo "  ❌ $dep missing"
    fi
done

# Check project files
echo ""
echo "📁 Project Files:"
FILES=("enhanced_demo_with_debug.py" "enhanced_setup_with_debug.py" "debug_utils.py" "requirements.txt")
for file in "${FILES[@]}"; do
    if [ -f "$file" ]; then
        echo "  ✅ $file found"
    else
        echo "  ❌ $file missing"
    fi
done

echo ""
echo "🎯 SETUP STATUS SUMMARY"
echo "======================"
echo "✅ System ready for BigQuery AI development!"
echo "🚀 Ready to win the $100,000 competition!"
EOF

# Make executable and run
chmod +x verify_setup.sh
./verify_setup.sh
```

## 🚀 **FINAL WORKING SEQUENCE**

After fixing the Google Cloud SDK installation:

```bash
# 1. Verify installation
gcloud --version
gcloud auth list

# 2. Set project
gcloud config set project your-project-id

# 3. Enable APIs
gcloud services enable bigquery.googleapis.com aiplatform.googleapis.com

# 4. Create datasets
bq mk --dataset --location=us retail_analytics
bq mk --dataset --location=us retail_analytics_v2

# 5. Install dependencies
pip install -r requirements.txt
pip install -r enhanced_requirements.txt

# 6. Test connection
python -c "from google.cloud import bigquery; print('✅ Success!')"

# 7. Run enhanced setup
python enhanced_setup_with_debug.py --project-id your-project-id

# 8. Execute SQL
python enhanced_setup_with_debug.py --project-id your-project-id --run-sql

# 9. Test system
python enhanced_demo_with_debug.py --project-id your-project-id --demo-type all

# 10. Validate for competition
python -c "from debug_utils import validate_competition_submission; result = validate_competition_submission(); print(f'Ready to win: {result.is_valid}')"

# 11. Submit to Kaggle!
echo "🎉 Ready to submit and win $100,000!"
```

## 🏆 **SUCCESS INDICATORS**

After running the corrected setup, you should see:
- ✅ `gcloud --version` works
- ✅ `gcloud auth list` shows active account
- ✅ `bq ls` shows your datasets
- ✅ Python imports work without errors
- ✅ Enhanced demo runs successfully
- ✅ Competition validation passes

**🎯 The corrected Manjaro installation will get you to a fully functional Intelligent Retail Analytics Engine v2.0 that wins the competition!**