import asyncio
import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from writer.test import research_data
from writer.report_writer import Writer
from publisher.publisher import Publisher

async def test_report_generation_and_publishing():
    print("🚀 Starting Report Generation and Publishing Test...")

    # 1. Mock AgentState
    print("📦 Preparing Mock State...")
    user_query = "What are the major technological challenges preventing widespread adoption of quantum computing?"
    
    start_state = {
        "user_query": user_query,
        "planner_query": [
            {"query_num": 1, "query": "Technological challenges of quantum computing"},
            {"query_num": 2, "query": "Quantum error correction evolution"},
            {"query_num": 3, "query": "Materials science for quantum processors"}
        ],
        "research_review": [
            {
                "query_num": 1,
                "raw_research_results": research_data
            }
        ]
    }

    # 2. Run Writer
    print("\n✍️  Running Writer...")
    writer = Writer()
    writer_result = await writer.run(start_state)
    
    # Update state with writer output
    current_state = start_state.copy()
    current_state.update({
        "report_table_of_contents": writer_result["table_of_contents"],
        "report_abstract": writer_result["abstract"],
        "report_introduction": writer_result["introduction"],
        "report_body": writer_result["report_body"],
        "report_conclusion": writer_result["conclusion"]
    })

    print("✅ Writer Complete!")
    print(f"   Abstract Length: {len(current_state['report_abstract'])} chars")
    print(f"   Body Length: {len(current_state['report_body'])} chars")

    # Save report to markdown file
    output_md_path = "writer/test_output_report.md"
    with open(output_md_path, 'w', encoding='utf-8') as f:
        # Write Table of Contents
        f.write("# Table of Contents\n\n")
        toc = current_state['report_table_of_contents']
        if isinstance(toc, dict):
            for chapter, subchapters in toc.items():
                f.write(f"- {chapter}\n")
                for sub in subchapters:
                    f.write(f"  - {sub}\n")
        else:
            f.write(str(toc))
        f.write("\n---\n\n")
        
        # Write Abstract
        f.write("# Abstract\n\n")
        f.write(current_state['report_abstract'])
        f.write("\n\n---\n\n")
        
        # Write Introduction
        f.write("# Introduction\n\n")
        f.write(current_state['report_introduction'])
        f.write("\n\n---\n\n")
        
        # Write Report Body
        f.write(current_state['report_body'])
        f.write("\n\n---\n\n")
        
        # Write Conclusion
        f.write("# Conclusion\n\n")
        f.write(current_state['report_conclusion'])
        f.write("\n")
    
    print(f"\n📄 Report saved to: {output_md_path}")

    # 3. Run Publisher
    print("\n🖨️  Running Publisher...")
    publisher = Publisher()
    final_state = await publisher.run("pdf", current_state)

    final_params = final_state.get('final_report_path', '')
    
    if final_params and os.path.exists(final_params):
        print(f"\n🎉 Success! PDF Report generated at: {final_params}")
    else:
        print("\n❌ Failed to generate PDF report.")

if __name__ == "__main__":
    asyncio.run(test_report_generation_and_publishing())
