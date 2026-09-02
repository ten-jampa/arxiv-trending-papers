# arXiv API Rate Limits and Respectful Client Usage

Research date: 2026-09-01.

Question driving this research: `founder-radar` calls
`https://export.arxiv.org/api/query` with no throttling/backoff and is
getting sustained HTTP 429 errors after roughly a dozen sequential
requests. What does arXiv actually document about rate limits, and what
should a small Python CLI do about it?

Primary sources consulted (fetched directly, 2026-09-01):

- <https://info.arxiv.org/help/api/index.html>
- <https://info.arxiv.org/help/api/tou.html> (Terms of Use for arXiv APIs)
- <https://info.arxiv.org/help/api/user-manual.html>
- <https://info.arxiv.org/help/oa/index.html> (OAI-PMH)
- <https://info.arxiv.org/help/bulk_data.html> (arXiv Bulk Data Access)

No web search was available in this session (no Serper key configured), so
findings are limited to the primary docs above plus direct empirical probes
against `export.arxiv.org` (see "Empirical observations" below). No
secondary blog posts or Stack Overflow threads were used.

## 1. Documented request rate

**Verified, from the official Terms of Use** (`tou.html`, section
"Limitations" → "Rate limits"):

> "When using the legacy APIs (including OAI-PMH, RSS, and the arXiv API),
> make no more than one request every three seconds, and limit requests to
> a single connection at a time."

This is the authoritative number for `export.arxiv.org/api/query`: **one
request every 3 seconds, single connection**. The same page adds: "Please
note that the following rate limits apply to all of the machines under
your control as a whole. You should not attempt to overcome these limits by
increasing the number of machines used to make requests." I.e. the limit is
enforced (or at least intended) per user/organization, not just per
connection, and running requests from multiple machines/IPs to dodge it is
explicitly against the ToU. "Attempt to circumvent rate limits" is listed
under "Things that you must not do."

**Verified, from the API User Manual** (`user-manual.html`, paging
section):

> "In cases where the API needs to be called multiple times in a row, we
> encourage you to play nice and incorporate a 3 second delay in your
> code."

This matches the ToU number and is the number the official example code in
the user manual's "detailed examples" section implements.

**A different, looser number exists for general site crawling** (not the
`/api/query` endpoint specifically), from the Bulk Data Access page
(`bulk_data.html`, "Play nice" section):

> "We ask that users intent on harvesting use the dedicated site
> export.arxiv.org for these purposes... For these purposes we suggest that
> a reasonable rate to be bursts at 4 requests per second with a 1 second
> sleep, per burst."

This "4 req/s burst, then 1s sleep" guidance is framed around crawling
arbitrary arxiv.org URLs (abstract pages, PDFs), not the structured
`/api/query` endpoint. It does not supersede or loosen the ToU's explicit
"one request every three seconds" rule for the API/OAI-PMH/RSS. **For
`founder-radar`'s use of `export.arxiv.org/api/query`, the 3-second rule in
the Terms of Use is the one to follow**; the 4 req/s figure is a separate,
looser guideline for bulk crawling of arxiv.org pages generally.

## 2. What causes sustained blocks, and how long do they last

The official docs do **not** publish a specific block duration, ban
threshold, or explicit statement that blocking is IP-based. What the ToU
does say (verified):

- Rate limits apply to "all of the machines under your control as a
  whole" — implying enforcement is tied to some identity broader than a
  single TCP connection (consistent with IP-based or account/key-based
  throttling, though arXiv does not name the mechanism).
- "If we think you are attempting to circumvent those limitations, that
  your use of arXiv APIs threatens normal operation or availability of the
  arXiv platform... we may further limit or block your access." This
  confirms blocking is a deliberate, escalating response to sustained
  violation, not a fixed short-lived counter — but no numeric duration is
  documented anywhere in the pages reviewed.
- No mention of exact block duration, decay window, or unblock mechanism
  in any of the five primary pages reviewed.

**Empirical observation (this session, `export.arxiv.org/api/query`,
2026-09-01, single IP, no prior throttling):**

- 18 consecutive requests at effectively zero delay (~60ms round-trip
  each) all returned `200 OK` with no `429` and no rate-limit-related
  response headers.
- The 19th rapid request did not return `429` at all — the connection
  hung and the client's 20-second read timeout fired (`ReadTimeout`) with
  no response ever received.
- No `Retry-After`, `X-RateLimit-*`, or similar headers were present on
  *any* successful response in this session (see point 3 below).

This is a small, single-run sample from one IP, so it is **inferred, not
documented**: it suggests export.arxiv.org's practical throttling response
to bursts may be to stall/hold the TCP connection rather than to return a
clean `429` promptly, at least under some load conditions. This is
consistent with third-hand reports that the API sits behind a
Varnish/CDN layer (`X-Served-By: cache-*` and `via: 1.1 google, 1.1
varnish...` were present on the plain 200 responses observed) that may
apply its own connection-level throttling ahead of the origin. The task's
report of *sustained* 429s after ~12 sequential requests is plausible
given the documented 3-second rule — 12 requests with no delay is a severe
violation of "one request per 3 seconds," and the ToU explicitly allows
arXiv to "further limit or block" access for exactly this kind of pattern.
Do not treat this session's specific 200/hang pattern as a guaranteed
behavior; it was one measurement at one point in time, and arXiv states its
limits and enforcement "may change in the future."

## 3. Retry-After header on 429

**Not documented** in any of the five official pages reviewed. None of the
pages mention `Retry-After`, HTTP header contracts for error responses, or
any structured error-signaling behavior at all — the ToU and manual only
describe the request-rate rule itself, not the shape of a throttling
response.

**Empirically**, in this session no `429` was actually produced by
`export.arxiv.org/api/query`; the throttling response observed was a
connection hang/timeout, not an HTTP error with headers, so a
`Retry-After` header could not be verified either way from this sample.

Recommendation given the uncertainty: **if a client does receive a `429`,
it should check for and respect a `Retry-After` header if present** (cheap,
standard, harmless to check), but **must not assume its absence means "retry
immediately"** — given it is undocumented, the client should fall back to
its own exponential backoff (see section 5) when `Retry-After` is missing.

## 4. Better bulk/discovery endpoint than repeated `/api/query` calls

**Verified, from `bulk_data.html`** ("Bulk Metadata Access" section):

> "OAI-PMH — arXiv supports the OAI protocol for metadata harvesting
> (OAI-PMH) to provide access to metadata for all articles, updated daily
> with new articles. **This is the preferred way to bulk-download or keep
> an up-to-date copy of arXiv metadata.**"

And from `user-manual.html`:

> "Large result sets put considerable load on the server and also take a
> long time to render. We recommend to refine queries which return more
> than 1,000 results, or at least request smaller slices. For bulk metadata
> harvesting or set information, etc., the OAI-PMH interface is more
> suitable."

**OAI-PMH base URL (verified, `oa/index.html`):**
`https://oaipmh.arxiv.org/oai?verb=Identify`
(arXiv supports OAI-PMH v2.0; metadata formats include `oai_dc`, `arXiv`,
and `arXivRaw`; updated nightly; same Terms of Use rate limits — one
request per 3 seconds — apply to OAI-PMH as to the API, per the ToU
"legacy APIs (including OAI-PMH, RSS, and the arXiv API)" wording.)

**For full-corpus / full-text bulk needs (verified, `bulk_data.html`):**

- **Kaggle** — "The full, machine-readable arXiv dataset is available on
  Kaggle. This includes all available articles and related features such
  as article titles, authors, categories, abstracts, full text PDFs, and
  more." (One-time/periodic snapshot download, not an API call pattern.)
- **Amazon S3** — described as "the accepted mechanism to download the
  complete corpus," with programmatic API/OAI-PMH access suggested only to
  "play catch-up" between S3 bucket updates.
- Explicit instruction: "Please do not attempt to download the complete
  corpus programmatically" via the API.

**Recommendation for `founder-radar`:** the current vertical slice is
single-paper lookup (`one arXiv paper -> ... -> brief`), so `/api/query`
against one arXiv ID is the right endpoint and is not the source of the
429s — the *lack of delay between calls* is. If/when the project expands to
batch discovery (per AGENTS.md, that expansion is explicitly gated and not
yet in scope), OAI-PMH (or the Kaggle/S3 snapshot for one-off large corpus
pulls) is the documented, correct alternative to calling `/api/query`
repeatedly in a loop.

## 5. Concrete client-side throttling recommendation

Based on the verified 3-second rule and the observed hang-on-burst
behavior, for a small Python CLI hitting `export.arxiv.org/api/query`
one-paper-at-a-time:

1. **Fixed minimum delay between requests: 3 seconds**, matching the
   documented ToU/user-manual rule exactly. This is simpler and more
   defensible than a token bucket for a "one paper at a time" CLI, and
   directly addresses the reported symptom (429s after ~12 unthrottled
   requests). Implement as a simple "sleep until 3s have elapsed since the
   last request completed" gate, not "sleep 3s after every request" (avoid
   compounding request latency into the delay budget).
2. **Single connection at a time** — verified requirement, don't fire
   concurrent/parallel requests at `export.arxiv.org` even for different
   paper IDs.
3. **Exponential backoff on non-200 responses (429 or otherwise) and on
   timeouts/hangs**, since the empirical test in this session shows the
   server may hang the connection rather than return a clean 429. Suggested
   shape: on failure, backoff `min(60, base * 2**attempt)` seconds
   (e.g. base=3s → 3s, 6s, 12s, 24s, 48s, cap 60s), capped at a small
   number of retries (e.g. 5) before surfacing a clear error to the CLI
   user. If a `Retry-After` header is present on a 429, prefer it over the
   computed backoff value.
4. **Reasonable client-side read timeout** (e.g. 30s) so a hung connection
   (as observed) fails fast into the backoff path instead of blocking the
   CLI indefinitely.
5. **Set a descriptive `User-Agent` header** identifying the tool and a
   contact channel (e.g. `founder-radar/0.1 (github.com/<org>/<repo>)`).
   This is **not explicitly required** by the docs reviewed — no
   `User-Agent` requirement was found in the ToU, API index, or user
   manual — but it is standard API-citizenship practice, costs nothing, and
   is consistent with the ToU's general spirit of accountable use
   ("we will collect certain private information about you, such as your
   name and email address" for registered API use — though this specific
   line refers to arXiv's own developer registration process, not an
   HTTP header, and was not verified to be enforced for anonymous
   `export.arxiv.org` calls).
6. **Do not parallelize across IPs/machines to raise effective
   throughput.** Verified as an explicit ToU violation ("You should not
   attempt to overcome these limits by increasing the number of machines
   used to make requests").
7. If `founder-radar` ever needs true batch/discovery throughput beyond
   occasional single-paper lookups, switch that use case to OAI-PMH
   (`https://oaipmh.arxiv.org/oai`) rather than looping `/api/query`,
   subject to the same 3-second rule but with resumption tokens designed
   for bulk harvesting instead of paged search results capped at 30,000
   items.

## What was verified vs inferred

**Verified directly from arXiv's own pages (quoted above with URLs):**

- The 3-second-per-request / single-connection rule (ToU + user manual,
  two independent confirmations).
- The 4 req/s-burst-then-1s-sleep guidance is a *separate* general-crawl
  recommendation on the Bulk Data Access page, not the API rate limit.
- ToU explicitly forbids circumventing rate limits via multiple machines.
- ToU states arXiv may block access if it judges use to be abusive, with
  no documented block duration.
- OAI-PMH is arXiv's own documented "preferred way to bulk-download or
  keep an up-to-date copy of arXiv metadata," base URL
  `https://oaipmh.arxiv.org/oai`.
- Kaggle and Amazon S3 are arXiv's documented mechanisms for full-corpus
  bulk/full-text access; programmatic API use for full-corpus download is
  explicitly discouraged ("Please do not attempt to download the complete
  corpus programmatically").
- No `Retry-After`, `User-Agent`, or other header-contract requirements are
  documented anywhere in the five pages reviewed.

**Inferred / empirically observed, not documented by arXiv:**

- That sustained unthrottled requests can produce a connection hang
  (client-side read timeout) rather than a clean `429` — observed once, in
  this session, 18 fast 200s followed by a hang on request 19, single IP,
  single point in time. Not a guaranteed or documented behavior.
- That blocking is IP-based specifically — the ToU's "all machines under
  your control" language is consistent with IP-based enforcement but does
  not name the mechanism.
- Any specific block duration — not stated anywhere; unknown.
- Whether `Retry-After` is ever sent on an actual `429` from
  `export.arxiv.org` — could not be verified in this session because no
  429 was actually observed (a hang was observed instead). Treat as unknown
  and defensively check for it anyway.

## Sources

- Terms of Use for arXiv APIs — <https://info.arxiv.org/help/api/tou.html>
- arXiv API User Manual — <https://info.arxiv.org/help/api/user-manual.html>
- arXiv API help index — <https://info.arxiv.org/help/api/index.html>
- Open Archives Initiative (OAI-PMH) — <https://info.arxiv.org/help/oa/index.html>
- arXiv Bulk Data Access — <https://info.arxiv.org/help/bulk_data.html>
