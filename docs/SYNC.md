# Working from the shared repository

Canonical repository: https://github.com/sevenhiremath/coverageproof (public, as requested by the user).

Online Work publishes through the GitHub connector because direct shell Git authentication is unavailable. GitHub was initialized empty and received the tested source snapshot. The older archive/bundle commit IDs describe earlier local history; they are not the GitHub main history. Do not merge those unrelated histories or force-push the bundle over main.

For the local scanner work, clone GitHub into a new folder using your authenticated Git client, create local/scanner-lab from origin/main, and keep changes under local-lab/. Preserve the earlier extraction and checkout. If that checkout later has lab changes, copy only the reviewed lab files or apply a scoped patch into the new branch. Do not overwrite the updated application with the older archive.

The uploaded application checkpoint passed 46 tests online. The local report independently verified only the older 33-test checkpoint. Local verification of the new app, live Ollama inference and genuine scanner imports remain separate pending tasks.

Repository visibility is public, verified through GitHub metadata. Presentation/video sharing and final submission are still pending. No invitations or permission changes are included in source publishing.
