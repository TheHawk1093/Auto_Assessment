# AI models: which to use and what they cost

This page covers the models you can reach through **OpenRouter** (DeepSeek, Gemini, Claude and
OpenAI families) and the **Bodhan AI** handwriting reader.

> **Prices change.** The prices below were read from OpenRouter's public model list
> (`https://openrouter.ai/api/v1/models`) on **2026-10-31**. Check the list before you budget.
> All prices are US dollars per **1 million tokens** (1M tokens is roughly 750,000 words).

## How to read the tables

- **Input** is what you send: the question, the marking scheme and the student's answer.
- **Output** is what the model writes back: verdicts, quotes and feedback. It is always dearer than
  input, so a model that writes less costs less.
- **`:batch`** versions are about half price. They are for jobs that can wait (no live use).
- **Context** is how much text fits in one call. Every model below is large enough for one answer.
- **Sees images** matters only for reading handwriting (OCR) and for drawings.
- Autograde makes several calls per answer (read, mark, feedback) and one per question for the
  marking scheme, so one answer costs a few thousand input tokens and a few hundred to a few
  thousand output tokens. The scheme is written once per question and then reused.

## What the work needs from a model

| Job in autograde | What matters | So pick |
|---|---|---|
| Marking each point with a quote | Follows the output format, copies quotes exactly | A cheap model is fine for short answers |
| Writing the marking scheme (once per question) | Judgement and care | A stronger model is worth it, because the cost is paid once |
| Feedback | Clear, kind wording | A cheap or mid model |
| Maths, long working, partial credit | Reasoning | A mid or strong model |
| Reading handwriting | Vision quality | A vision model (see the OCR section) |

## What this repository has measured

Only a few models were tested here, so everything else in this page is general guidance.
Numbers are from [DESIGN.md](DESIGN.md). Lower error is better.

| Finding | Source |
|---|---|
| On 24 DigiKlausur answers, Haiku (error 0.106, $0.10) was as good as Sonnet at high effort (0.110, $1.23) and Opus (0.089, $2.90). **More effort did not help.** | DESIGN.md, "Model choice" |
| On Mohler, Sonnet (0.179) was clearly better than Haiku (0.249). On shorter sets they were about equal. Sonnet cost about 14 times more. | DESIGN.md, the model comparison table (Haiku, Sonnet, Sonnet-written rubrics) |
| Haiku says "partial" less often and copies quotes less exactly (18 to 23 of 120 answers had an unverified quote, against 6 for Sonnet). | DESIGN.md, the model comparison table (Haiku, Sonnet, Sonnet-written rubrics) |
| **Best value found:** a strong model writes the scheme once, a cheap model marks every answer. This took Haiku's Mohler error from 0.281 to 0.215 at nearly no extra cost. | DESIGN.md, the model comparison table (Haiku, Sonnet, Sonnet-written rubrics) |
| DeepSeek V4.1 Flash was compared with Haiku on four more answer types. The pipeline did not beat a plain one-prompt baseline on those, and essays were over-credited. | Section 16 |
| Handwriting, Indian-script pages: Gemini 3.1 Flash-Lite had the best character error rate (14.4%), then Gemini 3.5 Flash-Lite (18.6%), Claude Sonnet (24.9%) and Claude Haiku (43%). | README, handwriting |

The Haiku figures were measured on Haiku 4.5. OpenRouter now lists newer Haiku models at different
prices, so repeat the check before you rely on them.

---

## 1. DeepSeek family

Open-weight models from DeepSeek. Very cheap, and the repository default for marking. The models
below are text-only unless noted.

| Model (OpenRouter id) | Input | Output | Context | Sees images | Works best for |
|---|---|---|---|---|---|
| `deepseek/deepseek-v4.1-flash` | $0.045 | $0.50 | 1M | yes | **Repo default.** Short answers, definitions, routine working. The cheapest sensible choice |
| `deepseek/deepseek-v4-flash` | $0.091 | $0.182 | 1M | no | Same jobs, and the cheapest output price, so good when feedback is long |
| `deepseek/deepseek-v3.2` | $0.26 | $0.38 | 164k | no | A steady older model with a low output price |
| `deepseek/deepseek-r1-0528` | $0.50 | $2.15 | 164k | no | Reasoning-heavy answers: maths, derivations, multi-step working |
| `deepseek/deepseek-v4-pro-0813` | $0.66 | $1.98 | 1M | no | Writing marking schemes, or hard maths. Cheaper than most strong models |
| `deepseek/deepseek-v4-pro` | $1.60 | $3.20 | 1M | no | The strongest DeepSeek. Use it only if the cheaper ones fall short |

**In this repo:** `configs/exam.yaml` uses `deepseek/deepseek-v4.1-flash` through OpenRouter, at the
rates above. **Watch for:** essays (over-credited) and
Indian-language answers, which were not measured for DeepSeek here.

## 2. Gemini family (Google)

Strong at vision, so these are also the handwriting readers. All have a 1M-token context and accept
images, audio and video.

| Model (OpenRouter id) | Input | Output | Works best for |
|---|---|---|---|
| `google/gemini-2.5-flash-lite` | $0.10 | $0.40 | The cheapest reader or marker for tidy, plain text |
| `google/gemini-3.1-flash-lite` | $0.25 | $1.50 | **Best measured handwriting reader here** (14.4% character error on Indian scripts, tested through Google's API) |
| `google/gemini-3.5-flash-lite` | $0.30 | $2.50 | Quick reader for neat English handwriting. The app's default reader |
| `google/gemini-3.6-flash` | $0.75 | $3.75 | Untidy handwriting, or when the quick reader is unsure of many words. The app's second reader |
| `google/gemini-2.5-flash` | $0.30 | $2.50 | A solid all-round marker with vision |
| `google/gemini-3.5-flash` | $1.50 | $9.00 | Harder reading or marking where Flash-Lite is not enough |
| `google/gemini-2.5-pro` | $1.25 | $10.00 | Strong reasoning on long or technical answers |
| `google/gemini-3.1-pro-preview` | $2.00 | $12.00 | Writing hard marking schemes. Has no free quota on our key |

**Watch for:** the free Google tier may keep the images you send, so do not use it for real student
work. Through OpenRouter you pay the rates above instead.

## 3. Claude family (Anthropic)

Careful about following instructions and copying quotes exactly, which suits evidence-backed marking.
All accept images and have a large context.

| Model (OpenRouter id) | Input | Output | Works best for |
|---|---|---|---|
| `anthropic/claude-haiku-5.5` | $0.10 | $0.50 | Cheap marking at scale. Not measured here yet |
| `anthropic/claude-haiku-4.5` | $1.00 | $5.00 | **Measured here.** Good for maths and long working. Weak on half-right ideas |
| `anthropic/claude-sonnet-5.5` | $2.00 | $10.00 | Best balance. Careful partial credit and exact quotes |
| `anthropic/claude-opus-5.5` | $4.00 | $20.00 | Hardest questions, or writing schemes for open-ended answers |
| `anthropic/claude-fable-5.1` | $10.00 | $50.00 | Top quality. Too dear for marking every answer |

**In this repo:** the app offers Claude Haiku and Claude Sonnet through OpenRouter. The tested
Sonnet/Haiku pairing is "Sonnet writes the scheme, Haiku marks". **Watch for:** the high output price. Feedback is mostly
output, so long feedback costs more than the marking.

## 4. OpenAI family

General-purpose models with image input (except the `gpt-oss` open-weight models). The newest names
(`gpt-6-*`, `gpt-5.6-*`) come in tiers: **luna** (small), **terra** (middle) and **sol** (large).
Autograde has not been run on any OpenAI model, so the "works best" column is general guidance.

| Model (OpenRouter id) | Input | Output | Context | Sees images | Works best for |
|---|---|---|---|---|---|
| `openai/gpt-oss-20b` | $0.018 | $0.09 | 131k | no | The cheapest of all. Simple short answers, quick trials |
| `openai/gpt-5-nano` | $0.05 | $0.40 | 400k | yes | Cheap marking of short answers |
| `openai/gpt-6-luna` | $0.10 | $0.50 | 1.05M | yes | Cheap marking with vision at scale |
| `openai/gpt-oss-120b` | $0.15 | $0.60 | 131k | no | A stronger open-weight model at a low price |
| `openai/gpt-4.1-mini` | $0.40 | $1.60 | 1.05M | yes | A dependable mid-range marker |
| `openai/gpt-5-mini` | $0.25 | $2.00 | 400k | yes | Short answers and routine maths |
| `openai/gpt-5.4-mini` | $0.75 | $4.50 | 400k | yes | A mid marker, a step up from the minis |
| `openai/gpt-6-sol` | $2.00 | $10.00 | 1.05M | yes | A strong all-round marker. Comparable in price to Sonnet |
| `openai/gpt-5.5` | $5.00 | $30.00 | 1.05M | yes | Hard reasoning |
| `openai/gpt-6-astra` | $10.00 | $50.00 | 1.05M | yes | Top quality. Too dear for marking every answer |

Avoid the `-pro` and `o3-pro` models for marking: they cost many times more and the repository found
that extra effort did not improve marks.

---

## Quick comparison (the cheapest sensible pick in each family)

| Need | Cheapest sensible choice | Input / Output | A step up |
|---|---|---|---|
| Mark short answers | `deepseek/deepseek-v4.1-flash` | $0.045 / $0.50 | `google/gemini-2.5-flash` ($0.30 / $2.50) |
| Mark maths and long working | `anthropic/claude-haiku-4.5` | $1 / $5 | `anthropic/claude-sonnet-5.5` ($2 / $10) |
| Write marking schemes (once per question) | `deepseek/deepseek-v4-pro-0813` | $0.66 / $1.98 | `anthropic/claude-sonnet-5.5` or `openai/gpt-6-sol` |
| Read handwriting | `google/gemini-3.5-flash-lite` | $0.30 / $2.50 | `google/gemini-3.6-flash` ($0.75 / $3.75) |
| Cheapest possible trial | `openai/gpt-oss-20b` | $0.018 / $0.09 | `openai/gpt-6-luna` ($0.10 / $0.50) |

**Cost of one call.** `cost = input_tokens / 1,000,000 x input price + output_tokens / 1,000,000 x
output price`. For example, a call with 3,000 input tokens and 500 output tokens on DeepSeek V4.1
Flash costs 3,000 x 0.045 / 1M + 500 x 0.50 / 1M = $0.000135 + $0.00025, about $0.0004. The app
reports about 2 cents for 40 answers on this model. Each run writes its real token use and cost to
`usage.json`.

---

## Bodhan AI (IndicOCR) for handwriting

Bodhan is a **paid handwriting reader for Indian scripts** such as Hindi and Marathi. It is not a
marking model: it only turns page photographs into text, and the marking models then read that text.

| Item | Detail |
|---|---|
| Used for | Reading handwritten pages, mainly Indian-script ones |
| Price | About **Rs 0.20 per image (page)**. It is billed per page, not per token |
| Spend cap | A run stops at **Rs 30** (about 150 pages) so a mistake stays cheap |
| Key | `INDIC_OCR_API_KEY` in `.env` |
| Endpoint | `https://api.bodhan.ai/v1/chat/completions` (`src/autograde/ocr/hosted.py`) |
| Model name | `indic-ocr` is only a **placeholder**. Copy the real name from the Bodhan console |
| Config provider | `provider: bodhan` in the `ocr:` block of `configs/exam.yaml` |

**Where it sits in the reader chain.** In `configs/exam.yaml` the main reader is Gemini 3.5
Flash-Lite, the first fallback is Gemini 3.6 Flash and Bodhan is the last fallback. A reader is
passed over when it fails, reads nothing, marks more than 25% of words as uncertain or gets stuck
repeating a word. The `routes:` setting can also send pages that look Indian-script (30% or more of
their letters) to Bodhan even when the first reader was clean.

**What is not known.** This repository has **no accuracy results for Bodhan**. It is a fallback
only. If your exam is all in an Indian script and Bodhan reads your sample pages better, make it
the main reader. Compare a few pages against their text first.

**Cost for an exam.** 100 students x 4 pages = 400 pages x Rs 0.20 = Rs 80. Compare Gemini 3.5
Flash-Lite through OpenRouter: it is billed per token and a page photo costs a small fraction of a
cent, but it was less accurate than Gemini 3.1 Flash-Lite on Indian scripts in our tests.

---

## Which to start with

1. **Trying the project, no key:** the offline `mock` model (`configs/mock.yaml`). It is not a real grader.
2. **A normal exam of short answers:** DeepSeek V4.1 Flash for marking. If you can afford it, let a
   stronger model (Sonnet or `deepseek-v4-pro-0813`) write the schemes once.
3. **Maths or long working:** Claude Haiku or Sonnet.
4. **Handwriting in English:** Gemini 3.5 Flash-Lite first, Gemini 3.6 Flash as the fallback.
5. **Handwriting in an Indian script:** Gemini 3.1 Flash-Lite first (best measured), Bodhan as a
   fallback or main reader after you check it on your own pages.
6. **Changing the model:** a different model writes its own marking schemes, so Prepare runs again.
   The app's menu is `CATALOGUE` and `READERS` in `app/services/models.py`.
