# KAFKA-21205 demonstration results

Mode: local CLI simulation (GitHub reads/writes substituted).

| Check | Original | Fixed |
| --- | --- | --- |
| Indented list | Collapses into one line | Preserved |
| Code after blank line | Lines joined / indentation lost | Preserved |
| Long indented code line | Wrapped / indentation lost | Preserved |
| Full description equals input | No | Yes |
| Second fixed run | — | Unchanged; no write needed |

Both exact CLI scripts exited successfully. The original passes its
lint checks while corrupting the Markdown. The fixed version preserves
the entire input and logs that no rewrite is necessary on both runs.
