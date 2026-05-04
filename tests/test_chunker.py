from docpipe.chunker import chunk_markdown, quality_metrics


def test_chunk_markdown_preserves_headings_and_tables() -> None:
    markdown = """# Title

Intro paragraph.

| A | B |
| --- | --- |
| 1 | 2 |

## Details

More content here.
"""

    chunks = chunk_markdown(markdown, max_chars=80)
    metrics = quality_metrics(markdown, chunks)

    assert chunks
    assert chunks[0].heading == "Title"
    assert metrics.tables == 1
    assert metrics.headings == 2


def test_chunk_markdown_splits_long_content() -> None:
    markdown = "\n\n".join([f"Paragraph {index} " + ("x" * 80) for index in range(10)])

    chunks = chunk_markdown(markdown, max_chars=200)

    assert len(chunks) > 1
    assert all(chunk.chars <= 260 for chunk in chunks)
