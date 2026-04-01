NEXT UP:
- a cache for basic "explain concept X" queries? (would I need to use
that in conjunction with routing?)
- routing? then i have a "two tier" routing structure -- with the user able to
select the model, and me able to modify the system prompt I'm sending.
  - ROUTES:
    - Explain
    - Check understanding
    - Develop paper / ideas 

- Testing
  - Ask AI to generate testing suite for basic functionality on front- back-ends
  
- Move the switch over next to the submit button so it's a better reminder to
use it


OPTIONAL:
- User feedback thumbs-up / thumbs-down?

- Conversation summary feature for conversations that reach a certain length?

  FACTS:
  - corpus before chunking ~250,000 words -> so 375,000 tokens
    - the context window for GPT-5 mini and nano is 500,000 tokens, so
    it's *technically* possible for me to send the entire corpus each time, but
    just barely. And that's far too much for the GPT-4 mini and micro models