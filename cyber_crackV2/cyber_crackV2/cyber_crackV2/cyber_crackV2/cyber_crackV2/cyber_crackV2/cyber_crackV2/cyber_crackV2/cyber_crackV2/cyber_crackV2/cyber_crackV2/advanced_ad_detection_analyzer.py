#!/usr/bin/env python3
"""
CYBER CRACK PRO - ADVANCED AD DETECTION ANALYZER
Komprehensif ad detection system with maximum bug/force-close prevention
"""

import asyncio
import json
import os
import re
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Any, Tuple
import logging
import xml.etree.ElementTree as ET

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class AdvancedAdDetectionAnalyzer:
    """
    Advanced system for detecting ads in APKs with maximum safety measures
    to prevent bugs/force-close when ads are removed
    """

    def __init__(self):
        # Comprehensive ad network patterns
        self.ad_networks = {
            'google_ads': {
                'identifiers': [
                    'com.google.android.gms.ads',
                    'com.google.ads',
                    'com.google.android.gms.ads.identifier',
                    'com.google.android.gms.ads.AdView',
                    'com.google.android.gms.ads.InterstitialAd',
                    'com.google.android.gms.ads.AdRequest',
                    'com.google.android.gms.ads.AdListener',
                    'AdManager',
                    'AdLoader',
                    'AdSize',
                    'AdUnitId',
                    'AdRequest.Builder',
                    'MobileAds'
                ],
                'permissions': [
                    'com.google.android.gms.permission.AD_ID',
                    'android.permission.INTERNET',
                    'android.permission.ACCESS_NETWORK_STATE'
                ],
                'risk_level': 'high',
                'crash_risk': 'high'
            },
            'facebook_ads': {
                'identifiers': [
                    'com.facebook.ads',
                    'com.facebook.ads.AudienceNetworkAds',
                    'com.facebook.ads.AdView',
                    'com.facebook.ads.InterstitialAd',
                    'FAN',
                    'AudienceNetwork'
                ],
                'permissions': [
                    'android.permission.ACCESS_COARSE_LOCATION',
                    'android.permission.GET_TASKS'
                ],
                'risk_level': 'medium',
                'crash_risk': 'medium'
            },
            'unity_ads': {
                'identifiers': [
                    'com.unity3d.ads',
                    'UnityAds',
                    'UnityAd'
                ],
                'permissions': [],
                'risk_level': 'low',
                'crash_risk': 'low'
            },
            'admob': {
                'identifiers': [
                    'com.google.ads',
                    'AdMob',
                    'AdMobView'
                ],
                'permissions': [],
                'risk_level': 'high',
                'crash_risk': 'high'
            },
            'applovin': {
                'identifiers': [
                    'com.applovin',
                    'AppLovin',
                    'Applovin'
                ],
                'permissions': [],
                'risk_level': 'medium',
                'crash_risk': 'medium'
            },
            'inmobi': {
                'identifiers': [
                    'com.inmobi',
                    'InMobi',
                    'InMobiSdk'
                ],
                'permissions': [
                    'android.permission.ACCESS_FINE_LOCATION'
                ],
                'risk_level': 'high',
                'crash_risk': 'high'
            },
            'vungle': {
                'identifiers': [
                    'com.vungle',
                    'Vungle',
                    'VunglePub'
                ],
                'permissions': [],
                'risk_level': 'low',
                'crash_risk': 'low'
            },
            'chartboost': {
                'identifiers': [
                    'com.chartboost',
                    'Chartboost'
                ],
                'permissions': [],
                'risk_level': 'low',
                'crash_risk': 'low'
            }
        }

        # Ad-related resource patterns
        self.ad_resource_patterns = [
            r'ad_.*',
            r'.*ad.*',
            r'banner_.*',
            r'.*banner.*',
            r'interstitial_.*',
            r'.*interstitial.*',
            r'rewarded_.*',
            r'.*rewarded.*',
            r'native_.*',
            r'.*native.*',
            r'video_.*',
            r'.*video.*',
            r'placement_.*',
            r'.*placement.*'
        ]

        # High-risk method patterns that often cause crashes when removed
        self.high_risk_methods = [
            r'onAdFailedToLoad',
            r'onAdLoaded',
            r'onAdOpened',
            r'onAdClosed',
            r'onRewarded',
            r'onRewardedVideoCompleted',
            r'onInterstitialLoaded',
            r'loadAd',
            r'show.*Ad',
            r'initialize.*Ad',
            r'createAd',
            r'requestAd',
            r'cacheAd'
        ]

        # Safe replacement patterns to prevent crashes
        self.safe_replacements = [
            {
                'pattern': r'(loadAd\([^)]*\)|show.*Ad\([^)]*\)|initialize.*Ad\([^)]*\))',
                'replacement': r'# [CCP SAFETY] Ad call safely stubbed\nconst/4 v0, 0x1  # Return success\nnop  # No operation to maintain bytecode flow'
            },
            {
                'pattern': r'(onAd\w+Failed\w+Load|onAd\w+Loaded|onAd\w+Closed|onRewarded)\s*\([^)]*\)\s*\{[^}]*\}',
                'replacement': r'# [CCP SAFETY] Ad callback safely stubbed\n.method public stubbedAdCallback()V\n.locals 1\nconst/4 v0, 0x0\nreturn-void\n.end method',
                'flags': re.DOTALL
            }
        ]

        # Layout ad component patterns
        self.ad_layout_patterns = [
            {
                'tag': r'com\.google\.android\.gms\.ads\.\w+AdView',
                'attributes': ['adSize', 'adUnitId']
            },
            {
                'tag': r'com\.facebook\.ads.\w+',
                'attributes': ['adSize', 'placementId']
            },
            {
                'tag': r'AdView|InterstitialAdView|BannerAdView',
                'attributes': ['.*']
            }
        ]

    async def analyze_apk_for_ads(self, apk_path: str) -> Dict[str, Any]:
        """
        Comprehensive analysis of APK for ad components with safety assessment
        """
        logger.info(f"🔍 Starting advanced ad detection for: {Path(apk_path).name}")

        try:
            # Extract APK to temporary directory
            with tempfile.TemporaryDirectory() as temp_dir:
                extracted_path = await self._extract_apk(apk_path, temp_dir)

                # Perform comprehensive analysis
                ad_analysis = {
                    'ad_networks_detected': [],
                    'ad_files': [],
                    'ad_smali_methods': [],
                    'ad_layouts': [],
                    'ad_resources': [],
                    'high_risk_components': [],
                    'crash_prone_methods': [],
                    'safety_recommendations': [],
                    'removal_complexity': 'low',  # Will be updated based on analysis
                    'total_ad_components': 0,
                    'safety_score': 100  # Higher is safer to remove
                }

                # Analyze different components
                await self._analyze_manifest(extracted_path, ad_analysis)
                await self._analyze_smali_files(extracted_path, ad_analysis)
                await self._analyze_layout_files(extracted_path, ad_analysis)
                await self._analyze_resources(extracted_path, ad_analysis)

                # Calculate safety metrics
                await self._calculate_safety_metrics(ad_analysis)

                # Generate safety recommendations
                await self._generate_safety_recommendations(ad_analysis)

                logger.info(f"✅ Ad detection completed: {ad_analysis['total_ad_components']} components found")
                logger.info(f"🛡️ Safety score: {ad_analysis['safety_score']}/100")

                return ad_analysis

        except Exception as e:
            logger.error(f"❌ Ad analysis failed: {e}")
            import traceback
            traceback.print_exc()
            return {
                'error': str(e),
                'ad_networks_detected': [],
                'ad_files': [],
                'ad_smali_methods': [],
                'ad_layouts': [],
                'ad_resources': [],
                'high_risk_components': [],
                'crash_prone_methods': [],
                'safety_recommendations': [],
                'removal_complexity': 'unknown',
                'total_ad_components': 0,
                'safety_score': 0
            }

    async def _extract_apk(self, apk_path: str, temp_dir: str) -> str:
        """Extract APK to temporary directory"""
        extracted_path = os.path.join(temp_dir, "extracted")
        os.makedirs(extracted_path, exist_ok=True)

        with zipfile.ZipFile(apk_path, 'r') as zip_ref:
            zip_ref.extractall(extracted_path)

        logger.debug(f"📦 APK extracted to: {extracted_path}")
        return extracted_path

    async def _analyze_manifest(self, extracted_path: str, ad_analysis: Dict[str, Any]):
        """Analyze AndroidManifest.xml for ad-related components"""
        manifest_path = os.path.join(extracted_path, 'AndroidManifest.xml')

        if not os.path.exists(manifest_path):
            logger.warning("⚠️ AndroidManifest.xml not found")
            return

        try:
            with open(manifest_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for ad network identifiers
            for network_name, network_info in self.ad_networks.items():
                for identifier in network_info['identifiers']:
                    if identifier.lower() in content.lower():
                        if network_name not in ad_analysis['ad_networks_detected']:
                            ad_analysis['ad_networks_detected'].append({
                                'name': network_name,
                                'identifier': identifier,
                                'risk_level': network_info['risk_level'],
                                'crash_risk': network_info['crash_risk']
                            })

                # Check for ad-related permissions
                for permission in network_info['permissions']:
                    if permission in content:
                        ad_analysis['ad_resources'].append({
                            'type': 'permission',
                            'name': permission,
                            'source': 'AndroidManifest.xml'
                        })

            # Check for ad service/receiver components
            ad_patterns = [
                r'<service[^>]*com\.google\.android\.gms\.[^>]*>',
                r'<receiver[^>]*com\.google\.android\.gms\.[^>]*>',
                r'<provider[^>]*com\.google\.android\.gms\.[^>]*>',
                r'<activity[^>]*AdActivity[^>]*>',
                r'<meta-data[^>]*name="com\.google\.android\.gms\.ads[^>]*>'
            ]

            for pattern in ad_patterns:
                matches = re.findall(pattern, content, re.IGNORECASE)
                for match in matches:
                    ad_analysis['ad_resources'].append({
                        'type': 'manifest_component',
                        'pattern': pattern,
                        'match': match[:100] + '...' if len(match) > 100 else match,
                        'source': 'AndroidManifest.xml'
                    })

        except Exception as e:
            logger.error(f"❌ Error analyzing manifest: {e}")

    async def _analyze_smali_files(self, extracted_path: str, ad_analysis: Dict[str, Any]):
        """Analyze smali files for ad-related methods and code"""
        smali_dir = os.path.join(extracted_path, 'smali')
        if not os.path.exists(smali_dir):
            # Look for smali files recursively
            for root, dirs, files in os.walk(extracted_path):
                for file in files:
                    if file.endswith('.smali'):
                        await self._analyze_single_smali_file(root, file, ad_analysis)
        else:
            for root, dirs, files in os.walk(smali_dir):
                for file in files:
                    if file.endswith('.smali'):
                        await self._analyze_single_smali_file(root, file, ad_analysis)

    async def _analyze_single_smali_file(self, root: str, file: str, ad_analysis: Dict[str, Any]):
        """Analyze single smali file for ad components"""
        file_path = os.path.join(root, file)

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            # Check for ad network identifiers
            for network_name, network_info in self.ad_networks.items():
                for identifier in network_info['identifiers']:
                    if identifier in content:
                        ad_analysis['ad_smali_methods'].append({
                            'file': file_path,
                            'network': network_name,
                            'identifier': identifier,
                            'risk_level': network_info['risk_level']
                        })

            # Check for high-risk methods that might cause crashes
            for method_pattern in self.high_risk_methods:
                matches = re.findall(method_pattern, content)
                for match in matches:
                    ad_analysis['crash_prone_methods'].append({
                        'file': file_path,
                        'method': match,
                        'pattern': method_pattern
                    })

            # Look for ad loading and display methods
            ad_method_patterns = [
                r'\.method.*loadAd\(',
                r'\.method.*show.*Ad\(',
                r'\.method.*initialize.*Ad\(',
                r'\.method.*create.*Ad\(',
                r'\.method.*request.*Ad\(',
                r'invoke.*loadAd',
                r'invoke.*show.*Ad',
                r'invoke.*initialize.*Ad'
            ]

            for pattern in ad_method_patterns:
                matches = re.findall(pattern, content)
                for match in matches:
                    ad_analysis['ad_smali_methods'].append({
                        'file': file_path,
                        'method_signature': match,
                        'type': 'ad_method'
                    })

        except Exception as e:
            logger.warning(f"⚠️ Error analyzing smali file {file_path}: {e}")

    async def _analyze_layout_files(self, extracted_path: str, ad_analysis: Dict[str, Any]):
        """Analyze layout XML files for ad components"""
        res_dir = os.path.join(extracted_path, 'res')
        if not os.path.exists(res_dir):
            return

        for root, dirs, files in os.walk(res_dir):
            for file in files:
                if file.endswith('.xml') and any(path in root for path in ['layout', 'values', 'drawable']):
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Check for ad view components
                        for ad_pattern in self.ad_layout_patterns:
                            tag_pattern = ad_pattern['tag']
                            matches = re.findall(
                                rf'<\s*{tag_pattern}[^>]*>.*?</\s*{tag_pattern}\s*>',
                                content,
                                re.DOTALL | re.IGNORECASE
                            )

                            for match in matches:
                                ad_analysis['ad_layouts'].append({
                                    'file': file_path,
                                    'component': tag_pattern,
                                    'content': match[:200] + '...' if len(match) > 200 else match,
                                    'type': 'layout_ad_component'
                                })

                        # Check for ad-related IDs and resource names
                        for resource_pattern in self.ad_resource_patterns:
                            # Look for ID attributes that suggest ads
                            id_matches = re.findall(
                                rf'android:id="@.*?/{resource_pattern}"',
                                content,
                                re.IGNORECASE
                            )

                            for match in id_matches:
                                ad_analysis['ad_resources'].append({
                                    'file': file_path,
                                    'type': 'layout_resource',
                                    'pattern': resource_pattern,
                                    'match': match
                                })

                    except Exception as e:
                        logger.warning(f"⚠️ Error analyzing layout file {file_path}: {e}")

    async def _analyze_resources(self, extracted_path: str, ad_analysis: Dict[str, Any]):
        """Analyze resource files for ad-related content"""
        res_dir = os.path.join(extracted_path, 'res')
        if not os.path.exists(res_dir):
            return

        # Check values files (strings.xml, etc.) for ad-related text
        for root, dirs, files in os.walk(res_dir):
            for file in files:
                if file.endswith('.xml') and 'values' in root:
                    file_path = os.path.join(root, file)
                    try:
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()

                        # Look for ad-related strings
                        ad_string_patterns = [
                            r'ad', r'Ad', r'AD',
                            r'banner', r'Banner', r'BANNER',
                            r'interstitial', r'Interstitial', r'INTERSTITIAL',
                            r'rewarded', r'Rewarded', r'REWARDED',
                            r'video_ad', r'VideoAd', r'ad_video',
                            r'native_ad', r'NativeAd', r'ad_native'
                        ]

                        for pattern in ad_string_patterns:
                            matches = re.findall(
                                rf'(".*?{pattern}.*?")',
                                content,
                                re.IGNORECASE
                            )

                            for match in matches:
                                ad_analysis['ad_resources'].append({
                                    'file': file_path,
                                    'type': 'string_resource',
                                    'pattern': pattern,
                                    'match': match
                                })

                    except Exception as e:
                        logger.warning(f"⚠️ Error analyzing resource file {file_path}: {e}")

    async def _calculate_safety_metrics(self, ad_analysis: Dict[str, Any]):
        """Calculate safety metrics and complexity for ad removal"""
        ad_analysis['total_ad_components'] = (
            len(ad_analysis['ad_smali_methods']) +
            len(ad_analysis['ad_layouts']) +
            len(ad_analysis['ad_resources'])
        )

        # Calculate removal complexity based on detected components
        complexity_score = 0
        safety_score = 100

        # High crash risk components reduce safety
        for network in ad_analysis['ad_networks_detected']:
            if network.get('crash_risk') == 'high':
                complexity_score += 3
                safety_score -= 20
            elif network.get('crash_risk') == 'medium':
                complexity_score += 2
                safety_score -= 10

        # High-risk methods reduce safety
        complexity_score += len(ad_analysis['crash_prone_methods']) * 2
        safety_score -= len(ad_analysis['crash_prone_methods']) * 5

        # More ad components = higher complexity
        complexity_score += ad_analysis['total_ad_components'] // 5

        # Determine complexity level
        if complexity_score <= 2:
            ad_analysis['removal_complexity'] = 'low'
        elif complexity_score <= 5:
            ad_analysis['removal_complexity'] = 'medium'
        else:
            ad_analysis['removal_complexity'] = 'high'

        # Ensure safety score is within bounds
        ad_analysis['safety_score'] = max(0, min(100, safety_score))

    async def _generate_safety_recommendations(self, ad_analysis: Dict[str, Any]):
        """Generate safety recommendations for ad removal"""
        recommendations = []

        if ad_analysis['removal_complexity'] == 'high':
            recommendations.append({
                'type': 'caution',
                'message': 'High complexity detected - proceed with extreme caution',
                'advice': 'Perform thorough testing after removal, backup original APK'
            })

        if any(net['crash_risk'] == 'high' for net in ad_analysis['ad_networks_detected']):
            recommendations.append({
                'type': 'high_risk',
                'message': 'High crash risk ad networks detected',
                'advice': 'Use safe stubbing instead of complete removal for these networks'
            })

        if len(ad_analysis['crash_prone_methods']) > 5:
            recommendations.append({
                'type': 'crash_risk',
                'message': 'Multiple crash-prone methods detected',
                'advice': 'Implement proper null checks and error handling'
            })

        if ad_analysis['safety_score'] < 50:
            recommendations.append({
                'type': 'safety',
                'message': 'Low safety score detected',
                'advice': 'Consider alternative approaches or manual review'
            })

        # Add general recommendations
        recommendations.extend([
            {
                'type': 'general',
                'message': 'Use safe replacement strategies',
                'advice': 'Replace ad calls with safe stubs instead of removing completely'
            },
            {
                'type': 'general',
                'message': 'Implement crash prevention',
                'advice': 'Add try-catch blocks around potentially problematic code'
            },
            {
                'type': 'general',
                'message': 'Test thoroughly',
                'advice': 'Always test the app after ad removal to ensure stability'
            }
        ])

        ad_analysis['safety_recommendations'] = recommendations

    def get_detection_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate a human-readable detection report"""
        report = []
        report.append("🎯 ADVANCED AD DETECTION REPORT")
        report.append("=" * 50)

        if analysis_result.get('error'):
            report.append(f"❌ Error: {analysis_result['error']}")
            return "\n".join(report)

        report.append(f"📦 APK: {Path(analysis_result.get('source_apk', 'unknown')).name}")
        report.append(f"🛡️ Safety Score: {analysis_result['safety_score']}/100")
        report.append(f"⚙️ Removal Complexity: {analysis_result['removal_complexity']}")
        report.append(f"📊 Total Ad Components: {analysis_result['total_ad_components']}")
        report.append("")

        # Ad networks detected
        if analysis_result['ad_networks_detected']:
            report.append("📡 AD NETWORKS DETECTED:")
            for network in analysis_result['ad_networks_detected']:
                report.append(f"  • {network['name']} (Risk: {network['risk_level']})")
            report.append("")

        # Ad files and methods
        if analysis_result['ad_smali_methods']:
            report.append(f"📝 Ad-Related Methods: {len(analysis_result['ad_smali_methods'])}")
            for method in analysis_result['ad_smali_methods'][:5]:  # Show first 5
                report.append(f"  • {method.get('identifier', method.get('method_signature', 'Unknown'))}")
            if len(analysis_result['ad_smali_methods']) > 5:
                report.append(f"  ... and {len(analysis_result['ad_smali_methods']) - 5} more")
            report.append("")

        # High-risk components
        if analysis_result['crash_prone_methods']:
            report.append(f"⚠️ High-Risk Components: {len(analysis_result['crash_prone_methods'])}")
            for method in analysis_result['crash_prone_methods'][:3]:  # Show first 3
                report.append(f"  • {method['method']} in {Path(method['file']).name}")
            if len(analysis_result['crash_prone_methods']) > 3:
                report.append(f"  ... and {len(analysis_result['crash_prone_methods']) - 3} more")
            report.append("")

        # Safety recommendations
        if analysis_result['safety_recommendations']:
            report.append("🛡️ SAFETY RECOMMENDATIONS:")
            for rec in analysis_result['safety_recommendations']:
                if rec['type'] == 'high_risk':
                    report.append(f"  ⚠️ {rec['message']}")
                    report.append(f"     Advice: {rec['advice']}")
            report.append("")

        return "\n".join(report)

    def get_safe_replacement_strategies(self) -> List[Dict[str, Any]]:
        """Get safe replacement strategies to prevent crashes"""
        return [
            {
                'strategy': 'Method Stubs',
                'description': 'Replace ad method calls with safe stubs that return default values',
                'examples': [
                    'Instead of removing loadAd(), replace with a no-op method that returns success',
                    'Replace showInterstitial() with a method that returns immediately without showing anything'
                ]
            },
            {
                'strategy': 'Null Checks',
                'description': 'Add null checks before accessing ad-related objects',
                'examples': [
                    'Check if adView is null before calling methods on it',
                    'Verify ad is loaded before attempting to show it'
                ]
            },
            {
                'strategy': 'Try-Catch Blocks',
                'description': 'Wrap ad-related code in try-catch to prevent crashes',
                'examples': [
                    'Surround ad initialization code with try-catch blocks',
                    'Handle exceptions gracefully without affecting app functionality'
                ]
            },
            {
                'strategy': 'Layout Placeholders',
                'description': 'Replace ad views with invisible placeholders',
                'examples': [
                    'Replace AdView with empty View of 0x0 dimensions',
                    'Use ViewStub that can be inflated conditionally'
                ]
            }
        ]

async def main():
    """Example usage of the Advanced Ad Detection Analyzer"""
    print("🎯 CYBER CRACK PRO - ADVANCED AD DETECTION ANALYZER")
    print("=" * 60)
    print("🔍 Comprehensive ad detection with maximum safety measures")
    print()

    analyzer = AdvancedAdDetectionAnalyzer()

    # Create a mock APK for demonstration
    mock_apk = Path("mock_app_for_ad_detection.apk")
    if not mock_apk.exists():
        mock_apk.write_bytes(b"PK\x03\x04" + b"mock_apk_content_for_ad_detection_demo")

    print(f"📱 Analyzing Application: {mock_apk.name}")
    print()

    try:
        # Perform comprehensive ad detection
        print("🔍 Starting advanced ad detection analysis...")
        analysis = await analyzer.analyze_apk_for_ads(str(mock_apk))

        # Display analysis results
        print(analyzer.get_detection_report(analysis))

        # Show safe replacement strategies
        print("🛡️ SAFE REPLACEMENT STRATEGIES:")
        strategies = analyzer.get_safe_replacement_strategies()
        for i, strategy in enumerate(strategies, 1):
            print(f"  {i}. {strategy['strategy']}")
            print(f"     {strategy['description']}")
        print()

        if analysis.get('error'):
            print(f"❌ Analysis Error: {analysis['error']}")
        else:
            print(f"✅ Analysis completed successfully!")
            print(f"📊 {analysis['total_ad_components']} ad components detected")
            print(f"🛡️ Safety score: {analysis['safety_score']}/100")
            print(f"⚙️ Removal complexity: {analysis['removal_complexity']}")

    except Exception as e:
        print(f"❌ Error during analysis: {e}")
        import traceback
        traceback.print_exc()

    finally:
        # Cleanup mock file
        if mock_apk.exists():
            mock_apk.unlink()

    print()
    print("🎯 ADVANCED AD DETECTION ANALYZER - COMPLETE")
    print("🛡️ Maximum safety measures for ad removal")

if __name__ == "__main__":
    asyncio.run(main())