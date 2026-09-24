# 🎬 DubStream • LinkedIn Post & Demo Resources

Welcome! All generated video assets, HTML templates, technical conversation summaries, and your finalized LinkedIn status copy have been transferred directly into this repository folder (`c:\Users\user\Desktop\ehte\projects\dubstream_netflix_ai\DubStream`).

---

## 📱 LinkedIn Status (Ready to Copy & Paste)

```markdown
When I moved to Finland for my Master's at LUT University, I wanted to learn Finnish faster. 🇫🇮

Watching movies in Finnish is one of the best ways to pick up everyday phrases, cadence, and vocabulary. But for non-native speakers, constantly switching focus between subtitles and audio breaks the immersion.

So I built a real-time solution: 

Introducing 𝐃𝐮𝐛𝐒𝐭𝐫𝐞𝐚𝐦 🎬 — an end-to-end, low-latency streaming pipeline that ingests video audio, translates spoken dialogue, and auto-dubs it into natural Finnish speech while generating synchronized subtitles in real-time.

Here is how the real-time inference pipeline works under the hood:

1️⃣ 𝐀𝐮𝐝𝐢𝐨 𝐈𝐧𝐠𝐞𝐬𝐭𝐢𝐨𝐧 & 𝐂𝐡𝐮𝐧𝐤𝐢𝐧𝐠: The browser captures video audio streams via the Web Audio API and transmits 16kHz PCM chunks over bi-directional WebSockets.
2️⃣ 𝐒𝐩𝐞𝐞𝐜𝐡 𝐑𝐞𝐜𝐨𝐠𝐧𝐢𝐭𝐢𝐨𝐧 (𝐒𝐓𝐓): Powered by OpenAI Whisper with Voice Activity Detection (VAD) to isolate spoken dialogue and generate intermediate timestamps.
3️⃣ 𝐍𝐞𝐮𝐫𝐚𝐥 𝐓𝐫𝐚𝐧𝐬𝐥𝐚𝐭𝐢𝐨𝐧 (𝐍𝐌𝐓): Translates English dialogue into Finnish, optimizing for natural spoken phrasing and timing constraints.
4️⃣ 𝐕𝐨𝐢𝐜𝐞 𝐒𝐲𝐧𝐭𝐡𝐞𝐬𝐢𝐬 & 𝐒𝐲𝐧𝐜𝐡𝐫𝐨𝐧𝐢𝐳𝐚𝐭𝐢𝐨𝐧: Employs edge-tts neural voice synthesis (fi-FI) combined with dynamic WebVTT subtitle alignment, streaming dubbed audio back to the client buffer with ~118ms latency.

💡 𝐖𝐡𝐚𝐭’𝐬 𝐧𝐞𝐱𝐭 (𝐯𝟐.𝟎 𝐑𝐨𝐚𝐝𝐦𝐚𝐩):
• Multi-speaker voice cloning (preserving the original actor's voice pitch and emotion in Finnish)
• Speaker diarization for multi-actor scenes
• Fully offline local LLM / NMT models for privacy-preserving, zero-cloud processing

🚀 𝐖𝐨𝐫𝐤𝐢𝐧𝐠 𝐥𝐢𝐯𝐞 𝐝𝐞𝐦𝐨 𝐜𝐨𝐦𝐢𝐧𝐠 𝐬𝐨𝐨𝐧! 

Check out the open-source repository on GitHub:
👉 https://github.com/ehtesum/DubStream

I'd love to hear your thoughts, feedback, or suggestions on optimizing real-time audio buffering! 

#MachineLearning #SpeechSynthesis #WhisperAI #Python #WebSockets #AI #SoftwareEngineering #Finland #EdTech #NLP #DeepLearning #OpenSource
```

---

## 📹 Video Assets in This Repository

All video versions have been converted to standard H.264 MP4 (playable in VLC and ready for LinkedIn upload) and are stored in the [`./Demo_Package/`](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/) directory:

| File Name | Format | Description | File Link |
| :--- | :--- | :--- | :--- |
| **`DubStream_Demo_Recording.mp4`** | MP4 (H.264) | **Final minimal white demo** (inside player bar only, no bottom mixer, clean cursor, simplified footer) | [Open MP4](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/DubStream_Demo_Recording.mp4) |
| **`DubStream_Demo_Inside_Bar_Only.mp4`** | MP4 (H.264) | Identical to final minimal white demo | [Open MP4](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/DubStream_Demo_Inside_Bar_Only.mp4) |
| **`DubStream_Demo_Previous_White.mp4`** | MP4 (H.264) | Previous white demo (includes the dual audio track mixer sliders below player) | [Open MP4](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/DubStream_Demo_Previous_White.mp4) |
| **`DubStream_Demo_Previous_Slate.mp4`** | MP4 (H.264) | Previous dark slate engineering theme demo | [Open MP4](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/DubStream_Demo_Previous_Slate.mp4) |
| **`DubStream_Demo_Recording.webp`** | Animated WebP | Lightweight browser-native animation format | [Open WebP](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/DubStream_Demo_Recording.webp) |
| **`DubStream_Demo_Screenshot.png`** | PNG (High-Res) | Static snapshot of the running interface for thumbnail / preview | [Open PNG](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/DubStream_Demo_Screenshot.png) |

---

## 🎨 Editable HTML Templates (Customize & Re-record)

If you would like to edit how the UI looks before re-recording:

1. **[`demo_template.html`](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/demo_template.html)**:
   * **Style:** Pure white background (`#ffffff`), 100% Vanilla CSS (no Tailwind dependency).
   * **Controls:** Transport bar inside video viewport, dual broadcast subtitles (English / Finnish), synchronized `python app.py` console.
   * **How to use:** Open in your editor, change any CSS or markup, and double-click to view immediately in Chrome/Edge/Firefox.

2. **[`demo_template_slate.html`](file:///c:/Users/user/Desktop/ehte/projects/dubstream_netflix_ai/DubStream/Demo_Package/demo_template_slate.html)**:
   * **Style:** Dark slate engineering palette (`#0f172a` Slate-900 / `#1e293b` Slate-800).
   * **Controls:** Full engineering layout with metrics and live stdout terminal.

---

## 💬 Summary of Generated Chats & Evolution

Here is the chronological progression and architectural context from the previous chat session (`649e7cc8-88fd-44df-a73c-55e759f71b16`):

1. **Initial Concept & Inspection**:
   * Analyzed the DubStream GitHub repository (`ehtesum/DubStream`), identifying the two-stage inference architecture: Stage 1 (Voice Profile / Tone Extraction) and Stage 2 (Tone-Matched Dubbing & Subtitle Synthesis).
2. **First Showcase (Sci-Fi / Synthwave UI)**:
   * Generated an animated card UI with glowing waveforms and neon badges.
   * **User Feedback:** *"change the video demo. its looks like totally ai."*
3. **Second Iteration (Real Localhost Developer UI)**:
   * Extracted actual template code from `DubStream/templates/player.html` and `DubStream/static/style.css`.
   * Recorded a realistic desktop view of `localhost:5000` with active terminal logs (`app.py`), WebSocket chunk dispatching, and latency meters (~118ms).
4. **Third Iteration (Non-Vibe Coded / Clean Engineering UI)**:
   * **User Feedback:** *"change backgroud color. make the ui look not vibe coded"*
   * Removed all neon gradients, glowing borders, and floating cards. Adopted a solid dark slate engineering theme with broadcast-standard subtitles.
5. **Fourth Iteration (Pure White Background & Vanilla CSS)**:
   * **User Feedback:** *"background wil be white. skip the tailwind css"*
   * Replaced the dark theme with pure white (`#ffffff`) canvas and 100% native Vanilla CSS.
   * Removed synthetic cursor click markers.
   * Simplified footer to strictly: `DubStream — working live demo coming soon.`
6. **Fifth Iteration (Inside Player Bar Only)**:
   * **User Feedback:** *"remove the playback bar at the bottom. only the inside player bar is enough"*
   * Removed the external audio mixer sliders below the video viewport, keeping only the internal player seekbar.
   * Re-encoded to H.264 MP4 (`DubStream_Demo_Recording.mp4`) for universal playback in VLC and LinkedIn.
7. **Workspace Packaging**:
   * Organized all templates, videos, and documentation into `Demo_Package` and mirrored into the active `DubStream` workspace.

---

## 📌 Posting Tips for LinkedIn
* **Native Video Upload:** Upload `DubStream_Demo_Recording.mp4` directly as a native LinkedIn video file (do not link YouTube/external video) to maximize algorithmic feed reach and enable silent autoplay.
* **Target Audience:** Mentioning your Master's journey at LUT University and Finnish language acquisition creates a relatable hook for tech recruiters, engineers, and international students in the Nordics.
