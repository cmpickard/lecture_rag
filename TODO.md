NEXT UP:     
- Add a way to delete conversations

  OPTIONAL FEATURES:


  NOT SURE IF HELPFUL:
  -- Add routing (?)
  -- Add query enrichment for retrieval
  -- Add structured query step that pulls course number from query, if present


  FACTS:
  - corpus before chunking ~250,000 words -> so 375,000 tokens
    - the context window for GPT-5 mini and nano is 500,000 tokens, so
    it's *technically* possible for me to send the entire corpus each time, but
    just barely. And that's far too much for the GPT-4 mini and micro models