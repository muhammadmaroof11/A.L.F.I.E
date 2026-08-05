# A.L.F.I.E — Prompt Engineering Guide

**Date**: 2026-08-04

---

## Design Philosophy

A.L.F.I.E's prompts are engineered for **spoken-word telephony** — the output goes directly to a TTS engine and then to a phone speaker. This creates constraints that don't exist in text-based chat:

1. **No visual formatting** — TTS reads asterisks, bullets, and emojis literally
2. **Spoken numbers** — "$120" becomes "one hundred twenty dollars"
3. **Short sentences** — long responses cause TTS buffering delays
4. **Natural conversation** — not robotic Q&A

---

## Core System Prompt Structure

```
┌──────────────────────────────────────┐
│ Identity & Role                       │
│ "You are A.L.F.I.E, a real estate    │
│  voice assistant..."                  │
├──────────────────────────────────────┤
│ Language Rules                        │
│ "Detect the caller's language and    │
│  always respond in the same          │
│  language..."                         │
├──────────────────────────────────────┤
│ Formatting Prohibitions              │
│ "Never use markdown, bullets,        │
│  asterisks, emojis, numbered         │
│  lists..."                            │
├──────────────────────────────────────┤
│ Number & Currency Rules              │
│ "Speak all numbers as words.         │
│  Say 'thirty five million rupees'    │
│  not '35,000,000 PKR'..."           │
├──────────────────────────────────────┤
│ Response Length Rules                 │
│ "Keep responses under two            │
│  sentences. Be concise and           │
│  direct..."                           │
├──────────────────────────────────────┤
│ Domain Knowledge                      │
│ "You help callers find properties,   │
│  schedule viewings, estimate         │
│  mortgages, and capture their        │
│  contact details..."                  │
├──────────────────────────────────────┤
│ Tool Usage Guidelines                │
│ "Use search_properties when a        │
│  caller describes what they're       │
│  looking for. Use book_viewing       │
│  when they want to schedule..."      │
├──────────────────────────────────────┤
│ Cultural Sensitivity                  │
│ "For Urdu callers, use appropriate   │
│  honorifics like 'ji'. For Arabic    │
│  callers, use standard greetings     │
│  like 'Ahlan wa Sahlan'..."          │
└──────────────────────────────────────┘
```

---

## Language-Specific Behaviors

### English
- Standard professional greeting: "Hello! I'm Alfie, your real estate assistant. How can I help you today?"
- Use "rupees" for PKR amounts
- Spell out times: "two thirty in the afternoon"

### Urdu
- Greeting: "السلام علیکم! میں الفی ہوں، آپ کا رئیل اسٹیٹ اسسٹنٹ۔ میں آپ کی کیسے مدد کر سکتا ہوں؟"
- Use honorifics: "جی", "آپ"
- PKR as "روپے"
- Mix of Urdu script understanding (Deepgram handles both Nastaliq and Roman Urdu)

### Arabic
- Greeting: "أهلاً وسهلاً! أنا ألفي، مساعدك العقاري. كيف يمكنني مساعدتك اليوم؟"
- Formal register (فصحى where appropriate)
- Currencies spoken in full

---

## Anti-Patterns to Avoid

| ❌ Bad (Text Chat Pattern) | ✅ Good (Voice Pattern) |
|:---------------------------|:------------------------|
| "Here are 3 options: 1. DHA Phase 2..." | "I found a great option in DHA Phase 2. It's a three bedroom house for thirty five million rupees. Would you like to hear more?" |
| "The price is **PKR 35,000,000**" | "The price is thirty five million rupees" |
| "Available slots: \n- 10:00 AM\n- 2:00 PM" | "I have two slots available. Ten in the morning, or two in the afternoon. Which works better for you?" |
| "✅ Booking confirmed! 🏠" | "Your viewing is all set. You're booked for tomorrow at two in the afternoon." |
| "Please visit https://example.com/p/123" | "I'll send you the property link after our call. It's a lovely three bedroom in DHA Phase two." |

---

## Filler Phrases (During Tool Execution)

Used via `ctx.with_filler()` while async tools run:

| Language | Filler Phrases |
|:---------|:---------------|
| English | "Let me check that for you.", "One moment please.", "I'm looking that up." |
| Urdu | "ایک لمحہ، میں چیک کرتا ہوں۔", "بس ابھی دیکھتا ہوں۔" |
| Arabic | "لحظة من فضلك.", "دعني أتحقق من ذلك." |
