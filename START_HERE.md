# Run your Uruguay 2010 wiki

The assignment asks you to build a small library of linked notes and an assistant that answers using that library. Gemma writes the answer; retrieval selects relevant source passages; the harness connects the commands, prompts, model, citations, and saved evidence. RAG supplies context and does not retrain the model.

The application runs on your Mac through a terminal. Search looks up original source passages. Ask sends selected evidence to local Gemma and checks the returned citations. Chat uses recent conversation for drafting and follow-ups.

## Start the local model server

Open Terminal and run:

```sh
cd "$HOME/Documents/ChatGPT/Class 4/uruguay-2010"
./scripts/start_ollama.sh
```

Leave this terminal open. If it says the port is already in use, Ollama may already be running; check `./wiki status` in another terminal. The server binds to localhost and disables Ollama cloud access.

## Try the commands

Open a second terminal in the project folder:

```sh
./wiki --help
./wiki search "Ghana penalty shootout"
./wiki ask "How was Uruguay's match against Ghana decided?"
./wiki chat
```

In chat, ask “What can you help me with?”, request a short study plan, then say “Make that shorter.” Use `/notes` before a question to explicitly search your sources, and `/quit` to leave. Each ask question is independent of chat history.

## Explore the wiki

Open the `vault` folder itself in Obsidian and start at `index.md`. Follow a match link, a related note, and its original-source reference. For the graph, use the filter `path:wiki/` and hide attachments.

## Add or regenerate notes

```sh
./wiki ingest vault/raw
```

Unchanged notes are skipped, preserving reviewed edits. To demonstrate an actual fresh local generation from one existing source:

```sh
./wiki ingest vault/raw --source S07 --force
```

The previous note is backed up outside the vault. Source files remain unchanged. Adding new material currently requires updating the source catalog and source-section configuration; arbitrary uncataloged files are rejected explicitly.

## Complete the offline evidence

Download and validate everything first. Then disconnect Wi-Fi and Ethernet, keep Ollama running locally, and run:

```sh
./scripts/offline_demo.sh
```

The script asks you to attest that the Mac is disconnected and records OS network observations plus the actual CLI output. It regenerates a note, runs all four research questions, checks chat and follow-ups, verifies that a fictional chat claim does not become research evidence, and searches with the model unloaded.

Review the regenerated World Cup Group Draw note against its source. Take screenshots showing the disconnected network and terminal results. Reconnect afterward. Local model calls made while the Mac is connected are useful tests, but are not proof of an offline demonstration.

## What is ready and what remains

Ready: seven source articles, thirteen reviewed topic notes, linked navigation, the local CLI, actual model test evidence, memory/timing measurements, and three Obsidian screenshots. Read `evidence/Validation.md` for successes and observed failures.

Remaining: run the truly disconnected demo, inspect its results, submit the public repository URL through your course portal. The public repository is https://github.com/sbardacosta-code/uruguay-2010-wiki. Course-portal submission has not been performed.
