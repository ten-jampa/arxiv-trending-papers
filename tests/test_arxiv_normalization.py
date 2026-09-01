import xml.etree.ElementTree as ET

from founder_radar.arxiv import ATOM_NS, normalize_entry

ATOM_XML = """<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns="http://www.w3.org/2005/Atom" xmlns:arxiv="http://arxiv.org/schemas/atom">
  <entry>
    <id>http://arxiv.org/abs/2608.28447v1</id>
    <updated>2026-08-31T00:00:00Z</updated>
    <published>2026-08-30T00:00:00Z</published>
    <title> Learning to Use Tools: Reinforcement Learning for Tool-Integrated Mathematical Reasoning </title>
    <summary> An abstract with a project link https://example.com/project. </summary>
    <author><name>Alice Smith</name></author>
    <author><name>Bob Jones</name></author>
    <link href="http://arxiv.org/abs/2608.28447v1" rel="alternate" type="text/html" />
    <link title="pdf" href="http://arxiv.org/pdf/2608.28447v1" rel="related" type="application/pdf" />
    <arxiv:primary_category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.AI" scheme="http://arxiv.org/schemas/atom"/>
    <category term="cs.LG" scheme="http://arxiv.org/schemas/atom"/>
    <arxiv:comment>Project page: https://github.com/example/tool-rl</arxiv:comment>
    <arxiv:doi>10.1000/example</arxiv:doi>
  </entry>
</feed>
"""


def test_normalize_arxiv_entry() -> None:
    root = ET.fromstring(ATOM_XML)
    entry = root.find("atom:entry", ATOM_NS)
    assert entry is not None
    paper = normalize_entry(entry, fetched_at="2026-09-01T00:00:00+00:00")
    data = paper.to_dict()

    assert data["paper_id"] == "arxiv:2608.28447v1"
    assert data["arxiv_id"] == "2608.28447v1"
    assert data["title"] == "Learning to Use Tools: Reinforcement Learning for Tool-Integrated Mathematical Reasoning"
    assert data["authors"] == ["Alice Smith", "Bob Jones"]
    assert data["primary_category"] == "cs.AI"
    assert data["categories"] == ["cs.AI", "cs.LG"]
    assert data["pdf_url"] == "http://arxiv.org/pdf/2608.28447v1"
    assert any(link["url"] == "https://github.com/example/tool-rl" for link in data["links"])
    assert any(link["url"] == "https://example.com/project" for link in data["links"])
