# Xiaohongshu Page Selectors Reference

This document contains CSS selectors for extracting content from Xiaohongshu pages.

## Search Results Page

URL Pattern: `https://www.xiaohongshu.com/search_result?keyword=xxx`

### Note Cards

```css
/* Primary selectors */
section.note-item
div[data-v-note-item]
a.cover

/* Fallback selectors */
div.search-result a[href*='/explore/']
```

### Note Card Elements

| Element | Selectors |
|---------|-----------|
| Title | `div.title`, `span.title`, `a.title`, `.note-content .title` |
| Author | `div.author-wrapper .name`, `span.author-name`, `.author .name` |
| Cover Image | `img` (first child) |
| Likes | `span.count`, `span.like-count` |
| Link | `a[href*='/explore/']` |

## Note Detail Page

URL Pattern: `https://www.xiaohongshu.com/explore/{note_id}`

### Main Elements

| Element | Selectors |
|---------|-----------|
| Title | `div.title`, `h1.title`, `#detail-title` |
| Author | `div.author-wrapper .username`, `.author-info .name` |
| Content | `div.note-content`, `div.desc`, `#detail-desc` |
| Images | `div.carousel img`, `div.note-image img`, `.swiper-slide img` |

### Engagement Counts

| Element | Selectors |
|---------|-----------|
| Likes | `[class*='like'] span`, `span:contains('点赞')` |
| Collects | `[class*='collect'] span`, `span:contains('收藏')` |
| Comments | `[class*='comment'] span`, `span:contains('评论')` |

### Tags

```css
a.tag
[class*='tag']
a[href*='/search_result/']
```

## Comments Section

### Comment Elements

| Element | Selectors |
|---------|-----------|
| Comment Container | `div.comment-item`, `div.comments-item`, `[class*='comment']` |
| Author | `.username`, `.name`, `[class*='author']` |
| Content | `.content`, `.comment-content`, `[class*='content']` |
| Likes | `.like-count`, `[class*='like']`, `span.count` |

## User Profile Page

URL Pattern: `https://www.xiaohongshu.com/user/profile/{user_id}`

### User Info

| Element | Selectors |
|---------|-----------|
| Username | `.user-name`, `[class*='username']` |
| Bio | `.user-desc`, `.bio` |
| Stats | `.stats`, `[class*='count']` |

## Login Detection

### Login Page Indicators

```css
/* Elements that indicate user is NOT logged in */
a:contains('登录')
button:contains('登录')
div:contains('登录/注册')
```

### Logged In Indicators

- Absence of login buttons
- Presence of user avatar
- Presence of user-specific elements

## Notes

1. Xiaohongshu uses dynamic class names with Vue.js
2. Selectors may need updates when site structure changes
3. Some content is loaded via JavaScript after page load
4. Use `wait --load networkidle` before extracting content

## Anti-Detection Tips

1. Use realistic request delays (2-3 seconds between actions)
2. Don't scroll too fast
3. Use session persistence to avoid repeated logins
4. Headed mode is more stable than headless for complex pages
