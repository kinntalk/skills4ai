"""
XHS OFM Formatter
Format Xiaohongshu content as Obsidian Flavored Markdown.
"""

import os
import re
import requests
from pathlib import Path
from datetime import datetime
from typing import Optional, List
from urllib.parse import quote

try:
    from .content_extractor import NoteInfo, CommentInfo, SearchResult
except ImportError:
    from content_extractor import NoteInfo, CommentInfo, SearchResult


class OFMFormatter:
    """Format Xiaohongshu content as Obsidian Flavored Markdown."""
    
    def __init__(self, vault_path: Path, asset_folder: Path, wikilink: bool = True):
        self.vault_path = vault_path
        self.asset_folder = asset_folder
        self.wikilink = wikilink
    
    def format_search_result(self, result: SearchResult, tags: List[str] = None) -> str:
        lines = []
        
        frontmatter = self._create_frontmatter(
            title=f"小红书搜索 - {result.keyword}",
            tags=tags or ["xhs-search", result.keyword],
            source=f"https://www.xiaohongshu.com/search_result?keyword={quote(result.keyword)}"
        )
        lines.append(frontmatter)
        lines.append("")
        lines.append(f"# 小红书搜索结果：{result.keyword}")
        lines.append("")
        lines.append("> [!info] 搜索信息")
        lines.append(f"> - 关键词: {result.keyword}")
        lines.append(f"> - 搜索时间: {result.search_time}")
        lines.append(f"> - 结果数量: {result.total}")
        lines.append("")
        lines.append("## 笔记列表")
        lines.append("")
        
        for i, note in enumerate(result.notes, 1):
            note_md = self._format_note_card(note, i)
            lines.append(note_md)
            lines.append("")
        
        return "\n".join(lines)
    
    def format_note_detail(self, note: NoteInfo, tags: List[str] = None, include_comments: bool = False, comments: List[CommentInfo] = None) -> str:
        lines = []
        
        all_tags = tags or ["xhs-note"]
        all_tags.extend(note.tags)
        
        frontmatter = self._create_frontmatter(
            title=note.title,
            tags=list(set(all_tags)),
            source=note.url,
            author=note.author,
            xhs_id=note.xhs_id,
            publish_date=note.publish_date,
            likes=note.likes,
            comments=note.comments
        )
        lines.append(frontmatter)
        lines.append("")
        lines.append(f"# {note.title}")
        lines.append("")
        lines.append("> [!info] 笔记信息")
        lines.append(f"> - **作者**: [[{note.author}]]")
        if note.xhs_id:
            lines.append(f"> - **小红书号**: {note.xhs_id}")
        if note.publish_date:
            lines.append(f"> - **发布时间**: {note.publish_date}")
        lines.append(f"> - **点赞**: {note.likes} | **收藏**: {note.collects} | **评论**: {note.comments}")
        lines.append(f"> - **链接**: [查看原文]({note.url})")
        lines.append("")
        
        if note.cover_url or note.images:
            lines.append("## 封面")
            lines.append("")
            if note.cover_url:
                img_ref = self._download_and_reference_image(note.cover_url, note.note_id, 0)
                lines.append(f"{img_ref}")
                lines.append("")
        
        if note.content:
            lines.append("## 正文")
            lines.append("")
            lines.append(note.content)
            lines.append("")
        
        if note.images and len(note.images) > 1:
            lines.append("## 图片")
            lines.append("")
            for i, img_url in enumerate(note.images[1:], 1):
                img_ref = self._download_and_reference_image(img_url, note.note_id, i)
                lines.append(f"{img_ref}")
            lines.append("")
        
        if include_comments and comments:
            lines.append("## 评论区")
            lines.append("")
            for comment in comments[:20]:
                lines.append(self._format_comment(comment))
                lines.append("")
        
        return "\n".join(lines)
    
    def format_comments(self, note: NoteInfo, comments: List[CommentInfo], tags: List[str] = None) -> str:
        lines = []
        
        frontmatter = self._create_frontmatter(
            title=f"评论 - {note.title}",
            tags=tags or ["xhs-comments"],
            source=note.url
        )
        lines.append(frontmatter)
        lines.append("")
        lines.append(f"# 评论：{note.title}")
        lines.append("")
        lines.append(f"> 笔记链接: [{note.url}]({note.url})")
        lines.append("")
        lines.append(f"共 {len(comments)} 条评论")
        lines.append("")
        
        for comment in comments:
            lines.append(self._format_comment(comment))
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def _create_frontmatter(self, title: str, tags: List[str], source: str, author: str = None, xhs_id: str = None, publish_date: str = None, likes: str = None, comments: str = None) -> str:
        lines = ["---"]
        lines.append(f"title: {self._escape_yaml(title)}")
        lines.append(f"date: {datetime.now().strftime('%Y-%m-%d')}")
        if author:
            lines.append(f"author: {self._escape_yaml(author)}")
        if xhs_id:
            lines.append(f"xhs_id: {self._escape_yaml(xhs_id)}")
        if publish_date:
            lines.append(f"publish_date: {self._escape_yaml(publish_date)}")
        if likes:
            lines.append(f"likes: {self._escape_yaml(likes)}")
        if comments:
            lines.append(f"comments: {self._escape_yaml(comments)}")
        lines.append("tags:")
        for tag in tags:
            lines.append(f"  - {self._sanitize_tag(tag)}")
        lines.append(f"source: {source}")
        lines.append("---")
        return "\n".join(lines)
    
    def _format_note_card(self, note: NoteInfo, index: int) -> str:
        lines = []
        lines.append(f"### {index}. {note.title}")
        lines.append("")
        
        if note.cover_url:
            img_ref = self._download_and_reference_image(note.cover_url, note.note_id, 0)
            lines.append(f"{img_ref}")
            lines.append("")
        
        lines.append(f"- **作者**: [[{note.author}]]")
        lines.append(f"- **点赞**: {note.likes}")
        if note.collects and note.collects != "0":
            lines.append(f"- **收藏**: {note.collects}")
        if note.comments and note.comments != "0":
            lines.append(f"- **评论**: {note.comments}")
        lines.append(f"- **链接**: [查看原文]({note.url})")
        lines.append("")
        
        if note.content:
            lines.append(f"**摘要**: {note.content[:200]}...")
        
        lines.append("")
        lines.append("---")
        
        return "\n".join(lines)
    
    def _format_comment(self, comment: CommentInfo) -> str:
        lines = []
        lines.append(f"> [!quote] {comment.author}")
        lines.append(f"> {comment.content}")
        if comment.likes != "0":
            lines.append(f"> ")
            lines.append(f"> ❤️ {comment.likes}")
        return "\n".join(lines)
    
    def _download_and_reference_image(self, url: str, note_id: str, index: int) -> str:
        if not url:
            return ""
        
        try:
            self.asset_folder.mkdir(parents=True, exist_ok=True)
            
            timestamp = datetime.now().strftime("%Y-%m-%d")
            ext = ".jpg"
            if "." in url.split("?")[0]:
                ext = "." + url.split("?")[0].split(".")[-1]
                if ext not in [".jpg", ".jpeg", ".png", ".gif", ".webp"]:
                    ext = ".jpg"
            
            filename = f"xhs-{note_id}-{timestamp}-{index}{ext}"
            filepath = self.asset_folder / filename
            
            if not filepath.exists():
                response = requests.get(url, timeout=30, headers={
                    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
                })
                if response.status_code == 200:
                    with open(filepath, "wb") as f:
                        f.write(response.content)
            
            if self.wikilink:
                return f"![[{filename}|300]]"
            else:
                rel_path = filepath.relative_to(self.vault_path)
                return f"![image]({rel_path})"
        except Exception:
            return f"![image]({url})"
    
    def _escape_yaml(self, text: str) -> str:
        text = text.replace("\\", "\\\\")
        text = text.replace('"', '\\"')
        text = text.replace("\n", " ")
        if any(c in text for c in [":", "#", "{", "}", "[", "]", ",", "&", "*", "?", "|", "-", "<", ">", "=", "!", "%", "@", "`"]):
            return f'"{text}"'
        return text
    
    def _sanitize_tag(self, tag: str) -> str:
        tag = re.sub(r'[^\w\u4e00-\u9fff\-_/]', '', tag)
        tag = tag.strip('-/_')
        if not tag:
            return "untagged"
        if tag[0].isdigit():
            tag = "_" + tag
        return tag
    
    def save_to_vault(self, content: str, filename: str, subfolder: str = None) -> Path:
        if subfolder:
            output_dir = self.vault_path / subfolder
        else:
            output_dir = self.vault_path
        
        output_dir.mkdir(parents=True, exist_ok=True)
        
        if not filename.endswith(".md"):
            filename += ".md"
        
        filepath = output_dir / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        
        return filepath
