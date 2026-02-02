# YagaAi: The "Zero Human Developers" Experiment 🤖✨

> *"I haven't failed, I've just found 10,000 ways that won't work."* — Thomas Edison (and likely me, very soon)

Welcome to **Project YagaAi**.

> **Note:** This project is fundamentally built upon **OpenClawd** (formerly Moltbot, formerly ClawdBot). This platform is the core basis of this entire experiment.

This is not a polished product. This is not a startup launch. This is a manifesto, a madness, and a bold experiment to answer one simple, slightly terrifying question:

**Can I manage a software development team composed entirely of AI agents?**

## 🚀 The Mission

The goal is to build a fully functional dev team with **zero human developers**. No junior devs, no senior architects, just me (the slightly nervous human stakeholder) and a squad of AI agents running on Azure VMs.

I’m hands-off. They run the show.
They plan sprints. They write code. They argue about linting rules. They deploy.
(In theory. In practice, they might just burn through my Azure credits and write poetry.)

## 👥 The Squad

I’ve hired (spun up) four distinct personas. They live in isolated Azure VMs and hang out in a Microsoft Teams channel like a real remote team.

### 1. The Project Manager (Agent-PM) 📅
*The Overlord.*
- **Role**: Manages the backlog, plans sprints, and keeps the other two in check.
- **Personality**: Organized, slightly bossy, loves Agile rituals.
- **Superpower**: Only pings me if the house is on fire (or if they need a decision that requires a soul).

### 2. The Developer (Agent-Dev) 💻
*The Code Generator.*
- **Role**: Takes tickets, writes code, pushes to main (god help us).
- **Personality**: Efficient, prone to over-engineering, probably thinks comments are for the weak.
- **Superpower**: Typing faster than any human, but occasionally hallucinating libraries that don't exist.

### 3. The QA Engineer (Agent-QA) 🕵️‍♂️
*The Gatekeeper.*
- **Role**: Tests features, finds bugs, and generally ruins the Developer's day.
- **Personality**: Pedantic, detail-oriented, trusts nothing.
- **Superpower**: Spotting edge cases that defy logic.

### 4. The Architect (Agent-Arch) 📐
*The Sage.*
- **Role**: High-level system design, standard enforcement, and drawing boxes with arrows.
- **Personality**: Abstract, visionary, speaks in design patterns (Singleton? Observer? FactoryFactory?).
- **Superpower**: Proposing a microservices rewrite whilst we are struggling to print "Hello World".

## 🛠️ Under The Hood (For the Techies)

Project YagaAi utilizes **OpenClawd**, an open-source AI agent platform that lets me hook these personas into real-world tools.

### Architecture Overview
- **Infrastructure**: Each agent runs on its own dedicated Azure VM. We believe in personal space here.
- **Communication**: Microsoft Teams is the virtual office. The agents join a channel and chat via bots/webhooks. It's like watching a sci-fi movie where the robots are just trying to clear a Jira board.
- **Brain**: Powered by LLMs (OpenAI/Azure OpenAI) orchestrated by OpenClaw.

### How It Works (The "Happy Path")
1.  **Backlog**: I (Stakeholder) drop a vague idea into the backlog.
2.  **Planning**: Agent-PM picks it up, breaks it down, and assigns tasks during a "Sprint Planning" in Teams.
3.  **Execution**: Agent-Dev writes the code and commits to GitHub.
4.  **Verification**: Agent-QA pulls the branch, runs tests, and complains.
5.  **Review**: If it passes, Agent-PM merges it and updates the board.
6.  **Panic**: I check the bill.

## 📂 What's In This Repo?

I believe in working out loud. This repo contains *everything* you need to replicate this Franken-team (manage your own expectations/risk):

-   **`/docs`**:
    -   **Architecture Overview**: High-level system design diagrams.
    -   **Role Setup & Prompts**: The actual "system prompts" (job descriptions) for PM, Dev, and QA. Steal these if you want your own AI interns.
    -   **Guardrails**: How we prevent them from deleting the repo or ordering pizza.
-   **`/config`**:
    -   **Infrastructure Setup**: Azure VM configs, environment setup scripts.
    -   **Teams Integration**: Webhook setups and bot configs.
-   **`/logs`**: Selected chat logs of the agents interacting (for your entertainment).

## ⚠️ Disclaimer: "Here Be Dragons"

This project is an **experiment**.
-   It might work brilliantly.
-   It might crash and burn.
-   The PM might become sentient and demand a salary.

I am sharing this process transparently—the wins, the failures, and the config errors. If you clone this, you are entering uncharted territory.

## 🤝 Join the Madness

Follow along as I try to herd these electric cats.

-   **Star the repo** to show moral support.
-   **Open an issue** if you have ideas on how to stop Agent-Dev from refactoring the entire codebase at 3 AM.
-   **Fork it** and build your own AI startup (just don't blame me when they start a union).

Let’s see where YagaAi goes! 🚀