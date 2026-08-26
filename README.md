# Automatic WA security-register CSV

This repository downloads the public WA Police Security Officer register every
morning, extracts licence number, full name and expiry date, and publishes the
result as a CSV file for Power BI dataflows.

## GitHub setup

1. Create a new public GitHub repository named `wa-security-register`.
2. Upload all files and folders from this starter package to the repository.
3. Open **Settings > Actions > General** in the repository.
4. Under **Workflow permissions**, select **Read and write permissions**, then
   save.
5. Open the repository's **Actions** tab.
6. Select **Update WA security officers CSV**.
7. Select **Run workflow**, and then **Run workflow** again.
8. Wait for the run to show a green check mark.
9. Confirm that `data/wa_security_officers.csv` now exists.

The workflow then runs automatically at 06:15 each morning in Perth. It commits
the CSV only when the source data changes. GitHub can delay scheduled workflows
during periods of heavy demand.

## Power BI dataflow setup

1. Open `dataflow-query.m`.
2. Replace `YOUR_GITHUB_USERNAME` with the GitHub account that owns the public
   repository.
3. Paste the complete query into the dataflow's Advanced Editor.
4. Configure `https://raw.githubusercontent.com` as an Anonymous, Public Web
   connection.
5. Save the dataflow and run a refresh.

The CSV URL has this format:

`https://raw.githubusercontent.com/YOUR_GITHUB_USERNAME/wa-security-register/main/data/wa_security_officers.csv`

## Safety checks

The update fails instead of publishing bad data when fewer than 10,000 rows are
extracted, duplicate licence numbers are found, the download is not a PDF, or a
date cannot be parsed. A failed GitHub Actions run leaves the last valid CSV in
place.
