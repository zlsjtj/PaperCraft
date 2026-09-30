# Primary research sources

Retrieved 2026-09-30. Search scope: a short targeted search for cache admission,
FIFO filtering, and variable-size object caches. The three papers below were
opened from author/academic or conference sources. No software was installed
and no published experiment was rerun. This is not an exhaustive novelty search.

## S1

Gil Einziger, Roy Friedman, Ben Manes. *TinyLFU: A Highly Efficient Cache
Admission Policy*. Author-uploaded paper, arXiv:1512.00727.

- Record: https://arxiv.org/abs/1512.00727
- Paper inspected: https://arxiv.org/pdf/1512.00727
- Relevant locations: abstract; design discussion of approximate frequencies
  and reset/aging, Sections 3–4.
- Mechanism: use approximate recent access frequencies to compare a newly
  accessed candidate with a cache eviction candidate. The policy can augment
  replacement policies; W-TinyLFU is a particular combined design.
- Condition: conclusions depend on access distributions, sampling/history, and
  the accompanying replacement policy. This source does not establish the DEMO
  service's response-time or reference-examination guarantees.

## S2

Juncheng Yang, Yazhuo Zhang, Ziyue Qiu, Yao Yue, K. V. Rashmi. *FIFO Queues are
All You Need for Cache Eviction*. SOSP 2023. DOI: 10.1145/3600006.3613147.

- Author-hosted paper inspected: https://www.cs.cmu.edu/~rvinayak/papers/s3-fifo-sosp-2023-fifo-queues-are-all-you-need-for-cache-eviction.pdf
- Author project: https://s3fifo.com/
- Relevant locations: Section 4.1, page 134 in proceedings (PDF page 5), and
  Sections 5–6 for evaluation conditions and discussion.
- Mechanism: small, main, and ghost FIFO queues; capped access counters; quick
  removal of low-reuse objects and reinsertion of accessed main-queue objects.
  Ghost entries record identities, not payloads.
- Condition: main evaluation and separate flash-filter experiments have
  different setups. None should be relabeled as the DEMO's capped CLOCK
  experiment. The payload-free reserve is not the S3-FIFO small queue.

## S3

Daniel S. Berger, Ramesh K. Sitaraman, Mor Harchol-Balter. *AdaptSize:
Orchestrating the Hot Object Memory Cache in a Content Delivery Network*.
NSDI 2017, pages 483–498.

- Conference record: https://www.usenix.org/conference/nsdi17/technical-sessions/presentation/berger
- Paper inspected: https://www.usenix.org/system/files/conference/nsdi17/nsdi17-berger.pdf
- Relevant locations: Section 2 for objectives; Sections 3–4 for size-aware
  admission and model-based tuning.
- Mechanism: probabilistic size-aware admission with parameters adapted using a
  Markov cache model. The first-level hot-object cache emphasizes object-hit
  ratio under changing request and size distributions.
- Condition: that objective differs from maximizing bytes avoided at the
  origin. Its CDN hierarchy and measured deployment should not be imported into
  this single-level, serial, hypothetical cache specification.

## Remaining uncertainty

Full prior-art coverage, closest-work ranking, and originality are unresolved.
The search has not exhaustively covered bounded CLOCK scans, free-space
reserves, eviction scheduling, admission transactionality, or memory-pressure
controllers. No published policy has a result row in the DEMO CSV. The source
notes are short original paraphrases, not copied paper text.
