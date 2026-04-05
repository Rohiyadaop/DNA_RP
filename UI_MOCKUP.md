# 🎨 BioGPT - Visual UI Mockup & Screenshots Guide

## 📱 **What BioGPT Looks Like**

### **Home Screen (Desktop View)**

```
┌─────────────────────────────────────────────────────────────────────┐
│ BioGPT - DNA AI Web Application                                     │
├─────────────────────────────────────────────────────────────────────┤
│                                                                     │
│  🧬 BioGPT • DNA AI Web Application                                │
│                                                                     │
│  Generate DNA sequences with NVIDIA Evo2                          │
│  from raw DNA or natural language ideas.                          │
│                                                                     │
│  Paste DNA, describe your intent, tune generation parameters,     │
│  and keep a local history of every run.                           │
│                                                                     │
│  ┌─────────────────────────────────────────────────────────────┐  │
│  │ Model: Evo2 40B  │  Modes: DNA + Prompt  │  History: 0 runs │  │
│  └─────────────────────────────────────────────────────────────┘  │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                     MAIN CONTENT AREA                              │
│                                                                     │
│  ┌─────────────────────────────┐  ┌──────────────────────────────┐ │
│  │    INPUT WORKSPACE          │  │   GENERATED OUTPUT           │ │
│  ├─────────────────────────────┤  ├──────────────────────────────┤ │
│  │ DNA │ PROMPT  (toggle)      │  │ Waiting for generation...    │ │
│  │                             │  │                              │ │
│  │ DNA Sequence or FASTA       │  │                              │ │
│  │ ┌─────────────────────────┐ │  │                              │ │
│  │ │ ATGCGTACGTTAGCCTAGGCTAA │ │  │                              │ │
│  │ │ GGCTAACCGTTA            │ │  │                              │ │
│  │ └─────────────────────────┘ │  │                              │ │
│  │ [Load example]              │  │                              │ │
│  │                             │  │                              │ │
│  │ 46 DNA bases detected       │  │                              │ │
│  │                             │  │                              │ │
│  │ ─────────────────────────── │  │                              │ │
│  │                             │  │                              │ │
│  │ Number of generated bases:  │  │                              │ │
│  │ [────── 120 ────────]       │  │                              │ │
│  │                             │  │                              │ │
│  │ Temperature:                │  │                              │ │
│  │ [────── 0.7 ────────]       │  │                              │ │
│  │                             │  │                              │ │
│  │ Top K:                      │  │                              │ │
│  │ [────── 4 ────────]         │  │                              │ │
│  │                             │  │                              │ │
│  │ ┌─────────────────────────┐ │  │ ┌────────────────────────────┐ │
│  │ │ Generate DNA Sequence   │ │  │ │ [Copy] [Download .txt]     │ │
│  │ └─────────────────────────┘ │  │ └────────────────────────────┘ │
│  └─────────────────────────────┘  └──────────────────────────────┘ │
│                                                                     │
├─────────────────────────────────────────────────────────────────────┤
│                        LOCAL HISTORY                               │
│                                                                     │
│  Last 8 Generations (Click to restore)                            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐             │
│  │ DNA          │  │ Prompt       │  │ DNA          │             │
│  │ Time: Now    │  │ Time: 2m ago │  │ Time: 5m ago │             │
│  │ Input:       │  │ Input:       │  │ Input:       │             │
│  │ ATGC...      │  │ promoter...  │  │ GCTA...      │             │
│  │ Generated: ...│ │ Generated: ...│ │ Generated: ...│             │
│  └──────────────┘  └──────────────┘  └──────────────┘             │
│                                                                     │
└─────────────────────────────────────────────────────────────────────┘
```

---

## 🎨 **After Generating (Colored Output)**

```
┌─────────────────────────────────────────────────────┐
│          GENERATED OUTPUT (STEP-BY-STEP)            │
├─────────────────────────────────────────────────────┤
│                                                     │
│  Input Type: DNA                                   │
│  Upstream Time: 1245 ms                            │
│  Model: Evo2 40B                                   │
│                                                     │
│  ┌────────────────────────────────────────────────┐ │
│  │ GENERATED DNA SEQUENCE                          │ │
│  │ (Color-Coded Bases: 256 bases generated)       │ │
│  ├────────────────────────────────────────────────┤ │
│  │                                                 │ │
│  │ ATGCGTACGTTAGCCTAGGCTAACCGTTAATGCGTACGTTAGCCT │ │
│  │ 🔵 🔴 🟢 🟡 🔵 🔴 🟢 🟡 🟢 🟢 🔵 🔴 🟢 🟡 🟣   │ │
│  │                                                 │ │
│  │ AGGCTAACCGTTAATGCGTACGTTAGCCTAGGCTAACCGTTAATG │ │
│  │ 🔴 🟢 🟡 🔵 🟢 🟡 🟣 🔵 🔵 🔴 🟢 🟡 🔵 🔴 🟢   │ │
│  │                                                 │ │
│  │ [More bases...]                                 │ │
│  │                                                 │ │
│  └────────────────────────────────────────────────┘ │
│                                                     │
│  ┌──────────────────────────────────────────────┐  │
│  │ [✓ Copied]         [Download .txt]           │  │
│  └──────────────────────────────────────────────┘  │
│                                                     │
└─────────────────────────────────────────────────────┘

Color Legend:
🔵 A (Adenine)   - Cyan  (Energy & Growth)
🔴 T (Thymine)   - Red   (Energy & Growth)
🟢 G (Guanine)   - Green (Strength & Resistance)
🟡 C (Cytosine)  - Yellow(Brain & Function)
```

---

## 📱 **Mobile View (Phone)**

```
┌──────────────────┐
│ BioGPT App       │
├──────────────────┤
│                  │
│ 🧬 BioGPT        │
│                  │
│ Generate DNA     │
│ with AI          │
│                  │
├──────────────────┤
│                  │
│ DNA │ Prompt ✓   │
│ ──────────────   │
│                  │
│ Paste DNA or     │
│ describe...      │
│ ┌──────────────┐ │
│ │ ATGCGTACG... │ │
│ │ ...          │ │
│ └──────────────┘ │
│                  │
│ Parameters:      │
│ Tokens: [120]    │
│ Temp:   [0.7]    │
│ Top K:  [4]      │
│                  │
│ [Generate DNA]   │
│                  │
├──────────────────┤
│                  │
│ Output:          │
│ ┌──────────────┐ │
│ │ Loading...   │ │
│ │ ⏳ 10 sec... │ │
│ └──────────────┘ │
│                  │
├──────────────────┤
│ History (5 runs) │
│ ┌──────────────┐ │
│ │ DNA • Now   │ │
│ │ ATGC...     │ │
│ └──────────────┘ │
│ ┌──────────────┐ │
│ │ Prompt • 2m │ │
│ │ promote... │ │
│ └──────────────┘ │
│                  │
└──────────────────┘
```

---

## ⚙️ **Prompt Mode Example**

```
┌─────────────────────────────────────────────────────┐
│         PROMPT MODE (Natural Language)              │
├─────────────────────────────────────────────────────┤
│                                                     │
│  DNA │ PROMPT ✓  (switched to prompt mode)         │
│                                                     │
│  Natural Language Prompt                            │
│  ┌──────────────────────────────────────────────┐  │
│  │ Design a GC-rich bacterial promoter sequence │  │
│  │ for synthetic biology experiments            │  │
│  │                                              │  │
│  │                                              │  │
│  └──────────────────────────────────────────────┘  │
│  [Load example]                                     │
│                                                     │
│  121 prompt characters                              │
│  ↓ Backend converts to DNA seed...                 │
│                                                     │
│  ─────────────────────────────────────────────     │
│  Parameters are same...                            │
│  [Generate DNA Sequence]                            │
│                                                     │
├─────────────────────────────────────────────────────┤
│  RESULT:                                            │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │ EVO2 SEED DERIVED FROM PROMPT              │    │
│  │ (What your words were converted to)        │    │
│  ├────────────────────────────────────────────┤    │
│  │ GCGCGCATGATGCGTACGTTAGCCTAGGCTAACTAATACAC │    │
│  │ 🟢 🟡 🟢 🟡 🔵 🔴 🔵 🔴 🟢 🟡 🔴 🟢 🟡 🔵  │    │
│  │ (48-640 bases: your description in DNA)    │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
│  ┌────────────────────────────────────────────┐    │
│  │ GENERATED DNA SEQUENCE (FROM YOUR PROMPT)  │    │
│  │ (What AI created based on your words)      │    │
│  ├────────────────────────────────────────────┤    │
│  │ GCGCGCATGATGCGTACGTTAGCCTAGGCTAACTAATACAC │    │
│  │ ATGCGTACGTTAGCCTAGGCTAACCGTTAATGCGTACGTAG │    │
│  │ 🟢 🟡 🟢 🟡 🔵 🔴 🔵 🔴 🟢 🟡...            │    │
│  │                                            │    │
│  │ [✓ Copy]  [Download .txt]                  │    │
│  └────────────────────────────────────────────┘    │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 💾 **Download & Copy Features**

```
COPY BUTTON:
┌──────────────────────┐
│ [Copy sequence]      │ ← Click
└──────────────────────┘
         ↓
┌──────────────────────┐
│ [✓ Copied]           │ ← Shows for 1.8 seconds
└──────────────────────┘
         ↓
      Ready to Paste!
┌──────────────────────┐
│ Ctrl+V in any app    │ ← Paste your DNA
│ ATGCGTACGTTA...      │
└──────────────────────┘


DOWNLOAD BUTTON:
┌──────────────────────┐
│ [Download .txt]      │ ← Click
└──────────────────────┘
         ↓
   FILE DOWNLOADED
┌──────────────────────┐
│ biogpt-evo2-         │
│ sequence.txt         │
│                      │
│ ATGCGTACGTTA...      │
│ GCTAGCTACGTT...      │
│ ATGCGTACGTTA...      │
└──────────────────────┘
         ↓
   Use in:
   • Research
   • Excel
   • Science Papers
   • Share with Team
```

---

## 📊 **History Feature Visual**

```
┌─────────────────────────────────────────────────────────┐
│              LOCAL HISTORY (Last 8 Runs)                │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  [Clear history]                                        │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ DNA          │  │ Prompt       │  │ DNA          │ │
│  │              │  │              │  │              │ │
│  │ 🕐 Just now  │  │ 🕐 2 mins ago│  │ 🕐 5 mins ago│ │
│  │              │  │              │  │              │ │
│  │ Input:       │  │ Input:       │  │ Input:       │ │
│  │ ATGC...      │  │ promoter...  │  │ gc-rich...   │ │
│  │ (3 lines)    │  │ (3 lines)    │  │ (3 lines)    │ │
│  │              │  │              │  │              │ │
│  │ Generated:   │  │ Generated:   │  │ Generated:   │ │
│  │ ATGCGTAC...  │  │ GCGCGCAT...  │  │ GCGCGCAT...  │ │
│  │ (shows 3     │  │ (shows 3     │  │ (shows 3     │ │
│  │  lines)      │  │  lines)      │  │  lines)      │ │
│  │              │  │              │  │              │ │
│  │ Click to     │  │ Click to     │  │ Click to     │ │
│  │ Load ↓       │  │ Load ↓       │  │ Load ↓       │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│      ↑ Click              ↑ Click          ↑ Click    │
│      Hover (lift up)                                   │
│                                                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│  │ DNA          │  │ DNA          │  │ [Empty Slot] │ │
│  │              │  │              │  │              │ │
│  │ 🕐 10m ago   │  │ 🕐 15m ago   │  │ Ready for    │ │
│  │              │  │              │  │ next run     │ │
│  │ Input: ...   │  │ Input: ...   │  │              │ │
│  │ Generated:...│  │ Generated:...│  │              │ │
│  └──────────────┘  └──────────────┘  └──────────────┘ │
│                                                         │
└─────────────────────────────────────────────────────────┘

What Happens When You Click:
┌─────────────────┐
│ Click History   │
│ Item            │
└────────┬────────┘
         ↓
┌──────────────────────────┐
│ • Input restores         │
│ • All parameters restore │
│ • Output shows again     │ ← Everything
│ • You can download again │    reloads
│ • Modify & regenerate    │
└──────────────────────────┘
```

---

## 🎨 **Color Coding Explained Visually**

```
YOUR GENERATED DNA:

A T G C A T G C A T G C A T G C
🔵 🔴 🟢 🟡 🔵 🔴 🟢 🟡 🔵 🔴 🟢 🟡 🔵 🔴 🟢 🟡

What Each Color Means:

┌─────────────────────────────────────────┐
│ 🔵 A (Adenine)                          │
│ Color: Cyan/Light Blue                  │
│ Role: Pairs with T                      │
│ Related: Energy metabolism              │
│ In Your Body: Muscles, energy           │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🔴 T (Thymine)                          │
│ Color: Red/Pink                         │
│ Role: Pairs with A                      │
│ Related: DNA structure integrity        │
│ In Your Body: Cell growth              │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🟢 G (Guanine)                          │
│ Color: Green                            │
│ Role: Pairs with C                      │
│ Related: Strength, disease resistance   │
│ In Your Body: Immune system            │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ 🟡 C (Cytosine)                         │
│ Color: Yellow                           │
│ Role: Pairs with G                      │
│ Related: Brain function, intelligence   │
│ In Your Body: Nervous system           │
└─────────────────────────────────────────┘

Visual Pattern Recognition:
┌─────────────────────────┐
│ 🔵 🔵 🔵 = Lots of A    │ Energy boost
│ 🟢 🟢 🟢 = Lots of G    │ Strong immunity
│ 🟡 🟡 🟡 = Lots of C    │ Smart genes
│ 🟢 🟡 🟢 🟡 = Balanced  │ Healthy
└─────────────────────────┘
```

---

## 🚀 **Step-by-Step Tutorial Flow**

```
USER JOURNEY:

1️⃣ LAND ON PAGE
┌──────────────────────┐
│ http://localhost:3000│
│ BioGPT loads        │
│ See instructions    │
└──────────────────────┘

2️⃣ CHOOSE MODE
┌──────────────────────┐
│ DNA │ PROMPT         │
│ ✓ DNA (default)     │
└──────────────────────┘

3️⃣ LOAD EXAMPLE
┌──────────────────────┐
│ [Load example]       │
│ Text fills auto     │
└──────────────────────┘

4️⃣ ADJUST PARAMETERS (Optional)
┌──────────────────────┐
│ Num Tokens: 120 (OK) │
│ Temperature: 0.7 (OK)│
│ Top K: 4 (OK)       │
│ (Keep defaults)     │
└──────────────────────┘

5️⃣ GENERATE
┌──────────────────────┐
│ [Generate DNA]       │
│ Click!              │
└──────────────────────┘

6️⃣ WAIT
┌──────────────────────┐
│ Loading Spinner     │
│ ⏳ Contacting       │
│    NVIDIA Evo2...   │
│ Time: 10-30 sec    │
└──────────────────────┘

7️⃣ SEE RESULTS
┌──────────────────────┐
│ Colored DNA appears │
│ 🔵🔴🟢🟡🔵🔴🟢🟡   │
│ (Your result)       │
└──────────────────────┘

8️⃣ ACTIONS
┌──────────────────────┐
│ [Copy sequence]      │
│ [Download .txt]      │
│ Scroll: See history  │
│ Click: Try again     │
└──────────────────────┘

9️⃣ HISTORY GROWS
┌──────────────────────┐
│ History now shows: 1 │
│ (Last 8 kept)       │
└──────────────────────┘
```

---

## 📈 **Loading & Response States**

```
STATE 1: Loading
┌──────────────────────────┐
│ GENERATED OUTPUT         │
├──────────────────────────┤
│                          │
│     ⏳ Loading Spinner    │
│     (spinning circle)    │
│                          │
│  Contacting NVIDIA       │
│  Evo2 and decoding a     │
│  fresh DNA sequence...   │
│                          │
│     (10-30 seconds)      │
│                          │
└──────────────────────────┘


STATE 2: Success
┌──────────────────────────┐
│ GENERATED OUTPUT         │
├──────────────────────────┤
│                          │
│ Input Type: DNA          │
│ Upstream Time: 1245 ms  │
│ Model Endpoint: ...      │
│                          │
│ ┌──────────────────────┐│
│ │ GENERATED SEQUENCE   ││
│ │ ATGCGTACGTTA...      ││
│ │ 🔵 🔴 🟢 🟡 🔵 🔴...   ││
│ └──────────────────────┘│
│                          │
│ [✓ Copy] [Download]     │
│                          │
└──────────────────────────┘


STATE 3: Error
┌──────────────────────────┐
│                          │
│ ❌ Error (Red Box)       │
│ NVIDIA API error:        │
│ Invalid API key          │
│                          │
│ Fix: Add key to .env     │
│                          │
└──────────────────────────┘
```

---

## 🎯 **User Journey Summary**

```
SIMPLE PATH: Load Example + Generate = 2 Minutes

INTERMEDIATE: Try Different Prompts = 5 Minutes

ADVANCED: Tune Parameters + Save = 10 Minutes

EXPERT: Deploy + Share = 30 Minutes
```

---

**This is what BioGPT looks like! Now go try it! 🚀**
