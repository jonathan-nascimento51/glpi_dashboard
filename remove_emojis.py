#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

def remove_emojis_from_file(file_path):
    """Remove emojis de um arquivo Python"""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Lista de emojis específicos para remover
    emojis_to_remove = [
        '🧪', '📅', '🔐', '✅', '🔍', '📊', '📋', '👤', '⚠️', '🎯', '🔧', '🔒',
        '🚀', '💡', '📈', '📉', '🔄', '⏰', '📝', '🎨', '🔥', '💻', '🌟', '⭐',
        '🎉', '🎊', '🎈', '🎁', '🎂', '🍰', '🍕', '🍔', '🍟', '🍗', '🍖', '🥓'
    ]
    
    # Remove cada emoji
    for emoji in emojis_to_remove:
        content = content.replace(emoji, '')
    
    # Remove espaços extras que podem ter sobrado
    content = re.sub(r'\s+', ' ', content)
    content = re.sub(r'" +"', '""', content)
    content = re.sub(r'print\(" +', 'print("', content)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"Emojis removidos de {file_path}")

if __name__ == "__main__":
    remove_emojis_from_file("test_glpi_date_filter.py")