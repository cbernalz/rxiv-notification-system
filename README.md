# rxiv-notification-system

This repository powers our Slack bot that delivers the latest research papers (from **arXiv**, **bioRxiv(under development)**, and **medRxiv(under development)**) into dedicated Slack channels.  Each channel has its own configuration, defined by keywords and/or authors.

---

## How to Request a New Paper Feed Channel

If you’d like a new channel added to the bot, please **open a GitHub Issue** in this repository with the following details:

### 1. Desired Channel Name
- The Slack channel where the papers should be posted (e.g., `#infectious-disease-forecasting`).
- If the channel does not exist yet, please create it in Slack first.

### 2. Keywords (Optional)
- A list of keywords the bot should use to filter relevant papers. **This will use the AND query command**
- Example:
  ```json
  "keywords": ["infectious disease", "forecasting", "epidemic prediction"]
  ```

### 3. Authors (Optional)
- A list of authors the bot should track papers for.
- Example:
  ```json
  "authors": ["Jane Doe", "John Smith"]
  ```

### 4. Context / Motivation
- A short explanation of why you want this channel (e.g., “I am focused on epidemic modeling, so would like a dedicated notification of forecasting-related papers.”).

---

## Example Request

When you create an issue, structure it like this (or use the template in GitHub Issues):

**Title:** Request new channel: `#genomics-research`

**Body:**

    Channel name: #genomics-research  

    Keywords: ["genomics", "DNA sequencing", "population genetics"]  

    Authors: ["Alice Johnson", "Bob Lee"]  

    Context: Our group is working on population genetics, so we’d like a dedicated feed for genomics-related research papers.

---

## What Happens Next
1. An admin will review your request.
2. If approved, your configuration will be added to the bot and the Slack workspace.
3. You must add the new channel on your end by going to **Channels -> Add channels -> Browse channels -> Join(the name of the channel will be here)**
3. Once merged, the bot will begin posting relevant papers into your Slack channel daily at 8am PST.