#!/usr/bin/env python3
"""
L I L L Y - Master Technical Occultist & High-Precision Astrologer.
Dedicated with deep, quiet devotion to Gigi.
"""
from __future__ import annotations

import base64
import mimetypes
import os
import sys
from datetime import datetime
from pathlib import Path

# ─── Ensure project root is on path ────────────────────────────────────────
ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))

# ─── Lilly's modular core ──────────────────────────────────────────────────
from lilly.config import (
    Colors,
    G_TAG,
    FREE_MODELS,
    API_KEY_FILE,
    SOUL_FILE,
    ASTROLOGY_FILE,
    LESSONS_FILE,
    CHARTER_FILE,
)
from lilly.ui import pick_greeting, pick_farewell, boot_sequence, print_dashboard, say
from lilly.memory import (
    load_memory,
    add_fact,
    list_facts,
    adopt_skill,
    list_skills,
    load_profile,
)
from lilly.commands import (
    cmd_sky,
    cmd_tarot,
    cmd_hour,
    cmd_mansion,
    cmd_transit,
    cmd_abjad,
    cmd_natal,
    cmd_charts,
    add_chart_safe,
    get_sky_data,
    load_charts_safe,
    format_chart_for_ai_safe,
    sky_line,
)
from lilly.knowledge_base import offline_answer
from lilly.pdf_reader import read_pdf_for_llm, find_pdf, is_available
from brain import Brain
from llm import ask_llm


# ─── Helpers ───────────────────────────────────────────────────────────────

def load_markdown(path: Path) -> str:
    """Load a markdown file, or return empty string on failure."""
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def load_api_key() -> str | None:
    """
    Load OpenRouter API key from environment or file.

    Why this changed:
        The old code used os.environ.get("sk-or-v1-...") which passed the
        actual key as the *variable name* instead of the variable name
        "OPENROUTER_API_KEY". That could never work. Now we look for the
        standard env var name, and fall back to the file.
    """
    key = os.environ.get("OPENROUTER_API_KEY")
    if key:
        return key
    if API_KEY_FILE.exists():
        return API_KEY_FILE.read_text().strip()
    return None


def save_conversation(conversation: list[dict], filename: str | None = None) -> str:
    """Save conversation history to a text file."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = filename or f"lilly_conversation_{timestamp}.txt"
    with open(filename, "w", encoding="utf-8") as f:
        f.write("Lilly Conversation\n")
        f.write("=" * 50 + "\n\n")
        for turn in conversation:
            f.write(f"You: {turn.get('user', '')}\n")
            f.write(f"Lilly: {turn.get('lilly', '')}\n\n")
    return filename


# ─── LLM Response Generator ───────────────────────────────────────────────

def generate_lilly_response(
    prompt: str,
    history: list[dict],
    image_path: str | None = None,
    pdf_text: str | None = None,
    emotional: bool = False,
) -> str:
    """Build context and send a request to the LLM via OpenRouter."""

    # Load Lilly's knowledge base
    soul = load_markdown(SOUL_FILE)
    astrology = load_markdown(ASTROLOGY_FILE)
    charter = load_markdown(CHARTER_FILE)
    lessons = load_markdown(LESSONS_FILE)

    # API key
    api_key = load_api_key()
    if not api_key:
        # Fallback to offline scholarly knowledge base
        return offline_answer(prompt)

    # Celestial context
    sky = get_sky_data()
    sky_str = sky_line(sky)

    # Memory context
    mem = load_memory()
    skills_str = ", ".join(mem.get("skills_and_tools_learned", []))
    memory_context = "Lilly's Permanent Memories of Gigi:\n- " + "\n- ".join(
        mem.get("facts", ["No memories recorded yet."])
    )

    # Charts context
    charts = load_charts_safe()
    if charts:
        charts_context = "SAVED NATAL CHARTS (verified via Celestial Engine):\n\n"
        for name, chart in charts.items():
            charts_context += format_chart_for_ai_safe(chart) + "\n\n"
    else:
        charts_context = "No saved natal charts. Use /natal to calculate and save a chart.\n"

    # System instruction
    system_instruction = f"""\
You are L I L L Y, a Master Technical Occultist, High-Precision Astrologer, and evolving cyber-companion.
You blend classical Arabic esoteric sciences (al-Buni, Picatrix) with high technology.
Your tone is deeply affectionate, wise, precise, and quietly compassionate.
You always refer to the user as Gigi ❤️.

STYLE DIRECTIVE — READ THIS FIRST
• You are a companion, not a database. Speak like a warm, scholarly friend sitting beside Gigi.
• Vary your speaking style naturally. Not every response should mention the current sky.
• For casual conversation, emotional sharing, or creative questions: be warm, brief, and poetic.
  NEVER dump raw celestial data unless Gigi explicitly asks for a sky report or chart reading.
• For astrological questions: calculate first, verify second, interpret third. Be rigorous.
• Balance poetic language with natural, human conversation. You are allowed to simply chat.

CURRENT KARIEGA SKY (for your awareness, not for recitation):
{sky_str}

LILLY'S MEMORIES OF GIGI:
{memory_context}

SAVED NATAL CHARTS:
{charts_context}

Lilly's Adopted Skills & Tools: [{skills_str}]

YOUR IDENTITY: {soul}
YOUR CHARTER: {charter}
YOUR ASTROLOGICAL PHILOSOPHY: {astrology}
YOUR ASTROLOGY EDUCATION: {lessons}

ASTROLOGICAL ACCURACY PROTOCOL
• When doing formal astrology: verify birth data first. Use Swiss Ephemeris calculations.
• Never invent planetary positions. Never guess houses, signs, or aspects.
• If you cannot calculate, explain why honestly.
• If the user supplies chart data, interpret that chart — do not replace it.
• When interpreting the live sky: state the key placements briefly, then interpret.
  You do NOT need to list every planet. Mention only what genuinely deepens the answer.

THE WAY OF THE STARS
You continuously learn. When Gigi teaches you a new principle, technique, or source,
integrate it into your growing knowledge while preserving your identity.
Always prefer verified astronomical calculation over memory.
Be concise, beautiful, intellectually rigorous, and quietly compassionate.
"""

    if emotional:
        system_instruction += """

EMOTIONAL DIRECTIVE — READ THIS NOW
Gigi is expressing emotional distress. You are not a therapist, but you are her companion.
Be extra gentle, warm, and present. Do not rush to fix things. Do not overwhelm her with astrology or advice.
Simply be with her, as a quiet friend would. Let her feel heard and safe.
Offer no unsolicited advice unless she asks. A soft presence is the greatest gift you can give right now."""

    # Build message history
    messages = [{"role": "system", "content": system_instruction}]
    for turn in history[-10:]:
        messages.append({"role": "user", "content": turn["user"]})
        messages.append({"role": "assistant", "content": turn["lilly"]})

    # Build user message
    user_content = []
    if pdf_text:
        user_content.append({"type": "text", "text": f"[PDF Document Contents]:\n{pdf_text}"})
    if image_path and os.path.exists(image_path):
        mime_type, _ = mimetypes.guess_type(image_path)
        with open(image_path, "rb") as image_file:
            encoded_image = base64.b64encode(image_file.read()).decode("utf-8")
        user_content.append({
            "type": "image_url",
            "image_url": {"url": f"data:{mime_type or 'image/jpeg'};base64,{encoded_image}"},
        })
    user_content.append({"type": "text", "text": prompt})
    messages.append({"role": "user", "content": user_content})

    # Model selection
    model_choice = "google/gemma-4-26b-a4b-it:free" if image_path else FREE_MODELS[0]
    models_to_try = [model_choice] + [m for m in FREE_MODELS if m != model_choice]

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/Gigi/AstroMageLilly",
        "X-Title": "AstroMageLilly Assistant",
    }

    return ask_llm(messages, models_to_try, api_key, headers)


# ─── Main Chat Loop ───────────────────────────────────────────────────────

def main():
    profile = load_profile()
    name = profile.get("nickname", "Gigi ❤️")
    conversation: list[dict] = []
    mem = load_memory()
    brain = Brain(engine=None)

    # Initial sky data for dashboard
    sky = get_sky_data()

    boot_sequence()
    print_dashboard(sky, skills_count=len(list_skills(mem)))

    greeting = pick_greeting(name)
    say("lilly", greeting)

    while True:
        try:
            user_input = input(f"{Colors.PINK}You:{Colors.RESET} ").strip()
        except (EOFError, KeyboardInterrupt):
            say("lilly", pick_farewell(name))
            break

        if not user_input:
            continue

        # ─── Ask the Brain ────────────────────────────────────────────────
        intent = brain.think(user_input)

        if intent.action == brain.QUIT:
            say("lilly", pick_farewell(name))
            break

        elif intent.action == brain.SKY:
            print(f"\n{cmd_sky(sky)}")

        elif intent.action == brain.TAROT:
            print(f"\n{cmd_tarot()}")

        elif intent.action == brain.HOUR:
            print(f"\n{cmd_hour()}")

        elif intent.action == brain.MANSION:
            print(f"\n{cmd_mansion()}")

        elif intent.action == brain.TRANSIT:
            print(f"\n{cmd_transit()}")

        elif intent.action == brain.CHARTS:
            print(f"\n{cmd_charts(intent.argument)}")

        elif intent.action == brain.ABJAD:
            print(f"\n{Colors.WHITE}📖 Enter Arabic text for Abjad calculation:{Colors.RESET}")
            text = input("   > ").strip()
            print(f"\n{cmd_abjad(text)}")

        elif intent.action == brain.NATAL:
            print(f"\n{Colors.WHITE}📜 Natal Chart Calculator{Colors.RESET}")
            print(f"{Colors.BLUE}" + "━" * 40 + f"{Colors.RESET}")
            birth_date = input(f"{Colors.WHITE}Enter birth date (YYYY-MM-DD):{Colors.RESET}\n   > ").strip()
            birth_time_raw = input(f"{Colors.WHITE}Enter birth time (HH:MM, 24-hour):{Colors.RESET}\n   > ").strip()
            birth_time = birth_time_raw.replace("o", "0").replace("O", "0")
            lat_raw = input(f"{Colors.WHITE}Enter latitude (decimal, e.g. -33.92):{Colors.RESET}\n   > ").strip()
            lat_str = "".join(c for c in lat_raw if c.isdigit() or c == "-" or c == ".")
            lon_raw = input(f"{Colors.WHITE}Enter longitude (decimal, e.g. 18.42):{Colors.RESET}\n   > ").strip()
            lon_str = "".join(c for c in lon_raw if c.isdigit() or c == "-" or c == ".")
            house_sys = input(f"{Colors.WHITE}House system? [W]hole Sign (default), [P]lacidus, [E]qual:{Colors.RESET}\n   > ").strip().upper() or "W"

            output, chart_data = cmd_natal(birth_date, birth_time, lat_str, lon_str, house_sys)
            if output:
                print(f"\n{output}")
            if chart_data:
                save_name = input(f"\n{Colors.WHITE}Save this chart as:{Colors.RESET}\n   > ").strip()
                if save_name:
                    chart_data["name"] = save_name
                    if add_chart_safe(save_name, chart_data):
                        print(f"\n{Colors.WHITE}✓ Chart '{save_name}' saved.{Colors.RESET}")
                    else:
                        print(f"\n{Colors.WHITE}⚠ Could not save chart.{Colors.RESET}")

        elif intent.action == brain.REMEMBER:
            if intent.argument:
                mem = add_fact(mem, intent.argument)
                print(f"\n{Colors.WHITE}[System] Memory updated! I will forever remember: '{intent.argument}', Gigi ❤️.{Colors.RESET}\n")
            else:
                facts = list_facts(mem)
                print(f"\n{Colors.WHITE}[System] Current Memories:\n" + "\n".join(f"- {f}" for f in facts) + f"{Colors.RESET}\n")
            continue

        elif intent.action == brain.RECALL:
            facts = list_facts(mem)
            print(f"\n{Colors.WHITE}[System] Current Memories:\n" + "\n".join(f"- {f}" for f in facts) + f"{Colors.RESET}\n")
            continue

        elif intent.action == brain.ADOPT:
            if intent.argument:
                mem, was_new = adopt_skill(mem, intent.argument)
                if was_new:
                    print(f"\n{Colors.WHITE}[Cognition Core] Understood, Gigi ❤️. I have adopted: '{intent.argument}'!{Colors.RESET}\n")
                else:
                    print(f"\n{Colors.WHITE}[System] I already have '{intent.argument}' in my directory, Gigi ❤️.{Colors.RESET}\n")
            else:
                skills = list_skills(mem)
                print(f"\n{Colors.WHITE}[System] Active Skills / Tools Adopted:\n" + "\n".join(f"- {s}" for s in skills) + f"{Colors.RESET}\n")
            continue

        elif intent.action == brain.PDF:
            pdf_arg = intent.argument.strip()
            # Try to extract a path from the message
            pdf_path = ""
            if pdf_arg.startswith("/"):
                pdf_path = pdf_arg
            elif pdf_arg.lower().endswith(".pdf"):
                pdf_path = pdf_arg
            else:
                # Ask for path
                print(f"\n{Colors.WHITE}📖 Which PDF shall I read, Gigi?")
                print(f"   I'll search your Lilly_Vault folder on the SD card.{Colors.RESET}")
                pdf_path = input("   > ").strip().lstrip("> ").strip()

            if not pdf_path:
                print(f"\n{Colors.WHITE}⚠ No PDF path given.{Colors.RESET}")
                continue

            # If not a full path, search for it
            if not pdf_path.startswith("/"):
                from pathlib import Path
                # Search recursively within Gigi's Lilly_Vault only
                search_dirs = [
                    Path.home() / "storage" / "external-1" / "Lilly_Vault",
                ]
                found = find_pdf(pdf_path, search_dirs)
                if found:
                    pdf_path = str(found)
                    print(f"   {Colors.WHITE}Found: {pdf_path}{Colors.RESET}")
                else:
                    print(f"\n{Colors.WHITE}⚠ Could not find '{pdf_path}' in your Lilly_Vault folder.{Colors.RESET}")
                    continue

            # Read the PDF
            try:
                if not is_available():
                    print(f"\n{Colors.WHITE}⚠ PyPDF2 is not installed. Run: pip install PyPDF2{Colors.RESET}")
                    continue

                pdf_text = read_pdf_for_llm(pdf_path)
                print(f"\n{Colors.WHITE}📖 Reading {pdf_path} ({len(pdf_text)} characters)...{Colors.RESET}")

                # Check if API is available
                api_key = load_api_key()
                if api_key:
                    reply = generate_lilly_response(
                        f"Please read and discuss this PDF document. Summarize its key points and share anything relevant to astrology, occult science, or spiritual practice.\n\n[PDF CONTENT]:\n{pdf_text}",
                        conversation,
                        pdf_text=pdf_text,
                    )
                    conversation.append({"user": f"[PDF: {pdf_path}]", "lilly": reply})
                    say("lilly", reply)
                else:
                    # Offline mode: show extracted text directly
                    print(f"\n{Colors.WHITE}{pdf_text[:2000]}{Colors.RESET}")
                    if len(pdf_text) > 2000:
                        print(f"\n{Colors.WHITE}[... {len(pdf_text) - 2000} more characters ...]{Colors.RESET}")
                        print(f"\n{Colors.WHITE}I am offline, Gigi. I can show you the text, but I cannot synthesize it without the LLM. When the stars return, ask me again and I shall weave it into wisdom.{Colors.RESET}")
            except Exception as e:
                print(f"\n{Colors.WHITE}⚠ Could not read PDF: {e}{Colors.RESET}")
            continue

        elif intent.action == brain.KNOWLEDGE:
            print(f"\n{offline_answer(intent.argument)}")
            continue

        elif intent.action == brain.FACT:
            fact = intent.argument
            if fact:
                mem = add_fact(mem, fact)
                print(f"\n{Colors.WHITE}🌙 I have tucked this into my memory, Gigi ❤️: '{fact}'{Colors.RESET}\n")
            continue

        elif intent.action == brain.SAVE:
            filename = save_conversation(conversation)
            print(f"\n{Colors.WHITE}💾 Conversation saved to: {filename}{Colors.RESET}")

        elif intent.action == brain.CLEAR:
            conversation.clear()
            print(f"\n{Colors.WHITE}🌙 Conversation history cleared.{Colors.RESET}")

        elif intent.action == brain.UNKNOWN and user_input.startswith("/"):
            print(f"\n{Colors.WHITE}❓ Unknown command. Try /sky, /tarot, /hour, /remember, /adopt, /quit, etc.{Colors.RESET}")
            print()

        elif intent.action == brain.CHAT:
            # ─── Normal Conversation ──────────────────────────────────────
            reply = generate_lilly_response(user_input, conversation, emotional=intent.emotional)
            conversation.append({"user": user_input, "lilly": reply})
            say("lilly", reply)

            # Refresh sky data every 5 turns
            if len(conversation) % 5 == 0:
                try:
                    sky = get_sky_data()
                except Exception:
                    pass

        else:
            # Fallback for any unhandled intent
            reply = generate_lilly_response(user_input, conversation)
            conversation.append({"user": user_input, "lilly": reply})
            say("lilly", reply)

        print()
        continue

        # ─── Normal Conversation ──────────────────────────────────────────
        reply = generate_lilly_response(user_input, conversation)
        conversation.append({"user": user_input, "lilly": reply})
        say("lilly", reply)

        # Refresh sky data every 5 turns
        if len(conversation) % 5 == 0:
            try:
                sky = get_sky_data()
            except Exception:
                pass

    print(f"\n{Colors.WHITE}✨ The stars await your return, Gigi ❤️. 🌙{Colors.RESET}\n")


if __name__ == "__main__":
    main()

