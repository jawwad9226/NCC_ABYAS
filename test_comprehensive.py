#!/usr/bin/env python3
"""
Comprehensive Testing Script for NCC ABYAS
Tests all Phase 3 features and Phase 4 optimizations
"""

import sys
import os
import time
import json
import requests
from typing import Dict, List, Any

# Add the project directory to Python path
sys.path.insert(0, '/home/jawwad-linux/Documents/NCC_ABYAS')

class NCC_ABYAS_Tester:
    """Comprehensive testing suite for NCC ABYAS application"""
    
    def __init__(self):
        self.test_results = {
            "passed": 0,
            "failed": 0,
            "errors": [],
            "performance_metrics": {}
        }
        self.start_time = time.time()
    
    def log_test(self, test_name: str, success: bool, message: str = ""):
        """Log test result"""
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"{status}: {test_name}")
        if message:
            print(f"   {message}")
        
        if success:
            self.test_results["passed"] += 1
        else:
            self.test_results["failed"] += 1
            self.test_results["errors"].append(f"{test_name}: {message}")
    
    def test_module_imports(self) -> None:
        """Test that all critical modules can be imported"""
        print("\n🧪 Testing Module Imports...")
        
        critical_modules = [
            'main', 'security', 'chat_interface', 'quiz_interface',
            'gamification', 'offline_manager', 'mobile_ui', 'accessibility',
            'chat_enhancements', 'quiz_analytics'
        ]
        
        for module in critical_modules:
            try:
                __import__(module)
                self.log_test(f"Import {module}", True)
            except Exception as e:
                self.log_test(f"Import {module}", False, str(e))
    
    def test_security_functions(self) -> None:
        """Test security module functionality"""
        print("\n🔒 Testing Security Functions...")
        
        try:
            from security import SecurityValidator, RateLimiter, secure_chat_input
            
            # Test SecurityValidator
            validator = SecurityValidator()
            
            # Test input sanitization
            dirty_input = '<script>alert("xss")</script>Hello'
            clean_input = validator.sanitize_input(dirty_input)
            self.log_test("XSS sanitization", '<script>' not in clean_input)
            
            # Test email validation
            valid_email = validator.validate_email("test@example.com")
            invalid_email = validator.validate_email("invalid-email")
            self.log_test("Email validation", valid_email and not invalid_email)
            
            # Test rate limiter
            limiter = RateLimiter()
            has_method = hasattr(limiter, 'check_rate_limit')
            self.log_test("RateLimiter.check_rate_limit exists", has_method)
            
            # Test secure chat input
            chat_result = secure_chat_input("Hello, this is a test message!")
            self.log_test("Secure chat input", chat_result.get('valid', False))
            
        except Exception as e:
            self.log_test("Security module", False, str(e))
    
    def test_gamification_system(self) -> None:
        """Test gamification features"""
        print("\n🎮 Testing Gamification System...")
        
        try:
            from gamification import BadgeSystem, award_xp
            
            # Test badge system
            badge_system = BadgeSystem()
            badges = badge_system.BADGES
            self.log_test("Badge system loaded", len(badges) > 0)
            
            # Test that award_xp function exists and is callable
            self.log_test("XP award function", callable(award_xp))
            
        except Exception as e:
            self.log_test("Gamification system", False, str(e))
    
    def test_offline_functionality(self) -> None:
        """Test offline manager and PWA features"""
        print("\n📱 Testing Offline Functionality...")
        
        try:
            from offline_manager import OfflineManager
            
            # Test offline manager initialization
            OfflineManager.init_offline_storage()
            self.log_test("Offline storage initialization", True)
            
            # Check if PWA files exist
            manifest_exists = os.path.exists('data/manifest.json')
            sw_exists = os.path.exists('data/service-worker.js')
            
            self.log_test("PWA manifest exists", manifest_exists)
            self.log_test("Service worker exists", sw_exists)
            
        except Exception as e:
            self.log_test("Offline functionality", False, str(e))
    
    def test_chat_enhancements(self) -> None:
        """Test chat enhancements and analytics"""
        print("\n💬 Testing Chat Enhancements...")
        
        try:
            from chat_enhancements import ChatEnhancements
            
            # Test chat enhancements initialization
            chat_enhancer = ChatEnhancements()
            self.log_test("Chat enhancements initialization", True)
            
            # Test message formatting
            markdown_text = "**Bold** and *italic* text"
            formatted = chat_enhancer.format_message_content(markdown_text)
            self.log_test("Markdown formatting", len(formatted) > len(markdown_text))
            
        except Exception as e:
            self.log_test("Chat enhancements", False, str(e))
    
    def test_quiz_analytics(self) -> None:
        """Test quiz analytics functionality"""
        print("\n📊 Testing Quiz Analytics...")
        
        try:
            # Just test that the module imports correctly
            import quiz_analytics
            
            # Test that key functions exist
            has_analytics_function = hasattr(quiz_analytics, 'create_quiz_performance_summary')
            self.log_test("Quiz analytics functions exist", has_analytics_function)
            
        except Exception as e:
            self.log_test("Quiz analytics", False, str(e))
    
    def test_mobile_ui(self) -> None:
        """Test mobile UI components"""
        print("\n📱 Testing Mobile UI...")
        
        try:
            from mobile_ui import inject_mobile_css, create_card
            
            # Test CSS injection function exists
            self.log_test("Mobile CSS injection function", callable(inject_mobile_css))
            
            # Test card creation function
            self.log_test("Card creation function", callable(create_card))
            
        except Exception as e:
            self.log_test("Mobile UI", False, str(e))
    
    def test_accessibility_features(self) -> None:
        """Test accessibility features"""
        print("\n♿ Testing Accessibility Features...")
        
        try:
            from accessibility import inject_accessibility_css, add_skip_navigation
            
            # Test accessibility functions exist
            self.log_test("Accessibility CSS injection", callable(inject_accessibility_css))
            self.log_test("Skip navigation function", callable(add_skip_navigation))
            
        except Exception as e:
            self.log_test("Accessibility features", False, str(e))
    
    def test_performance_optimizations(self) -> None:
        """Test performance optimizations"""
        print("\n⚡ Testing Performance Optimizations...")
        
        try:
            # Test import time for main module
            start_time = time.time()
            import main
            import_time = time.time() - start_time
            
            self.log_test("Main module import time", import_time < 2.0, f"{import_time:.3f}s")
            self.test_results["performance_metrics"]["import_time"] = import_time
            
            # Test function performance
            start_time = time.time()
            base64_data = main.get_image_as_base64('data/logo.svg')
            function_time = time.time() - start_time
            
            self.log_test("Image base64 conversion", len(base64_data) > 0, f"{function_time:.3f}s")
            self.test_results["performance_metrics"]["image_conversion_time"] = function_time
            
        except Exception as e:
            self.log_test("Performance optimizations", False, str(e))
    
    def test_application_startup(self) -> None:
        """Test application startup and basic functionality"""
        print("\n🚀 Testing Application Startup...")
        
        try:
            # Test that main app can be imported without errors
            import main
            self.log_test("Main application import", True)
            
            # Test core utilities
            from core_utils import setup_gemini, Config
            
            # Test configuration
            config_valid = hasattr(Config, 'BASE_DIR') and hasattr(Config, 'DATA_DIR')
            self.log_test("Configuration loaded", config_valid)
            
        except Exception as e:
            self.log_test("Application startup", False, str(e))
    
    def run_all_tests(self) -> Dict[str, Any]:
        """Run comprehensive test suite"""
        print("🧪 Starting NCC ABYAS Comprehensive Test Suite...")
        print("=" * 60)
        
        # Run all test categories
        self.test_application_startup()
        self.test_module_imports()
        self.test_security_functions()
        self.test_gamification_system()
        self.test_offline_functionality()
        self.test_chat_enhancements()
        self.test_quiz_analytics()
        self.test_mobile_ui()
        self.test_accessibility_features()
        self.test_performance_optimizations()
        
        # Calculate total test time
        total_time = time.time() - self.start_time
        self.test_results["performance_metrics"]["total_test_time"] = total_time
        
        # Print summary
        print("\n" + "=" * 60)
        print("🎯 TEST SUMMARY")
        print("=" * 60)
        print(f"✅ Tests Passed: {self.test_results['passed']}")
        print(f"❌ Tests Failed: {self.test_results['failed']}")
        print(f"⏱️  Total Time: {total_time:.2f}s")
        
        if self.test_results["errors"]:
            print(f"\n❌ ERRORS ({len(self.test_results['errors'])}):")
            for error in self.test_results["errors"]:
                print(f"   • {error}")
        
        if self.test_results["performance_metrics"]:
            print(f"\n⚡ PERFORMANCE METRICS:")
            for metric, value in self.test_results["performance_metrics"].items():
                if isinstance(value, float):
                    print(f"   • {metric}: {value:.3f}s")
                else:
                    print(f"   • {metric}: {value}")
        
        # Determine overall result
        success_rate = self.test_results["passed"] / (self.test_results["passed"] + self.test_results["failed"]) * 100
        
        if success_rate >= 95:
            print(f"\n🎉 EXCELLENT! Success rate: {success_rate:.1f}%")
        elif success_rate >= 85:
            print(f"\n✅ GOOD! Success rate: {success_rate:.1f}%")
        elif success_rate >= 70:
            print(f"\n⚠️  FAIR! Success rate: {success_rate:.1f}%")
        else:
            print(f"\n❌ NEEDS WORK! Success rate: {success_rate:.1f}%")
        
        return self.test_results

if __name__ == "__main__":
    tester = NCC_ABYAS_Tester()
    results = tester.run_all_tests()
    
    # Exit with appropriate code
    exit_code = 0 if results["failed"] == 0 else 1
    sys.exit(exit_code)
