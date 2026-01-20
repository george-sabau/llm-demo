# 🚀 Hybrid Semantic Search with Vector Embeddings (FastText + Solr)

This repository documents the complete **Hybrid Semantic Search** concept, combining traditional **keyword-based search** with **vector-based semantic similarity**.  
The goal is to enable **natural language search** with higher relevance, even when exact keyword matches are missing.

---

## 🧠 Core Concept

Classic search engines rely on keywords. This system enhances them by introducing **semantic understanding** through vector embeddings.

Both **search queries** and **documents** are represented as vectors in the same vector space.  
Their similarity is computed mathematically and combined with the keyword score to produce a **hybrid ranking**.

---

## 📐 Mathematical Foundation: Cosine Similarity

The semantic similarity between a query vector **Q** and a document vector **D** is calculated using **cosine similarity**:

\[
\text{sim}(Q, D) = \cos(\theta) = \frac{Q \cdot D}{\|Q\| \|D\|}
\]

### Interpretation of Cosine Values

| Value | Meaning |
|-----:|--------|
| `1.0` | Perfectly similar (same direction) |
| `~0.85` | Highly similar |
| `0.0` | No similarity (orthogonal, 90° angle) |
| `-1.0` | Opposite meaning (180° angle) |

> Vector **normalization** removes magnitude effects — similarity is based purely on **direction (meaning)**.

---

## 📊 Vector Geometry Intuition

### A) Angle-Based Similarity

- Small angle → high similarity
- Large angle → low similarity
- Opposite vectors → negative similarity

Words and phrases naturally cluster by **semantic meaning** inside the vector space.

---

## 🔍 Hybrid Search Scoring Model

The final ranking score is calculated as:

\[
\text{Score} =
\text{KeywordScore(query, document)}
+
\cos(\text{QueryVector}, \text{DocumentVector})
\]

### Why Hybrid Search?

- **Keyword score** → precision and control
- **Vector similarity** → semantic recall
- **Hybrid score** → best overall relevance

This approach is often referred to as:
- Hybrid Search
- Neural Search
- Natural Language Search

---

## 🔄 Online Flow: Search Query Execution

1. **User Input**
   - User enters a search query in the frontend  
     Example: `"hello world"`

2. **Vectorization**
   - Query text is converted into a vector using **FastText**
   - Uses the domain-specific embedding model: `RWA_MODEL`

3. **Normalization**
   - Query vector is normalized to unit length  
     (ensures fair cosine similarity scoring)

4. **Hybrid Solr Query**
   - Keyword-based query is executed in Solr
   - Vector similarity is computed against stored document vectors

5. **Ranking & Results**
   - Solr returns documents ranked by the **hybrid score**
   - Highest combined relevance appears first

---

## 🏗 Offline Flow: Indexing & Vector Generation

1. **Fetch Candidates**
   - Products / documents are retrieved from the source database

2. **Select Vector-Worthy Attributes**
   - Only semantic-rich fields are chosen, for example:
      - Name
      - Description
      - Category
      - Long text fields

3. **Vectorization**
   - Selected text is transformed into **100-dimensional vectors**
   - Same model (`RWA_MODEL`) must be used for **queries and documents**

4. **Persistence in Solr**
   - Each vector dimension is stored as a dedicated numeric field:

   ```text
   v1_float, v2_float, v3_float, ... v100_float

6. **Persistence in Solr**
   - Asynchronous Processing
   - Vector generation is decoupled from core indexing
   - No negative impact on indexing performance
   - Allows independent re-vectorization if the model changes

---

## 🧠 Embedding Model Strategy

### Why FastText?
- Lightweight and fast
- Handles out-of-vocabulary (OOV) words via subword information
- Works well for domain-specific terminology
- Efficient for large-scale indexing pipelines

FastText provides a strong balance between **performance**, **semantic quality**, and **operational simplicity**.

---

### Model Composition

- **Base model**
   - Pretrained FastText embeddings

- **Fine-tuning corpus**
   - Domain-specific documents
   - Product descriptions
   - Internal knowledge bases
   - Business terminology

> ⚠️ All vectors **must be generated using the same embedding model**  
> Mixing models invalidates cosine similarity comparisons.

---

## 🧪 Example Semantic Behavior

Semantic search allows concept matching even when keywords differ.

| Query | Matching Document | Explanation |
|-----|------------------|-------------|
| `"hello world"` | `"hi world"` | Similar greeting semantics |
| `"buy phone"` | `"purchase mobile"` | Synonym understanding |
| `"cheap flight"` | `"low cost airline"` | Contextual similarity |
| `"kids shoes"` | `"children footwear"` | Domain-level semantics |

---

## ⚙️ Performance Considerations

- Vector generation is executed **offline**
- Indexing pipeline is **asynchronous**
- Query-time cost is limited to:
   - Keyword scoring
   - Vector dot product (cosine similarity)

This avoids:
- Expensive ANN infrastructure
- Heavy re-ranking pipelines
- Latency spikes under load

---

## 🧬 Relation to RAG (Retrieval-Augmented Generation)

This hybrid search system serves as an ideal **retrieval layer** for RAG architectures.

### RAG Flow Integration

1. User query is converted into a vector
2. Hybrid search retrieves top-K relevant documents
3. Retrieved content is passed to an LLM
4. LLM generates grounded, context-aware responses

### Benefits
- Reduced hallucinations
- Domain-aware responses
- Improved factual grounding

---

## 🏛 Architectural Advantages

- No dependency on ANN libraries
- Compatible with existing Solr deployments
- Incremental adoption possible
- Supports gradual ML maturity

This makes the approach ideal for **enterprise-scale systems**.

---

## ✅ Key Takeaways

- Cosine similarity captures semantic alignment
- Vector normalization is mandatory
- Hybrid search improves relevance significantly
- Keyword + vector scoring is production-proven
- Architecture is future-proof for AI extensions

---

## 📘 Glossary

| Term | Description |
|----|------------|
| Vector Embedding | Numeric semantic representation of text |
| Cosine Similarity | Angle-based similarity metric |
| Hybrid Search | Keyword + semantic search |
| FastText | Subword-based embedding model |
| RAG | Retrieval-Augmented Generation |

---
