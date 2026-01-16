"""
RAG System Module
Core RAG logic with grounding, citations, and LLM integration (Gemini)
"""
from typing import List, Dict, Tuple, Optional
import google.generativeai as genai
import os


class RAGSystem:
    """
    Retrieval-Augmented Generation system.
    Grounds answers in retrieved context, provides citations.
    """

    def __init__(self, retriever, embedder, api_key: Optional[str] = None):
        """
        Initialize RAG system with Gemini API.

        Args:
            retriever: Retriever instance
            embedder: Embedder instance
            api_key: Google Gemini API key (uses GOOGLE_API_KEY env var if not provided)
        """
        self.retriever = retriever
        self.embedder = embedder

        api_key = api_key or os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY not set")

        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.0-flash')
        self.temperature = 0

        print(f"[RAG] Using Gemini API (gemini-2.0-flash) with temperature=0")

    def answer_question(
        self,
        query: str,
        conversation_history: List[Dict],
        top_k: int = 5,
        debug: bool = True
    ) -> Tuple[str, List[Dict]]:
        """
        Answer a question using RAG with citations.

        Args:
            query: User question
            conversation_history: List of prior messages
            top_k: Number of chunks to retrieve
            debug: Print retrieval details

        Returns:
            (answer_with_citations, retrieved_chunks)
        """
        # Step 1: Retrieve relevant chunks
        query_embedding = self.embedder.embed_query(query)
        retrieved_chunks = self.retriever.retrieve(
            query_embedding, top_k=top_k)

        if debug:
            self._print_retrieval_info(query, retrieved_chunks)

        # Step 2: Check if anything was retrieved
        if not retrieved_chunks:
            return "Not found in the document.", []

        # Step 3: Build context for LLM
        context_text = self._build_context(retrieved_chunks)

        # Step 4: Generate answer using LLM
        answer = self._generate_answer(
            query=query,
            context=context_text,
            conversation_history=conversation_history,
            retrieved_chunks=retrieved_chunks
        )

        return answer, retrieved_chunks

    def _print_retrieval_info(self, query: str, chunks: List[Dict]) -> None:
        """Print retrieval debug information."""
        print("\n" + "="*80)
        print(f"[RETRIEVAL] Query: {query}")
        print(f"[RETRIEVAL] Retrieved {len(chunks)} chunks")
        print("-"*80)

        for i, chunk in enumerate(chunks, 1):
            print(
                f"\n{i}. Chunk ID: {chunk['chunk_id']} | Page: {chunk['page']} | Score: {chunk['similarity_score']:.4f}")
            print(f"   Text: {chunk['text'][:150]}...")

        print("\n" + "="*80 + "\n")

    def _build_context(self, chunks: List[Dict]) -> str:
        """Build context string from retrieved chunks."""
        context_parts = []

        for chunk in chunks:
            context_parts.append(f"[{chunk['chunk_id']}]\n{chunk['text']}\n")

        return "\n".join(context_parts)

    def _generate_answer(
        self,
        query: str,
        context: str,
        conversation_history: List[Dict],
        retrieved_chunks: List[Dict]
    ) -> str:
        """
        Generate answer using Gemini with grounding in context.
        If Gemini quota is hit, return the top retrieved chunk as the answer.
        """
        # Build system prompt for grounding
        system_prompt = """You are a document-grounded Q&A assistant. Your task is to answer questions strictly based on the provided document context.

CRITICAL RULES:
1. Answer ONLY using information from the provided context
2. If the answer is not in the context, respond exactly with: "Not found in the document."
3. Every answer must include citations in format [p13] or [p13:c2]
4. Do NOT use external knowledge or hallucinate
5. Do NOT invent numbers or facts not in the context
6. Be concise and factual

IMPORTANT: The document content is prefixed with [chunk_id] markers like [p13:c2].
Always cite these exact markers in your answer."""

        # Build user message with context
        user_message = f"""{system_prompt}

Question: {query}

Document Context:
{context}

Answer this question ONLY using the above context. Include citations."""

        # Call Gemini with temperature control
        try:
            response = self.model.generate_content(
                user_message,
                generation_config=genai.types.GenerationConfig(
                    temperature=self.temperature,
                    max_output_tokens=1000
                )
            )
            answer = response.text.strip() if response.text else "Not found in the document."
        except Exception as e:
            print(f"[ERROR] Gemini API error: {e}")
            # If Gemini quota is hit, return the top retrieved chunk as the answer
            if retrieved_chunks:
                top_chunk = retrieved_chunks[0]
                answer = f"[Gemini unavailable] Top relevant document chunk:\n[{top_chunk['chunk_id']}] {top_chunk['text'][:500]}"
            else:
                answer = "Not found in the document."

        # Post-process: ensure answer has citations or "Not found"
        answer = self._ensure_citation_format(answer, retrieved_chunks)

        return answer

    def _ensure_citation_format(self, answer: str, chunks: List[Dict]) -> str:
        """
        Ensure answer includes proper citations.
        If answer doesn't reference "Not found", add citations.
        """
        # If answer says not found, return as-is
        if "Not found in the document" in answer:
            return answer

        # Check if answer already has citations
        if "[p" in answer and "]" in answer:
            return answer

        # If no citations, add top chunk reference
        if chunks:
            top_chunk_id = chunks[0]["chunk_id"]
            answer = f"{answer} [{top_chunk_id}]"

        return answer
