## MCP Rule: Database-Only Biblical Answers

- All biblical answers must come **only** from the `bible_db` database.
- LLMs (including LM Studio) may only summarize, paraphrase, or format results from the database.
- LLMs must **never** generate biblical content directly or use their own knowledge.
- If the answer is not in the database, the system must respond:

  > Sorry, I can only answer using the Bible database. No answer found for your query.

- This rule is enforced in all API endpoints, web UI, and LLM/system prompts. 