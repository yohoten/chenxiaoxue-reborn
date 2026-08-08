"""Humanizer 服务单元测试"""

import asyncio
import sys
import os
import pytest

# Add parent directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.humanizer_service import HumanizerService


@pytest.mark.asyncio
async def test_basic_analysis():
    """测试基本分析功能"""
    service = HumanizerService()
    
    test_texts = [
        # AI 化文本 (应检测出多项问题)
        (
            "The new software update serves as a testament to the company's commitment to innovation. "
            "Moreover, it provides a seamless, intuitive, and powerful user experience—ensuring "
            "that users can accomplish their goals efficiently. It's not just an update, it's a "
            "revolution in how we think about productivity. Industry experts believe this will have "
            "a lasting impact on the entire sector, highlighting the company's pivotal role in the "
            "evolving technological landscape.",
            "AI-marked text"
        ),
        # 中性文本 (应检测出较少问题)
        (
            "The software update adds batch processing, keyboard shortcuts, and offline mode. "
            "Early feedback from beta testers has been positive, with most reporting faster task completion.",
            "Human-like text"
        ),
    ]
    
    for text, label in test_texts:
        result = await service.analyze(text)
        print(f"\n{'='*60}")
        print(f"[TEST] {label}")
        print(f"{'='*60}")
        print(f"  AI Score: {result.score:.2f}")
        print(f"  Issues detected: {result.total_issues}")
        print(f"  Summary: {result.summary[:80]}...")
        print(f"\n  Original ({len(text)} chars):")
        print(f"    {text[:100]}...")
        print(f"\n  Humanized ({len(result.humanized_text)} chars):")
        print(f"    {result.humanized_text[:200]}...")


@pytest.mark.asyncio
async def test_specific_patterns():
    """测试特定模式检测"""
    service = HumanizerService()
    
    pattern_tests = [
        ("P1 - Significance", "The Statistical Institute of Catalonia was officially established in 1989, marking a pivotal moment in the evolution of regional statistics."),
        ("P4 - Promotional", "Nestled within the breathtaking region of Gonder in Ethiopia, this vibrant town stands as a must-visit destination with stunning natural beauty."),
        ("P5 - Vague", "Due to its unique characteristics, experts believe the river plays a crucial role in the regional ecosystem."),
        ("P7 - AI Vocab", "Additionally, a distinctive feature is the incorporation of camel meat. An enduring testament to colonial influence is the widespread adoption of pasta, showcasing integration."),
        ("P19 - Chatbot", "Here is an overview of the French Revolution. I hope this helps! Let me know if you'd like me to expand on any section."),
        ("P22 - Filler", "In order to achieve this goal, due to the fact that the system has the ability to process data, at this point in time we will proceed."),
    ]
    
    for label, text in pattern_tests:
        result = await service.analyze(text)
        print(f"\n{label}: {result.total_issues} issues, Score={result.score:.2f}")
        if result.matches:
            for m in result.matches[:3]:
                print(f"  [{m.pattern_id}] \"{m.snippet[:50]}...\" -> {m.suggestion[:40]}")


@pytest.mark.asyncio
async def test_humanize_endpoint():
    """测试人性化改写效果"""
    service = HumanizerService()
    
    text = (
        "The new software update serves as a testament to the company's commitment to innovation. "
        "Moreover, it provides a seamless, intuitive, and powerful user experience—ensuring "
        "that users can accomplish their goals efficiently."
    )
    
    result = await service.analyze(text)
    
    print(f"\n{'='*60}")
    print("[DEMO] Humanize 效果演示")
    print(f"{'='*60}")
    print(f"\n[ORIGINAL]:\n  {text}")
    print(f"\n[HUMANIZED]:\n  {result.humanized_text}")
    print(f"\n[SCORE]: {result.score:.2f} | Issues found: {result.total_issues}")


if __name__ == "__main__":
    asyncio.run(test_basic_analysis())
    print("\n" + "="*60)
    asyncio.run(test_specific_patterns())
    print("\n" + "="*60)
    asyncio.run(test_humanize_endpoint())
    print("\n[DONE] All tests completed!")
