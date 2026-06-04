# AI Legal Assistant — PDF Generator Container
# Multi-arch: linux/amd64 + linux/arm64 (Apple Silicon / AWS Graviton)
FROM python:3.12-slim

WORKDIR /app

# Install reportlab (only runtime dep for PDF generation)
RUN pip install --no-cache-dir reportlab==4.2.5

# Copy scripts only — skill .md files are used via Claude Code, not in container
COPY scripts/ ./scripts/
COPY generate_sample_contract.py .

# Non-root user for security
RUN useradd -m -u 1001 legal && chown -R legal:legal /app
USER legal

# Default: run PDF generator. Override CMD for other scripts.
# Usage: docker run --rm -v $(pwd):/data ghcr.io/<owner>/ai-legal-claude:latest \
#          python scripts/generate_legal_pdf.py /data/CONTRACT-REVIEW.md /data/output.pdf
ENTRYPOINT ["python"]
CMD ["scripts/generate_legal_pdf.py", "--help"]
