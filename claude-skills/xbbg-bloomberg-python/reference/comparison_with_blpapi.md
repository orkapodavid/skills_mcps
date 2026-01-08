# comparison_with_blpapi.md

Use xbbg when:
- Building research notebooks, analytics pipelines, and screening workflows.
- Preferring pandas-native returns and simple function calls.
- Needing quick prototypes and batch/scheduled retrieval.

Use raw blpapi when:
- Building production trading systems or latency-sensitive services.
- Requiring fine-grained event loop control and advanced services.
- Handling mission-critical real-time streaming with custom handlers.

Key differences:
- xbbg: `bdp`/`bdh`/`bds`/`bdib` functions, DataFrames, caching, session helpers.
- blpapi: low-level session/event management, greater flexibility, more boilerplate.
