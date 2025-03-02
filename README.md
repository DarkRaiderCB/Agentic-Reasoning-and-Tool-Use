# AI-Powered Shopping Assistant (Prototype)

This is a **mockup prototype** for an AI-powered **Shopping Assistant** that helps users with e-commerce queries such as **product search, price comparison, discount application, return policies, and delivery estimates**. The system currently uses **rule-based query parsing and tool-based decision-making**, as per the assignment instructions.

---

## **1. Comparative Conceptual Map**

| Approach            | Key Features | Similarities to This Project | Differences |
|---------------------|-------------|-----------------------------|-------------|
| **ReAct (Reason + Act)** | Interleaves reasoning & action steps | Uses `_reason()`, `_use_tool()`, and `_act()` to log decision-making | Rule-based, no LLM-driven decisions yet |
| **Toolformer** | Self-learns tool-use patterns | Uses tools dynamically like `ProductSearch`, `PriceComparison`, etc. | Predefined tool triggers, no self-learning |
| **ATC (Chain of Tools)** | LLM dynamically selects & sequences tools | Sequences multiple tools for a single query (e.g., search → discount → delivery) | Hardcoded tool chaining instead of LLM-based chaining |
| **LATS (Language Agent Tree Search)** | Uses Monte Carlo Tree Search for decision-making | Evaluates multiple options like store-based price comparisons | No probabilistic decision-making |
| **ReST meets ReAct** | Self-improves through iterative training | Logs query details and extracts structured information | No self-improvement yet, purely rule-based |

**Key Insights**:
- **Primary Inspiration**: ReAct’s thought-action-observation loop drives your sequential workflow (`_reason`, `_use_tool`, `_act`).
- **Toolformer Influence**: Multi-tool design `[ProductSearch]`, `[ShippingEstimator]` mirrors Toolformer’s embedded tool approach.
- **Chain of Tools Echo**: Sequential tool use in `_format_product_response` resembles static chaining.
- **LATS Nod**: Structured reasoning suggests planning intent, but lacks dynamic exploration.
- **ReST Minimal**: Parsing aligns with structured input handling, but no iteration.

NOTE: The present design is majorly ReAct based, but with addition of LLM instead of rule-based codes, the decision making can be made dynamic, signifying properties of ATC like approaches.

---

## **2. Short Written Analysis (Performance & Results)**

### **Strengths**
- **Structured query parsing:** Uses **regex patterns** for **accurate intent detection**.
- **Tool-based execution:** Calls **e-commerce tools dynamically** for efficient processing.

### **Limitations**
- **Lack of adaptability:** No self-learning; requires **manual updates** for new queries.
- **No multi-turn reasoning:** Cannot refine queries over multiple interactions.
- **Hardcoded logic:** Unlike LLMs, decisions **aren’t context-aware** or dynamically generated.

The above limitations are primarily due to rule based approach, and can be mitigated with use of LLMs to demonstrate a mixture of ReAt, Toolformer and ATC.

- **Query 1**: "Find a floral skirt under $140 in size S. Is it in stock, and can I apply a discount code 'SAVE10'?"
  - **Result**: "I found a Floral Summer Skirt in size S for $35.99 at StoreA. It's in stock (10 available). With discount code 'SAVE10', the final price would be $32.39."
  - **Performance**: Successfully parsed query, searched products, and applied discount.

- **Query 2**: "I need white sneakers (size 8) for under $70 that can arrive by Monday."
  - **Result**: "I found a White Athletic Sneakers in size 8 for $65.99 at StoreB. It's in stock (5 available). It can be delivered by [Monday date] (estimated 5-7 days) for $5.99 shipping." (Availability depends on date; assumes feasible for demo.)
  - **Performance**: Correctly handled search and shipping, though shipping feasibility varies with random days.

- **Query 3**: "I found a 'casual denim jacket' at $80 on StoreA. Any better deals?"
  - **Result**: "Here are the prices for the casual denim jacket across stores: - StoreB: $75.99 - StoreA: $80.00 - StoreC: $82.99"
  - **Performance**: Accurately compared prices, identifying StoreB as cheapest.

- **Query 4**: "I want to buy a cocktail dress from StoreB, but only if returns are hassle-free. Do they accept returns?"
  - **Result**: "StoreB accepts returns within 14 days. Return shipping fee applies. Return shipping fee applies."
  - **Performance**: Correctly fetched return policy, though "hassle-free" interpretation is subjective.

**Analysis**:
- **Strengths**: Handles basic search, shipping, discounts, comparisons, and returns with 100% accuracy on mock data when query aligns with database.
- **Limitations**: Fails on queries outside mock data (e.g., unavailable products). No iterative refinement or error correction beyond basic failure messages.
---

## **3. Design Decisions (Agent Architecture & Tool Selection)**

### **System Architecture**
1. **System Prompt (mockup)** - Defines agent behavior and available tools.
2. **Query Parser** - Extracts **product names, prices, colors, sizes, dates, and discounts**.
3. **Tool-Based Execution** - Calls relevant tools based on parsed query.
4. **Structured Response** - Combines **tool results** into a **human-readable output**.
5. **Rule-Based Reasoning**: A static decision tree (`handle_query`) parses queries and selects tools based on type (search, comparison, return), inspired by ReAct’s thought-action loop. No LLM is used; regex patterns (`search_patterns`) and conditional logic replace dynamic reasoning.
6. **Sequential Tool Execution**: Tools are called in a predefined order (`_format_product_response`), reflecting Chain of Tools’ chaining but hardcoded rather than programmatically generated.
7. **Logging**: `_reason`, `_act`, and `_use_tool` methods provide transparency, echoing ReST meets ReAct’s structured logging, aiding debugging and user understanding.

### **Tool Selection**
| **Tool Name** | **Function** |
|--------------|-------------|
| `ProductSearch` | Finds products based on query details |
| `PriceComparison` | Compares prices across stores |
| `ShippingEstimator` | Provides estimated delivery time & cost |
| `ReturnPolicyChecker` | Retrieves store return policies |
| `DiscountCalculator` | Applies discount codes |

**Why These Choices?**:
- Simplicity and control via rules suit a mock implementation without LLM complexity.
- Tools cover core shopping needs (search, shipping, pricing, returns), managing ReAct’s practicality and Toolformer’s versatility.
- Static chaining ensures predictable multi-step responses, adapting Chain of Tools’ structure.
---

## **4. Challenges & Improvements**

### **Challenges**
1. **Limited Scope**: Current mock database restricts functionality to predefined items, failing on unseen products.
2. **Static Reasoning**: Hardcoded rules lack adaptability to ambiguous or complex queries (e.g., “hassle-free” interpretation).
4. **No Reflection**: Unlike LATS, no dynamic error correction or retry mechanism exists beyond failure messages.

### **Future Enhancements**
- **LLM Integration:** Use an LLM to replace regex-based parsing.  
- **Self-Improving System:** Implement **ReST-like iterative training** for better responses.  
- **Dynamic Tool Selection:** Replace hardcoded tool calls with **LLM-driven decision-making**.  
- **Multi-Turn Dialogue:** Maintain context to improve user interaction.
---

## **5. Open Questions & References**
### **Open Questions**
1. How can we balance **efficiency** (rule-based logic) with **adaptability** (LLM-based reasoning)?
2. To what extent **few-shot learning** help reduce reliance on regex parsing?
3. **Tool Expansion**: Could adding tools (e.g., user reviews) enhance functionality, and how to integrate them?

### **References**
- Yao et al., "ReAct: Synergizing Reasoning and Acting in Language Models." [(arXiv:2210.03629)](https://arxiv.org/abs/2210.03629)
- Schick et al., "Toolformer: Language Models Can Teach Themselves to Use Tools." [(arXiv:2302.04761)](https://arxiv.org/abs/2302.04761)
- Zhou et al., "Language Agent Tree Search (LATS): Combining MCTS with LLMs." [(arXiv:2310.04406)](https://arxiv.org/abs/2310.04406)
- Shi et al., "Chain of Tools: Automated Tool Use in LLMs." [(arXiv:2405.16533)](https://arxiv.org/abs/2405.16533)
- Aksitov et al., "ReST Meets ReAct: Self-Training Language Agents with Reasoning and Acting." [(arXiv:2312.10003)](https://arxiv.org/abs/2312.10003)
---

## **Final Thoughts**
This **mockup prototype** lays the groundwork for an **AI-powered shopping assistant** with structured tool-based reasoning. The present rule-based approach aligns with the assignment requirements.

Additionally, the present approach, however, is good enough to define the workflow and pipeline for a possible LLM-based variant too.

---
**Author:** Sanyog Mishra  
**Last Updated:** February 2025
**Video Link:** [(Visit here)](https://youtu.be/Wyc58-0SUDE)

---

THANKS FOR VISITING!!
