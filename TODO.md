NEXT UP:     
- Add a way to delete conversations
- Make markdown appear prettier

  OPTIONAL FEATURES:
  -- Personality drop-down menu -- each selection tied to a different system prompt
    -- Socratic -> prompts the user to think through things with questions
    -- Objections -> reasoning model?
    -- Explainer ->
    -- Zoomer Mode -> "God is hype af no cap, bro." etc.
    -- Paper mode? -> allows access to outside sources
    ==> OR, query classification
    
  -- MAYBE: Single slider that toggles between Explainer mode and Dialogue mode
    -- the former is fast and straightfoward, using a smaller model
    -- the latter is slower and smarter, using a reasoning model


  NOT SURE IF HELPFUL:
  -- Add routing (?)
  -- Add query enrichment for retrieval
  -- Add structured query step that pulls course number from query, if present


  FACTS:
  - corpus before chunking ~250,000 words -> so 375,000 tokens
    - the context window for GPT-5 mini and nano is 500,000 tokens, so
    it's *technically* possible for me to send the entire corpus each time, but
    just barely. And that's far too much for the GPT-4 mini and micro models