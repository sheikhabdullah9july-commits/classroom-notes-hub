# Release review — 15 October 2026

Four workflow tests pass with an isolated SQLite database. Browser captures verify home and course pages with synthetic course data.

Changes: registration cannot self-assign privileged roles; pending note views/downloads are restricted; uploads are outside static assets and have unique names; anonymous chat events are ignored; external login redirects are rejected; insecure token-disclosure recovery is disabled by default; admin bootstrap uses prompted credentials; secrets can load from `.env`; debug is opt-in and server binds to localhost. Original attribution is preserved.

A fresh, isolated installation using every original requirements pin completed successfully and all four tests passed there too.

Not verified: real email delivery, end-to-end browser chat across users, production deployment. CSRF protection, input validation, and upload-content scanning need further work.
