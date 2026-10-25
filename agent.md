# AGENTS.md — Developer & AI Agent Guidelines

See [AGENTS.md](AGENTS.md) for full architectural contracts, platform notes, and safety rules.

## Quick Summary
- **Security**: Never commit session JSONs, cookies, `.env`, or `*.db` files.
- **Animation**: All camera moves use `SeniorMotionDirectorEngine` with damped spring recoil and multiplane parallax.
- **Subtitles**: ASS word-level spring pop typography with `MarginV = 440`.
- **Instagram CLI**: Use `scripts/instagram_manager.py` for status, upload, like, comment, and story operations.
- **Windows**: Use forward slashes in FFmpeg path references and wrap stdout in UTF-8.
