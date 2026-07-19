# MRL_Batch_Test_Install Test Script
# Developed by Kevin Kuhn (Mining Raw Letters)

"""
Test script for MRL Batch Test Install extension.
Run this from RoboFont's scripting window to test the extension.
"""

import sys
import os
import traceback
from mojo.roboFont import OpenWindow

# Add the lib directory to the path so we can import our module
lib_path = os.path.dirname(__file__)
if lib_path not in sys.path:
    sys.path.insert(0, lib_path)

try:
    import mrl_batch_test_install
    
    # Test 1: Try to import the controller
    print("✓ Successfully imported mrl_batch_test_install module")
    
    # Test 2: Check if controller class exists
    if hasattr(mrl_batch_test_install, 'MrlBatchTestInstallController'):
        print("✓ MrlBatchTestInstallController class found")
        
        # Test 3: Try to create an instance
        try:
            controller = mrl_batch_test_install.MrlBatchTestInstallController()
            print("✓ Successfully created controller instance")
            
            # Test 4: Try to open the window
            try:
                OpenWindow(mrl_batch_test_install.MrlBatchTestInstallController)
                print("✓ Successfully opened MRL Batch Test Install window")
                print("\n🎉 Extension test completed successfully!")
                print("The MRL Batch Test Install extension is ready to use.")
                
            except Exception as window_error:
                print(f"✗ Error opening window: {window_error}")
                traceback.print_exc()
                
        except Exception as instance_error:
            print(f"✗ Error creating controller instance: {instance_error}")
            traceback.print_exc()
            
    else:
        print("✗ MrlBatchTestInstallController class not found")
        
except ImportError as import_error:
    print(f"✗ Import error: {import_error}")
    print("Make sure the extension is properly installed.")
    traceback.print_exc()
    
except Exception as general_error:
    print(f"✗ Unexpected error: {general_error}")
    traceback.print_exc()
    
print("\n" + "="*50)
print("MRL Batch Test Install Extension Test Complete")
print("="*50) 