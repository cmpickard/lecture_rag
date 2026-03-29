NEXT UP:
- Tinker with system prompt:
                      -- decide how much external knowledge to allow
                      -- other improvements?

- think about which model to use                      


  OPTIONAL FEATURES:
  -- Add an easy way for the LLM to offer a list of topics that it can respond to
  -- Personality drop-down menu -- each selection tied to a different system prompt
    -- Socratic -> prompts the user to think through things with questions
    -- Objections ->
    -- Explainer ->
    -- Zoomer Mode -> "God is hype af no cap, bro." etc.
  
  -- More stylistic changes
    -- dialog messages have a tag -- e.g. "Talkrates:"
    -- A different font for the assistnat messages


  NOT SURE IF HELPFUL:
  -- Add routing (?)
  -- Add query enrichment for retrieval
  -- Add structured query step that pulls course number from query, if present


  FACTS:
  - corpus before chunking ~250,000 words -> so 375,000 tokens
    - the context window for GPT-5 mini and nano is 500,000 tokens, so
    it's *technically* possible for me to send the entire corpus each time, but
    just barely. And that's far too much for the GPT-4 mini and micro models