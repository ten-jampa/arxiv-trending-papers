from founder_radar.arxiv import parse_arxiv_id


def test_parse_plain_arxiv_id() -> None:
    assert parse_arxiv_id("2608.28447") == "2608.28447"


def test_parse_versioned_arxiv_id() -> None:
    assert parse_arxiv_id("2608.28447v1") == "2608.28447v1"


def test_parse_abs_url() -> None:
    assert parse_arxiv_id("https://arxiv.org/abs/2608.28447") == "2608.28447"


def test_parse_pdf_url() -> None:
    assert parse_arxiv_id("https://arxiv.org/pdf/2608.28447.pdf") == "2608.28447"


def test_parse_old_style_arxiv_id() -> None:
    assert parse_arxiv_id("math/0211159") == "math/0211159"


def test_parse_old_style_versioned_arxiv_id() -> None:
    assert parse_arxiv_id("hep-th/9711200v1") == "hep-th/9711200v1"


def test_parse_old_style_abs_url() -> None:
    assert parse_arxiv_id("https://arxiv.org/abs/math/0211159") == "math/0211159"


def test_parse_old_style_pdf_url() -> None:
    assert parse_arxiv_id("https://arxiv.org/pdf/hep-th/9711200.pdf") == "hep-th/9711200"


def test_parse_arxiv_id_rejects_garbage() -> None:
    import pytest as _pytest
    with _pytest.raises(ValueError):
        parse_arxiv_id("not-an-id")
