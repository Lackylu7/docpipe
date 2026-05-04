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
    assert chunks[0].heading_path == ["Title"]
    assert metrics.tables == 1
    assert metrics.headings == 2
    assert metrics.quality_score > 0
    assert isinstance(metrics.warnings, list)


def test_chunk_markdown_splits_long_content() -> None:
    markdown = "\n\n".join([f"Paragraph {index} " + ("x" * 80) for index in range(10)])

    chunks = chunk_markdown(markdown, max_chars=200)

    assert len(chunks) > 1
    assert all(chunk.chars <= 260 for chunk in chunks)


def test_chunk_markdown_tracks_nested_heading_path() -> None:
    markdown = """# Root

Intro.

## Child

Details.
"""

    chunks = chunk_markdown(markdown, max_chars=50)

    assert chunks[-1].heading_path == ["Root", "Child"]
    assert chunks[-1].token_estimate > 0
