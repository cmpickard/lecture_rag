NEXT UP:
- Reorganization and refactor

- Testing
  - Test what happens when you ask outside of expertise area
  - Test more with the 2 modes -- esp. help writing papers
  - Ask AI to generate testing suite for basic functionality on front- back-ends

- Prompt refinement
  - Don't just say, "DONT OVERWHELM", give an example of an interaction,
    User: "I want to write a paper arguing that animal suffering isn't a problem
    for the soul-making theodicy is b/c animals don't have souls."

    Assistant: "Interesting idea! To adequately defend that thesis, there are a
    few obvious and important questions you'll need to answer.
    
    First, why should
    we think animals don't have souls? What evidence do you have for this? How
    would you convince someone who agrees with you that souls exist that no
    animal does have or has ever had a soul? Or, is the claim that the Soul-making
    Theodicy is *committed* to animals not having souls? If that's the claim, then
    you'll want to give an argument explaining why that entailment is plausible-enough
    that we shouldn't outright reject the Soul-making Theodicy.
    
    Second, why should we think that
    having a soul is required for suffering? Why not think, instead, that all
    that's required for suffering is the potential for sentient experiences --
    for which, all one needs is a moderately complex brain? (And clearly some
    animals have sentient experiences, therefore etc.) "


OPTIONAL:
- User feedback thumbs-up / thumbs-down?

- Conversation summary feature for conversations that reach a certain length?

  FACTS:
  - corpus before chunking ~250,000 words -> so 375,000 tokens
    - the context window for GPT-5 mini and nano is 500,000 tokens, so
    it's *technically* possible for me to send the entire corpus each time, but
    just barely. And that's far too much for the GPT-4 mini and micro models