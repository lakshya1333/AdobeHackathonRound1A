#!/usr/bin/env python3
"""
Ground Truth Analyzer
Analyzes current output vs expected ground truth
"""

import json
import os
from pathlib import Path

def analyze_ground_truth():
    """Analyze our results vs expected ground truth"""
    
    # Expected ground truth from user examples
    expected_ground_truth = {
        "file01.pdf": {
            "title": "Application form for grant of LTC advance",
            "outline": []  # User said 0 entries expected
        },
        "file02.pdf": {
            "title": "Overview Foundation Level Extensions",
            "outline": [
                {"level": "H1", "text": "Revision History", "page": 2},
                {"level": "H1", "text": "Table of Contents", "page": 3},
                {"level": "H1", "text": "Acknowledgements", "page": 4},
                {"level": "H1", "text": "1. Introduction to the Foundation Level Extensions", "page": 5},
                {"level": "H1", "text": "2. Introduction to Foundation Level Agile Tester Extension", "page": 6},
                {"level": "H2", "text": "2.1 Intended Audience", "page": 6},
                {"level": "H2", "text": "2.2 Career Paths for Testers", "page": 6},
                {"level": "H2", "text": "2.3 Learning Objectives", "page": 6},
                {"level": "H2", "text": "2.4 Entry Requirements", "page": 7},
                {"level": "H2", "text": "2.5 Structure and Course Duration", "page": 7},
                {"level": "H2", "text": "2.6 Keeping It Current", "page": 8},
                {"level": "H1", "text": "3. Overview of the Foundation Level Extension – Agile TesterSyllabus", "page": 9},
                {"level": "H2", "text": "3.1 Business Outcomes", "page": 9},
                {"level": "H2", "text": "3.2 Content", "page": 9},
                {"level": "H1", "text": "4. References", "page": 11},
                {"level": "H2", "text": "4.1 Trademarks", "page": 11},
                {"level": "H2", "text": "4.2 Documents and Web Sites", "page": 11}
            ]
        },
        "file03.pdf": {
            "title": "RFP:Request for Proposal To Present a Proposal for Developing the Business Plan for the Ontario Digital Library",
            "outline": [
                {"level": "H1", "text": "Ontario's Digital Library", "page": 1},
                {"level": "H1", "text": "A Critical Component for Implementing Ontario's Road Map to Prosperity Strategy", "page": 1},
                {"level": "H2", "text": "Summary", "page": 1},
                {"level": "H3", "text": "Timeline:", "page": 1},
                {"level": "H2", "text": "Background", "page": 2}
                # ... more entries from the full ground truth
            ]
        },
        "file04.pdf": {
            "title": "Parsippany -Troy Hills STEM Pathways",
            "outline": [
                {"level": "H1", "text": "PATHWAY OPTIONS", "page": 0}
            ]
        },
        "file05.pdf": {
            "title": "",
            "outline": [
                {"level": "H1", "text": "HOPE To SEE You THERE!", "page": 0}
            ]
        }
    }
    
    print("="*80)
    print("GROUND TRUTH ANALYSIS")
    print("="*80)
    
    output_dir = Path("output")
    
    for pdf_file, expected in expected_ground_truth.items():
        print(f"\nAnalyzing {pdf_file}:")
        print("-" * 50)
        
        # Load our output
        output_file = output_dir / f"{pdf_file.replace('.pdf', '_hackathon_optimized.json')}"
        
        if output_file.exists():
            with open(output_file, 'r', encoding='utf-8') as f:
                our_result = json.load(f)
            
            print(f"Expected title: '{expected['title']}'")
            print(f"Our title: '{our_result.get('title', 'N/A')}'")
            print(f"Title match: {expected['title'] == our_result.get('title', '')}")
            
            print(f"\nExpected outline entries: {len(expected['outline'])}")
            print(f"Our outline entries: {len(our_result.get('outline', []))}")
            
            if len(expected['outline']) > 0:
                print("\nExpected outline:")
                for i, entry in enumerate(expected['outline']):
                    print(f"  {i+1}. {entry['level']}: {entry['text']} (page {entry['page']})")
                
                print("\nOur top outline entries:")
                for i, entry in enumerate(our_result.get('outline', [])[:5]):
                    print(f"  {i+1}. {entry['level']}: {entry['text']} (page {entry['page']})")
            else:
                print("Expected: No outline entries")
                print("Our result: Found entries - likely over-detection")
                
                # Show what we detected to understand the issue
                print("\nOur detected entries (first 10):")
                for i, entry in enumerate(our_result.get('outline', [])[:10]):
                    print(f"  {i+1}. {entry['level']}: '{entry['text']}' (page {entry['page']})")
        else:
            print(f"Output file not found: {output_file}")
    
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)
    print("Key Issues Identified:")
    print("1. Over-detection: Finding too many headings (especially form fields)")
    print("2. Granularity: Detecting individual labels vs document sections")
    print("3. Context awareness: Need to distinguish forms vs structured documents")
    print("4. Title accuracy: Some titles are truncated or incorrect")
    print("\nRecommendations:")
    print("1. Add document type detection (form vs article vs manual)")
    print("2. Implement minimum text length filters")
    print("3. Add contextual filtering for form fields")
    print("4. Improve title extraction logic")
    print("5. Add semantic grouping to reduce noise")

if __name__ == "__main__":
    analyze_ground_truth()
