# Contributing

Thanks for helping keep this list useful. Please read this before opening a pull request.

## What belongs here

Links that help someone play, understand, host, or follow WARDOGS. That includes official channels, community tools, wikis, guides, news coverage, creators, servers, and technical reference pages.

What does not belong:

- Cheats, aimbots, mod menus, account sellers, boosting services, or anything that violates the game's terms of service.
- Referral or affiliate links.
- Sites that only exist to capture search traffic and add nothing over pages already listed.
- Your own project, unless it works and offers something the existing entries do not. Say in the pull request that it is yours.

## Adding an entry

1. Search the README first to make sure the link is not already listed.
2. Open the link yourself and confirm it loads and matches the description.
3. Add it to the right section. Keep related items together and put sub-pages of a site as nested bullets under the main entry.
4. Use this format:

   ```markdown
   - [Name](https://example.com/) - Short neutral description that ends in a period.
   ```

   The description should say what the page is or does, not how good it is. Avoid words like "best", "amazing", or "must-have".

5. One entry per pull request, unless the entries are pages from the same site that only make sense together.
6. In the pull request description, say where you found the link and, if it is a community tool, whether it is built on beta or Early Access data.

## Removing or changing an entry

Open a pull request that removes or edits the line and explain why. Good reasons include a dead link, a site that has changed purpose, a site that started selling cheats or accounts, or a link that was superseded by an official page.

## Automated link checks

A GitHub Actions workflow runs once a day and requests every link in the README. If a link does not return a successful response after retries, the workflow opens a pull request that removes that line, one pull request per link. A maintainer reviews it before anything is merged.

Some sites block automated requests even though they work in a browser. Responses of 403, 429, and 503 are treated as "blocked" rather than dead, and are listed in the workflow summary without opening a pull request. If a working link still gets flagged for another reason, add its domain or full URL to `.linkcheck-ignore` with a short comment explaining why, and the checker will skip it.

If the workflow opened a pull request for a link that still works, close the pull request without merging and add the URL to `.linkcheck-ignore`. The checker will not open a second pull request for the same URL while one exists, open or closed.

## Style

- Sentence case for headings.
- Straight quotes, not curly quotes.
- No emoji in entries.
- Descriptions in plain English. Expand acronyms the first time they appear in a section.
- Keep the Contents section in sync with the headings.

## Reporting problems

Open an issue if you are not sure whether something belongs, if a link looks suspicious, or if you found a category that should exist but does not.
