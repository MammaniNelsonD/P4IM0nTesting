
![photo_4947718376021232482_y](https://github.com/user-attachments/assets/8ecd6a2d-e922-49d2-b2aa-5d8a9f4df658)

# P4IM0nTesting 🕷️💀 (v2.5)

**Advanced AI-Driven Pentesting Assistant for Burp Suite**

![photo_4947718376021232484_w](https://github.com/user-attachments/assets/00f97742-cb44-4514-8e84-d66123a8feef)
![photo_4947718376021232485_w](https://github.com/user-attachments/assets/8ad7c8ae-c722-416c-94f2-d08e46fe6f67)


## 🚀 Overview
**P4IM0nTesting** is a powerful Burp Suite extension capable of analyzing HTTP requests and automatically generating **20+ targeted attack vectors** using advanced AI models (**Gemini 1.5** & **ChatGLM-4**). Wrapped in a stunning **Cyberpunk UI**, it acts as your automated Red Team sidekick.

## ✨ Key Features
*   🤖 **Multi-Brain AI**: Switch between **Google Gemini** and **ZhipuAI (ChatGLM)** instantly.
*   🔥 **Auto-Exploit**: Generates 20 custom payloads (SQLi, XSS, SSTI, etc.) based on the specific request context.
*   🕵️ **Passive Scout**: Silently detects leaked API Keys (AWS, Slack, Private Keys) in background responses.
*   🔓 **403 Bypass**: Automated bypass techniques for forbidden endpoints.
*   🎯 **Param Sniper**: Identifies critical parameters (id, admin, file) for focused testing.
*   📊 **Detailed Reports**: Exports full HTML mission reports with request/response evidence.
*   🎨 **Cyberpunk UI**: Neon aesthetics for the elite hacker experience.

## 🛠️ Installation
1.  **Requirements**:
    *   Burp Suite (Community or Pro).
    *   **Jython Standalone JAR (2.7)** loaded in *Extender > Options*.
2.  **Load Extension**:
    *   Go to *Extender > Extensions > Add*.
    *   Select `Extension type: Python`.
    *   Select the `gemini_auto_exploit.py` file.
    *   Click *Next*. You should see the Cyberpunk banner in the Output tab.

## 💻 Usage
1.  **Initialize**:
    *   Go to the **P4IM0nTesting** tab.
    *   Select your AI Agent (`Gemini` or `ChatGLM`).
    *   Paste your **API Key** and click `[INIT]`.
2.  **Auto-Hack**:
    *   In *Proxy* or *Repeater*, **Right-Click** any request.
    *   Select `>> P4IM0nTesting: AUTO-EXPLOIT`.
    *   Watch the **NetRunner Console** generate and execute vectors in real-time.
3.  **Manual Ops**:
    *   Use the `CHAT` bar to ask the AI for advice on specific vulnerabilities.
    *   Click `HTML REPORT` to save your findings.

## ⚠️ Disclaimer
Created for **authorized security testing** and educational purposes only. The authors are not responsible for misuse. Hack the planet responsibly. 🌍
