#!/usr/bin/env python3
"""
Simple test script for planner agent functionality.
Tests the complete flow from user query to dependency tree.
"""

from planner.v2.load_model import load_gemini_model
from planner.v2.query_enhancer import enhance_search_query
from planner.v2.ambiguity_finder import analyze_query_ambiguities
from planner.v2.ambiguity_resolver import ambiguity_resolver, UserResponse
from planner.v2.plan_tree import build_dependency_research_tree


def ask_user_questions(questions, max_questions=4):
    """Ask user clarifying questions in terminal."""
    user_responses = []
    
    print("\n" + "="*60)
    print("CLARIFYING QUESTIONS")
    print("="*60)
    print("Please answer the following questions to refine your search:")
    print()
    
    # Limit to max_questions
    questions_to_ask = questions[:max_questions]
    
    for i, question in enumerate(questions_to_ask, 1):
        print(f"Q{i}: {question}")
        answer = input(f"A{i}: ").strip()
        
        if answer:  # Only add non-empty answers
            user_responses.append(UserResponse(question=question, answer=answer))
        
        print()
    
    return user_responses


def test_planner_agent():
    """Test the complete planner agent flow."""
    
    print("="*80)
    print("PLANNER AGENT TEST")
    print("="*80)
    
    # Step 1: Get user query
    user_query = input("Enter your research query: ").strip()
    
    if not user_query:
        print("No query provided. Exiting.")
        return
    
    print(f"\nOriginal Query: {user_query}")
    
    # Step 2: Load model
    print("\nLoading Gemini model...")
    model = load_gemini_model()
    
    if not model:
        print("Failed to load model. Exiting.")
        return
    
    print("✓ Model loaded successfully")
    
    # Step 3: Enhance query
    print("\nEnhancing query...")
    enhanced_query = enhance_search_query(user_query, model)
    print(f"Enhanced Query: {enhanced_query}")
    
    # Step 4: First ambiguity analysis
    print("\nAnalyzing ambiguities (Round 1)...")
    ambiguity_analysis_1 = analyze_query_ambiguities(enhanced_query, model)
    
    if ambiguity_analysis_1.clarifying_questions:
        print(f"Found {len(ambiguity_analysis_1.clarifying_questions)} potential ambiguities")
        
        # Step 5: Get user responses
        user_responses_1 = ask_user_questions(ambiguity_analysis_1.clarifying_questions)
        
        if user_responses_1:
            # Step 6: Resolve ambiguities
            print("Resolving ambiguities (Round 1)...")
            resolver_result_1 = ambiguity_resolver(enhanced_query, user_responses_1, model)
            enhanced_query = resolver_result_1.refined_query
            print(f"Refined Query: {enhanced_query}")
        else:
            print("No user responses provided. Continuing with original enhanced query.")
    else:
        print("No ambiguities found in first analysis.")
    
    # # Step 7: Second iteration of ambiguity analysis
    # print("\nAnalyzing ambiguities (Round 2)...")
    # ambiguity_analysis_2 = analyze_query_ambiguities(enhanced_query, model)
    
    # if ambiguity_analysis_2.clarifying_questions:
    #     print(f"Found {len(ambiguity_analysis_2.clarifying_questions)} remaining ambiguities")
        
    #     # Get user responses for second round
    #     user_responses_2 = ask_user_questions(ambiguity_analysis_2.clarifying_questions)
        
    #     if user_responses_2:
    #         # Resolve second round of ambiguities
    #         print("Resolving ambiguities (Round 2)...")
    #         resolver_result_2 = ambiguity_resolver(enhanced_query, user_responses_2, model)
    #         enhanced_query = resolver_result_2.refined_query
    #         print(f"Final Refined Query: {enhanced_query}")
    #     else:
    #         print("No additional responses provided. Using current refined query.")
    # else:
    #     print("No additional ambiguities found.")
    
    # Step 8: Create dependency tree
    print("\nGenerating dependency research tree...")
    dependency_tree = build_dependency_research_tree(
        enhanced_query,
        model,
        max_depth=2,
        max_dependencies_per_node=2
    )
    
    # Display results
    print("\n" + "="*80)
    print("FINAL RESULTS")
    print("="*80)
    
    print(f"Final Query: {enhanced_query}")
    print()
    
    print("Dependency Tree Generated:")
    dependency_tree.print_tree()
    
    print("\n" + "="*80)
    print("EXECUTION SUMMARY")
    print("="*80)
    
    leaf_questions = dependency_tree.get_leaf_questions()
    execution_order = dependency_tree.get_execution_order()
    
    print(f"Total Questions: {dependency_tree.total_questions}")
    print(f"Leaf Questions: {len(leaf_questions)}")
    print(f"Max Depth: {dependency_tree.max_depth}")
    
    print(f"\nFirst 3 questions to research:")
    for i, node in enumerate(execution_order[:3], 1):
        print(f"  {i}. {node.question.question_text}")
    
    # Save dependency tree to JSON file
    print(f"\nSaving dependency tree to JSON...")
    tree_data = dependency_tree.to_dict()
    
    import json
    from datetime import datetime
    
    # Create filename with timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"dependency_tree_{timestamp}.json"
    
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(tree_data, f, indent=2, ensure_ascii=False)
        print(f"✓ Dependency tree saved to: {filename}")
    except Exception as e:
        print(f"Error saving JSON file: {e}")
    
    print("\n✓ Planner agent test completed successfully!")


if __name__ == "__main__":
    try:
        test_planner_agent()
    except KeyboardInterrupt:
        print("\n\nTest interrupted by user.")
    except Exception as e:
        print(f"\nError during test: {e}")
        import traceback
        traceback.print_exc()