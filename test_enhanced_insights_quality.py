#!/usr/bin/env python3
"""
Test script for Enhanced Insights Quality
Demonstrates the improved quality of biblical insights through specific test cases
and quality metrics evaluation.
"""

import json
import sys
import os
import time
from colorama import Fore, Style, init
import requests

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(__file__))

init(autoreset=True)

class InsightsQualityTester:
    """Test and evaluate the quality of biblical insights"""
    
    def __init__(self):
        self.api_base_url = "http://localhost:5200"
        self.test_results = []
        
    def test_insights_quality(self):
        """Test the quality of insights with various query types"""
        print(f"{Fore.CYAN}🔍 Testing Enhanced Insights Quality")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        # Test cases designed to evaluate different aspects of insight quality
        test_cases = [
            {
                "query": "John 1:1",
                "category": "Verse Analysis",
                "expected_quality_indicators": [
                    "original_language_analysis",
                    "theological_depth",
                    "cross_references",
                    "translation_comparison",
                    "historical_context"
                ],
                "description": "Tests deep verse analysis with original language insights"
            },
            {
                "query": "What is the meaning of agape love?",
                "category": "Lexical Analysis",
                "expected_quality_indicators": [
                    "greek_word_study",
                    "semantic_range",
                    "biblical_usage",
                    "theological_implications",
                    "practical_application"
                ],
                "description": "Tests lexical analysis and word study capabilities"
            },
            {
                "query": "How does the Bible describe salvation?",
                "category": "Thematic Analysis",
                "expected_quality_indicators": [
                    "thematic_development",
                    "cross_testament_connections",
                    "systematic_theology",
                    "biblical_evidence",
                    "contemporary_relevance"
                ],
                "description": "Tests thematic analysis across biblical history"
            },
            {
                "query": "What is the significance of the temple in biblical history?",
                "category": "Historical Analysis",
                "expected_quality_indicators": [
                    "historical_progression",
                    "cultural_context",
                    "theological_development",
                    "prophetic_fulfillment",
                    "christological_connections"
                ],
                "description": "Tests historical and cultural analysis"
            },
            {
                "query": "How should Christians understand forgiveness?",
                "category": "Practical Theology",
                "expected_quality_indicators": [
                    "biblical_principles",
                    "practical_application",
                    "theological_foundation",
                    "pastoral_implications",
                    "contemporary_challenges"
                ],
                "description": "Tests practical theology and application"
            }
        ]
        
        for i, test_case in enumerate(test_cases, 1):
            print(f"\n{Fore.YELLOW}Test {i}: {test_case['category']}")
            print(f"{Fore.YELLOW}Query: '{test_case['query']}'")
            print(f"{Fore.YELLOW}Description: {test_case['description']}{Style.RESET_ALL}")
            
            result = self._test_single_case(test_case)
            self.test_results.append(result)
            
            # Display quality metrics
            self._display_quality_metrics(result)
            
        # Generate comprehensive quality report
        self._generate_quality_report()
    
    def _test_single_case(self, test_case):
        """Test a single case and evaluate quality"""
        start_time = time.time()
        
        try:
            # Call the enhanced insights API
            response = requests.post(
                f"{self.api_base_url}/api/contextual_insights/insights",
                json={"query": test_case['query']},
                timeout=60
            )
            
            elapsed_time = time.time() - start_time
            
            if response.status_code == 200:
                data = response.json()
                
                # Evaluate quality metrics
                quality_metrics = self._evaluate_quality(data, test_case)
                
                return {
                    "test_case": test_case,
                    "success": True,
                    "response_time": elapsed_time,
                    "quality_metrics": quality_metrics,
                    "response_data": data
                }
            else:
                return {
                    "test_case": test_case,
                    "success": False,
                    "error": f"API error: {response.status_code}",
                    "response_time": elapsed_time
                }
                
        except Exception as e:
            return {
                "test_case": test_case,
                "success": False,
                "error": str(e),
                "response_time": time.time() - start_time
            }
    
    def _evaluate_quality(self, response_data, test_case):
        """Evaluate the quality of insights based on multiple criteria"""
        metrics = {
            "completeness": 0.0,
            "scholarly_depth": 0.0,
            "theological_accuracy": 0.0,
            "practical_relevance": 0.0,
            "original_language_usage": 0.0,
            "cross_reference_quality": 0.0,
            "translation_comparison": 0.0,
            "structural_organization": 0.0,
            "overall_quality": 0.0
        }
        
        # Extract analysis text
        analysis_text = ""
        if 'insights' in response_data:
            if 'comprehensive_analysis' in response_data['insights']:
                analysis_text = response_data['insights']['comprehensive_analysis']
            elif 'summary' in response_data['insights']:
                analysis_text = response_data['insights']['summary']
        
        if not analysis_text:
            return metrics
        
        # Evaluate completeness
        metrics["completeness"] = self._evaluate_completeness(analysis_text, test_case)
        
        # Evaluate scholarly depth
        metrics["scholarly_depth"] = self._evaluate_scholarly_depth(analysis_text)
        
        # Evaluate theological accuracy
        metrics["theological_accuracy"] = self._evaluate_theological_accuracy(analysis_text)
        
        # Evaluate practical relevance
        metrics["practical_relevance"] = self._evaluate_practical_relevance(analysis_text)
        
        # Evaluate original language usage
        metrics["original_language_usage"] = self._evaluate_original_language_usage(analysis_text)
        
        # Evaluate cross-reference quality
        metrics["cross_reference_quality"] = self._evaluate_cross_reference_quality(analysis_text)
        
        # Evaluate translation comparison
        metrics["translation_comparison"] = self._evaluate_translation_comparison(analysis_text)
        
        # Evaluate structural organization
        metrics["structural_organization"] = self._evaluate_structural_organization(analysis_text)
        
        # Calculate overall quality
        metrics["overall_quality"] = sum(metrics.values()) / len(metrics)
        
        return metrics
    
    def _evaluate_completeness(self, text, test_case):
        """Evaluate how completely the analysis addresses the query"""
        score = 0.0
        
        # Check for expected quality indicators
        expected_indicators = test_case.get('expected_quality_indicators', [])
        found_indicators = 0
        
        for indicator in expected_indicators:
            if indicator.lower().replace('_', ' ') in text.lower():
                found_indicators += 1
        
        if expected_indicators:
            score = found_indicators / len(expected_indicators)
        
        # Bonus for comprehensive coverage
        if len(text) > 1000:
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_scholarly_depth(self, text):
        """Evaluate the scholarly depth of the analysis"""
        score = 0.0
        
        # Check for scholarly language and concepts
        scholarly_indicators = [
            'exegesis', 'hermeneutics', 'lexical', 'morphological', 'syntactical',
            'theological', 'historical', 'cultural', 'contextual', 'systematic',
            'doctrinal', 'orthodox', 'interpretation', 'analysis', 'scholarly'
        ]
        
        found_indicators = sum(1 for indicator in scholarly_indicators 
                             if indicator in text.lower())
        
        score = min(found_indicators / len(scholarly_indicators), 1.0)
        
        # Bonus for structured analysis
        if '**' in text and text.count('**') > 4:
            score += 0.1
        
        return min(score, 1.0)
    
    def _evaluate_theological_accuracy(self, text):
        """Evaluate theological accuracy and soundness"""
        score = 0.5  # Base score for biblical content
        
        # Check for theological terms
        theological_terms = [
            'god', 'jesus', 'christ', 'holy spirit', 'salvation', 'grace', 'faith',
            'sin', 'redemption', 'atonement', 'justification', 'sanctification'
        ]
        
        found_terms = sum(1 for term in theological_terms 
                         if term in text.lower())
        
        score += (found_terms / len(theological_terms)) * 0.3
        
        # Bonus for biblical references
        if text.count(':') > 5:  # Likely verse references
            score += 0.2
        
        return min(score, 1.0)
    
    def _evaluate_practical_relevance(self, text):
        """Evaluate practical relevance and application"""
        score = 0.0
        
        # Check for practical application language
        practical_indicators = [
            'application', 'practice', 'life', 'christian', 'believer', 'faith',
            'practical', 'apply', 'today', 'modern', 'contemporary', 'daily'
        ]
        
        found_indicators = sum(1 for indicator in practical_indicators 
                             if indicator in text.lower())
        
        score = min(found_indicators / len(practical_indicators), 1.0)
        
        return score
    
    def _evaluate_original_language_usage(self, text):
        """Evaluate usage of original language analysis"""
        score = 0.0
        
        # Check for original language indicators
        language_indicators = [
            'hebrew', 'greek', 'aramaic', 'strong', 'lexical', 'morphology',
            'grammar', 'syntax', 'etymology', 'semantic', 'lemma'
        ]
        
        found_indicators = sum(1 for indicator in language_indicators 
                             if indicator in text.lower())
        
        score = min(found_indicators / len(language_indicators), 1.0)
        
        return score
    
    def _evaluate_cross_reference_quality(self, text):
        """Evaluate quality of cross-references"""
        score = 0.0
        
        # Check for cross-reference language
        cross_ref_indicators = [
            'cross-reference', 'related', 'similar', 'parallel', 'connection',
            'theme', 'pattern', 'fulfillment', 'prophecy', 'echo'
        ]
        
        found_indicators = sum(1 for indicator in cross_ref_indicators 
                             if indicator in text.lower())
        
        score = min(found_indicators / len(cross_ref_indicators), 1.0)
        
        return score
    
    def _evaluate_translation_comparison(self, text):
        """Evaluate translation comparison quality"""
        score = 0.0
        
        # Check for translation comparison
        translation_indicators = [
            'kjv', 'asv', 'ylt', 'tahot', 'translation', 'version', 'compare',
            'differ', 'similar', 'literal', 'dynamic'
        ]
        
        found_indicators = sum(1 for indicator in translation_indicators 
                             if indicator in text.lower())
        
        score = min(found_indicators / len(translation_indicators), 1.0)
        
        return score
    
    def _evaluate_structural_organization(self, text):
        """Evaluate structural organization and clarity"""
        score = 0.0
        
        # Check for structured format
        if '**' in text and text.count('**') > 4:
            score += 0.4
        
        # Check for numbered sections
        if any(f"{i}." in text for i in range(1, 8)):
            score += 0.3
        
        # Check for clear paragraphs
        paragraphs = text.split('\n\n')
        if len(paragraphs) > 3:
            score += 0.3
        
        return min(score, 1.0)
    
    def _display_quality_metrics(self, result):
        """Display quality metrics for a test result"""
        if not result['success']:
            print(f"{Fore.RED}❌ Test failed: {result.get('error', 'Unknown error')}")
            return
        
        metrics = result['quality_metrics']
        
        print(f"{Fore.GREEN}✅ Test completed in {result['response_time']:.1f}s")
        print(f"{Fore.CYAN}Quality Metrics:")
        
        # Display key metrics
        key_metrics = [
            ("Overall Quality", metrics['overall_quality']),
            ("Completeness", metrics['completeness']),
            ("Scholarly Depth", metrics['scholarly_depth']),
            ("Theological Accuracy", metrics['theological_accuracy']),
            ("Practical Relevance", metrics['practical_relevance']),
            ("Original Language Usage", metrics['original_language_usage']),
            ("Cross-Reference Quality", metrics['cross_reference_quality']),
            ("Translation Comparison", metrics['translation_comparison']),
            ("Structural Organization", metrics['structural_organization'])
        ]
        
        for metric_name, score in key_metrics:
            color = Fore.GREEN if score >= 0.7 else Fore.YELLOW if score >= 0.4 else Fore.RED
            print(f"  {metric_name}: {color}{score:.2f}{Style.RESET_ALL}")
    
    def _generate_quality_report(self):
        """Generate a comprehensive quality report"""
        print(f"\n{Fore.CYAN}{'='*60}")
        print(f"{Fore.CYAN}ENHANCED INSIGHTS QUALITY REPORT")
        print(f"{Fore.CYAN}{'='*60}{Style.RESET_ALL}")
        
        successful_tests = [r for r in self.test_results if r['success']]
        failed_tests = [r for r in self.test_results if not r['success']]
        
        print(f"\n{Fore.GREEN}✅ Successful Tests: {len(successful_tests)}/{len(self.test_results)}")
        print(f"{Fore.RED}❌ Failed Tests: {len(failed_tests)}/{len(self.test_results)}")
        
        if successful_tests:
            # Calculate average metrics
            avg_metrics = {}
            metric_names = ['overall_quality', 'completeness', 'scholarly_depth', 
                          'theological_accuracy', 'practical_relevance', 
                          'original_language_usage', 'cross_reference_quality',
                          'translation_comparison', 'structural_organization']
            
            for metric in metric_names:
                values = [r['quality_metrics'][metric] for r in successful_tests]
                avg_metrics[metric] = sum(values) / len(values)
            
            print(f"\n{Fore.CYAN}Average Quality Metrics:")
            for metric_name in metric_names:
                score = avg_metrics[metric_name]
                color = Fore.GREEN if score >= 0.7 else Fore.YELLOW if score >= 0.4 else Fore.RED
                print(f"  {metric_name.replace('_', ' ').title()}: {color}{score:.2f}{Style.RESET_ALL}")
            
            # Overall assessment
            overall_avg = avg_metrics['overall_quality']
            if overall_avg >= 0.8:
                assessment = f"{Fore.GREEN}EXCELLENT - High-quality insights with scholarly depth"
            elif overall_avg >= 0.6:
                assessment = f"{Fore.YELLOW}GOOD - Solid insights with room for improvement"
            elif overall_avg >= 0.4:
                assessment = f"{Fore.RED}FAIR - Basic insights need enhancement"
            else:
                assessment = f"{Fore.RED}POOR - Significant improvement needed"
            
            print(f"\n{Fore.CYAN}Overall Assessment: {assessment}{Style.RESET_ALL}")
        
        if failed_tests:
            print(f"\n{Fore.RED}Failed Tests:")
            for test in failed_tests:
                print(f"  • {test['test_case']['query']}: {test.get('error', 'Unknown error')}")
        
        # Recommendations for improvement
        print(f"\n{Fore.CYAN}Recommendations for Further Enhancement:")
        recommendations = [
            "Increase original language analysis depth",
            "Enhance cross-reference connections",
            "Improve translation comparison quality",
            "Strengthen practical application sections",
            "Add more historical and cultural context",
            "Enhance structural organization",
            "Improve theological depth and accuracy"
        ]
        
        for rec in recommendations:
            print(f"  • {rec}")

def main():
    """Main test function"""
    tester = InsightsQualityTester()
    tester.test_insights_quality()

if __name__ == "__main__":
    main()