"""Brain Service 单元测试"""

import asyncio
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.brain_service import brain_service, CATEGORIES


async def test_create_and_get_entry():
    """测试创建和获取条目"""
    # Create
    entry = await brain_service.create_entry(
        category="people",
        title="Test Person Zhang San",
        data={"age": 28, "occupation": "Engineer"},
        notes="Met at tech conference"
    )
    print(f"\n[CREATE] Created: {entry.category}/{entry.id}")
    print(f"  Title: {entry.title}")
    print(f"  File: {entry.file_path}")

    # Get
    fetched = await brain_service.get_entry("people", entry.id)
    assert fetched is not None, "Failed to fetch entry"
    print(f"[GET] Fetched: {fetched.title}")
    print(f"  Frontmatter: age={fetched.frontmatter.get('age')}")

    # Search
    results = await brain_service.search("Zhang San")
    assert results.total > 0, "Search should find entry"
    print(f"[SEARCH] Found {results.total} results for 'Zhang San'")

    return entry


async def test_create_place_with_notes():
    """测试创建地点条目"""
    entry = await brain_service.create_entry(
        category="places",
        title="Cafe Mocha Shanghai",
        data={
            "category": "cafe",
            "location": "Shanghai",
            "cuisine": "Coffee & Dessert",
            "rating": 4.5,
        },
        notes="Great pour-over coffee. Try the tiramisu."
    )
    print(f"\n[PLACE] Created: {entry.category}/{entry.id}")
    print(f"  Location: {entry.frontmatter.get('location')}")
    return entry


async def test_update_entry():
    """测试更新条目"""
    entry = await brain_service.create_entry(
        category="games",
        title="Elden Ring",
        data={"genre": "Action RPG", "platform": "PC"},
        notes="Just started playing"
    )
    print(f"\n[UPDATE BEFORE] {entry.title}")

    updated = await brain_service.update_entry(
        category="games",
        slug=entry.id,
        data={"rating": 9.5, "status": "playing"},
        notes="Reached level 45, amazing open world"
    )
    assert updated is not None
    print(f"[UPDATE AFTER] Rating: {updated.frontmatter.get('rating')}")
    print(f"  Notes include 'level 45': {'level 45' in updated.content}")


async def test_list_and_search():
    """测试列出和搜索"""
    # Create several entries
    entries_data = [
        ("tech", "MacBook Pro M4", {"brand": "Apple", "specs": "M4 chip, 32GB RAM"}),
        ("tech", "RTX 5090", {"brand": "NVIDIA", "specs": "32GB VRAM"}),
        ("media", "Three-Body Problem", {"author": "Liu Cixin", "genre": "Sci-Fi"}),
        ("orgs", "OpenAI", {"industry": "AI", "founders": "Sam Altman"}),
        ("ideas", "AI-powered garden system", {"status": "concept"}),
    ]
    for cat, title, data in entries_data:
        await brain_service.create_entry(category=cat, title=title, data=data)

    # List all
    all_entries = await brain_service.list_entries(limit=20)
    print(f"\n[LIST ALL] Total: {len(all_entries)} entries")

    # List by category
    tech_entries = await brain_service.list_entries(category="tech")
    print(f"[LIST tech] Found {len(tech_entries)} tech entries")

    # Search
    results = await brain_service.search("MacBook")
    print(f"[SEARCH MacBook] Found {results.total} results")
    for e in results.entries:
        print(f"  - [{e.category}] {e.title}")

    results2 = await brain_service.search("AI")
    print(f"[SEARCH AI] Found {results2.total} results")
    for e in results2.entries:
        print(f"  - [{e.category}] {e.title}")


async def test_stats():
    """测试统计"""
    stats = await brain_service.get_stats()
    print(f"\n[STATS] Total entries: {stats['total_entries']}")
    for cat, info in stats['categories'].items():
        if info['count'] > 0:
            cat_label = {"people":"Person", "places":"Place", "games":"Game",
                         "tech":"Tech", "events":"Event", "media":"Media",
                         "ideas":"Idea", "orgs":"Org"}.get(cat, cat)
            print(f"  [{cat_label}] count={info['count']}")


async def test_templates():
    """测试模板"""
    templates = brain_service.list_templates()
    print(f"\n[TEMPLATES] Available: {len(templates)}")
    for t in templates:
        print(f"  - {t['id']} (file: {t['file']})")

    person_template = brain_service.get_template("person")
    assert person_template is not None
    print(f"[TEMPLATE person] Length: {len(person_template)} chars")


async def test_delete():
    """测试删除"""
    entry = await brain_service.create_entry(
        category="ideas",
        title="Temporary test idea",
        notes="Will be deleted"
    )
    print(f"\n[DELETE] Created temp entry: {entry.id}")

    deleted = await brain_service.delete_entry("ideas", entry.id)
    assert deleted, "Delete should succeed"
    print(f"[DELETE] Successfully deleted: {entry.id}")

    # Verify gone
    fetched = await brain_service.get_entry("ideas", entry.id)
    assert fetched is None, "Entry should not exist after deletion"
    print(f"[VERIFY] Entry confirmed deleted")


async def cleanup():
    """清理测试数据"""
    import shutil
    from pathlib import Path
    from app.services.brain_service import BRAIN_ROOT

    entries = await brain_service.list_entries(limit=100)
    for e in entries:
        await brain_service.delete_entry(e.category, e.id)
    print(f"\n[CLEANUP] Removed all test entries")


if __name__ == "__main__":
    print("=" * 60)
    print("Brain Service Tests")
    print("=" * 60)

    asyncio.run(test_create_and_get_entry())
    asyncio.run(test_create_place_with_notes())
    asyncio.run(test_update_entry())
    asyncio.run(test_list_and_search())
    asyncio.run(test_stats())
    asyncio.run(test_templates())
    asyncio.run(test_delete())

    # Cleanup test data
    asyncio.run(cleanup())

    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
