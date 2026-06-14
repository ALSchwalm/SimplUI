# Project Tracks

This file tracks all major tracks for the project. Each track has its own detailed plan in its respective folder.

---

- [x] **Track: I want to make a significant rewrite of this project. Instead of using gradio, with the server acting as a kind of "proxy" for the comfyui server, I would like the server to basically just be serving a static page. All the actual logic to interact with the websocket and http endpoints of comfyui would be done in the client with no involvement from the simplui server**
*Link: [./archive/static_client_rewrite_20260612/](./archive/static_client_rewrite_20260612/)*

---

- [~] **Track: I want to change the behvaior on page refresh. First, it currently seems like some state is preserved across page reloads. We should not do that. When the page is refreshed it should be a completely new session with no memory of the previous one. We shoudl also add a modal dialog warning when the user attempts to go back/refresh/natvigate away**
*Link: [./fresh_sessions_navigate_away_20260614/](./fresh_sessions_navigate_away_20260614/)*
