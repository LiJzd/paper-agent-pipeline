# Literature Search - 学术文献搜索

基于 Semantic Scholar API 的学术文献搜索 skill，用于论文工作流的文献搜索阶段。

## 功能

| 功能 | 说明 |
|------|------|
| 关键词搜索 | 按关键词搜索论文，获取标题、摘要、年份、引用数 |
| 引用追踪 | 获取某篇论文的引用列表或参考文献列表 |
| 影响力评估 | 按引用量、影响力评分排序 |
| 作者搜索 | 按作者名搜索所有论文 |
| 相关推荐 | 基于种子论文推荐相关文献 |

## 使用方式

### 搜索论文
```bash
python3 ~/.claude/skills/literature-search/scripts/s2_search.py search "query" --limit 20 --fields title,year,citationCount,abstract,authors
```

### 获取论文详情
```bash
python3 ~/.claude/skills/literature-search/scripts/s2_search.py paper <paper_id> --fields title,year,citationCount,abstract,authors,referenceCount
```

### 获取引用列表
```bash
python3 ~/.claude/skills/literature-search/scripts/s2_search.py citations <paper_id> --limit 20 --fields title,year,citationCount
```

### 获取参考文献
```bash
python3 ~/.claude/skills/literature-search/scripts/s2_search.py references <paper_id> --limit 20 --fields title,year,citationCount
```

### 作者搜索
```bash
python3 ~/.claude/skills/literature-search/scripts/s2_search.py author "author name" --limit 10 --fields name,hIndex,citationCount,paperCount
```

### 相关论文推荐
```bash
python3 ~/.claude/skills/literature-search/scripts/s2_search.py recommend <paper_id> --limit 10
```

## 参数说明

### fields 可选值
- `title` - 标题
- `abstract` - 摘要
- `year` - 年份
- `citationCount` - 引用数
- `referenceCount` - 参考文献数
- `authors` - 作者列表
- `venue` - 期刊/会议
- `url` - 链接
- `externalIds` - 外部 ID（DOI, ArXiv 等）
- `influentialCitationCount` - 有影响力的引用数
- `isOpenAccess` - 是否开放获取
- `fieldsOfStudy` - 研究领域
- `tldr` - AI 生成的简短摘要

### 排序选项
搜索结果默认按相关性排序。可通过 `--sort citationCount:desc` 按引用量排序。

## 输出格式

所有命令输出 JSON 格式，便于后续处理。

### 搜索结果示例
```json
{
  "total": 1234,
  "offset": 0,
  "limit": 20,
  "papers": [
    {
      "paperId": "abc123",
      "title": "Paper Title",
      "year": 2024,
      "citationCount": 150,
      "abstract": "...",
      "authors": [{"name": "Author One"}, {"name": "Author Two"}]
    }
  ]
}
```

## 速率限制

- 无需 API Key：100 次请求 / 5 分钟
- 建议在请求间添加 1 秒延迟
- 脚本内置自动重试和延迟逻辑

## 工作流集成

在论文工作流中，文献搜索智能体按以下步骤使用此 skill：

1. **初始搜索**：根据需求分析师提供的关键词搜索 Top 50 篇
2. **筛选排序**：按引用量筛选 Top 20 高影响力论文
3. **深度追踪**：对 Top 5 篇获取引用/参考文献，发现更多关键文献
4. **输出结果**：生成 `references_raw.json` 和 `top_papers.md`
