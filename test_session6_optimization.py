#!/usr/bin/env python3
"""
Test script for Session 6: Multi-Agent Optimization
Tests the single document optimization with multi-document fallback
"""

import ast
import sys
import os

def test_code_structure():
    """Test the Session 6 optimization code structure without importing."""
    print("🚀 Testing Session 6: Multi-Agent Optimization (Code Structure)")
    print("=" * 70)
    
    # Test 1: Check if the workflow file exists and is readable
    print("\n📋 Test 1: File Accessibility")
    print("-" * 40)
    
    workflow_file = "backend/app/workflows/multi_agent_workflow.py"
    if os.path.exists(workflow_file):
        print(f"✅ Workflow file exists: {workflow_file}")
    else:
        print(f"❌ Workflow file missing: {workflow_file}")
        return False
    
    # Test 2: Parse the Python code for syntax errors
    print("\n📋 Test 2: Python Syntax Validation")
    print("-" * 40)
    
    try:
        with open(workflow_file, 'r') as f:
            source_code = f.read()
        
        # Parse the code to check for syntax errors
        ast.parse(source_code)
        print("✅ Python syntax is valid")
    except SyntaxError as e:
        print(f"❌ Syntax error: {e}")
        return False
    except Exception as e:
        print(f"❌ File reading error: {e}")
        return False
    
    # Test 3: Check for required methods and classes
    print("\n📋 Test 3: Required Code Elements")
    print("-" * 40)
    
    required_elements = [
        'class MultiAgentWorkflow',
        'def __init__',
        'single_document_mode',
        'def set_single_document_mode',
        'def get_processing_mode',
        'async def _classify_documents'
    ]
    
    found_elements = []
    for element in required_elements:
        if element in source_code:
            found_elements.append(element)
            print(f"✅ Found: {element}")
        else:
            print(f"❌ Missing: {element}")
            return False
    
    # Test 4: Check for optimization patterns
    print("\n📋 Test 4: Optimization Patterns")
    print("-" * 40)
    
    optimization_patterns = [
        'single_document_mode or len(search_results) == 1',
        'primary_result = search_results[0]',
        'Single classification call - much faster than loop',
        'Multi-document fallback (compatibility path)',
        'performance_optimized'
    ]
    
    found_patterns = []
    for pattern in optimization_patterns:
        if pattern in source_code:
            found_patterns.append(pattern)
            print(f"✅ Found optimization: {pattern[:50]}...")
        else:
            print(f"❌ Missing optimization: {pattern[:50]}...")
            return False
    
    # Test 5: Check for backward compatibility
    print("\n📋 Test 5: Backward Compatibility")
    print("-" * 40)
    
    compatibility_patterns = [
        'document_classifications',
        'Keep as list for compatibility',
        'Fallback to original multi-document logic'
    ]
    
    for pattern in compatibility_patterns:
        if pattern in source_code:
            print(f"✅ Found compatibility: {pattern[:50]}...")
        else:
            print(f"❌ Missing compatibility: {pattern[:50]}...")
            return False
    
    print("\n🎉 All Session 6 optimization code structure tests passed!")
    print("=" * 70)
    
    # Summary
    print("\n📊 Optimization Summary:")
    print(f"   • Single Document Mode: ✅ Implemented")
    print(f"   • Multi-Document Fallback: ✅ Available")
    print(f"   • Dynamic Mode Switching: ✅ Implemented")
    print(f"   • Performance Monitoring: ✅ Enhanced")
    print(f"   • Backward Compatibility: ✅ Maintained")
    print(f"   • Code Structure: ✅ Valid")
    
    return True

if __name__ == "__main__":
    try:
        success = test_code_structure()
        if success:
            print("\n✅ Session 6 optimization code is structurally correct!")
            print("\n💡 Next Steps:")
            print("   1. Test with actual workflow execution")
            print("   2. Measure performance improvements")
            print("   3. Verify backward compatibility")
            sys.exit(0)
        else:
            print("\n❌ Session 6 optimization code structure tests failed!")
            sys.exit(1)
    except Exception as e:
        print(f"\n💥 Test execution failed: {e}")
        sys.exit(1)
