# MannMitra V5 database

MannMitra supports two storage modes:

1. **SQLite local mode** — default when `MONGO_URI` is empty. This makes classroom demos easy.
2. **MongoDB Atlas mode** — enabled automatically when `MONGO_URI` is present. Collections are `users`, `journals`, `chats`, `habits`, and `community_posts`.

The model layer hides the storage difference, so routes and services remain unchanged.
