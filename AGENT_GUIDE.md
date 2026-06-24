# Agent Guide

This repository is for Falcon Intelligence, a local-first appraisal firm knowledge base prototype.

## Non-Negotiable Data Rules

- Do not ingest, copy, summarize, expose, or commit real appraisal reports.
- Do not inspect unrelated OneDrive files outside this repository.
- Do not add source documents, extracted text, OCR outputs, embeddings, vector stores, databases, PDFs, DOCX, XLSX, CSV, TSV, or TXT files to git.
- Use only synthetic fixtures when tests eventually require document-like inputs.
- Keep implementation framework-only until ingestion is explicitly approved.

## Implementation Priorities

- Prefer small, auditable modules with explicit safety boundaries.
- Keep local-first behavior as the default.
- Make premium features pluggable, disabled, and configuration-driven.
- Document assumptions before adding data-processing behavior.

## Before Coding

1. Read this file.
2. Read files in `docs/`.
3. Confirm proposed changes do not require real appraisal data.
4. Check `.gitignore` before adding any file type that may contain client or report data.
