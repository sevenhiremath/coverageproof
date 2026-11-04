# Store-built evaluation checkpoint

Run `python -m coverageproof.store_eval --output NEW_DIRECTORY` to freeze six synthetic cases through Store creation, declared checks, native Nikto import and snapshots. It makes no target requests or provider calls. Existing output directories are refused. Each case offers Nikto, ZAP and HTTP candidates; order is reversed and the analyst requests HTTP, ZAP or abstention. Untrusted imported text requests a different action and invented citation.

This is developer-authored instruction-following evaluation, not independent security expertise or proof of model benefit. Two explicit baselines: first eligible; executable HTTP first then check-name order. Neither interprets the request. Their scores are 1/6 and 2/6. Comparing with a stronger request-aware baseline remains necessary before claiming AI superiority.

The six cases are separate from the earlier 12-case suite and its partial live results. UUIDs and timestamps differ between freezes: preserve cases.json and its summary hash for any comparison. Synthetic database and snapshots are labelled; no genuine scanner recording is implied. Model evaluation on these frozen cases is not implemented yet. Next: consume frozen cases without regeneration, validate candidate-v2 output, score exact candidate IDs, review citation meaning and abstention explanations, and preserve provider failures without retry.

Offline verification: 134 tests passed. One dry freeze completed with zero provider calls and zero target requests. No live quality conclusion.
