"""
topic_parser.py — Extract a clean list of syllabus topics from raw text.
Uses Gemini API when available; falls back to a robust heuristic parser.
Includes aggressive OCR spell-fix for BTech/degree syllabi.
"""

import re
import os


def extract_topics(raw_text: str, api_key: str = "", model: str = "gemini-1.5-flash", max_topics: int = 80) -> list[str]:
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


# ── OCR fixer ─────────────────────────────────────────────────────────────────

def _fix_ocr(text: str) -> str:
    """Fix common OCR errors in BTech/degree syllabi."""

    # Character-level OCR swaps (very common)
    char_fixes = [
        (r'\brn\b',   'm'),        # rn → m
        (r'\bvv\b',   'w'),        # vv → w
        (r'(?<=[a-z])1(?=[a-z])', 'l'),  # digit 1 inside word → l
        (r'(?<=[a-z])0(?=[a-z])', 'o'),  # digit 0 inside word → o
    ]
    for pat, rep in char_fixes:
        text = re.sub(pat, rep, text)

    # Word-level fixes (common in scanned BTech syllabi)
    word_fixes = {
        # Module / lexical analysis
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
        r'\bAnalyser\b':      'Analyser',
        r'\bAnalyzer\b':      'Analyzer',

        # Syntax analysis
        r'\bSyntax\s+crror\b':    'Syntax error',
        r'\bSyntax\s+enor\b':     'Syntax error',
        r'\bhandlng\b':           'handling',
        r'\bhandllng\b':          'handling',
        r'\bGrammers\b':          'Grammars',
        r'\bGramrners\b':         'Grammars',
        r'\bGrammars\b':          'Grammars',
        r'\bDerivahon\b':         'Derivation',
        r'\bDenvation\b':         'Derivation',
        r'\bEliminating\b':       'Eliminating',
        r'\bEhminahag\b':         'Eliminating',
        r'\bEliminaling\b':       'Eliminating',
        r'\bAmbiguity\b':         'Ambiguity',
        r'\bAmblguity\b':         'Ambiguity',
        r'\brecursion\b':         'recursion',
        r'\brecurslon\b':         'recursion',
        r'\bfactonng\b':          'factoring',
        r'\bfactorlng\b':         'factoring',
        r'\bParsing\b':           'Parsing',
        r'\bParslng\b':           'Parsing',
        r'\bPredictlve\b':        'Predictive',
        r'\bPredictive\b':        'Predictive',
        r'\bRecursive\b':         'Recursive',
        r'\bRecurslve\b':         'Recursive',
        r'\bDescent\b':           'Descent',
        r'\bDescenl\b':           'Descent',

        # Bottom-up parsing
        r'\bPrunlng\b':           'Pruning',
        r'\bprecedence\b':        'precedence',
        r'\bprecedenee\b':        'precedence',
        r'\bConstructlng\b':      'Constructing',
        r'\bcanonical\b':         'canonical',
        r'\bcanonlcal\b':         'canonical',

        # Syntax directed / intermediate code
        r'\btranslahon\b':        'translation',
        r'\btranslatlon\b':       'translation',
        r'\bdefinitions\b':       'definitions',
        r'\bdefinthons\b':        'definitions',
        r'\bdefinithons\b':       'definitions',
        r'\battnbuted\b':         'attributed',
        r'\battrlbuted\b':        'attributed',
        r'\bevaluahon\b':         'evaluation',
        r'\bevaluatlon\b':        'evaluation',
        r'\bEnvironments\b':      'Environments',
        r'\bEavlronments\b':      'Environments',
        r'\bEavlronrnents\b':     'Environments',
        r'\bIsSuCS\b':            'Issues',
        r'\borganivahon\b':       'organization',
        r'\borganizahon\b':       'organization',
        r'\borganisahon\b':       'organization',
        r'\ballocaton\b':         'allocation',
        r'\ballocatlon\b':        'allocation',
        r'\bstrategies\b':        'strategies',
        r'\bstrategles\b':        'strategies',
        r'\bstratcgics\b':        'strategies',
        r'\bGeneration\b':        'Generation',
        r'\bGencration\b':        'Generation',
        r'\bGeneratlon\b':        'Generation',
        r'\bIntermediate\b':      'Intermediate',
        r'\blntermediate\b':      'Intermediate',
        r'\blatermediate\b':      'Intermediate',
        r'\bQuadruples\b':        'Quadruples',
        r'\bQuadruoles\b':        'Quadruples',
        r'\bTriples\b':           'Triples',
        r'\bTrlples\b':           'Triples',
        r'\bGraphical\b':         'Graphical',
        r'\bGraphlcal\b':         'Graphical',
        r'\brepresentations\b':   'representations',
        r'\brepresentatlons\b':   'representations',
        r'\bThree-Address\b':     'Three-Address',
        r'\bThree\s*-\s*Adress\b': 'Three-Address',

        # Code optimization / generation
        r'\bOptimization\b':      'Optimization',
        r'\bOptimizahon\b':       'Optimization',
        r'\bOptlmization\b':      'Optimization',
        r'\bOptmizahon\b':        'Optimization',
        r'\boptimization\b':      'optimization',
        r'\boptlmization\b':      'optimization',
        r'\bPrincipal\b':         'Principal',
        r'\bPnacipal\b':          'Principal',
        r'\bPrlncipal\b':         'Principal',
        r'\bindependent\b':       'independent',
        r'\bindependenl\b':       'independent',
        r'\bgenerator\b':         'generator',
        r'\bgeneralor\b':         'generator',
        r'\bTarget\b':            'Target',
        r'\bTargel\b':            'Target',
        r'\bLanguage\b':          'Language',
        r'\bLanguage\b':          'Language',
        r'\bsimple\b':            'simple',
        r'\bslmple\b':            'simple',
        r'\bumple\b':             'simple',

        # General academic words
        r'\bSvatax\b':            'Syntax',
        r'\bSvntax\b':            'Syntax',
        r'\bCCCA\b':              '',
        r'\bKAL\b':               '',
        r'\banalysls\b':          'analysis',
        r'\bAnalysls\b':          'Analysis',
        r'\bCompller\b':          'Compiler',
        r'\bcompller\b':          'compiler',
        r'\bPhases\b':            'Phases',
        r'\bPhase\b':             'Phase',
        r'\bsynthesls\b':         'synthesis',
        r'\bSynthesls\b':         'Synthesis',
        r'\bsource\b':            'source',
        r'\bsouree\b':            'source',
        r'\bprogram\b':           'program',
        r'\bprogam\b':            'program',
        r'\btranslation\b':       'translation',
        r'\btranslatlon\b':       'translation',
        r'\bcode\b':              'code',
        r'\bcodo\b':              'code',
        r'\bParse\b':             'Parse',
        r'\bParse\b':             'Parse',
        r'\bTrees\b':             'Trees',
        r'\bTree\b':              'Tree',
        r'\bToken\b':             'Token',
        r'\bTokens\b':            'Tokens',
        r'\bInput\b':             'Input',
        r'\blnput\b':             'Input',
        r'\bRole\b':              'Role',
        r'\bRoie\b':              'Role',
        r'\bContext\b':           'Context',
        r'\bFree\b':              'Free',
        r'\bShift\b':             'Shift',
        r'\bShifl\b':             'Shift',
        r'\bReduce\b':            'Reduce',
        r'\bReduco\b':            'Reduce',
        r'\bOperator\b':          'Operator',
        r'\bOperalor\b':          'Operator',
        r'\bBottom\b':            'Bottom',
        r'\bBollom\b':            'Bottom',
        r'\bHandle\b':            'Handle',
        r'\bHandie\b':            'Handle',
        r'\bRun-Time\b':          'Run-Time',
        r'\bRun\s*-\s*Timc\b':   'Run-Time',
        r'\bSource\b':            'Source',
        r'\bSouree\b':            'Source',
        r'\bStorage\b':           'Storage',
        r'\bStorago\b':           'Storage',
        r'\bLocal\b':             'Local',
        r'\bLocai\b':             'Local',
        r'\bGlobal\b':            'Global',
        r'\bGlobai\b':            'Global',
        r'\bMachine\b':           'Machine',
        r'\bMachlne\b':           'Machine',
        r'\bDependent\b':         'Dependent',
        r'\bDependenl\b':         'Dependent',
        r'\bdesign\b':            'design',
        r'\bdesiqn\b':            'design',
        r'\bIssues\b':            'Issues',
        r'\blssues\b':            'Issues',
    }

    for pat, rep in word_fixes.items():
        text = re.sub(pat, rep, text, flags=re.IGNORECASE if pat[0] != '(' else 0)

    # Clean up double spaces
    text = re.sub(r'  +', ' ', text)
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text


# ── Heuristic extractor ───────────────────────────────────────────────────────

def _heuristic_extract(text: str, max_topics: int) -> list[str]:
    topics = []

    # Normalize separators to newlines for uniform processing
    normalized = text
    normalized = re.sub(r'[;_]', '\n', normalized)
    normalized = re.sub(r'\.\s+(?=[A-Z])', '\n', normalized)
    normalized = re.sub(r',\s*', '\n', normalized)

    lines = normalized.splitlines()

    for line in lines:
        line = line.strip()
        if not line or len(line) < 4:
            continue
        # Skip pure module headers without content
        if re.match(r'^(syllabus|module|unit|chapter|section|part)\s*[-–—\d]*$', line, re.IGNORECASE):
            continue
        if re.match(r'^\d+$', line):
            continue
        if len(line) > 120:
            continue

        t = _clean(line)
        if _is_valid(t):
            topics.append(t)

    # Also extract module header titles from parentheses
    for match in re.finditer(r'\(([^)]{10,80})\)', text, re.IGNORECASE):
        t = _clean(match.group(1))
        if _is_valid(t):
            topics.append(t)

    return _dedup(topics)


def _clean(s: str) -> str:
    s = re.sub(r'[^\w\s\-/().,&:\']', ' ', s)
    s = re.sub(r'\s+', ' ', s).strip().strip('.-,;:')
    return s


def _is_valid(t: str) -> bool:
    if len(t) < 5 or len(t) > 120:
        return False
    if re.match(r'^\d+$', t):
        return False
    if len(t.split()) < 1:
        return False
    return True


def _dedup(topics: list[str]) -> list[str]:
    seen, result = set(), []
    for t in topics:
        key = t.lower().strip()
        if key not in seen and len(key) > 3:
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


# ── LLM extractor ─────────────────────────────────────────────────────────────

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