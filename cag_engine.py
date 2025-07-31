import os
import asyncio
from typing import Optional

from cache_builder import AdvancedCacheManager
from retriever import CAGHybridRetriever
from llm_interface import get_llm_response_async
from query_processor import QueryProcessor
from data_processor import process_new_document

class CAGEngine:
    def __init__(self):
        """
        Initializes the CAGEngine in a standby state.
        """
        self.cache_manager = AdvancedCacheManager()
        self.query_processor = QueryProcessor()
        self.processed_data: Optional[dict] = None
        self.retriever: Optional[CAGHybridRetriever] = None
        print("CAG Engine initialized successfully in standby mode.")

    def _setup_retriever_for_document(self, document_url: str):
        """
        Sets up the retriever for a specific document, processing it if not already cached.
        """
        if not self.processed_data or self.processed_data.get('full_documents', [{}])[0].get('id') != document_url:
            print(f"Setting up retriever for new document: {document_url}")
            self.processed_data = process_new_document(document_url)
            self.retriever = CAGHybridRetriever(self.processed_data)
        else:
            print(f"Using existing retriever for document: {document_url}")

    async def generate_batch_answers(self, queries: list[str], document_url: str):
        """
        Asynchronously generates answers for a batch of queries.
        It runs both the document retrieval and LLM calls for all questions concurrently.
        """
        try:
            self._setup_retriever_for_document(document_url)
            if self.retriever is None:
                raise ValueError("Retriever could not be initialized.")

            # Helper function to run sync retrieval in a thread, then call the async LLM
            async def retrieve_and_generate(query: str):
                try:
                    loop = asyncio.get_running_loop()
                    relevant_docs = await loop.run_in_executor(
                        None, self.retriever.retrieve, query
                    )

                    relevant_entries = [
                        {
                            'text_snippet': doc.page_content,
                            'chunk_id': doc.metadata.get('chunk_id'),
                            'source_doc_id': doc.metadata.get('source_doc_id')
                        }
                        for doc in relevant_docs
                    ]

                    response = await get_llm_response_async(query, relevant_entries)
                    return response
                except Exception as e:
                    error_message = f"Error processing query '{query}': {e}"
                    print(error_message)
                    return error_message

            tasks = [retrieve_and_generate(query) for query in queries]
            responses = await asyncio.gather(*tasks)
            return responses

        except Exception as e:
            batch_error_message = f"Error in batch processing setup: {e}"
            print(batch_error_message)
            return [batch_error_message] * len(queries)
