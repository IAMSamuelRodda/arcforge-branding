# User Personalization & Learning Analysis

**Date**: 2025-11-11
**Context**: Understanding how to make Brand Forge learn user styles, communication preferences, and brand-specific patterns

---

## Problem Statement

Brand Forge should learn and adapt to:
1. **User communication style**: Formal vs casual, technical vs creative language
2. **Brand preferences**: Which visual directions, color schemes, compositions perform best
3. **Approval patterns**: What the user consistently approves/rejects and why
4. **Workflow preferences**: How much guidance needed, checkpoint frequency, etc.

**Key Question**: Is this RAG, LangChain, LLM chat interface, or something else?

---

## Component Clarification

### 1. RAG (Retrieval-Augmented Generation)

**What it is**:
- Retrieves relevant documents/knowledge from a database
- Augments LLM context with retrieved information
- Uses vector embeddings for semantic search

**Use cases**:
- "Find similar approved logos from past projects"
- "What prompts worked well for this brand's aesthetic?"
- "Retrieve design guidelines from past conversations"

**Example**:
```python
# User asks: "Generate a logo like the one we approved last month"
query_embedding = embed("logo approved last month")
similar_results = vectordb.search(query_embedding, top_k=5)
context = format_results(similar_results)
llm_response = llm.generate(f"{context}\n\nUser: {user_query}")
```

**Verdict for user learning**: ✅ **Yes, this is RAG** - Retrieving past interactions/preferences

---

### 2. LangChain Memory

**What it is**:
- Manages conversation history and context
- Multiple memory types: Buffer, Summary, Entity, Knowledge Graph
- Structures how past interactions are fed to LLM

**Use cases**:
- Conversation history within a session
- Summarizing long conversations
- Tracking entities mentioned (brands, colors, styles)

**Example**:
```python
from langchain.memory import ConversationSummaryMemory

memory = ConversationSummaryMemory(llm=llm)
memory.save_context(
    {"input": "I want a minimalist logo"},
    {"output": "Great! I'll generate clean, simple designs"}
)

# Later in conversation
context = memory.load_memory_variables({})
# Returns summary of past conversation
```

**Verdict for user learning**: ⚠️ **Partial** - Good for session memory, not long-term learning

---

### 3. LLM Chat Interface (System Prompts)

**What it is**:
- System-level instructions that persist across messages
- Defines LLM behavior, tone, personality
- Static per-conversation (not learned)

**Use cases**:
- Setting communication style
- Defining role/persona
- Providing fixed context

**Example**:
```python
system_prompt = """You are a brand design assistant.
User preferences: Minimalist aesthetic, sans-serif fonts, muted colors.
Communication style: Professional but friendly, explain design choices."""

messages = [
    {"role": "system", "content": system_prompt},
    {"role": "user", "content": "Generate a logo"},
]
```

**Verdict for user learning**: ❌ **No** - Static configuration, not learning

---

## User Personalization Architecture

### What You Actually Want: **Hybrid Approach**

Your use case requires **all three layers working together**:

```
┌────────────────────────────────────────────────────────────────┐
│                    USER PERSONALIZATION SYSTEM                  │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Layer 1: USER PROFILE (Static preferences)                    │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite: users.db                                        │  │
│  │  • User ID: samuel_rodda                                 │  │
│  │  • Communication style: "professional, detailed"         │  │
│  │  • Preferred guidance level: "high" (explain choices)    │  │
│  │  • Checkpoint frequency: "every 50 generations"          │  │
│  │  • Last updated: 2025-11-11                              │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  Layer 2: BRAND-SPECIFIC LEARNING (Structured analytics)       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  SQLite: brand_learnings.db                              │  │
│  │  • Brand: ArcForge                                       │  │
│  │  • Visual direction: Minimalist (80% approval rate)      │  │
│  │  • Color accuracy: SD 3.5 best (+15% vs Flux)           │  │
│  │  • Best prompts: "geometric", "clean lines", "metallic" │  │
│  │  • Approval patterns: Rejects busy compositions          │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  Layer 3: INTERACTION HISTORY (RAG - Semantic retrieval)       │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  VectorDB: Pinecone/Weaviate                             │  │
│  │  • Past conversations (timestamped)                      │  │
│  │  • Approved/rejected generations (with feedback)         │  │
│  │  • Design evolution notes                                │  │
│  │  • Semantic search: "find logos like that anvil design"  │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  Layer 4: SESSION MEMORY (LangChain - Short-term context)      │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  ConversationSummaryMemory                               │  │
│  │  • Current session history (last 10 messages)            │  │
│  │  • Active context: "We're refining the anvil concept"    │  │
│  │  • Entities mentioned: anvil, circuit traces, orange     │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│  Layer 5: DYNAMIC SYSTEM PROMPT (Assembled from above)         │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │  System Prompt Builder                                   │  │
│  │  • Injects user profile (communication style)            │  │
│  │  • Injects brand learnings (best practices)              │  │
│  │  • Injects relevant history (RAG retrieval)              │  │
│  │  • Includes session context (LangChain memory)           │  │
│  │  → Personalized system prompt per request                │  │
│  └──────────────────────────────────────────────────────────┘  │
│                          │                                      │
│                          ▼                                      │
│                    LLM API Call                                 │
│              (Claude, GPT-4, etc.)                              │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

---

## Detailed Layer Breakdown

### Layer 1: User Profile (SQLite)

**What to store**:
```python
# users table
{
    "user_id": "samuel_rodda",
    "communication_style": "professional_detailed",  # vs casual, terse, creative
    "explanation_level": "high",  # low, medium, high
    "checkpoint_frequency": 50,  # generations between checkpoints
    "preferred_models": ["sd35", "flux"],  # if user has model preferences
    "created_at": "2025-11-11",
    "last_active": "2025-11-11"
}
```

**Why SQLite, not RAG**:
- Small, structured data
- Exact lookups by user_id
- Updated manually by user or through settings UI

---

### Layer 2: Brand-Specific Learning (SQLite)

**What to store**:
```python
# brand_learnings table
{
    "brand_id": "arcforge",
    "user_id": "samuel_rodda",

    # Visual preferences (from approval patterns)
    "visual_direction": {
        "minimalist": 0.80,  # 80% approval rate
        "cosmic": 0.45,
        "industrial": 0.62
    },

    # Model performance (which model works best)
    "model_performance": {
        "sd35": {"avg_score": 0.78, "approval_rate": 0.75},
        "flux": {"avg_score": 0.72, "approval_rate": 0.68},
        "dalle": {"avg_score": 0.65, "approval_rate": 0.60}
    },

    # Effective prompt keywords
    "effective_keywords": [
        {"keyword": "geometric", "score_boost": 0.12},
        {"keyword": "metallic", "score_boost": 0.08},
        {"keyword": "clean lines", "score_boost": 0.15}
    ],

    # Rejection patterns (what user dislikes)
    "rejection_patterns": [
        {"pattern": "busy composition", "rejection_rate": 0.85},
        {"pattern": "too many colors", "rejection_rate": 0.78}
    ],

    "last_updated": "2025-11-11"
}
```

**Why SQLite, not RAG**:
- Aggregated analytics (not raw interactions)
- Queried by brand_id + metric
- Updated via batch analytics jobs (daily/weekly)

**How it's computed**:
```python
def update_brand_learnings(brand_id: str):
    """Compute brand-specific patterns from generation history."""

    # Get all generations for this brand
    generations = db.query(
        "SELECT * FROM generations WHERE brand_id = ?",
        (brand_id,)
    )

    # Compute approval rates by visual direction
    visual_direction_stats = {}
    for gen in generations:
        direction = gen['visual_direction']
        if direction not in visual_direction_stats:
            visual_direction_stats[direction] = {'approved': 0, 'total': 0}

        visual_direction_stats[direction]['total'] += 1
        if gen['approval_status'] == 'approved':
            visual_direction_stats[direction]['approved'] += 1

    # Store learned patterns
    for direction, stats in visual_direction_stats.items():
        approval_rate = stats['approved'] / stats['total']
        db.execute(
            "UPDATE brand_learnings SET visual_direction = ? WHERE brand_id = ?",
            ({direction: approval_rate}, brand_id)
        )
```

---

### Layer 3: Interaction History (RAG)

**What to store**:
```python
# VectorDB documents
{
    "id": "conv_2025_11_11_001",
    "user_id": "samuel_rodda",
    "brand_id": "arcforge",
    "timestamp": "2025-11-11T14:30:00Z",
    "interaction_type": "approval",

    # Text content (embedded)
    "content": """
    User approved image #1234 with feedback:
    'Love the metallic anvil shape with orange highlights.
    The circuit traces feel too busy though - simplify next iteration.'

    Image metadata:
    - Model: Stable Diffusion 3.5
    - Prompt: 'A minimalist geometric logo featuring an anvil shape...'
    - Visual direction: Minimalist
    - Quality score: 0.82
    """,

    # Metadata (for filtering)
    "metadata": {
        "generation_id": 1234,
        "approval_status": "approved",
        "visual_direction": "minimalist",
        "model": "sd35",
        "has_feedback": true
    }
}
```

**Why RAG (VectorDB)**:
- Need semantic search: "Find logos similar to that anvil design"
- Large, unstructured text (conversations, feedback)
- Cross-session retrieval: "What did we discuss about anvils last month?"

**Retrieval examples**:
```python
# Example 1: Find similar approved designs
query = "Find logos with anvil shapes that user approved"
results = vectordb.search(
    embed(query),
    filter={"user_id": "samuel_rodda", "approval_status": "approved"},
    top_k=5
)

# Example 2: Recall past feedback on a topic
query = "What feedback did user give about color usage?"
results = vectordb.search(
    embed(query),
    filter={"has_feedback": true, "brand_id": "arcforge"},
    top_k=10
)
```

---

### Layer 4: Session Memory (LangChain)

**What to store**:
```python
from langchain.memory import ConversationSummaryBufferMemory

memory = ConversationSummaryBufferMemory(
    llm=llm,
    max_token_limit=2000,  # Keep last ~10 messages
    return_messages=True
)

# During session
memory.save_context(
    {"input": "I want to refine the anvil logo from checkpoint 2"},
    {"output": "I'll retrieve the anvil concepts from checkpoint 2 and generate variations..."}
)

# Later in same session
context = memory.load_memory_variables({})
# Returns: "User is refining anvil logo from checkpoint 2..."
```

**Why LangChain Memory**:
- Short-term context within a session
- Automatic summarization as conversation grows
- Entity tracking (mentioned brands, concepts, etc.)

---

### Layer 5: Dynamic System Prompt Assembly

**How it all comes together**:

```python
class PersonalizedPromptBuilder:
    """Builds personalized system prompts from user profile, learnings, history."""

    def __init__(self, user_id: str, brand_id: str):
        self.user_id = user_id
        self.brand_id = brand_id

        # Load static profile
        self.profile = self._load_user_profile(user_id)

        # Load brand learnings
        self.learnings = self._load_brand_learnings(brand_id)

        # Initialize RAG retriever
        self.retriever = VectorDBRetriever(vectordb)

        # Initialize session memory
        self.memory = ConversationSummaryBufferMemory(llm=llm)

    def build_system_prompt(self, user_query: str) -> str:
        """Build personalized system prompt for this request."""

        # Base system prompt
        base = """You are a brand design assistant for Brand Forge.
Your role is to help users generate and refine brand assets."""

        # Inject user communication style
        style_instructions = self._get_style_instructions(self.profile)

        # Inject brand-specific learnings
        brand_context = self._format_brand_learnings(self.learnings)

        # Retrieve relevant past interactions (RAG)
        relevant_history = self.retriever.retrieve(
            query=user_query,
            filter={"user_id": self.user_id, "brand_id": self.brand_id},
            top_k=3
        )
        history_context = self._format_history(relevant_history)

        # Get session memory
        session_context = self.memory.load_memory_variables({})

        # Assemble personalized prompt
        system_prompt = f"""{base}

## User Communication Preferences
{style_instructions}

## Brand-Specific Learnings (ArcForge)
{brand_context}

## Relevant Past Interactions
{history_context}

## Current Session Context
{session_context}

Now respond to the user's request with this personalized context."""

        return system_prompt

    def _get_style_instructions(self, profile: dict) -> str:
        """Convert profile settings to LLM instructions."""
        style = profile['communication_style']

        if style == 'professional_detailed':
            return """- Use professional, clear language
- Provide detailed explanations of design choices
- Include technical reasoning (color theory, composition)"""
        elif style == 'casual_brief':
            return """- Use casual, friendly tone
- Keep explanations concise
- Focus on outcomes, not technical details"""
        # ... more styles

    def _format_brand_learnings(self, learnings: dict) -> str:
        """Format brand learnings for system prompt."""
        return f"""
Based on past approvals for this brand:
- Visual direction: Minimalist style (80% approval rate)
- Best model: Stable Diffusion 3.5 (78% avg score)
- Effective keywords: "geometric", "metallic", "clean lines"
- Avoid: Busy compositions, too many colors
"""

    def _format_history(self, results: List[dict]) -> str:
        """Format RAG retrieval results."""
        if not results:
            return "No relevant past interactions."

        formatted = []
        for i, result in enumerate(results, 1):
            formatted.append(f"{i}. {result['content'][:200]}...")

        return "\n".join(formatted)
```

---

## Implementation Roadmap

### Phase 1 (v1.0): Basic Profiles + Analytics
**Storage**: SQLite only
- User profile table (communication style, preferences)
- Brand learnings table (computed from generation history)
- No RAG, no LangChain yet

**Why start here**:
- Simplest implementation
- Covers 80% of personalization needs
- No external dependencies
- $0 cost

### Phase 2 (v1.1): Session Memory
**Add**: LangChain memory
- Track conversation within sessions
- Summarize long exchanges
- Maintain context across approval checkpoints

**Why now**:
- User has multi-turn conversations
- Need to reference earlier in session
- LangChain handles summarization

### Phase 3 (v1.2): Semantic History Retrieval
**Add**: RAG with VectorDB
- Store all interactions, feedback, approved/rejected generations
- Semantic search for "find logos like X"
- Cross-session learning

**Why last**:
- Most complex (VectorDB hosting)
- Highest cost ($20-50/month)
- Only needed once user has rich history (6+ months of usage)

---

## Cost Analysis

| Component | Phase | Cost |
|-----------|-------|------|
| SQLite user profiles | v1.0 | $0 |
| SQLite brand learnings | v1.0 | $0 |
| LangChain memory | v1.1 | $0 (local) |
| RAG embeddings | v1.2 | ~$5/month (1K interactions) |
| VectorDB (Pinecone) | v1.2 | $25/month (Starter plan) |
| **Total** | **v1.2** | **~$30/month** |

---

## Answers to Your Questions

### "Is this RAG?"
**Partial**: Layer 3 (Interaction History) is RAG. But you also need Layers 1-2 (structured data) and Layer 4 (session memory).

### "Is this LangChain?"
**Partial**: Layer 4 (Session Memory) uses LangChain. But it's one piece of the puzzle.

### "Is it on the LLM chat interface side?"
**Yes, ultimately**: Layer 5 assembles everything into the system prompt that goes to the LLM. But the learning happens in Layers 1-3 (storage), not in the LLM itself.

---

## Key Insight

**User personalization is a HYBRID**:
- 🗄️ **Structured data** (SQLite) for profiles and analytics
- 🔍 **RAG** (VectorDB) for semantic search of past interactions
- 💬 **LangChain** for session memory management
- 🤖 **System prompts** to inject all the above into LLM context

The LLM doesn't "learn" - you build a personalization engine that **feeds learned context to the LLM** on every request.

---

## Recommendation

**Start simple, scale complexity**:

1. **v1.0**: SQLite profiles + learnings (covers 80% of needs, $0 cost)
2. **v1.1**: Add LangChain session memory (better UX, $0 cost)
3. **v1.2**: Add RAG if user has rich history (6+ months, ~$30/month)

Don't over-engineer early. User profiles and analytics will feel personalized without needing RAG/VectorDB upfront.
