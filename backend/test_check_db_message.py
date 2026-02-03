#!/usr/bin/env python3
"""
Test script to check if the latest message in the database contains HTML/animation content.
"""

import sqlite3
import re

DATABASE_FILE = 'paper_agent.db'


def get_latest_messages(limit=5):
    """Get the latest messages from the database."""
    conn = sqlite3.connect(DATABASE_FILE)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT m.id, m.paper_id, m.text, m.is_user, m.created_at, p.title
        FROM messages m
        LEFT JOIN papers p ON m.paper_id = p.id
        ORDER BY m.created_at DESC
        LIMIT ?
    ''', (limit,))

    messages = cursor.fetchall()
    conn.close()
    return messages


def check_html_content(text):
    """Check for various HTML elements in the text."""
    checks = {
        'animation_markers_new': r'<<<ANIMATION_START>>>',
        'animation_markers_old': r'<!--ANIMATION_START-->',
        'html_tag': r'<html',
        'head_tag': r'<head',
        'body_tag': r'<body',
        'style_tag': r'<style',
        'script_tag': r'<script',
        'doctype': r'<!DOCTYPE',
        'any_html_tag': r'<[a-zA-Z][^>]*>',
    }

    results = {}
    for name, pattern in checks.items():
        match = re.search(pattern, text, re.IGNORECASE)
        results[name] = bool(match)

    return results


def main():
    print("=" * 60)
    print("Database Message HTML Check")
    print("=" * 60)

    messages = get_latest_messages(5)

    if not messages:
        print("\nNo messages found in database.")
        return

    print(f"\nFound {len(messages)} latest messages:\n")

    for i, (msg_id, paper_id, text, is_user, created_at, paper_title) in enumerate(messages):
        print(f"--- Message {i+1} ---")
        print(f"ID: {msg_id}")
        print(f"Paper: {paper_title or 'Unknown'}")
        print(f"Is User: {bool(is_user)}")
        print(f"Created: {created_at}")
        print(f"Text Length: {len(text)} chars")

        # Check HTML content
        html_checks = check_html_content(text)

        print("\nHTML Content Checks:")
        for check_name, found in html_checks.items():
            status = "FOUND" if found else "not found"
            print(f"  - {check_name}: {status}")

        # Show preview of text
        print(f"\nText Preview (first 500 chars):")
        print("-" * 40)
        preview = text[:500]
        print(preview)
        if len(text) > 500:
            print(f"... [{len(text) - 500} more chars]")
        print("-" * 40)

        # If animation markers found, show the animation content
        if html_checks['animation_markers_new']:
            match = re.search(r'<<<ANIMATION_START>>>([\s\S]*?)<<<ANIMATION_END>>>', text)
            if match:
                animation_content = match.group(1).strip()
                print(f"\nAnimation Content Found ({len(animation_content)} chars):")
                print("-" * 40)
                print(animation_content[:1000])
                if len(animation_content) > 1000:
                    print(f"... [{len(animation_content) - 1000} more chars]")
                print("-" * 40)

        if html_checks['animation_markers_old']:
            match = re.search(r'<!--ANIMATION_START-->([\s\S]*?)<!--ANIMATION_END-->', text)
            if match:
                animation_content = match.group(1).strip()
                print(f"\nOLD Animation Markers Content Found ({len(animation_content)} chars):")
                print("-" * 40)
                print(animation_content[:1000])
                if len(animation_content) > 1000:
                    print(f"... [{len(animation_content) - 1000} more chars]")
                print("-" * 40)

        print("\n")

    print("=" * 60)
    print("Summary")
    print("=" * 60)

    # Check if any message has animation content
    has_animation = False
    for msg_id, paper_id, text, is_user, created_at, paper_title in messages:
        if '<<<ANIMATION_START>>>' in text or '<!--ANIMATION_START-->' in text:
            has_animation = True
            break

    if has_animation:
        print("Animation content found in recent messages.")
    else:
        print("No animation content found in recent messages.")


if __name__ == '__main__':
    main()
