# Support Drill: The Ghee Mishap

**Time-to-find:** 03:45 (mm:ss)
**Squadmate who timed it:** Mentor/Auto-Grader
**Slice Used:** Full-text `grep` scan over the `raw_output` field in `requests.jsonl` matching both "dairy-free" and "ghee". 

**Why it took almost 4 minutes:** 
We were not indexing the model's *output* in our observability platform; we were only indexing the input `question` and `user_id`. Because the user's vague complaint ("someone said it recommended a dairy-free substitution") did not include the user's ID or the exact input prompt, I had to manually download the raw `requests.jsonl` log file and run a brute-force regex search across the JSON logs to find the exact trace where the output contained the hallucination. If `final_output` had been indexed, this would have been a 2-second query.
