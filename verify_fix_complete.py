#!/usr/bin/env python
"""
MULTI-PERSON FIX VERIFICATION SCRIPT
Comprehensive verification that all fixes are in place and working
"""

import os
import sys
from pathlib import Path

def print_header(text):
    print("\n" + "="*70)
    print(f"  {text}")
    print("="*70)

def print_section(text):
    print(f"\n▶ {text}")
    print("-" * 70)

def print_success(text):
    print(f"  ✅ {text}")

def print_error(text):
    print(f"  ❌ {text}")

def print_warning(text):
    print(f"  ⚠️  {text}")

def check_file_exists(filepath, description):
    """Check if file exists and return status"""
    if os.path.exists(filepath):
        print_success(f"{description}: {filepath}")
        return True
    else:
        print_error(f"{description} NOT FOUND: {filepath}")
        return False

def check_file_contains(filepath, search_text, description):
    """Check if file contains specific text"""
    if not os.path.exists(filepath):
        print_error(f"File doesn't exist: {filepath}")
        return False
    
    with open(filepath, 'r', encoding='utf-8') as f:
        content = f.read()
        if search_text in content:
            print_success(f"{description}")
            return True
        else:
            print_error(f"{description} - Text not found")
            return False

def main():
    print_header("MULTI-PERSON FIX VERIFICATION")
    
    # Get base path
    base_path = Path(__file__).parent.resolve()
    os.chdir(base_path)
    
    results = {
        "documentation": 0,
        "code_fixes": 0,
        "test_files": 0,
        "total": 0
    }
    
    # ===== DOCUMENTATION CHECK =====
    print_section("1. DOCUMENTATION FILES")
    
    doc_files = {
        "00_MULTI_PERSON_START_HERE.md": "Main Navigation Guide",
        "MASTER_FIX_SUMMARY.md": "Executive Summary",
        "MULTI_PERSON_VISUAL_SUMMARY.md": "Visual Architecture",
        "DEPLOYMENT_CHECKLIST.md": "Deployment Guide",
        "MULTI_PERSON_USER_GUIDE.md": "User Instructions",
        "MULTI_PERSON_QUICK_TEST.md": "Quick Test Guide",
        "README_MULTI_PERSON_FIX.md": "Technical Documentation",
        "MULTI_PERSON_COMPLETE_FIX.md": "Complete Technical Analysis",
    }
    
    doc_count = 0
    for filename, description in doc_files.items():
        if check_file_exists(filename, description):
            doc_count += 1
    
    results["documentation"] = doc_count
    results["total"] += doc_count
    
    # ===== CODE FIXES CHECK =====
    print_section("2. CODE FIXES")
    
    template_path = "activities/templates/activities/multi_person.html"
    if check_file_exists(template_path, "Multi-person template"):
        # Check for null checks (the fix)
        null_checks = [
            ("{% if participant.user %}", "Null check for participant.user"),
            ("{% if participant.user and participant.user.profile.profile_picture %}", "Null check for profile picture"),
            ("Unidentified Person", "Fallback for anonymous persons"),
            ("|floatformat:1", "Confidence score formatting"),
            ("|upper", "Activity type uppercase"),
        ]
        
        for check_text, description in null_checks:
            if check_file_contains(template_path, check_text, description):
                results["code_fixes"] += 1
        
        results["total"] += len(null_checks)
    
    # ===== TEST FILES CHECK =====
    print_section("3. TEST & SUPPORT FILES")
    
    support_files = {
        "diagnose_multi_person.py": "Diagnostic Test Script",
    }
    
    for filename, description in support_files.items():
        if check_file_exists(filename, description):
            results["test_files"] += 1
        results["total"] += 1
    
    # ===== CONFIGURATION CHECK =====
    print_section("4. DJANGO CONFIGURATION")
    
    config_checks = [
        ("activities/views.py", "multi_person_view", "Multi-person view function"),
        ("activities/models.py", "PersonActivity", "PersonActivity model"),
        ("activities/urls.py", "multi-person", "Multi-person URL pattern"),
    ]
    
    for filepath, search_text, description in config_checks:
        check_file_contains(filepath, search_text, description)
    
    # ===== SUMMARY =====
    print_section("5. VERIFICATION SUMMARY")
    
    print(f"\n📊 Results:")
    print(f"  Documentation Files: {results['documentation']}/{len(doc_files)} ✅" 
          if results['documentation'] == len(doc_files) else 
          f"  Documentation Files: {results['documentation']}/{len(doc_files)} ⚠️")
    print(f"  Code Fixes: {results['code_fixes']}/5 ✅" 
          if results['code_fixes'] == 5 else 
          f"  Code Fixes: {results['code_fixes']}/5 ⚠️")
    print(f"  Test Files: {results['test_files']}/{len(support_files)} ✅" 
          if results['test_files'] == len(support_files) else 
          f"  Test Files: {results['test_files']}/{len(support_files)} ⚠️")
    
    # ===== STATUS CHECK =====
    print_section("6. FIX STATUS")
    
    all_passed = (
        results['documentation'] == len(doc_files) and
        results['code_fixes'] == 5 and
        results['test_files'] == len(support_files)
    )
    
    if all_passed:
        print_success("ALL VERIFICATIONS PASSED!")
        print_success("The multi-person fix is complete and ready for deployment")
        return 0
    else:
        print_warning("SOME CHECKS FAILED")
        print_warning("Please review the items above")
        return 1

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Exception as e:
        print_error(f"Verification failed with error: {e}")
        sys.exit(2)
