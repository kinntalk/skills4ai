"""
XHS Content Extractor
Extract notes and comments from Xiaohongshu pages.
"""

import re
import json
from typing import Optional
from bs4 import BeautifulSoup
from dataclasses import dataclass, field, asdict
from datetime import datetime


@dataclass
class NoteInfo:
    note_id: str
    title: str
    author: str
    author_id: Optional[str] = None
    xhs_id: Optional[str] = None
    likes: str = "0"
    collects: str = "0"
    comments: str = "0"
    publish_date: Optional[str] = None
    cover_url: Optional[str] = None
    images: list = field(default_factory=list)
    content: str = ""
    url: str = ""
    tags: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CommentInfo:
    author: str
    content: str
    author_id: Optional[str] = None
    likes: str = "0"
    time: Optional[str] = None
    replies: list = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SearchResult:
    keyword: str
    notes: list = field(default_factory=list)
    total: int = 0
    search_time: str = ""
    
    def to_dict(self) -> dict:
        return {
            "keyword": self.keyword,
            "notes": [n.to_dict() for n in self.notes],
            "total": self.total,
            "search_time": self.search_time
        }


class XHSExtractor:
    """Extract content from Xiaohongshu pages."""
    
    NOTE_ID_PATTERN = re.compile(r'/explore/([a-zA-Z0-9]+)')
    USER_ID_PATTERN = re.compile(r'/user/profile/([a-zA-Z0-9]+)')
    
    def __init__(self):
        pass
    
    def extract_search_results(self, html: str, keyword: str) -> SearchResult:
        soup = BeautifulSoup(html, "html.parser")
        result = SearchResult(
            keyword=keyword,
            search_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        )
        
        notes = self._extract_note_cards(soup)
        result.notes = notes
        result.total = len(notes)
        
        return result
    
    def _extract_note_cards(self, soup: BeautifulSoup) -> list:
        notes = []
        
        note_cards = soup.select("section.note-item, div[data-v-note-item], a.cover")
        
        if not note_cards:
            note_cards = soup.select("div.search-result a[href*='/explore/']")
        
        for card in note_cards:
            note = self._extract_single_card(card)
            if note:
                notes.append(note)
        
        return notes
    
    def _extract_single_card(self, element) -> Optional[NoteInfo]:
        try:
            href = element.get("href", "") or element.select_one("a[href*='/explore/']")
            if isinstance(href, str):
                pass
            else:
                href = href.get("href", "") if href else ""
            
            note_id_match = self.NOTE_ID_PATTERN.search(href)
            if not note_id_match:
                href_elem = element.select_one("a[href*='/explore/']") if hasattr(element, 'select_one') else None
                if href_elem:
                    href = href_elem.get("href", "")
                    note_id_match = self.NOTE_ID_PATTERN.search(href)
            
            if not note_id_match:
                return None
            
            note_id = note_id_match.group(1)
            
            title = self._extract_title(element)
            author = self._extract_author(element)
            cover_url = self._extract_cover(element)
            likes = self._extract_likes(element)
            
            return NoteInfo(
                note_id=note_id,
                title=title,
                author=author,
                likes=likes,
                cover_url=cover_url,
                url=f"https://www.xiaohongshu.com/explore/{note_id}"
            )
        except Exception:
            return None
    
    def _extract_title(self, element) -> str:
        title_selectors = [
            "div.title",
            "span.title",
            "a.title",
            ".note-content .title",
            "[class*='title']"
        ]
        
        for selector in title_selectors:
            title_elem = element.select_one(selector)
            if title_elem:
                return title_elem.get_text(strip=True)
        
        return "无标题"
    
    def _extract_author(self, element) -> str:
        author_selectors = [
            "div.author-wrapper .name",
            "span.author-name",
            ".author .name",
            "[class*='author']",
            "a[href*='/user/profile/']"
        ]
        
        for selector in author_selectors:
            author_elem = element.select_one(selector)
            if author_elem:
                return author_elem.get_text(strip=True)
        
        return "未知作者"
    
    def _extract_cover(self, element) -> Optional[str]:
        img = element.select_one("img")
        if img:
            return img.get("src") or img.get("data-src")
        return None
    
    def _extract_likes(self, element) -> str:
        like_selectors = [
            "span.count",
            "span.like-count",
            "[class*='like']",
            "[class*='count']"
        ]
        
        for selector in like_selectors:
            like_elem = element.select_one(selector)
            if like_elem:
                text = like_elem.get_text(strip=True)
                if text:
                    return text
        
        return "0"
    
    def extract_note_detail(self, html: str, note_id: str) -> Optional[NoteInfo]:
        soup = BeautifulSoup(html, "html.parser")
        
        try:
            title = self._extract_detail_title(soup)
            author = self._extract_detail_author(soup)
            xhs_id = self._extract_detail_xhs_id(soup)
            publish_date = self._extract_detail_publish_date(soup)
            content = self._extract_detail_content(soup)
            images = self._extract_detail_images(soup)
            likes = self._extract_detail_likes(soup)
            collects = self._extract_detail_collects(soup)
            comments = self._extract_detail_comments_count(soup)
            tags = self._extract_detail_tags(soup)
            
            return NoteInfo(
                note_id=note_id,
                title=title,
                author=author,
                xhs_id=xhs_id,
                publish_date=publish_date,
                content=content,
                images=images,
                likes=likes,
                collects=collects,
                comments=comments,
                tags=tags,
                url=f"https://www.xiaohongshu.com/explore/{note_id}"
            )
        except Exception:
            return None
    
    def _extract_detail_title(self, soup: BeautifulSoup) -> str:
        title_selectors = [
            "div.title",
            "h1.title",
            "#detail-title",
            "[class*='title']"
        ]
        
        for selector in title_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return "无标题"
    
    def _extract_detail_author(self, soup: BeautifulSoup) -> str:
        author_selectors = [
            "div.author-wrapper .username",
            ".author-info .name",
            "[class*='author-name']",
            "a[href*='/user/profile/']"
        ]
        
        for selector in author_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return "未知作者"
    
    def _extract_detail_xhs_id(self, soup: BeautifulSoup) -> Optional[str]:
        """提取作者的小红书号"""
        xhs_id_selectors = [
            "div.author-wrapper .user-id",
            ".author-info .xhs-id",
            "[class*='user-id']",
            "[class*='xhs-id']",
        ]
        
        for selector in xhs_id_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text and text != "小红书号":
                    return text
        
        return None
    
    def _extract_detail_publish_date(self, soup: BeautifulSoup) -> Optional[str]:
        """提取发布日期"""
        date_selectors = [
            "div.date",
            "span.date",
            "[class*='date']",
            "time",
        ]
        
        for selector in date_selectors:
            elem = soup.select_one(selector)
            if elem:
                text = elem.get_text(strip=True)
                if text and len(text) >= 8:
                    return text
        
        return None
    
    def _extract_detail_content(self, soup: BeautifulSoup) -> str:
        content_selectors = [
            "div.note-content",
            "div.desc",
            "#detail-desc",
            "[class*='content']",
            "[class*='desc']"
        ]
        
        for selector in content_selectors:
            elem = soup.select_one(selector)
            if elem:
                return elem.get_text(strip=True)
        
        return ""
    
    def _extract_detail_images(self, soup: BeautifulSoup) -> list:
        images = []
        img_selectors = [
            "div.carousel img",
            "div.note-image img",
            ".swiper-slide img",
            "[class*='image'] img"
        ]
        
        for selector in img_selectors:
            imgs = soup.select(selector)
            for img in imgs:
                src = img.get("src") or img.get("data-src")
                if src and src not in images:
                    images.append(src)
        
        return images
    
    def _extract_detail_likes(self, soup: BeautifulSoup) -> str:
        return self._extract_engagement_count(soup, "like", "点赞")
    
    def _extract_detail_collects(self, soup: BeautifulSoup) -> str:
        return self._extract_engagement_count(soup, "collect", "收藏")
    
    def _extract_detail_comments_count(self, soup: BeautifulSoup) -> str:
        return self._extract_engagement_count(soup, "comment", "评论")
    
    def _extract_engagement_count(self, soup: BeautifulSoup, class_hint: str, text_hint: str) -> str:
        selectors = [
            f"[class*='{class_hint}'] span",
            f"[class*='{class_hint}']",
            f"span:contains('{text_hint}')",
        ]
        
        for selector in selectors:
            try:
                elems = soup.select(selector)
                for elem in elems:
                    text = elem.get_text(strip=True)
                    if text and (text.isdigit() or '万' in text or 'k' in text.lower()):
                        return text
            except Exception:
                continue
        
        return "0"
    
    def _extract_detail_tags(self, soup: BeautifulSoup) -> list:
        tags = []
        tag_selectors = [
            "a.tag",
            "[class*='tag']",
            "a[href*='/search_result/']"
        ]
        
        for selector in tag_selectors:
            elems = soup.select(selector)
            for elem in elems:
                tag = elem.get_text(strip=True).lstrip("#")
                if tag and tag not in tags:
                    tags.append(tag)
        
        return tags
    
    def extract_comments(self, html: str, limit: int = 50) -> list:
        soup = BeautifulSoup(html, "html.parser")
        comments = []
        
        comment_selectors = [
            "div.comment-item",
            "div.comments-item",
            "[class*='comment']",
        ]
        
        comment_elems = []
        for selector in comment_selectors:
            comment_elems = soup.select(selector)
            if comment_elems:
                break
        
        for i, elem in enumerate(comment_elems[:limit]):
            comment = self._extract_single_comment(elem)
            if comment:
                comments.append(comment)
        
        return comments
    
    def _extract_single_comment(self, element) -> Optional[CommentInfo]:
        try:
            author = "匿名用户"
            author_selectors = [".username", ".name", "[class*='author']"]
            for selector in author_selectors:
                author_elem = element.select_one(selector)
                if author_elem:
                    author = author_elem.get_text(strip=True)
                    break
            
            content = ""
            content_selectors = [".content", ".comment-content", "[class*='content']"]
            for selector in content_selectors:
                content_elem = element.select_one(selector)
                if content_elem:
                    content = content_elem.get_text(strip=True)
                    break
            
            likes = "0"
            like_selectors = [".like-count", "[class*='like']", "span.count"]
            for selector in like_selectors:
                like_elem = element.select_one(selector)
                if like_elem:
                    likes = like_elem.get_text(strip=True)
                    break
            
            return CommentInfo(
                author=author,
                content=content,
                likes=likes
            )
        except Exception:
            return None
    
    def extract_note_id_from_url(self, url: str) -> Optional[str]:
        match = self.NOTE_ID_PATTERN.search(url)
        if match:
            return match.group(1)
        return None
