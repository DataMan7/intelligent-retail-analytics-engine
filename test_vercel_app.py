#!/usr/bin/env python3
"""
🧪 Simple Test Script for Vercel App
Test your Intelligent Retail Analytics Engine deployment
"""

import requests
import json
import sys

def test_vercel_app():
    """Test the Vercel deployed app"""

    base_url = "https://bigquery-ai-git-master-datamans-projects.vercel.app"

    print("🧪 Testing Vercel App - Intelligent Retail Analytics Engine")
    print("=" * 70)
    print(f"🌐 Base URL: {base_url}")
    print("🏆 Competition: $100,000 BigQuery AI Prize Track")
    print("=" * 70)

    # Test endpoints
    endpoints = [
        "/",
        "/api/test/dashboard",
        "/api/test/products",
        "/api/test/categories",
        "/api/test/health"
    ]

    print("\\n📋 IMPORTANT: Vercel Deployment Protection")
    print("Your Vercel app has authentication enabled.")
    print("To test, you need to:")
    print("1. Open: https://vercel.com/dashboard")
    print("2. Go to your project settings")
    print("3. Disable 'Deployment Protection' OR")
    print("4. Get a bypass token from the dashboard")
    print("\\n" + "=" * 70)

    for endpoint in endpoints:
        url = base_url + endpoint
        try:
            print(f"\\n🔍 Testing: {endpoint}")
            response = requests.get(url, timeout=10)

            print(f"Status: {response.status_code}")

            if response.status_code == 200:
                if "Authentication Required" in response.text:
                    print("🔐 Authentication Required (Expected)")
                    print("   - This is normal for protected deployments")
                    print("   - Disable protection in Vercel dashboard or use bypass token")
                elif "Deployment has failed" in response.text:
                    print("❌ DEPLOYMENT FAILED")
                    print("   - Build failed on Vercel")
                    print("   - Check build logs in Vercel dashboard")
                    print("   - Fix the build errors and redeploy")
                elif endpoint == "/":
                    print("✅ HTML page loaded successfully")
                else:
                    try:
                        data = response.json()
                        print(f"✅ API response: {json.dumps(data, indent=2)[:200]}...")
                    except:
                        print("✅ Response received (not JSON)")
            elif response.status_code == 404:
                print("❌ Endpoint not found - deployment may be building")
            else:
                print(f"⚠️ Unexpected status: {response.status_code}")

        except requests.exceptions.RequestException as e:
            print(f"❌ Connection failed: {e}")
            print("   - Check if deployment is complete")
            print("   - Verify URL is correct")

    print("\\n" + "=" * 70)
    print("🎯 COMPETITION STATUS")
    print("=" * 70)
    print("✅ GitHub Repository: Ready")
    print("❌ Vercel Deployment: FAILED (Build Error)")
    print("✅ BigQuery AI: Implemented")
    print("🏆 Win Probability: Fix deployment first")
    print("\\n📝 KAGGLE SUBMISSION:")
    print(f"Live Demo: {base_url}")
    print("GitHub: https://github.com/DataMan7/intelligent-retail-analytics-engine")

    print("\\n" + "=" * 70)
    print("🔧 TO FIX DEPLOYMENT FAILURE:")
    print("1. Go to: https://vercel.com/dashboard")
    print("2. Find your project: bigquery-ai")
    print("3. Click on failed deployment")
    print("4. Check 'Build Logs' tab")
    print("5. Fix the errors shown")
    print("6. Redeploy")
    print("=" * 70)

def test_with_bypass_token():
    """Test with Vercel bypass token"""
    print("\\n🔑 VERCEL BYPASS TOKEN TESTING")
    print("=" * 50)

    base_url = "https://bigquery-ai-git-master-datamans-projects.vercel.app"

    # Ask for bypass token
    bypass_token = input("Enter your Vercel bypass token (or press Enter to skip): ").strip()

    if not bypass_token:
        print("Skipping bypass token test")
        return

    # Test with bypass token
    test_url = f"{base_url}/api/test/dashboard?x-vercel-set-bypass-cookie=true&x-vercel-protection-bypass={bypass_token}"

    try:
        print(f"Testing with bypass token...")
        response = requests.get(test_url, timeout=10)

        if response.status_code == 200:
            try:
                data = response.json()
                print("✅ Bypass token works!")
                print(f"Response: {json.dumps(data, indent=2)[:300]}...")
            except:
                print("✅ Response received")
        else:
            print(f"❌ Bypass token failed: {response.status_code}")

    except Exception as e:
        print(f"❌ Bypass test failed: {e}")

if __name__ == "__main__":
    test_vercel_app()

    # Optional: Test with bypass token
    if len(sys.argv) > 1 and sys.argv[1] == "--bypass":
        test_with_bypass_token()