# **High-Resilience RPA Agent for Desktop Automation**

![Python Version](https://img.shields.io/badge/Python-3.11%2B-blue)
![License](https://img.shields.io/badge/License-Apache_2.0-blue)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen)](tests/) 
[![Code Style](https://img.shields.io/badge/Code_Style-Black-black)](https://github.com/psf/black)

This project is a **high-resilience Robotic Process Automation (RPA) Agent**, engineered to interact with legacy Windows desktop software, particularly in remote environments. While its initial mission is to automate medical billing, its architecture is fundamentally a **generic, configuration-driven automation engine**. Its reliability is ensured by a unique local GUI simulator, the **Stunt Action Facsimile (SAF)**, and its future is guided by an evolution towards situational awareness via an explicit GUI map (`GuiMap`).

## 🚀 Visual Demonstration

![Demo of the Bot in Action](docs/demo.gif)
_The bot in action, interacting with the Stunt Action Facsimile (SAF) to process a batch of invoices._

---

## 🎯 The Challenge: The Hidden Cost of Manual Processes

> The manual data entry required by many legacy systems is a critical operational bottleneck. It's a repetitive, high-stakes process that inevitably leads to:
> -   **Critical Errors:** A single transcription mistake can cause claim rejections, delaying revenue for weeks and requiring costly rework.
> -   **Wasted Human Potential:** Hours of skilled staff time are consumed by low-value tasks instead of complex problem-solving.
> -   **Inhibited Scalability:** Processing capacity is hard-limited by headcount, directly hindering business growth.

## ✨ The Solution: A Conscious and Reliable Software Agent

This is not a simple "copy-and-paste" script. It is a software agent built on robust architectural pillars to ensure stable, maintainable, and adaptable operation.

## 🏗️ Core Architectural Principles

1.  **Modular, Layered Design:** A strict separation of concerns (`data_handler`, `automation`, `core`) allows each component to be tested and evolved independently, fostering high cohesion and low coupling.
2.  **Error Handling as Control Flow:** The agent's logic is governed by a **Finite State Machine (FSM)** which is, in turn, directed by a custom exception hierarchy. Errors are not terminal failures; they are **business events** that intelligently guide the bot toward retry states, controlled failure, or success.
3.  **Philosophy of "Chaotic Input, Internal Order":** The system assumes external data sources (Excel files, GUI fields) are unpredictable. At the point of entry, all data is immediately sanitized, validated, and transformed into **immutable internal data models (`dataclasses`)**. This enforces a predictable, type-safe, and secure operational core.
4.  **Configuration-Driven Behavior:** The agent has no hardcoded business logic. Its operational parameters, data mappings, and—critically—its knowledge of the environment (`GuiMap`) are externalized to `.ini` files. **The bot learns from its configuration.**

---

## 🚀 Quick Start Guide

### 1. Prerequisites

-   **Python 3.11+**
-   **`pip`** and **`venv`** (included with modern Python installations).
-   **On Linux:** `xdotool` is required for GUI interaction (`sudo apt-get install xdotool` or equivalent for your distribution).

### 2. Installation

1.  **Clone the repository:**
    ```bash
    git clone <URL_OF_YOUR_REPOSITORY>
    cd facturacion_medica_bot
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    # For Linux / macOS
    python3 -m venv .venv
    source .venv/bin/activate

    # For Windows
    python -m venv .venv
    .\.venv\Scripts\activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### 3. Configuration

The bot's behavior is managed through profiles located in `config/profiles/`.

1.  **Copy the example profile:**
    ```bash
    cp config/profiles/dev_example.ini config/profiles/my_profile.ini
    ```
2.  **Edit your profile:** Open `config/profiles/my_profile.ini` and adjust the settings. The most critical setting to start is `window_title` in the `[AutomationSettings]` section, which must match the exact title of the application window you want to automate.

---

## 🏃 Usage

To run the bot, specify the configuration profile and the path to the input Excel file from the project root:

```bash
python src/main.py --profile <your_profile_name> --input-file <path/to/your/file.xlsx>
```

**Example (running against the SAF simulator):**
```bash
python src/main.py --profile dev_saf --input-file data/samples/facturacion_anonymized.xlsx
```

---

## 🛠️ A Developer-Centric Ecosystem (DevEx)

Beyond the agent itself, the project is a complete ecosystem of tools and practices designed to accelerate development, ensure data safety, and maintain high code quality.

-   **Stunt Action Facsimile (SAF): The Digital Dojo**
    The SAF is the cornerstone of our quality and development strategy. It is a **digital twin** of the target application, written in `tkinter`, which enables:
    -   An ultra-fast development and debugging loop without reliance on slow, unreliable remote connections.
    -   Fully automated **end-to-end integration testing**, a capability notoriously difficult to achieve in desktop RPA.
    -   A true CI/CD pipeline, allowing for confident, frequent deployments.

-   **Supporting Toolchain (`scripts/`)**
    -   **`anonymize_data.py`:** A powerful utility to generate safe, realistic test data from production files, using configuration profiles to define anonymization rules.
    -   **`generate_mapping_profile.py`:** An intelligent assistant that inspects an Excel file and bootstraps a configuration profile, dramatically reducing setup time.
    -   **`find_windows.py`:** A helper script to discover the exact titles of running windows for easy configuration.

-   **Professional Dependency Management**
    The project uses `pip-tools` (`requirements.in`/`.txt`) for deterministic and secure dependency management, ensuring identical environments from development to production.

---

## 💻 Recommended Development Workflow

The project is designed for a fast, safe, and efficient development loop using the SAF simulator.

#### Step A: Run the Simulator (SAF)
The SAF is your primary development environment. Launch it first.
```bash
# In your first terminal, launch the Stunt Action Facsimile
python saf/app.py
```

#### Step B: Run the Bot against the Simulator
In a separate terminal, run the bot using the dedicated SAF profile. This allows you to test and debug your logic in a controlled, local environment.
```bash
# In a second terminal, execute the bot, pointing it at the SAF
python src/main.py --profile dev_saf --input-file data/samples/facturacion_anonymized.xlsx
```

## ✅ Testing Strategy

Our quality strategy is centered on **automated integration tests against the SAF**. This allows us to validate the bot's end-to-end behavior in a fast, deterministic, and controlled environment. Unit tests are used to verify pure business logic within isolated components (e.g., `DataFilterer`, `GuiMapLoader`).

```bash
# Run the full test suite (unit and integration)
pytest
```

## 📂 Project Structure
```
facturacion_medica_bot/
├── config/                 # Configuration profiles (.ini) and the GUI map.
├── data/                   # Input, output, samples, and reports.
├── docs/                   # Architectural documentation.
├── saf/                    # Source code for the Stunt Action Facsimile (Simulator).
├── scripts/                # Developer support toolchain.
├── src/                    # The bot's main source code.
│   ├── automation/         # Automation logic, FSM, and navigation engine.
│   ├── core/               # Orchestrator, data models, and custom exceptions.
│   ├── data_handler/       # Data loading, filtering, and validation pipeline.
│   └── main.py             # Application entry point.
├── tests/                  # Unit and integration tests.
├── requirements.in         # Abstract dependencies (for pip-tools).
├── requirements.txt        # Frozen dependencies (generated).
└── README.md               # This document.
```

## 🗺️ Evolutionary Roadmap: The Path to Autonomy

The project is on a deliberate path to evolve from a sequence-following automaton into an intelligent, situationally-aware agent.

### **Hito 5: The Cartographer & The Conscious Navigator (In Progress)**
-   **Mission:** To replace fragile, "blind" navigation with a system that understands the GUI's structure.
-   **Key Artifacts:**
    -   **`GuiMap`:** A data model, loaded from a `.ini` file, that serves as the bot's "map" of the world. It defines the layout and relationship of tabs, fields, and landmarks.
    -   **`Navigator`:** A navigation engine that uses the `GuiMap` to plan and execute verified movements, confirming its arrival at each destination.
-   **Outcome:** The bot will know **where it is** at all times, eliminating an entire class of brittle failures.

### **Hito 6: The Resilient & Self-Correcting Agent (Planned)**
-   **Mission:** To empower the bot to handle the unexpected.
-   **Key Artifacts:**
    -   **Recovery Protocol:** When a navigation fails, the `Navigator` will activate a protocol to:
        1.  **Detect Known Interruptions:** Identify known pop-ups or dialogs (cataloged in the `GuiMap`) and execute the correct recovery action (e.g., press `{ESC}`).
        2.  **Reorient via Landmarks:** If lost, the agent will actively search for a known `landmark` to recalibrate its position on the map.
-   **Outcome:** The bot will graduate from **failing on an error** to **actively solving it**. It will adapt and self-correct, achieving a superior level of autonomy.

## 📚 Further Reading

For a deep dive into design decisions and implementation patterns, see the:
-   **[Architectural Decision Record & Development Guide](./docs/ARCHITECTURE.md)**

## ⚖️ License
This project is licensed under the Apache 2.0 License. A full `LICENSE` file will be added to the repository shortly.
