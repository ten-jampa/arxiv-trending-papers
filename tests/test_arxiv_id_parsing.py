from founder_radar.arxiv import parse_arxiv_id


def test_parse_plain_arxiv_id() -> None:
    assert parse_arxiv_id("2608.28447") == "2608.28447"


def test_parse_versioned_arxiv_id() -> None:
    assert parse_arxiv_id("2608.28447v1") == "2608.28447v1"


def test_parse_abs_url() -> None:
    assert parse_arxiv_id("https://arxiv.org/abs/2608.28447") == "2608.28447"


def test_parse_pdf_url() -> None:
    assert parse_arxiv_id("https://arxiv.org/pdf/2608.28447.pdf") == "2608.28447"
