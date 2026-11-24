# product-agent

Daily AI routine that researches demand (Etsy, Gumroad, Meta-ads-to-website), picks evidence-backed digital products, builds them with the pipelines in `tools/`, and delivers listing and ad packs under `daily/`.
- `PLAYBOOK.md`: what the agent does each run.
- `config.json`: regions, price bands, limits, delivery branch, local run time.
- `memory/`: products built, rejected ideas, and real results (paste sales/clicks into `results.csv`: the agent learns from them).
- `tools/`: generators and test harnesses (sheets, builders, n8n).
Not part of the Vantix app code.
