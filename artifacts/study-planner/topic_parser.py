"""
topic_parser.py — Extract a clean list of syllabus topics from raw text.
Uses Gemini API when available; falls back to a robust heuristic parser.
Includes aggressive OCR spell-fix for BTech/degree syllabi.
"""

import re
import os


def extract_topics(raw_text: str, api_key: str = "", model: str = "gemini-1.5-flash", max_topics: int = 120) -> list[str]:
    text = _fix_ocr(raw_text)
    heuristic = _heuristic_extract(text, max_topics)

    if api_key:
        try:
            llm = _llm_extract(text, api_key, model, max_topics)
            merged = _merge(heuristic, llm)
            return merged[:max_topics]
        except Exception:
            pass

    return heuristic[:max_topics]


# OCR fixer

def _fix_ocr(text: str) -> str:
    """Fix common OCR errors in BTech/degree syllabi."""

    char_fixes = [
        (r'\brn\b',   'm'),
        (r'\bvv\b',   'w'),
        (r'(?<=[a-z])1(?=[a-z])', 'l'),
        (r'(?<=[a-z])0(?=[a-z])', 'o'),
    ]
    for pat, rep in char_fixes:
        text = re.sub(pat, rep, text)

    word_fixes = {
        r'\bbexical\b':       'lexical',
        r'\blexlcal\b':       'lexical',
        r'\bLexlcal\b':       'Lexical',
        r'\bwnting\b':        'writing',
        r'\bwntten\b':        'written',
        r'\bBootstrappng\b':  'Bootstrapping',
        r'\bBootstraplng\b':  'Bootstrapping',
        r'\bBuffenng\b':      'Buffering',
        r'\bButfennag\b':     'Buffering',
        r'\bButfering\b':     'Buffering',
        r'\bBuffennng\b':     'Buffering',
        r'\bRecogaihon\b':    'Recognition',
        r'\bRecognihon\b':    'Recognition',
        r'\bRecognrtion\b':   'Recognition',
        r'\bSpecificahon\b':  'Specification',
        r'\bSpeclfication\b': 'Specification',
        r'\bSyntax\s+crror\b':    'Syntax error',
        r'\bSyntax\s+enor\b':     'Syntax error',
        r'\bhandlng\b':           'handling',
        r'\bhandllng\b':          'handling',
        r'\bGrammers\b':          'Grammars',
        r'\bGramrners\b':         'Grammars',
        r'\bDerivahon\b':         'Derivation',
        r'\bDenvation\b':         'Derivation',
        r'\bEhminahag\b':         'Eliminating',
        r'\bEliminaling\b':       'Eliminating',
        r'\bAmblguity\b':         'Ambiguity',
        r'\brecurslon\b':         'recursion',
        r'\bfactonng\b':          'factoring',
        r'\bfactorlng\b':         'factoring',
        r'\bParslng\b':           'Parsing',
        r'\bPredictlve\b':        'Predictive',
        r'\bRecurslve\b':         'Recursive',
        r'\bDescenl\b':           'Descent',
        r'\bPrunlng\b':           'Pruning',
        r'\bprecedenee\b':        'precedence',
        r'\bConstructlng\b':      'Constructing',
        r'\bcanonlcal\b':         'canonical',
        r'\btranslahon\b':        'translation',
        r'\btranslatlon\b':       'translation',
        r'\bdefinthons\b':        'definitions',
        r'\bdefinithons\b':       'definitions',
        r'\battnbuted\b':         'attributed',
        r'\battrlbuted\b':        'attributed',
        r'\bevaluahon\b':         'evaluation',
        r'\bevaluatlon\b':        'evaluation',
        r'\bEavlronments\b':      'Environments',
        r'\bEavlronrnents\b':     'Environments',
        r'\bIsSuCS\b':            'Issues',
        r'\borganivahon\b':       'organization',
        r'\borganizahon\b':       'organization',
        r'\borganisahon\b':       'organization',
        r'\ballocaton\b':         'allocation',
        r'\ballocatlon\b':        'allocation',
        r'\bstrategles\b':        'strategies',
        r'\bstratcgics\b':        'strategies',
        r'\bGencration\b':        'Generation',
        r'\bGeneratlon\b':        'Generation',
        r'\blntermediate\b':      'Intermediate',
        r'\blatermediate\b':      'Intermediate',
        r'\bQuadruoles\b':        'Quadruples',
        r'\bTrlples\b':           'Triples',
        r'\bGraphlcal\b':         'Graphical',
        r'\brepresentatlons\b':   'representations',
        r'\bThree\s*-\s*Adress\b': 'Three-Address',
        r'\bOptimizahon\b':       'Optimization',
        r'\bOptlmization\b':      'Optimization',
        r'\bOptmizahon\b':        'Optimization',
        r'\boptlmization\b':      'optimization',
        r'\bPnacipal\b':          'Principal',
        r'\bPrlncipal\b':         'Principal',
        r'\bindependenl\b':       'independent',
        r'\bgeneralor\b':         'generator',
        r'\bTargel\b':            'Target',
        r'\bSvatax\b':            'Syntax',
        r'\bSvntax\b':            'Syntax',
        r'\bCCCA\b':              '',
        r'\bKAL\b':               '',
        r'\banalysls\b':          'analysis',
        r'\bAnalysls\b':          'Analysis',
        r'\bCompller\b':          'Compiler',
        r'\bcompller\b':          'compiler',
        r'\bsynthesls\b':         'synthesis',
        r'\bSynthesls\b':         'Synthesis',
        r'\bsouree\b':            'source',
        r'\bprogam\b':            'program',
        r'\bcodo\b':              'code',
        r'\bRoie\b':              'Role',
        r'\bShifl\b':             'Shift',
        r'\bReduco\b':            'Reduce',
        r'\bOperalor\b':          'Operator',
        r'\bBollom\b':            'Bottom',
        r'\bHandie\b':            'Handle',
        r'\bRun\s*-\s*Timc\b':   'Run-Time',
        r'\bSouree\b':            'Source',
        r'\bStorago\b':           'Storage',
        r'\bLocai\b':             'Local',
        r'\bGlobai\b':            'Global',
        r'\bMachlne\b':           'Machine',
        r'\bDependenl\b':         'Dependent',
        r'\bdesiqn\b':            'design',
        r'\blssues\b':            'Issues',
        r'\blnput\b':             'Input',
    }

    for pat, rep in word_fixes.items():
        text = re.sub(pat, rep, text, flags=re.IGNORECASE if pat[0] != '(' else 0)

    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


# Heuristic extractor

# Module/unit header prefix: "Module-1", "Module -1 (Title)", "Unit 3:", etc.
# Also strips optional parenthesized title like "(Mobile Computing Architecture)"
_MODULE_PREFIX = re.compile(
    r'\b(?:Module|Unit|Chapter|Section|Part)\s*[-\u2013]?\s*\d+[IVX]*\s*[:\-]?\s*'
    r'(?:\([^)]+\)\s*)?',
    re.IGNORECASE,
)

# ALL-CAPS module title immediately following the header prefix
# e.g. "INTRODUCTION TO CLOUD COMPUTING" before the first real topic word
_CAPS_TITLE = re.compile(
    r'^[A-Z][A-Z\s\d&,/()\-]+(?=\s+[A-Za-z][a-z]|\s*$)'
)

# Primary topic separators:
#   en-dash / em-dash:            "Topic A \u2013 Topic B"
#   space-hyphen-Capital:         "Management -Word Processing"
#   space-hyphen-space:           "Topic A - Topic B"
#   word-hyphen-space-Capital:    "computing- Limitations"
_SEPARATOR = re.compile(
    r'\s*[\u2013\u2014]\s*'
    r'|\s+-(?=[A-Z])'
    r'|\s+-\s+'
    r'|(?<=\w)-\s+(?=[A-Z])',
)


def _heuristic_extract(text: str, max_topics: int) -> list[str]:
    # 1. Join soft line-wraps so wrapped topics become single strings
    text = re.sub(r'(?<!\n)\n(?!\n)', ' ', text)
    text = re.sub(r' {2,}', ' ', text)

    # 2. Split on primary dash separators to get topic groups
    parts = _SEPARATOR.split(text)

    topics = []
    for raw in parts:
        raw = raw.strip()
        if not raw:
            continue

        # Strip module/unit header prefix + optional parenthesized title
        raw = _MODULE_PREFIX.sub('', raw).strip()

        # Strip leading ALL-CAPS module title (e.g. "INTRODUCTION TO CLOUD COMPUTING")
        raw = _CAPS_TITLE.sub('', raw).strip()

        # Skip if entire chunk is still an ALL-CAPS label (module title)
        if re.match(r'^[A-Z0-9\s&,/()\-]+$', raw) and len(raw.split()) <= 8:
            continue

        # 3. Split on sentence boundaries (". Capital" = new main topic)
        sentence_parts = re.split(r'(?<=[.!?])\s+(?=[A-Z])', raw)

        for sp in sentence_parts:
            sp = sp.strip().strip('.-,;: ')
            if not sp or _MODULE_PREFIX.match(sp):
                continue

            # 4. Split on commas — these are secondary topic separators
            #    e.g. "Functions, Devices, Middleware and gateways" → 3 topics
            comma_parts = [c.strip().strip('.-;: ') for c in sp.split(',')]

            for cp in comma_parts:
                if not cp:
                    continue
                t = _clean(cp)
                if _is_valid(t):
                    topics.append(t)

    return _dedup(topics)


def _clean(s: str) -> str:
    s = re.sub(r'[^\w\s\-/().,&:\']', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip().strip('.-,;:')
    return s


def _is_valid(t: str) -> bool:
    if len(t) > 120:
        return False
    if re.match(r'^\d+$', t):
        return False
    # Allow short abbreviations like FDMA, IaaS, OFDM (3-5 chars, letter-only)
    if re.match(r'^[A-Za-z]{3,5}$', t):
        return len(t) >= 3
    if len(t) < 5:
        return False
    return True


def _dedup(topics: list[str]) -> list[str]:
    seen, result = set(), []
    for t in topics:
        key = t.lower().strip()
        if key not in seen and len(key) > 2:
            seen.add(key)
            result.append(t)
    return result


def _merge(a: list[str], b: list[str]) -> list[str]:
    combined = list(a)
    existing = {x.lower() for x in a}
    for t in b:
        if t.lower() not in existing:
            combined.append(t)
            existing.add(t.lower())
    return combined


# LLM extractor

def _llm_extract(text: str, api_key: str, model: str, max_topics: int) -> list[str]:
    import google.generativeai as genai
    import json

    genai.configure(api_key=api_key)
    m = genai.GenerativeModel(model)

    prompt = f"""
You are a BTech/degree syllabus parser. Extract ALL individual study topics from the syllabus text below.
The text may have OCR errors — use context to infer the correct topic names.
Return ONLY a JSON array of topic strings — no preamble, no explanation, no markdown.
Each topic should be a short clear phrase (3–15 words). Include every subtopic and concept.
Maximum {max_topics} items.

Syllabus text:
\"\"\"
{text[:4000]}
\"\"\"

Return format: ["Topic 1", "Topic 2", ...]
"""
    resp = m.generate_content(prompt)
    raw  = resp.text.strip()
    raw  = re.sub(r'^```json\s*|^```\s*|```$', '', raw, flags=re.MULTILINE).strip()
    topics = json.loads(raw)
    if not isinstance(topics, list):
        return []
    return [str(t).strip() for t in topics if t and isinstance(t, str)]
