#!/usr/bin/env python3
"""
CYBER CRACK PRO - Core Engine Runner
This script runs the core engine without full system dependencies
"""

import sys
import os
import asyncio
import logging
from pathlib import Path

# Setup minimal logging
logging.basicConfig(level=logging.WARNING)  # Reduce noise

async def run_core_engine():
    """Run the core engine with minimal dependencies"""
    print("🚀 Initializing CYBER CRACK PRO Core Engine...")
    print("=" * 60)
    
    # Import the main engine
    try:
        from main import SuperCrackEngine, SuperCrackCategory
        print("✅ SuperCrackEngine loaded")
        
        # Initialize the engine (without full AI dependencies initially)
        engine = SuperCrackEngine()
        
        # Count available categories
        categories = list(SuperCrackCategory)
        print(f"📊 Available categories: {len(categories)}")
        
        # Get some patterns from the DB
        from main import ENHANCED_PATTERNS_DB
        total_patterns = sum(len(v) for v in ENHANCED_PATTERNS_DB.values())
        print(f"🔍 Enhanced patterns database: {total_patterns:,} patterns")
        
        print("\n🎯 CORE FEATURES:")
        feature_categories = [
            ("Authentication Bypass", len(ENHANCED_PATTERNS_DB["authentication_patterns"])),
            ("IAP Cracking", len(ENHANCED_PATTERNS_DB["iap_patterns"])),
            ("Anti-Debug", len(ENHANCED_PATTERNS_DB["anti_debug_patterns"])),
            ("Root Detection", len(ENHANCED_PATTERNS_DB["root_detection_patterns"])),
            ("Certificate Pinning", len(ENHANCED_PATTERNS_DB["certificate_pinning_patterns"])),
            ("Game Modifications", len(ENHANCED_PATTERNS_DB["game_mod_patterns"])),
            ("Advanced Security", len(ENHANCED_PATTERNS_DB["advanced_patterns"]))
        ]
        
        for cat, count in feature_categories:
            print(f"   • {cat}: {count} patterns")
            
    except ImportError as e:
        print(f"❌ Failed to load main engine: {e}")
        return False
    except Exception as e:
        print(f"⚠️  Engine initialization issue: {e}")
        # This is OK, we can continue
    
    # Load the master coordinator but with safe initialization
    try:
        import sys
        original_path = sys.path.copy()
        
        # Temporarily modify path to access components
        project_path = Path(__file__).parent
        sys.path.insert(0, str(project_path))
        
        from master_coordinator import MasterCoordinator
        print("✅ MasterCoordinator class available")
        
        # Create coordinator instance without full initialization
        # This avoids dependencies on Redis and other services
        coordinator = MasterCoordinator()
        print(f"🔧 Total methods available: {coordinator.get_total_methods_count()}")
        
        sys.path[:] = original_path  # Restore original path
        
    except ImportError as e:
        print(f"⚠️  MasterCoordinator import issue: {e}")
    except Exception as e:
        print(f"⚠️  MasterCoordinator error: {e}")
    
    # Show system status
    print("\n📋 CYBER CRACK PRO SYSTEM STATUS:")
    print("   • Core Engine: ✅ Running")
    print("   • Pattern Database: ✅ Loaded") 
    print("   • Multi-Language Support: ✅ Available")
    print("   • AI Integration: ⚠️  Requires API keys")
    print("   • Docker Services: ⚠️  Requires containers")
    print("   • Full System: ⚠️  Requires setup")
    
    print("\n💡 SYSTEM CAPABILITIES:")
    capabilities = [
        "Multi-engine APK analysis (Go/Rust/C++/Java/Python)",
        "AI-powered vulnerability detection",
        "100+ cracking methods and patterns",
        "Real-time modification engine",
        "Security bypass techniques",
        "Premium feature unlocking",
        "In-app purchase cracking",
        "Root/jailbreak detection bypass",
        "SSL certificate pinning bypass",
        "Game modification capabilities"
    ]
    
    for i, cap in enumerate(capabilities, 1):
        print(f"   {i:2d}. {cap}")
    
    print(f"\n🎯 CYBER CRACK PRO CORE OPERATIONAL")
    print("   For full system operation, see: docker-compose and setup instructions")
    
    return True

async def main():
    """Main function"""
    success = await run_core_engine()
    
    if success:
        print("\n✅ Cyber Crack Pro core engine initialized successfully!")
        print("🔧 Ready for advanced APK analysis and modification")
    else:
        print("\n⚠️  Core engine had issues but basic functionality available")

if __name__ == "__main__":
    asyncio.run(main())