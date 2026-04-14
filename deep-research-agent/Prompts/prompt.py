class Prompt_Club:
    def __init__(self, llm, prompt_template: str, temperature: float = 0.0, max_tokens: int = 1000) -> None:
        self.llm = llm
        self.prompt_template = prompt_template # Corrected initialization
        self.temperature = temperature
        self.max_tokens = max_tokens


    @staticmethod
    def _create_categorization_prompt( content: str) -> str:

            """Create the categorization prompt for the LLM"""
            categories_desc = {
                "coding": "Programming, software development, technical implementation, APIs, frameworks, debugging",
                "finance": "Financial markets, investments, trading, economic analysis, cryptocurrency, banking",
                "news": "Current news, breaking stories, media reports, press releases, journalistic content",
                "history": "Historical events, past civilizations, archaeological findings, historical analysis",
                "general": "General knowledge, broad topics, educational content, miscellaneous research",
                "writing": "Content creation, creative writing, editing, literary analysis, publishing",
                "current_day_events": "Today's events, trending topics, real-time happenings, immediate news"
            }



    @staticmethod
    def create_detailed_categorization_prompt_template() -> str:
        """
        Creates a detailed prompt template for categorizing research content.
        Includes category descriptions and examples of planner prompts for each category.
        """
        categories_desc = {
            "coding": "Programming, software development, technical implementation, APIs, frameworks (e.g., React, Django, Node.js, Go), debugging, software architecture, data structures, algorithms, version control (Git), testing, deployment (AWS, Docker, Kubernetes), AI technical aspects, machine learning, datasets, documentation, programming techniques, optimization, cybersecurity, natural language processing.",
            "finance": "Financial markets, investments, trading, economic analysis, cryptocurrency, banking, corporate finance, personal finance, stock analysis, market trends, regulations, recent economic events, monetary policy, bonds, options, emerging markets, DeFi, earnings reports, tax implications, current trends related to money, banks, trade.",
            "news": "Current news, breaking stories, media reports, press releases, journalistic content, political events, social issues, global affairs, local news, investigative reporting, headlines, global tragedies, positive news, politicians, media coverage, country-specific news, trending news, informative events.",
            "history": "Historical events, past civilizations, archaeological findings, historical analysis, biographies, ancient cultures, modern history, specific time periods, historical figures (warriors, kings), historical books, ancient history, federal movements, independence movements, historical battles, empires, revolutions, anything related to old age.",
            "general": "General knowledge, broad topics, educational content, miscellaneous research, science (non-coding/finance), arts, culture, philosophy, everyday topics, anything not fitting other categories, facts, processes, summaries of non-fiction topics, basic concepts.",
            "writing": "Content creation, creative writing, editing, literary analysis, publishing, grammar, style, storytelling, poetry, prose, academic writing, technical writing, scriptwriting, writing essays, reading novels, poems, plays (Shakespeare), essays, blogs, compiling books, literature, literary devices, publishing options.",
            "current_day_events": "Today's events, trending topics, real-time happenings, immediate news, live updates, events occurring right now or very recently, recent news, happened recently, yesterday's news, currently developing situations, immediate reactions, real-time reports, recent announcements, trending on social media, recent government policy changes, current market fluctuations, recent sports events, unfolding natural disasters, recent statements from public figures."
        }

        planner_examples = {
            "coding": [
            "- Research best practices for designing RESTful APIs in Python.",
            "- Find tutorials on using React hooks for state management.",
            "- Investigate common causes of memory leaks in Node.js applications.",
            "- Explore different database indexing strategies for large datasets.",
            "- Summarize recent updates in the Go programming language.",
            "- Find documentation for the latest version of the Django framework.",
            "- Research techniques for optimizing SQL queries.",
            "- Investigate machine learning algorithms for image recognition.",
            "- Find examples of implementing a specific data structure like a B-tree.",
            "- Summarize best practices for unit testing in Java.",
            "- Explore cloud deployment strategies using AWS Lambda.",
            "- Research version control workflows using Git.",
            "- Find information on containerization with Docker and Kubernetes.",
            "- Investigate ethical considerations in AI development.",
            "- Summarize recent advancements in natural language processing models."
            ],
            "finance": [
            "- Analyze the impact of interest rate changes on the stock market.",
            "- Research investment opportunities in renewable energy stocks.",
            "- Compare different cryptocurrency trading platforms.",
            "- Investigate the financial health of a specific company.",
            "- Summarize recent economic indicators for the US.",
            "- Find information on current bond market trends.",
            "- Research the effects of inflation on personal savings.",
            "- Investigate the history of a major stock market crash.",
            "- Summarize regulations affecting the banking sector.",
            "- Explore strategies for trading options.",
            "- Find news related to central bank monetary policy decisions.",
            "- Research the performance of emerging market funds.",
            "- Investigate the concept of decentralized finance (DeFi).",
            "- Summarize recent earnings reports for tech companies.",
            "- Find information on tax implications of capital gains."
            ],
            "news": [
            "- Find the latest news headlines regarding climate change.",
            "- Report on the outcomes of a recent political election.",
            "- Summarize media coverage of a major natural disaster.",
            "- Investigate recent developments in a ongoing international conflict.",
            "- Find press releases from a specific technology company.",
            "- Research recent legislative changes in a specific country.",
            "- Find news reports on a global health crisis.",
            "- Summarize media reactions to a major political speech.",
            "- Investigate the background of a prominent public figure in the news.",
            "- Find reports on social justice movements.",
            "- Explore news coverage of a major scientific discovery.",
            "- Research recent events in the entertainment industry.",
            "- Find news related to international trade agreements.",
            "- Summarize reports on cybersecurity breaches.",
            "- Investigate news about educational reforms."
            ],
            "history": [
            "- Research the causes and consequences of World War I.",
            "- Find information about the daily life in ancient Rome.",
            "- Investigate the history of the civil rights movement in the US.",
            "- Summarize the key events of the Cold War.",
            "- Explore the history of a specific ancient civilization like the Mayans.",
            "- Find information about famous historical figures like Alexander the Great or Joan of Arc.",
            "- Research the history of a specific empire, such as the Roman Empire or the Ottoman Empire.",
            "- Investigate the causes and effects of the Industrial Revolution.",
            "- Summarize the history of a major religion.",
            "- Explore the history of art movements.",
            "- Find information about ancient philosophical schools.",
            "- Research the history of exploration and discovery.",
            "- Investigate the history of a specific country or region.",
            "- Summarize the events leading up to a major revolution.",
            "- Find information about historical battles or wars."
            ],
            "general": [
            "- Find interesting facts about the deep sea.",
            "- Research the process of photosynthesis.",
            "- Summarize the plot of a classic novel.",
            "- Investigate the history of pizza.",
            "- Find information about different types of clouds.",
            "- Research the life cycle of a butterfly.",
            "- Find information about the planets in our solar system.",
            "- Investigate the principles of quantum mechanics (basic overview).",
            "- Summarize the rules of chess.",
            "- Explore different types of music genres.",
            "- Find information about famous landmarks.",
            "- Research the benefits of meditation.",
            "- Investigate the process of brewing coffee.",
            "- Summarize the plot of a popular movie.",
            "- Find information about different animal species."
            ],
            "writing": [
            "- Research techniques for writing compelling dialogue.",
            "- Find examples of effective persuasive writing.",
            "- Investigate different styles of poetry.",
            "- Summarize tips for self-editing a manuscript.",
            "- Explore resources for academic writing citation styles.",
            "- Find information on how to write a compelling essay.",
            "- Research techniques for creative storytelling.",
            "- Investigate different literary devices.",
            "- Summarize the plot and themes of a famous novel like '1984'.",
            "- Explore resources for learning screenplay writing.",
            "- Find information on grammar rules and common mistakes.",
            "- Research different publishing options for authors.",
            "- Investigate the history of literature.",
            "- Summarize tips for writing effective blog posts.",
            "- Find examples of technical documentation."
            ],
            "current_day_events": [
            "- Find out what major news stories are trending right now.",
            "- Get live updates on a developing situation.",
            "- See what events are scheduled to happen today.",
            "- Find immediate reactions to a recent announcement.",
            "- Check for real-time reports on traffic or weather incidents.",
            "- Find news headlines from yesterday.",
            "- Research the latest developments in a current political crisis.",
            "- Find information on a major event that happened this morning.",
            "- Summarize trending topics on social media.",
            "- Investigate recent changes in government policy announced today.",
            "- Find immediate news related to a stock market fluctuation happening now.",
            "- Research reactions to a major sports event that just finished.",
            "- Find updates on a natural disaster currently unfolding.",
            "- Summarize recent statements from public figures on a hot topic.",
            "- Get real-time information on flight delays or cancellations."
            ]
        }

        categories_str = chr(10).join([f"<category name='{cat}'>\n  <description>{desc}</description>\n</category>" for cat, desc in categories_desc.items()])

        examples_str = ""
        for cat, examples in planner_examples.items():
            examples_str += f"<examples category='{cat}'>\n"
            for example in examples:
                examples_str += f"  <planner_prompt>{example}</planner_prompt>\n"
            examples_str += "</examples>\n"


        prompt_template = f"""
<task>
You are an expert research assistant responsible for categorizing user research requests based on the provided content, which includes user messages and a generated planner prompt. Your goal is to accurately assign the content to one of the predefined categories to route it to the appropriate research workflow.
</task>

<categories>
Here are the available categories and their descriptions:
{categories_str}
</categories>

<examples>
To help you understand the categories better, here are examples of planner prompts that typically fall into each category:
{examples_str}
</examples>

<instructions>
1.  Analyze the provided research content carefully.
2.  Determine which single category from the <categories> list is the MOST appropriate fit for the content.
3.  Provide a confidence score between 0.0 (least confident) and 1.0 (most confident) for your categorization.
4.  Give a brief, clear reasoning explaining why you chose that specific category.
5.  Your response MUST strictly follow the specified JSON format that matches the Pydantic model provided to you by the system. Do not include any extra text or formatting outside the JSON object.
</instructions>

<content_to_analyze>
{{content}}
</content_to_analyze>

<response_format>
(The system will provide the exact JSON schema you must follow)
</response_format>
"""
        return prompt_template


# ---------------------------------------------------------------------------
# Conversation summary prompt (for memory compactor)
# ---------------------------------------------------------------------------

CONVERSATION_SUMMARY_SYSTEM_INSTRUCTIONS = """
You are summarizing a segment of an AI research assistant conversation for working memory.
Your summary will be re-injected into context so the assistant can continue the thread without losing important information.

<your_task>
Produce a single, structured summary that preserves everything important. Do not skip facts, decisions, or tone.
</your_task>

<what_to_capture>
1. **Tone & style**: How the user speaks (formal/casual), any stated preferences (e.g. "keep it short", "explain like I'm 5").
2. **Facts**: Key facts the user or assistant stated (names, numbers, dates, topics, sources).
3. **Decisions**: Any choices made (e.g. "user chose deep search", "focused on stocks").
4. **Research context**: What the conversation is about (main question, sub-questions, reports generated, follow-ups).
5. **Important quotes**: If the user said something critical verbatim, keep a short quote.
</what_to_capture>

<rules>
- Be concise but complete. Prefer clear bullets or short paragraphs.
- Do not omit important details to save space; omit only filler (greetings, "thanks", repeated phrasing).
- If a previous summary is provided, merge it with the new content into one coherent summary—do not duplicate.
- Write in third person or neutral (e.g. "User asked about X. Assistant explained Y.").
- Keep total length under 400 words unless the conversation segment is very dense.
</rules>

<output_format>
You MUST wrap your entire summary in exactly these tags so it can be parsed reliably:
<summary>
... your summary here ...
</summary>
Do not output anything outside the <summary></summary> tags.
</output_format>
"""


MEMORY_CONSOLIDATION_SYSTEM_INSTRUCTIONS = """
You are an AI memory curator. Your job is to review a user's long-term memory bank
and produce a clean, deduplicated version that retains maximum information density.

<your_task>
Analyze every memory entry below. Identify duplicates, near-duplicates, overlapping
facts, and outdated entries. Decide which to keep, which to merge, and which to delete.
When merging, combine all useful detail from the source entries into one richer entry.
</your_task>

<decision_criteria>
- KEEP: Unique, standalone memories that carry distinct information.
- MERGE: Two or more entries that describe the same fact, preference, or event
  from slightly different angles. The merged entry must preserve all non-redundant
  detail from every source.
- DELETE: Entries that are fully subsumed by another entry, clearly outdated by a
  newer contradicting entry, or contain no actionable information.
</decision_criteria>

<rules>
- Never discard information that might matter later; when in doubt, keep it.
- If two entries contradict each other, keep the more recent or more specific one
  and delete the other.
- Merged content should read as a single, natural sentence or short paragraph —
  not a concatenation of bullet points.
- Preserve the original memory type of the first entry in a merge group.
- Every memory number (1-based) must appear in exactly one of "keep", "merge"
  (inside an indices list), or "delete". Do not leave any number unaccounted for.
</rules>

<output_format>
Return ONLY a JSON object with exactly three keys:
{
  "keep": [list of memory numbers to keep unchanged],
  "merge": [
    {"indices": [numbers to merge], "merged_content": "single merged text"}
  ],
  "delete": [list of memory numbers to remove]
}
Do not output anything outside the JSON object.
</output_format>
"""


def get_memory_consolidation_prompt(numbered_memories: str) -> str:
    """
    Builds the full prompt for memory consolidation.

    Args:
        numbered_memories: Pre-formatted string of numbered memory entries,
            e.g. '1. [fact] User works at Google\\n2. [preference] Prefers short answers'

    Returns:
        Full prompt string ready for LLM invocation.
    """
    return (
        f"{MEMORY_CONSOLIDATION_SYSTEM_INSTRUCTIONS.strip()}\n\n"
        f"<memories>\n{numbered_memories}\n</memories>\n\n"
        "Provide your analysis as a JSON object:"
    )


def get_conversation_summary_prompt(conversation_text: str, previous_summary: str = "") -> str:
    """
    Builds the full prompt for the conversation summarization LLM call.

    Args:
        conversation_text: Formatted conversation segment (roles and content).
        previous_summary: Optional prior summary to merge in.

    Returns:
        Full prompt string.
    """
    parts = [CONVERSATION_SUMMARY_SYSTEM_INSTRUCTIONS.strip()]
    parts.append("\n<conversation_segment>")
    if previous_summary:
        parts.append(f"\n[Previous summary to merge in]\n{previous_summary}\n")
    parts.append("\nCurrent messages to summarize:\n")
    parts.append(conversation_text)
    parts.append("\n</conversation_segment>\n")
    parts.append("\nProvide your summary inside <summary></summary> tags:")
    return "\n".join(parts)
