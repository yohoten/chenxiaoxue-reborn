"""
Humanizer: Remove AI Writing Patterns

基于 Wikipedia "Signs of AI writing" 的 AI 文本检测与人性化改写服务。
检测 24 种 AI 写作模式并提供改进建议。

参考: https://en.wikipedia.org/wiki/Wikipedia:Signs_of_AI_writing
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional


# ─── 数据模型 ────────────────────────────────────────────────

@dataclass
class PatternMatch:
    """单个模式匹配结果"""
    pattern_id: str          # 模式编号 e.g. "P1", "P2"
    pattern_name: str        # 模式名称
    severity: str            # "high" / "medium" / "low"
    snippet: str             # 匹配到的文本片段
    position: int            # 在原文中的位置 (字符索引)
    length: int              # 匹配文本长度
    suggestion: str          # 改进建议
    replacement: str         # 建议替换文本


@dataclass
class HumanizerResult:
    """人性化分析结果"""
    original_text: str
    humanized_text: str
    matches: List[PatternMatch] = field(default_factory=list)
    total_issues: int = 0
    score: float = 0.0       # 0.0 (完全人类) ~ 1.0 (完全AI)
    summary: str = ""


# ─── 模式检测器基类 ──────────────────────────────────────────

class PatternDetector:
    """AI 写作模式检测器基类"""

    def detect(self, text: str) -> List[PatternMatch]:
        """检测文本中的 AI 写作模式"""
        raise NotImplementedError

    def fix(self, text: str) -> str:
        """修复检测到的模式"""
        raise NotImplementedError


# ── P1: Undue Emphasis on Significance ──────────────────────

P1_KEYWORDS = [
    r"stands?\s+as\s+a",
    r"serves?\s+as\s+a",
    r"is\s+a\s+testament",
    r"is\s+a\s+reminder",
    r"a\s+(vital|significant|crucial|pivotal|key)\s+(role|moment)",
    r"underscores?\s+its\s+(importance|significance)",
    r"highlights?\s+its\s+(importance|significance)",
    r"reflects?\s+broader",
    r"symbolizing\s+its\s+(ongoing|enduring|lasting)",
    r"setting\s+the\s+stage\s+for",
    r"marking\s+(the|a)\s+(shift|turning\s+point)",
    r"shaping\s+the",
    r"represents?\s+a\s+shift",
    r"key\s+turning\s+point",
    r"evolving\s+landscape",
    r"focal\s+point",
    r"indelible\s+mark",
    r"deeply\s+rooted",
    r"contributing\s+to\s+the",
]


class SignificanceDetector(PatternDetector):
    """P1: 过度强调重要性、遗产和更广泛趋势"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P1_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P1",
                    pattern_name="过度强调重要性",
                    severity="high",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion='替换浮夸表述为具体事实，删除无意义的「重要性」声明',
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        # Remove common inflated patterns
        result = re.sub(
            r',?\s*(?:marking|shaping|symbolizing)\s+a\s+(?:pivotal|significant|vital|crucial)\s+(?:moment|role|shift).*?(?=\.|,|$)',
            '', result
        )
        result = re.sub(
            r'\s*This\s+(?:initiative|movement|project)\s+was\s+part\s+of\s+a\s+broader\s+movement[^.]*\.',
            '', result
        )
        return result


# ── P2: Notability Name-dropping ────────────────────────────

P2_KEYWORDS = [
    r"(?:independent|local|regional|national|international|major)\s+(?:media|news|press)\s+(?:outlets?|coverage)",
    r"written\s+by\s+a\s+leading\s+expert",
    r"active\s+social\s+media\s+presence",
    r"(?:cited|featured|published|mentioned)\s+in\s+(?:\w+\s+)+(?:Times?|Post|Guardian|BBC|CNN|Forbes|Bloomberg)",
]


class NotabilityDetector(PatternDetector):
    """P2: 过度强调知名度和媒体报道"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P2_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P2",
                    pattern_name="空洞的知名度声明",
                    severity="high",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="提供具体引用上下文，或删除空洞的列举",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(
            r'Her\s+views?\s+have\s+been\s+(?:cited|featured)\s+in\s+[^.]*\.',
            '', result
        )
        result = re.sub(
            r'She\s+maintains?\s+an\s+active\s+social\s+media\s+presence[^.]*\.',
            '', result
        )
        return result


# ── P3: Superficial -ing Analyses ───────────────────────────

P3_KEYWORDS = [
    r"(?:highlighting|underscoring|emphasizing)\s+(?:the\s+)?",
    r"ensuring\s+(?:that\s+)?",
    r"(?:reflecting|symbolizing)\s+(?:the\s+)?",
    r"contributing\s+to\s+",
    r"(?:cultivating|fostering)\s+",
    r"encompassing\s+",
    r"showcasing\s+",
]


class IngAnalysisDetector(PatternDetector):
    """P3: 以 -ing 结尾的表层分析"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P3_KEYWORDS:
            for m in re.finditer(pattern + r'[^,;.]+', text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P3",
                    pattern_name="-ing 表层分析",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="移除 -ing 短语，将核心信息转为独立陈述句",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        # Remove trailing -ing clauses
        result = re.sub(r',\s*(?:highlighting|underscoring|emphasizing|reflecting|symbolizing|showcasing)\s+the\s+[^,.\n]+', '', result)
        result = re.sub(r',\s*(?:contributing|ensuring|fostering|cultivating|encompassing)\s+[^,.\n]+', '', result)
        return result


# ── P4: Promotional Language ────────────────────────────────

P4_KEYWORDS = [
    r"boasts?\s+a",
    r"\bvibrant\b",
    r"\bprofound\b",
    r"enhancing\s+its",
    r"(?:showcasing|exemplifies?)\s+",
    r"commitment\s+to",
    r"natural\s+beauty",
    r"\bnestled\b",
    r"in\s+the\s+heart\s+of",
    r"\bgroundbreaking\b",
    r"\brenowned\b",
    r"\bbreathtaking\b",
    r"must-visit",
    r"\bstunning\b",
]


class PromotionalDetector(PatternDetector):
    """P4: 促销性/广告式语言"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P4_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P4",
                    pattern_name="促销式语言",
                    severity="high",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="替换为中性、客观的描述，使用具体细节替代夸张形容词",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        replacements = {
            r'\bnestled\s+within\b': 'located in',
            r'\bnestled\b': 'located',
            r'in\s+the\s+heart\s+of\b': 'in',
            r'\bbreathtaking\b': '',
            r'\bstunning\b': '',
            r'\brenowned\b': 'well-known',
            r'\bgroundbreaking\b': 'innovative',
            r'\bvibrant\b': 'busy',
            r'\bprofound\b': 'significant',
            r'boasts?\s+a\b': 'has a',
        }
        for old, new in replacements.items():
            result = re.sub(old, new, result, flags=re.IGNORECASE)
        return result


# ── P5: Vague Attributions ──────────────────────────────────

P5_KEYWORDS = [
    r"Industry\s+reports?\b",
    r"Observers?\s+have\s+cited",
    r"Experts?\s+(?:argue|believe|say|claim)",
    r"Some\s+critics?\s+argue",
    r"Several\s+(?:sources?|publications?)",
]


class VagueAttributionDetector(PatternDetector):
    """P5: 模糊归因和推诿用语"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P5_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P5",
                    pattern_name="模糊归因",
                    severity="high",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="替换为具体来源引用，或删除空洞的专家观点",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(
            r'(?:Due\s+to\s+its\s+unique\s+characteristics|Experts?\s+believe)[^.]*\.',
            '', result
        )
        return result


# ── P6: Formulaic Challenges Sections ──────────────────────

P6_KEYWORDS = [
    r"Despite\s+(?:its|these|this)",
    r"faces?\s+several\s+challenges",
    r"Despite\s+these\s+challenges",
    r"Challenges\s+and\s+(?:Legacy|Future)",
    r"Future\s+Outlook",
]


class ChallengesDetector(PatternDetector):
    """P6: 公式化的"挑战与未来展望"段落"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P6_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P6",
                    pattern_name="公式化挑战段落",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="用具体事例和数据替代模板式断言",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(
            r'Despite\s+(?:its|these|this)\s+\w+[^.]*faces?\s+several\s+challenges[^.]*\.',
            '', result
        )
        result = re.sub(
            r'Despite\s+these\s+challenges[^.]*continues?\s+to\s+thrive[^.]*\.',
            '', result
        )
        return result


# ── P7: AI Vocabulary ────────────────────────────────────────

P7_WORDS = [
    r"\bAdditionally\b",
    r"\balign\s+with\b",
    r"\bcrucial\b",
    r"\bdelve\b",
    r"\bemphasizing\b",
    r"\benduring\b",
    r"\benhance\b",
    r"\bfostering\b",
    r"\bgarner\b",
    r"\bhighlight\b",
    r"\binterplay\b",
    r"\bintricate\b",
    r"\bintricacies\b",
    r"\bpivotal\b",
    r"\bshowcase\b",
    r"\btapestry\b",
    r"\btestament\b",
    r"\bunderscore\b",
    r"\bvaluable\b",
]

P7_EXCLUSIONS = [
    r"highlight\s+(?:text|color|button|selection)",
    r"valuable\s+(?:resource|item|asset|lesson)",
    r"enhance\s+(?:image|photo|quality)",
]


class AIVocabularyDetector(PatternDetector):
    """P7: 过度使用的 AI 词汇"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for i, pattern in enumerate(P7_WORDS):
            for m in re.finditer(pattern, text, re.IGNORECASE):
                # Check exclusions
                excluded = False
                for exc in P7_EXCLUSIONS:
                    if re.search(exc, text, re.IGNORECASE) and m.group() in exc:
                        excluded = True
                        break
                if excluded:
                    continue
                matches.append(PatternMatch(
                    pattern_id="P7",
                    pattern_name="AI 高频词汇",
                    severity="low",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion=f"将 '{m.group()}' 替换为更自然的同义词或简化表达",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        replacements = {
            r'\bAdditionally\b': 'Also',
            r'\benhance\b': 'improve',
            r'\bemphasizing\b': 'stressing',
            r'\bfostering\b': 'building',
            r'\bgarner\b': 'get',
            r'\bintricate\b': 'complex',
            r'\bintricacies\b': 'complexities',
            r'\bpivotal\b': 'important',
            r'\bshowcase\b': 'show',
            r'\btestament\b': 'proof',
            r'\bunderscore\b': 'stress',
            r'\bvaluable\b': 'useful',
            r'\bdelve\b': 'dive',
            r'\binterplay\b': 'interaction',
            r'\btapestry\b': 'mix',
        }
        for old, new in replacements.items():
            result = re.sub(old, new, result, flags=re.IGNORECASE)
        return result


# ── P8: Copula Avoidance ────────────────────────────────────

P8_KEYWORDS = [
    r"serves?\s+as\s+(?:a|an|the)",
    r"stands?\s+as\s+(?:a|an|the)",
    r"marks?\s+(?:a|an|the)",
    r"represents?\s+(?:a|an|the)",
    r"boasts?\s+(?:a|an|the)",
    r"features?\s+(?:a|an|the)",
    r"offers?\s+(?:a|an|the)",
]


class CopulaAvoidanceDetector(PatternDetector):
    """P8: "is"/"are" 回避"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P8_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P8",
                    pattern_name="系动词回避",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion=f"将 '{m.group()}' 替换为简单的 'is' 或 'has'",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        replacements = {
            r'serves?\s+as\s+(?:a|an|the)\b': 'is',
            r'stands?\s+as\s+(?:a|an|the)\b': 'is',
            r'marks?\s+(?:a|an|the)\b': 'is',
            r'represents?\s+(?:a|an|the)\b': 'is',
            r'boasts?\s+(?:a|an|the)\b': 'has',
            r'features?\s+(?:a|an|the)\b': 'has',
            r'offers?\s+(?:a|an|the)\b': 'has',
        }
        for old, new in replacements.items():
            result = re.sub(old, new, result, flags=re.IGNORECASE)
        return result


# ── P9: Negative Parallelisms ──────────────────────────────

P9_PATTERNS = [
    r"It'?s?\s+not\s+just\s+(?:about\s+)?[^,]+,\s*it'?s?\s+",
    r"Not\s+only\s+[^,]+,\s*but\s+(?:also\s+)?",
    r"It'?s?\s+not\s+merely\s+[^,]+,\s*it'?s?\s+",
]


class NegativeParallelismDetector(PatternDetector):
    """P9: 否定平行结构"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P9_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P9",
                    pattern_name="否定平行结构",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion='简化表述，直接陈述核心观点，避免「不仅是...也是...」结构',
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(
            r"It'?s?\s+not\s+just\s+(?:about\s+)?[^,]+,\s*it'?s?\s+[^.]+\.",
            '', result
        )
        return result


# ── P10: Rule of Three ──────────────────────────────────────

P10_PATTERNS = [
    r"(?:\w+,\s+){2}(?:and\s+)?\w+\s+(?:sessions?|opportunities?|insights?|features?|benefits?)",
    r"(?:innovation|inspiration|insight)s?,\s+(?:\w+,\s+)?(?:and\s+)?\w+",
]


class RuleOfThreeDetector(PatternDetector):
    """P10: 三要素规则过度使用"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P10_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P10",
                    pattern_name="三要素规则",
                    severity="low",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="减少并列项数量，拆分或简化三要素列举",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        # This is complex - just flag rather than auto-fix
        return result


# ── P11: Elegant Variation (Synonym Cycling) ──────────────

P11_PATTERNS = [
    # Detect when same concept is referred to with different words in proximity
]


class SynonymCyclingDetector(PatternDetector):
    """P11: 同义词替换过度"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        # Look for repeated noun phrases that vary terms unnecessarily
        # e.g., "protagonist... main character... central figure... hero"
        synonym_groups = [
            (r'\b(protagonist|main\s+character|central\s+figure|hero)\b', '避免为同一对象使用过多不同称呼'),
            (r'\b(company|firm|corporation|enterprise|organization)\b', '统一组织称呼'),
            (r'\b(important|crucial|significant|vital|critical|essential)\b', '减少重要性形容词堆砌'),
            (r'\b(problem|challenge|issue|difficulty|obstacle)\b', '统一问题相关用词'),
            (r'\b(beautiful|stunning|breathtaking|gorgeous|picturesque)\b', '减少华丽形容词堆砌'),
        ]
        for group_pattern, suggestion in synonym_groups:
            occurrences = list(re.finditer(group_pattern, text, re.IGNORECASE))
            if len(occurrences) >= 3:
                # Check if they're within 500 chars of each other
                positions = [m.start() for m in occurrences]
                for i in range(1, len(positions)):
                    if positions[i] - positions[0] < 500:
                        matches.append(PatternMatch(
                            pattern_id="P11",
                            pattern_name="过度同义词替换",
                            severity="low",
                            snippet=text[positions[0]:positions[i] + 50],
                            position=positions[0],
                            length=positions[i] - positions[0] + 50,
                            suggestion=suggestion,
                            replacement="",
                        ))
                        break
        return matches

    def fix(self, text: str) -> str:
        return text  # Complex - manual review recommended


# ── P12: False Ranges ──────────────────────────────────────

P12_PATTERNS = [
    r"from\s+the\s+\w+\s+of\s+[^,]+to\s+the\s+\w+\s+of\s+[^,]+",
    r"from\s+[^,]+to\s+[^,]+,\s*from\s+[^,]+to\s+",
]


class FalseRangeDetector(PatternDetector):
    """P12: 虚假范围表述"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P12_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P12",
                    pattern_name="虚假范围表述",
                    severity="low",
                    snippet=m.group()[:80],
                    position=m.start(),
                    length=min(m.end() - m.start(), 80),
                    suggestion='将「从X到Y」的修辞结构替换为具体的列举',
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        return text  # Needs manual review


# ── P13: Em Dash Overuse ────────────────────────────────────

class EmDashDetector(PatternDetector):
    """P13: 长破折号过度使用"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        count = text.count('—') + text.count('–') + text.count(' — ')
        if count >= 2:
            # Find each dash
            for m in re.finditer(r'(—|–)', text):
                matches.append(PatternMatch(
                    pattern_id="P13",
                    pattern_name="长破折号过度使用",
                    severity="low",
                    snippet=m.group(),
                    position=m.start(),
                    length=1,
                    suggestion=f"全文共 {count} 处破折号，建议替换为逗号或分号",
                    replacement=", ",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        # Replace em dashes used as punctuation with commas or semicolons
        # Only replace those surrounded by words (not at line boundaries)
        result = re.sub(r'(\w)—(\w)', r'\1, \2', result)
        result = re.sub(r'(\w)—\s+', r'\1, ', result)
        result = re.sub(r'\s+—(\w)', r', \1', result)
        return result


# ── P14: Boldface Overuse ──────────────────────────────────

class BoldfaceDetector(PatternDetector):
    """P14: 粗体滥用"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        bold_count = len(re.findall(r'\*\*[^*]+\*\*', text))
        if bold_count >= 3:
            for m in re.finditer(r'\*\*([^*]+)\*\*', text):
                matches.append(PatternMatch(
                    pattern_id="P14",
                    pattern_name="粗体滥用",
                    severity="low",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="减少粗体使用，只在关键术语上使用",
                    replacement=m.group(1),
                ))
        return matches

    def fix(self, text: str) -> str:
        return re.sub(r'\*\*([^*]+)\*\*', r'\1', text)


# ── P15: Inline-Header Lists ──────────────────────────────

P15_PATTERNS = [
    r'\*\*[^*]+\*\*:\s+',
]


class InlineHeaderDetector(PatternDetector):
    """P15: 行内标题列表"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        header_count = len(re.findall(r'-\s+\*\*[^*]+\*\*:', text))
        if header_count >= 2:
            for m in re.finditer(r'-\s+\*\*([^*]+)\*\*:', text):
                matches.append(PatternMatch(
                    pattern_id="P15",
                    pattern_name="行内标题列表",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion=f"将标题列表 '{m.group(1)}' 改写为自然段落",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        # Replace "- **Header:** content" with paragraph format
        result = re.sub(r'-\s+\*\*([^*]+)\*\*:\s+', lambda m: m.group(1) + ' ', result)
        return result


# ── P16: Title Case Headings ──────────────────────────────

class TitleCaseDetector(PatternDetector):
    """P16: 标题大写"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for m in re.finditer(r'^(#{1,6}\s+)([A-Z][A-Za-z\s]+)$', text, re.MULTILINE):
            heading_text = m.group(2)
            # Check if it's title case (most words capitalized)
            words = heading_text.split()
            upper_words = sum(1 for w in words if w[0].isupper() if len(words) > 1)
            if upper_words >= len(words) * 0.6 and len(words) >= 3:
                matches.append(PatternMatch(
                    pattern_id="P16",
                    pattern_name="标题大写 (Title Case)",
                    severity="low",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="将标题改为普通句子大小写",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        def to_sentence_case(m):
            prefix = m.group(1)
            heading = m.group(2)
            # Only capitalize first word and proper nouns
            words = heading.split()
            if len(words) >= 3 and sum(1 for w in words if w[0].isupper()) >= len(words) * 0.6:
                words[0] = words[0].capitalize()
                for i in range(1, len(words)):
                    words[i] = words[i].lower()
                return prefix + ' '.join(words)
            return m.group()

        result = re.sub(
            r'^(#{1,6}\s+)([A-Z][A-Za-z\s]+)$',
            to_sentence_case,
            result if 'result' in dir() else text,
            flags=re.MULTILINE
        )
        # Actually let me just do it properly
        lines = text.split('\n')
        new_lines = []
        for line in lines:
            m = re.match(r'^(#{1,6}\s+)(.+)$', line)
            if m:
                prefix = m.group(1)
                heading = m.group(2)
                words = heading.split()
                if len(words) >= 3 and sum(1 for w in words if w[0].isupper()) >= len(words) * 0.6:
                    words[0] = words[0].capitalize()
                    for i in range(1, len(words)):
                        words[i] = words[i].lower()
                    new_lines.append(prefix + ' '.join(words))
                else:
                    new_lines.append(line)
            else:
                new_lines.append(line)
        return '\n'.join(new_lines)


# ── P17: Emojis ─────────────────────────────────────────────

class EmojiDetector(PatternDetector):
    """P17: 表情符号滥用"""

    EMOJI_PATTERN = re.compile(
        '[' u'\U0001F600-\U0001F64F'  # emoticons
        u'\U0001F300-\U0001F5FF'  # symbols & pictographs
        u'\U0001F680-\U0001F6FF'  # transport & map symbols
        u'\U0001F1E0-\U0001F1FF'  # flags (iOS)
        u'\U00002702-\U000027B0'  # dingbats
        u'\U000024C2-\U0001F251'  # enclosed characters
        ']+'
    )

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for m in self.EMOJI_PATTERN.finditer(text):
            matches.append(PatternMatch(
                pattern_id="P17",
                pattern_name="表情符号滥用",
                severity="low",
                snippet=m.group(),
                position=m.start(),
                length=m.end() - m.start(),
                suggestion="移除装饰性表情符号，改用文字表达",
                replacement="",
            ))
        return matches

    def fix(self, text: str) -> str:
        return self.EMOJI_PATTERN.sub('', text)


# ── P18: Curly Quotation Marks ────────────────────────────

class CurlyQuoteDetector(PatternDetector):
    """P18: 花引号"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for m in re.finditer(r'[\u201C\u201D\u2018\u2019]', text):
            matches.append(PatternMatch(
                pattern_id="P18",
                pattern_name="花引号",
                severity="low",
                snippet=m.group(),
                position=m.start(),
                length=1,
                suggestion="将花引号替换为直引号",
                replacement='"',
            ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = result.replace('\u201C', '"').replace('\u201D', '"')
        result = result.replace('\u2018', "'").replace('\u2019', "'")
        return result


# ── P19: Collaborative Communication Artifacts ────────────

P19_KEYWORDS = [
    r"I\s+hope\s+this\s+helps?",
    r"Of\s+course!",
    r"Certainly!",
    r"You're\s+absolutely\s+right!",
    r"Would\s+you\s+like\s+",
    r"let\s+me\s+know\s+",
    r"here\s+is\s+a\s+",
    r"Here\s+are\s+",
]


class ChatbotArtifactDetector(PatternDetector):
    """P19: 聊天机器人协作痕迹"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P19_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P19",
                    pattern_name="聊天机器人痕迹",
                    severity="high",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="删除聊天机器人友好用语，直接呈现信息",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(r'I\s+hope\s+this\s+helps?[!.]?', '', result)
        result = re.sub(r'Let\s+me\s+know\s+if\s+you[^.]*\.', '', result)
        result = re.sub(r'(Of\s+course|Certainly|You\'re\s+absolutely\s+right)[!.]', '', result)
        result = re.sub(r'\s+Would\s+you\s+like\s+[^?]+\?', '', result)
        return result


# ── P20: Knowledge-Cutoff Disclaimers ─────────────────────

P20_KEYWORDS = [
    r"as\s+of\s+\d{4}",
    r"Up\s+to\s+my\s+last\s+(training\s+)?update",
    r"While\s+specific\s+details\s+are\s+(limited|scarce)",
    r"based\s+on\s+available\s+information",
    r"While\s+I\s+don'?t\s+have\s+(?:access\s+to\s+)?(?:real-time|the\s+most\s+up-to-date)",
    r"my\s+(knowledge\s+)?cutoff\s+date",
    r"I\s+(?:do\s+n?')?t\s+have\s+(?:access\s+to\s+)?(?:real-time|the\s+latest)",
]


class CutoffDisclaimerDetector(PatternDetector):
    """P20: 知识截止日期声明"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P20_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P20",
                    pattern_name="知识截止声明",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="删除知识截止声明，直接呈现信息",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(
            r'While\s+specific\s+details\s+are\s+(?:limited|scarce)[^.]*\.',
            '', result
        )
        # Remove "as of YYYY" phrases
        result = re.sub(r',?\s*as\s+of\s+\d{4}', '', result)
        return result


# ── P21: Sycophantic Tone ──────────────────────────────────

P21_KEYWORDS = [
    r"Great\s+question!",
    r"Excellent\s+question!",
    r"That'?s?\s+a\s+(?:great|fantastic|excellent|wonderful)\s+(?:point|question)",
    r"You'?re?\s+absolutely\s+right",
    r"That'?s?\s+an\s+excellent\s+point",
]


class SycophanticDetector(PatternDetector):
    """P21: 谄媚/迎合语气"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P21_KEYWORDS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P21",
                    pattern_name="谄媚语气",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="删除过度恭维用语，直接回答问题",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(
            r'(Great|Excellent|That\'s?\s+a\s+(great|excellent|fantastic))\s+(question|point)[!.]?\s*',
            '', result
        )
        result = re.sub(r'You\'?re?\s+absolutely\s+right[!.]?\s*', '', result)
        return result


# ── P22: Filler Phrases ────────────────────────────────────

P22_PAIRS = [
    (r"In\s+order\s+to", "To"),
    (r"Due\s+to\s+the\s+fact\s+that", "Because"),
    (r"At\s+this\s+point\s+in\s+time", "Now"),
    (r"In\s+the\s+event\s+that", "If"),
    (r"has\s+the\s+ability\s+to", "can"),
    (r"It\s+is\s+important\s+to\s+note\s+that", ""),
    (r"in\s+order\s+to\s+achieve\s+this\s+goal", "To achieve this"),
    (r"in\s+order\s+to\s+accomplish\s+this", "To accomplish this"),
    (r"a\s+number\s+of", "several"),
    (r"the\s+majority\s+of", "most"),
    (r"in\s+terms\s+of", "regarding"),
    (r"with\s+regard\s+to", "about"),
    (r"in\s+relation\s+to", "about"),
    (r"on\s+a\s+\w+\s+basis", lambda m: m.group(1) + "ly" if m.group(1) else "regularly"),
]


class FillerDetector(PatternDetector):
    """P22: 填充短语"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern, replacement in P22_PAIRS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                rep = replacement if isinstance(replacement, str) else replacement(m)
                matches.append(PatternMatch(
                    pattern_id="P22",
                    pattern_name="填充短语",
                    severity="low",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion=f"将 '{m.group()}' 简化为 '{rep}'",
                    replacement=rep,
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        for pattern, replacement in P22_PAIRS:
            if isinstance(replacement, str):
                result = re.sub(pattern, replacement, result, flags=re.IGNORECASE)
            else:
                result = re.sub(
                    r'on\s+a\s+(\w+)\s+basis',
                    lambda m: m.group(1) + 'ly' if m.group(1) else 'regularly',
                    result,
                    flags=re.IGNORECASE
                )
        return result


# ── P23: Excessive Hedging ─────────────────────────────────

P23_PATTERNS = [
    r"\bcould\s+potentially\s+possibly\b",
    r"\bpossibly\s+could\s+be\b",
    r"\bmight\s+potentially\b",
    r"\bit\s+could\s+be\s+argued\b",
    r"\barguably\b",
    r"\bconceivably\b",
]


class HedgingDetector(PatternDetector):
    """P23: 过度模糊化/回避性语言"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P23_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P23",
                    pattern_name="过度模糊化",
                    severity="low",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="减少过度修饰，直接陈述",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(r'\bcould\s+potentially\s+possibly\b', 'could', result, flags=re.IGNORECASE)
        result = re.sub(r'\bpossibly\s+could\s+be\b', 'could be', result, flags=re.IGNORECASE)
        result = re.sub(r'\bmight\s+potentially\b', 'might', result, flags=re.IGNORECASE)
        result = re.sub(r'\bit\s+could\s+be\s+argued\b', 'arguably', result, flags=re.IGNORECASE)
        return result


# ── P24: Generic Positive Conclusions ─────────────────────

P24_PATTERNS = [
    r"The\s+future\s+looks?\s+bright\s+for\s+",
    r"Exciting\s+times\s+lie\s+ahead",
    r"continues?\s+their?\s+journey\s+toward\s+excellence",
    r"This\s+represents?\s+a\s+major\s+step\s+in\s+the\s+right\s+direction",
    r"The\s+(?:future|possibilities)\s+(?:looks?|are)\s+(?:bright|promising|limitless)",
    r"only\s+time\s+will\s+tell",
]


class GenericConclusionDetector(PatternDetector):
    """P24: 通用正面结论"""

    def detect(self, text: str) -> List[PatternMatch]:
        matches = []
        for pattern in P24_PATTERNS:
            for m in re.finditer(pattern, text, re.IGNORECASE):
                matches.append(PatternMatch(
                    pattern_id="P24",
                    pattern_name="通用正面结论",
                    severity="medium",
                    snippet=m.group(),
                    position=m.start(),
                    length=m.end() - m.start(),
                    suggestion="用具体计划/数据替代空洞的乐观展望",
                    replacement="",
                ))
        return matches

    def fix(self, text: str) -> str:
        result = text
        result = re.sub(r'The\s+future\s+looks?\s+bright\s+for\s+the\s+\w+[^.]*\.', '', result)
        result = re.sub(r'Exciting\s+times\s+lie\s+ahead[^.]*\.', '', result)
        result = re.sub(r'This\s+represents?\s+a\s+major\s+step\s+in\s+the\s+right\s+direction[^.]*\.', '', result)
        return result


# ─── 主 Humanizer 服务 ──────────────────────────────────────

ALL_DETECTORS: List[PatternDetector] = [
    SignificanceDetector(),
    NotabilityDetector(),
    IngAnalysisDetector(),
    PromotionalDetector(),
    VagueAttributionDetector(),
    ChallengesDetector(),
    AIVocabularyDetector(),
    CopulaAvoidanceDetector(),
    NegativeParallelismDetector(),
    RuleOfThreeDetector(),
    SynonymCyclingDetector(),
    FalseRangeDetector(),
    EmDashDetector(),
    BoldfaceDetector(),
    InlineHeaderDetector(),
    TitleCaseDetector(),
    EmojiDetector(),
    CurlyQuoteDetector(),
    ChatbotArtifactDetector(),
    CutoffDisclaimerDetector(),
    SycophanticDetector(),
    FillerDetector(),
    HedgingDetector(),
    GenericConclusionDetector(),
]

DETECTOR_WEIGHTS = {
    "P1": 1.0, "P2": 1.0, "P3": 0.7, "P4": 1.0, "P5": 1.0, "P6": 0.7,
    "P7": 0.4, "P8": 0.7, "P9": 0.7, "P10": 0.4, "P11": 0.3, "P12": 0.3,
    "P13": 0.3, "P14": 0.2, "P15": 0.7, "P16": 0.2, "P17": 0.2, "P18": 0.1,
    "P19": 1.0, "P20": 0.7, "P21": 0.7, "P22": 0.3, "P23": 0.3, "P24": 0.7,
}

PATTERN_NAMES = {
    "P1": "过度强调重要性 (Undue Significance)",
    "P2": "空洞的知名度声明 (Notability)",
    "P3": "-ing 表层分析 (Superficial -ing)",
    "P4": "促销式语言 (Promotional)",
    "P5": "模糊归因 (Vague Attribution)",
    "P6": "公式化挑战段落 (Formulaic Challenges)",
    "P7": "AI 高频词汇 (AI Vocabulary)",
    "P8": "系动词回避 (Copula Avoidance)",
    "P9": "否定平行结构 (Negative Parallelism)",
    "P10": "三要素规则 (Rule of Three)",
    "P11": "过度同义词替换 (Synonym Cycling)",
    "P12": "虚假范围表述 (False Range)",
    "P13": "长破折号过度使用 (Em Dash)",
    "P14": "粗体滥用 (Boldface)",
    "P15": "行内标题列表 (Inline Header)",
    "P16": "标题大写 (Title Case)",
    "P17": "表情符号滥用 (Emoji)",
    "P18": "花引号 (Curly Quotes)",
    "P19": "聊天机器人痕迹 (Chatbot Artifacts)",
    "P20": "知识截止声明 (Cutoff Disclaimers)",
    "P21": "谄媚语气 (Sycophantic)",
    "P22": "填充短语 (Filler Phrases)",
    "P23": "过度模糊化 (Excessive Hedging)",
    "P24": "通用正面结论 (Generic Conclusions)",
}


class HumanizerService:
    """AI 文本人性化检测与修复服务"""

    def __init__(self):
        self.detectors = ALL_DETECTORS

    async def analyze(self, text: str) -> HumanizerResult:
        """
        分析文本中的 AI 写作模式
        
        Returns:
            HumanizerResult 包含所有检测到的模式匹配和修复建议
        """
        all_matches = []
        for detector in self.detectors:
            try:
                matches = detector.detect(text)
                all_matches.extend(matches)
            except Exception:
                continue

        # Sort by position
        all_matches.sort(key=lambda m: m.position)

        # Calculate score
        score = self._calculate_score(all_matches, text)

        # Generate humanized version
        humanized = self._apply_fixes(text)

        # Generate summary
        summary = self._generate_summary(all_matches, score)

        return HumanizerResult(
            original_text=text,
            humanized_text=humanized,
            matches=all_matches,
            total_issues=len(all_matches),
            score=score,
            summary=summary,
        )

    def _calculate_score(self, matches: List[PatternMatch], text: str) -> float:
        """计算 AI 化程度分数 0.0~1.0"""
        if not text or not matches:
            return 0.0

        total_weight = 0.0
        weighted_score = 0.0

        for m in matches:
            weight = DETECTOR_WEIGHTS.get(m.pattern_id, 0.3)
            total_weight += weight
            weighted_score += weight

        if total_weight == 0:
            return 0.0

        raw_score = min(weighted_score / max(total_weight, 1), total_weight / 10)
        return min(raw_score, 1.0)

    def _apply_fixes(self, text: str) -> str:
        """按顺序应用所有修复"""
        result = text
        for detector in self.detectors:
            try:
                result = detector.fix(result)
            except Exception:
                continue

        # Clean up multiple spaces, empty lines
        result = re.sub(r' {2,}', ' ', result)
        result = re.sub(r'\n{3,}', '\n\n', result)
        result = re.sub(r'\.{2,}', '.', result)
        result = re.sub(r',{2,}', ',', result)

        return result.strip()

    def _generate_summary(self, matches: List[PatternMatch], score: float) -> str:
        """生成分析摘要"""
        if not matches:
            return "[OK] No obvious AI writing patterns detected. The text looks natural."

        # Group by pattern
        pattern_counts = {}
        for m in matches:
            pattern_counts[m.pattern_id] = pattern_counts.get(m.pattern_id, 0) + 1

        severity_counts = {"high": 0, "medium": 0, "low": 0}
        for m in matches:
            if m.severity in severity_counts:
                severity_counts[m.severity] += 1

        parts = [
            f"[AI Score] {score:.0%}",
            f"   - Found {len(matches)} potential AI writing patterns",
            f"   - High: {severity_counts['high']} | Medium: {severity_counts['medium']} | Low: {severity_counts['low']}",
            "",
            "[Detected Patterns]:",
        ]

        for pid, count in sorted(pattern_counts.items()):
            name = PATTERN_NAMES.get(pid, pid)
            parts.append(f"   - {name}: {count}")

        if score > 0.3:
            parts.extend([
                "",
                "[Suggestion]: Consider using /api/humanizer/humanize endpoint for auto-fix.",
            ])

        return "\n".join(parts)


# ─── 全局单例 ────────────────────────────────────────────────

humanizer_service = HumanizerService()
