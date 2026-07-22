# 🟡 Blinkit Category Discovery Engine

> An AI-assisted research engine exploring what prevents quick-commerce users from expanding beyond habitual categories.

Built as part of a Product Management case study on **category expansion at Blinkit**.

## 🎯 The Problem

Blinkit has built a powerful replenishment habit:

**Need → Search → Add → Checkout**

But buying from a new category often requires a different journey:

**Discover → Explore → Evaluate → Build confidence → Purchase**

This raises the core product question:

> **Could Blinkit's strong replenishment habit make it harder for customers to discover and adopt categories beyond their usual purchases?**

---

## 🧠 Research Framework

I started with three behavioral hypotheses:

| Stage | Potential barrier | User thought |
|---|---|---|
| 👀 **KNOW** | Awareness | “I didn't know Blinkit sold this.” |
| 🧠 **CONSIDER** | Mental availability | “I know they sell it, but Blinkit isn't where I'd think of buying it.” |
| 🛡️ **CONFIDENCE** | Decision support & trust | “Can I confidently choose and buy this here?” |

These are **hypotheses to test — not conclusions to prove.**

---

## 🔬 Research Pipeline

I built a multi-stage pipeline to separate potentially useful behavioral evidence from generic review noise.

```text
3,776 public conversations
          ↓
   Targeted retrieval
          ↓
    674 candidates
       (17.8%)
          ↓
 Structured AI classification
          ↓
    Human validation
          ↓
    Insight synthesis
```

### Sources

- Apple App Store
- Google Play Store
- YouTube
- Blinkit, Zepto & BigBasket conversations

Reddit was explored but excluded from the final corpus due to API-access constraints.

---

## 🔎 Why Not Just Ask an LLM to Analyze All Reviews?

Most public quick-commerce feedback concerns:

- delivery
- refunds
- customer support
- product quality
- app issues

Sending everything directly to an LLM risks producing generic themes rather than answering the product question.

Instead, the engine uses:

### 1. High-recall retrieval
Find conversations that *might* contain category-discovery evidence.

### 2. Structured classification
Claude evaluates candidates against a controlled behavioral taxonomy.

### 3. Human validation
Only evidence-supported signals advance to insight synthesis.

> **Retrieval ≠ evidence.**

---

## 🤖 Classification Taxonomy

Each candidate can be structured across dimensions including:

- Discovery relevance
- Primary theme
- New-category barrier
- Purchase trigger
- Consideration level
- Category mentioned
- Jobs-to-be-done
- Alternative platform
- Segment signals

The classifier explicitly supports **`UNKNOWN` / `NONE`** when evidence is insufficient.

> **Evidence is allowed to reject the hypothesis.**

---

## 💡 Key Research Learning

Secondary research can observe some parts of the journey better than others:

### 👀 KNOW — Observable
> “I didn't know they sell this.”

### 🧠 CONSIDER — Harder to observe
> “Blinkit never came to mind.”

### 🛡️ CONFIDENCE — Observable
> “Can I trust buying this here?”

The **consideration gap is structurally difficult to observe in review data** because users rarely review a platform they never considered.

This becomes a key question for primary user research.

---

## 🛠️ Repository

```text
├── collect_appstore.py
├── collect_playstore.py
├── collect_youtube.py
├── collect_competitors.py
├── collect_reddit.py
├── combine.py
├── build_discovery_sample.py
├── taxonomy.py
├── extract.py
├── config.py
└── requirements.txt
```

### Built with

**Python · Pandas · Anthropic Claude · GitHub**

Interactive research explorer planned with **Next.js + Vercel**.

---

## ⚠️ Research Limitations

- Public reviews overrepresent strong positive/negative experiences.
- The corpus is **directional, not representative** of Blinkit's customer population.
- Platforms users never considered are difficult to observe in review data.
- AI classification can over-infer intent; human validation remains necessary.

---


> **Don't use AI to manufacture insights. Use it to find the evidence worth investigating.**