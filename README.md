# Illinois Brady/Giglio officer database

A searchable dashboard of law enforcement officers who appear on Brady/Giglio lists kept by Illinois prosecutors, built from records obtained through Freedom of Information Act requests.

## How the pieces fit together

```
Brady_Giglio_Statewide_List_for_Pulitzer.xlsx
        │  xlsx_to_csv.py (cleans and converts)
        ▼
brady_giglio_cleaned.csv  ──(fetched by)──▶  illinois-brady-giglio-embed.html

illinois-brady-giglio-methodology.md
        │  md_to_pdf.py
        ▼
illinois-brady-giglio-methodology.pdf  ──(linked from)──▶  the dashboard footer
```

## Files

| File | What it is | Purpose |
|---|---|---|
| `Brady_Giglio_Statewide_List_for_Pulitzer.xlsx` | The original, hand-compiled spreadsheet of officers. | The source of truth. Edit this when records change, then re-run the conversion script. |
| `xlsx_to_csv.py` | Python script (needs `openpyxl`). | Cleans the spreadsheet (trims whitespace, separates job titles from ILETSB IDs, standardizes dates, fixes a status typo) and writes the CSV. |
| `brady_giglio_cleaned.csv` | The cleaned data, 1,094 records. | What the dashboard loads. Columns: `n, id, role, cty, dept, d, dk, cat, src, st, ag, cc` (`d` is the display date, `dk` a sortable date key). |
| `illinois-brady-giglio-embed.html` | The dashboard: a single self-contained page. | Lets readers search, filter by county, status and category, sort, page through results and download the data as CSV. It fetches the CSV at load time from the URL in `CONFIG.dataUrl`. |
| `illinois-brady-giglio-methodology.md` | Methodology write-up in Markdown. | Explains how the data was obtained and compiled, editorial judgment calls, the data dictionary and limitations. |
| `md_to_pdf.py` | Python script (needs the `markdown` package and Google Chrome). | Renders the methodology Markdown into a PDF. |
| `illinois-brady-giglio-methodology.pdf` | PDF version of the methodology. | The file readers download from the link in the dashboard footer (`CONFIG.methodologyUrl`). |
| `.gitignore` | Git settings. | Keeps macOS `.DS_Store` files out of the repository. |

## Updating the data

1. Edit the spreadsheet.
2. Regenerate the CSV:

   ```bash
   python3 xlsx_to_csv.py Brady_Giglio_Statewide_List_for_Pulitzer.xlsx
   ```

3. If the methodology changed, regenerate the PDF:

   ```bash
   python3 md_to_pdf.py
   ```

4. Commit and push. The dashboard reads the CSV from GitHub, so it picks up the new data after the push.

## Running the dashboard locally

Browsers block `fetch` from `file://` pages, so serve the folder instead of double-clicking the HTML:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000/illinois-brady-giglio-embed.html>.

## Configuration

The "EDIT THESE" block near the top of the script in `illinois-brady-giglio-embed.html` holds the page title, description, credit line, page size, `dataUrl` (must be a `raw.githubusercontent.com` link, not a `github.com/.../blob/` page) and `methodologyUrl`.

## Credits

Reporting by Max Blaisdell and Sam Stecklow.
