# Security Fix Summary

This patch applies code-level remediations for the security feedback in `Pasted text(25).txt`.

## Already fixed in the uploaded project before this patch

- Plaintext credit card fields were already removed from the current `Submission` model and `SubmissionForm`.
- The submission details template no longer asks for card number, expiry, or CVV.
- A Stripe checkout flow had already been introduced for grading-payment collection.
- `GEMINI_API_KEY` was already loaded from the environment in current `settings.py`; the exposed historical key still must be revoked in the provider dashboard.
- `cards.delete_card_view` already required login, POST, and card ownership.

## Fixed by this patch

- Moved Django `SECRET_KEY` to `DJANGO_SECRET_KEY`; production now fails closed if it is missing.
- Added `.env.example` and cleaned `.gitignore` so secrets and generated data are not committed.
- Updated deployment/CI workflows to provide `DJANGO_SECRET_KEY`.
- Validated login `next` redirects with `url_has_allowed_host_and_scheme()`.
- Made logout POST-only with `@require_POST`.
- Added login-attempt throttling using Django cache.
- Required login for submission start/details/checkout/success/cancel/confirmation.
- Enforced submission ownership using `get_object_or_404(Submission, pk=pk, user=request.user)`.
- Reintroduced `TrackedCard.user` and added a migration.
- Required login for all tracking and market-watch endpoints.
- Filtered tracking list/detail/edit/delete by `request.user` and assigned new tracked cards to the authenticated user.
- Fixed the card-notes IDOR by checking `Card.user` before saving notes.
- Restricted card retrieval querysets to the authenticated user's cards.
- Required login and rate-limited AI scan/report requests.
- Replaced uploaded scan extension derivation from attacker-controlled MIME subtype with an allowlist.
- Added base64 validation, size limit, and Pillow image verification before saving uploaded scans.
- Updated dependency pins: `Django==4.2.28` and `sqlparse==0.5.5`.

## Still requires operational action outside the code patch

- Rotate `DJANGO_SECRET_KEY` in production and invalidate existing sessions.
- Revoke/rotate the leaked OpenRouter/GEMINI key in the provider dashboard and audit usage.
- Configure `DJANGO_SECRET_KEY`, `GEMINI_API_KEY`, and `STRIPE_SECRET_KEY` in the deployed service environment, not only CI/CD.
- Purge historical plaintext payment data from any existing production database/backups.
- If the repository with leaked secrets was public or shared, consider history rewriting with BFG/git-filter-repo, then require collaborators to re-clone.
- Ensure the production web server serves media with `X-Content-Type-Options: nosniff`; Django now sets the app header, but Nginx/Apache/CDN media serving needs its own header configuration.
