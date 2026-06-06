# """
# Full Pipeline Integration Tests — Multi-Rag
# ============================================
# Tests every ingestion path (PDF, DOCX, TXT, Image/OCR) and every
# graph routing path (doc query, web-fallback query, small-talk).

# Run with:
#     uv run pytest src/tests/full_pipeline_test_pytest.py -v -s
# """

# import os
# import sys
# import asyncio
# import logging

# import pytest

# # Force HuggingFace to use local cache — no network calls during test collection
# os.environ["TRANSFORMERS_OFFLINE"] = "1"
# os.environ["HF_HUB_OFFLINE"] = "1"

# sys.path.insert(0, os.getcwd())

# from dotenv import load_dotenv
# load_dotenv()

# import logger  # noqa: F401

# from langchain_core.messages import HumanMessage, AIMessage

# from src.entity.config_entity import (
#     DataIngestionConfig,
#     ContentEmbedderConfig,
#     DataTransformationConfig,
#     ContentTransformationConfig,
# )
# from src.pipeline.Vectiorizer_pipeline import VectiorizerPipeline
# from src.pipeline.GraphRunner_pipeline import RunGraphPipeline


# # ─────────────────────────────────────────────────────────────
# #  Test Data Paths
# # ─────────────────────────────────────────────────────────────

# DATA_DIR  = "data"
# TXT_FILE  = os.path.join(DATA_DIR, "growing_ai_tools.txt")
# PDF_FILE  = os.path.join(DATA_DIR, "Digital India Report.pdf")
# DOCX_FILE = os.path.join(DATA_DIR, "google.docx")
# IMG_FILE  = os.path.join(DATA_DIR, "Optical_Recognition.png")

# THREAD_ID = "pytest-full-integration-001"
# ARTIFACT  = f"artifacts/{THREAD_ID}"

# INGESTION_CONFIGS = [
#     DataIngestionConfig(
#         input_file_path=TXT_FILE,
#         save_file_path=f"{ARTIFACT}/ingestion/growing_ai_tools.pdf",
#     ),
#     DataIngestionConfig(
#         input_file_path=PDF_FILE,
#         save_file_path=f"{ARTIFACT}/ingestion/digital_india.pdf",
#     ),
#     DataIngestionConfig(
#         input_file_path=DOCX_FILE,
#         save_file_path=f"{ARTIFACT}/ingestion/google.pdf",
#     ),
#     DataIngestionConfig(
#         input_file_path=IMG_FILE,
#         save_file_path=f"{ARTIFACT}/ingestion/optical_recognition.pdf",
#     ),
# ]

# TRANSFORMATION_CONFIGS = [
#     DataTransformationConfig(vector_store_path=f"{ARTIFACT}/transformation/growing_ai_tools"),
#     DataTransformationConfig(vector_store_path=f"{ARTIFACT}/transformation/digital_india"),
#     DataTransformationConfig(vector_store_path=f"{ARTIFACT}/transformation/google"),
#     DataTransformationConfig(vector_store_path=f"{ARTIFACT}/transformation/optical_recognition"),
# ]

# GRAPH_CONFIG = {"configurable": {"thread_id": THREAD_ID}}


# # ─────────────────────────────────────────────────────────────
# #  Module-scoped fixture — run pipeline ONCE for the whole module
# # ─────────────────────────────────────────────────────────────

# @pytest.fixture(scope="module")
# def pipeline_result():
#     print("\n[FIXTURE] Starting VectiorizerPipeline for all 4 files...")
#     pipeline = VectiorizerPipeline(
#         content_embedder_config=ContentEmbedderConfig(
#             data_ingestion_configs=INGESTION_CONFIGS
#         ),
#         content_transformation_config=ContentTransformationConfig(
#             data_transformation_configs=TRANSFORMATION_CONFIGS
#         ),
#     )
#     result = asyncio.run(pipeline.initiate(thread_id=THREAD_ID))
#     print(f"[FIXTURE] Pipeline done. Artifacts: {[a.vector_store_path for a in result.data_transformation_artifacts]}")
#     return result


# @pytest.fixture(scope="module")
# def vector_store_paths(pipeline_result):
#     paths = [art.vector_store_path for art in pipeline_result.data_transformation_artifacts]
#     print(f"\n[FIXTURE] Vector store paths: {paths}")
#     return paths


# # ─────────────────────────────────────────────────────────────
# #  Helper
# # ─────────────────────────────────────────────────────────────

# def _make_state(query: str, paths: list) -> dict:
#     return {
#         "messages": [HumanMessage(content=query)],
#         "vector_store_file_paths": paths,
#         "queries": [],
#         "retreived_results": [],
#         "ai_response": "",
#     }


# def _run_graph(state: dict, thread_suffix: str = "") -> dict:
#     config = {"configurable": {"thread_id": f"{THREAD_ID}{thread_suffix}"}}
#     query  = state["messages"][0].content
#     print(f"\n[GRAPH] Running query: '{query}'")
#     pipeline = RunGraphPipeline()
#     result = asyncio.run(pipeline.run_graph(state, config=config))
#     ai_resp = result.get("ai_response", "")
#     print(f"[GRAPH] AI response preview: '{ai_resp[:120]}...' " if len(ai_resp) > 120 else f"[GRAPH] AI response: '{ai_resp}'")
#     return result


# # ─────────────────────────────────────────────────────────────
# #  1. Pre-flight: verify all source files exist
# # ─────────────────────────────────────────────────────────────

# class TestDataFilesExist:

#     def test_txt_file_exists(self):
#         print(f"\n[CHECK] {TXT_FILE} -> exists={os.path.exists(TXT_FILE)}")
#         assert os.path.exists(TXT_FILE), f"Missing: {TXT_FILE}"

#     def test_pdf_file_exists(self):
#         print(f"\n[CHECK] {PDF_FILE} -> exists={os.path.exists(PDF_FILE)}")
#         assert os.path.exists(PDF_FILE), f"Missing: {PDF_FILE}"

#     def test_docx_file_exists(self):
#         print(f"\n[CHECK] {DOCX_FILE} -> exists={os.path.exists(DOCX_FILE)}")
#         assert os.path.exists(DOCX_FILE), f"Missing: {DOCX_FILE}"

#     def test_image_file_exists(self):
#         print(f"\n[CHECK] {IMG_FILE} -> exists={os.path.exists(IMG_FILE)}")
#         assert os.path.exists(IMG_FILE), f"Missing: {IMG_FILE}"


# # ─────────────────────────────────────────────────────────────
# #  2. Vectorization Pipeline Tests
# # ─────────────────────────────────────────────────────────────

# class TestVectorizerPipeline:

#     def test_pipeline_returns_artifact(self, pipeline_result):
#         print(f"\n[PIPELINE] Result: {pipeline_result}")
#         assert pipeline_result is not None, "Pipeline returned None"

#     def test_artifact_has_transformation_list(self, pipeline_result):
#         has_attr = hasattr(pipeline_result, "data_transformation_artifacts")
#         print(f"[PIPELINE] Has 'data_transformation_artifacts': {has_attr}")
#         assert has_attr

#     def test_artifact_count_matches_input_files(self, pipeline_result):
#         count = len(pipeline_result.data_transformation_artifacts)
#         print(f"[PIPELINE] Artifact count: {count} (expected 4)")
#         assert count == 4, f"Expected 4 artifacts, got {count}"

#     def test_all_vector_store_paths_non_empty(self, pipeline_result):
#         for art in pipeline_result.data_transformation_artifacts:
#             print(f"[PIPELINE] Vector store path: '{art.vector_store_path}'")
#             assert art.vector_store_path, f"Empty path in artifact: {art}"

#     def test_all_vector_stores_exist_on_disk(self, pipeline_result):
#         for art in pipeline_result.data_transformation_artifacts:
#             exists = os.path.exists(art.vector_store_path)
#             print(f"[PIPELINE] Path on disk '{art.vector_store_path}' -> exists={exists}")
#             assert exists, f"Vector store not found on disk: {art.vector_store_path}"


# # ─────────────────────────────────────────────────────────────
# #  3. Graph Tests — TXT (growing_ai_tools)
# # ─────────────────────────────────────────────────────────────

# class TestGraphPipelineTxtQuery:

#     def test_txt_query_returns_result(self, vector_store_paths):
#         print("\n[TXT] Testing TXT-based query...")
#         state  = _make_state("What are the growing AI tools mentioned?", vector_store_paths)
#         result = _run_graph(state, "-txt")
#         assert result is not None

#     def test_txt_query_has_ai_response(self, vector_store_paths):
#         state  = _make_state("What are the growing AI tools mentioned?", vector_store_paths)
#         result = _run_graph(state, "-txt2")
#         ai = result.get("ai_response", "")
#         print(f"[TXT] ai_response length: {len(ai)}")
#         assert isinstance(ai, str) and ai.strip(), "ai_response is empty for TXT query"

#     def test_txt_query_last_message_is_ai(self, vector_store_paths):
#         state   = _make_state("List the AI tools described in the document.", vector_store_paths)
#         result  = _run_graph(state, "-txt3")
#         last    = result["messages"][-1]
#         print(f"[TXT] Last message type: {type(last).__name__}")
#         assert isinstance(last, AIMessage)


# # ─────────────────────────────────────────────────────────────
# #  4. Graph Tests — PDF (Digital India Report)
# # ─────────────────────────────────────────────────────────────

# class TestGraphPipelinePdfQuery:

#     def test_pdf_query_returns_result(self, vector_store_paths):
#         print("\n[PDF] Testing PDF-based query...")
#         state  = _make_state("What is the Digital India initiative about?", vector_store_paths)
#         result = _run_graph(state, "-pdf")
#         assert result is not None

#     def test_pdf_query_has_ai_response(self, vector_store_paths):
#         state  = _make_state("Summarise the key goals of Digital India.", vector_store_paths)
#         result = _run_graph(state, "-pdf2")
#         ai = result.get("ai_response", "")
#         print(f"[PDF] ai_response length: {len(ai)}")
#         assert ai.strip(), "ai_response is empty for PDF query"

#     def test_pdf_query_last_message_is_ai(self, vector_store_paths):
#         state  = _make_state("What sectors does Digital India target?", vector_store_paths)
#         result = _run_graph(state, "-pdf3")
#         last   = result["messages"][-1]
#         print(f"[PDF] Last message type: {type(last).__name__}")
#         assert isinstance(last, AIMessage)


# # ─────────────────────────────────────────────────────────────
# #  5. Graph Tests — DOCX (google.docx)
# # ─────────────────────────────────────────────────────────────

# class TestGraphPipelineDocxQuery:

#     def test_docx_query_returns_result(self, vector_store_paths):
#         print("\n[DOCX] Testing DOCX-based query...")
#         state  = _make_state("What does the Google document talk about?", vector_store_paths)
#         result = _run_graph(state, "-docx")
#         assert result is not None

#     def test_docx_query_has_ai_response(self, vector_store_paths):
#         state  = _make_state("Summarise the content of the Google document.", vector_store_paths)
#         result = _run_graph(state, "-docx2")
#         ai = result.get("ai_response", "")
#         print(f"[DOCX] ai_response length: {len(ai)}")
#         assert ai.strip(), "ai_response is empty for DOCX query"

#     def test_docx_query_last_message_is_ai(self, vector_store_paths):
#         state  = _make_state("What are the main points in the Google document?", vector_store_paths)
#         result = _run_graph(state, "-docx3")
#         last   = result["messages"][-1]
#         print(f"[DOCX] Last message type: {type(last).__name__}")
#         assert isinstance(last, AIMessage)


# # ─────────────────────────────────────────────────────────────
# #  6. Graph Tests — Image / OCR (Optical_Recognition.png)
# # ─────────────────────────────────────────────────────────────

# class TestGraphPipelineImageOcrQuery:

#     def test_image_query_returns_result(self, vector_store_paths):
#         print("\n[IMG] Testing image/OCR-based query...")
#         state  = _make_state("What text is present in the image document?", vector_store_paths)
#         result = _run_graph(state, "-img")
#         assert result is not None

#     def test_image_query_has_ai_response(self, vector_store_paths):
#         state  = _make_state("Describe what is written in the scanned image.", vector_store_paths)
#         result = _run_graph(state, "-img2")
#         ai = result.get("ai_response", "")
#         print(f"[IMG] ai_response length: {len(ai)}")
#         assert ai.strip(), "ai_response is empty for image/OCR query"

#     def test_image_query_last_message_is_ai(self, vector_store_paths):
#         state  = _make_state("What does the optical recognition image contain?", vector_store_paths)
#         result = _run_graph(state, "-img3")
#         last   = result["messages"][-1]
#         print(f"[IMG] Last message type: {type(last).__name__}")
#         assert isinstance(last, AIMessage)


# # ─────────────────────────────────────────────────────────────
# #  7. Graph Routing Edge Cases
# # ─────────────────────────────────────────────────────────────

# class TestGraphRoutingBehaviour:

#     def test_small_talk_returns_response(self):
#         print("\n[ROUTING] Testing small talk (no vector store)...")
#         state  = _make_state("Hello! How are you?", [])
#         result = _run_graph(state, "-smalltalk")
#         ai = result.get("ai_response", "")
#         print(f"[ROUTING] Small talk response: '{ai[:80]}'")
#         assert ai.strip(), "No response for small talk"

#     def test_small_talk_last_message_is_ai(self):
#         state  = _make_state("Who are you?", [])
#         result = _run_graph(state, "-identity")
#         last   = result["messages"][-1]
#         print(f"[ROUTING] Identity last message type: {type(last).__name__}")
#         assert isinstance(last, AIMessage)

#     def test_web_search_fallback_returns_response(self, vector_store_paths):
#         print("\n[ROUTING] Testing web-search fallback (question not in docs)...")
#         state  = _make_state(
#             "What is the latest version of Python released in 2025?",
#             vector_store_paths,
#         )
#         result = _run_graph(state, "-websearch")
#         ai = result.get("ai_response", "")
#         print(f"[ROUTING] Web-search response: '{ai[:80]}'")
#         assert ai.strip(), "No response for web-search fallback query"

#     def test_messages_list_grows_after_graph(self, vector_store_paths):
#         state  = _make_state("Tell me about AI tools.", vector_store_paths)
#         result = _run_graph(state, "-msgcount")
#         count  = len(result["messages"])
#         print(f"[ROUTING] Messages after graph: {count}")
#         assert count >= 2, f"Expected >= 2 messages, got {count}"
