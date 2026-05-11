#!/usr/bin/env python3
"""Semantic Scholar API 客户端 - 学术文献搜索工具"""

import json
import sys
import time
import argparse
import urllib.request
import urllib.parse
import urllib.error

BASE_URL = "https://api.semanticscholar.org/graph/v1"
DEFAULT_DELAY = 1.0  # 请求间隔（秒）

def api_get(endpoint, params=None, retries=3):
    """发送 GET 请求到 Semantic Scholar API"""
    url = f"{BASE_URL}/{endpoint}"
    if params:
        query = urllib.parse.urlencode(params)
        url = f"{url}?{query}"

    for attempt in range(retries):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "LiteratureSearchSkill/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                return json.loads(resp.read().decode("utf-8"))
        except urllib.error.HTTPError as e:
            if e.code == 429:  # Rate limit
                wait = min(2 ** attempt * 5, 30)
                print(f"[Rate limited] Waiting {wait}s...", file=sys.stderr)
                time.sleep(wait)
                continue
            elif e.code == 404:
                return {"error": f"Not found: {endpoint}"}
            else:
                if attempt < retries - 1:
                    time.sleep(2)
                    continue
                return {"error": f"HTTP {e.code}: {e.reason}"}
        except Exception as e:
            if attempt < retries - 1:
                time.sleep(2)
                continue
            return {"error": str(e)}

    return {"error": "Max retries exceeded"}


def search_papers(query, limit=20, offset=0, fields=None, year=None, venue=None, sort=None):
    """搜索论文"""
    if fields is None:
        fields = "title,year,citationCount,abstract,authors,venue,url,externalIds,influentialCitationCount,isOpenAccess,tldr"

    params = {
        "query": query,
        "limit": min(limit, 100),
        "offset": offset,
        "fields": fields,
    }
    if year:
        params["year"] = year
    if venue:
        params["venue"] = venue
    if sort:
        params["sort"] = sort

    result = api_get("paper/search", params)
    if "error" in result:
        return result

    return {
        "total": result.get("total", 0),
        "offset": result.get("offset", 0),
        "limit": result.get("next", 0) - result.get("offset", 0) if "next" in result else limit,
        "papers": result.get("data", [])
    }


def get_paper(paper_id, fields=None):
    """获取论文详情"""
    if fields is None:
        fields = "title,year,citationCount,referenceCount,abstract,authors,venue,url,externalIds,influentialCitationCount,isOpenAccess,fieldsOfStudy,tldr"
    return api_get(f"paper/{paper_id}", {"fields": fields})


def get_citations(paper_id, limit=20, offset=0, fields=None):
    """获取引用列表（谁引用了这篇论文）"""
    if fields is None:
        fields = "title,year,citationCount,authors,venue"
    params = {"fields": fields, "limit": min(limit, 100), "offset": offset}
    result = api_get(f"paper/{paper_id}/citations", params)
    if "error" in result:
        return result
    citations = [item.get("citingPaper", {}) for item in result.get("data", [])]
    return {"total": len(citations), "papers": citations}


def get_references(paper_id, limit=20, offset=0, fields=None):
    """获取参考文献列表（这篇论文引用了谁）"""
    if fields is None:
        fields = "title,year,citationCount,authors,venue"
    params = {"fields": fields, "limit": min(limit, 100), "offset": offset}
    result = api_get(f"paper/{paper_id}/references", params)
    if "error" in result:
        return result
    refs = [item.get("citedPaper", {}) for item in result.get("data", [])]
    return {"total": len(refs), "papers": refs}


def search_author(query, limit=10, fields=None):
    """搜索作者"""
    if fields is None:
        fields = "name,hIndex,citationCount,paperCount,affiliations"
    params = {"query": query, "limit": min(limit, 100), "fields": fields}
    result = api_get("author/search", params)
    if "error" in result:
        return result
    return {
        "total": result.get("total", 0),
        "authors": result.get("data", [])
    }


def get_recommendations(paper_id, limit=10, fields=None):
    """获取相关论文推荐"""
    if fields is None:
        fields = "title,year,citationCount,authors,abstract"
    params = {"limit": min(limit, 100), "fields": fields}
    # Recommendations use a different endpoint
    url = f"https://api.semanticscholar.org/recommendations/v1/papers/forpaper/{paper_id}"
    query = urllib.parse.urlencode(params)
    full_url = f"{url}?{query}"

    for attempt in range(3):
        try:
            req = urllib.request.Request(full_url, headers={"User-Agent": "LiteratureSearchSkill/1.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                result = json.loads(resp.read().decode("utf-8"))
                return {"papers": result.get("recommendedPapers", [])}
        except Exception as e:
            if attempt < 2:
                time.sleep(2)
                continue
            return {"error": str(e)}


def format_output(data, pretty=True):
    """格式化输出"""
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False)
    return json.dumps(data, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description="Semantic Scholar 学术文献搜索")
    subparsers = parser.add_subparsers(dest="command", help="可用命令")

    # search 命令
    sp_search = subparsers.add_parser("search", help="搜索论文")
    sp_search.add_argument("query", help="搜索关键词")
    sp_search.add_argument("--limit", type=int, default=20, help="返回数量（默认20）")
    sp_search.add_argument("--offset", type=int, default=0, help="偏移量")
    sp_search.add_argument("--fields", type=str, help="返回字段（逗号分隔）")
    sp_search.add_argument("--year", type=str, help="年份筛选（如 2020-2025 或 2024）")
    sp_search.add_argument("--venue", type=str, help="期刊/会议筛选")
    sp_search.add_argument("--sort", type=str, help="排序方式（如 citationCount:desc）")

    # paper 命令
    sp_paper = subparsers.add_parser("paper", help="获取论文详情")
    sp_paper.add_argument("paper_id", help="论文 ID（S2 ID 或 DOI/ArXiv 前缀）")
    sp_paper.add_argument("--fields", type=str, help="返回字段")

    # citations 命令
    sp_cite = subparsers.add_parser("citations", help="获取引用列表")
    sp_cite.add_argument("paper_id", help="论文 ID")
    sp_cite.add_argument("--limit", type=int, default=20, help="返回数量")
    sp_cite.add_argument("--offset", type=int, default=0, help="偏移量")
    sp_cite.add_argument("--fields", type=str, help="返回字段")

    # references 命令
    sp_ref = subparsers.add_parser("references", help="获取参考文献")
    sp_ref.add_argument("paper_id", help="论文 ID")
    sp_ref.add_argument("--limit", type=int, default=20, help="返回数量")
    sp_ref.add_argument("--offset", type=int, default=0, help="偏移量")
    sp_ref.add_argument("--fields", type=str, help="返回字段")

    # author 命令
    sp_author = subparsers.add_parser("author", help="搜索作者")
    sp_author.add_argument("query", help="作者姓名")
    sp_author.add_argument("--limit", type=int, default=10, help="返回数量")
    sp_author.add_argument("--fields", type=str, help="返回字段")

    # recommend 命令
    sp_rec = subparsers.add_parser("recommend", help="获取相关论文推荐")
    sp_rec.add_argument("paper_id", help="种子论文 ID")
    sp_rec.add_argument("--limit", type=int, default=10, help="返回数量")
    sp_rec.add_argument("--fields", type=str, help="返回字段")

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    result = None

    if args.command == "search":
        result = search_papers(
            args.query, limit=args.limit, offset=args.offset,
            fields=args.fields, year=args.year, venue=args.venue, sort=args.sort
        )
    elif args.command == "paper":
        result = get_paper(args.paper_id, fields=args.fields)
    elif args.command == "citations":
        result = get_citations(
            args.paper_id, limit=args.limit, offset=args.offset, fields=args.fields
        )
    elif args.command == "references":
        result = get_references(
            args.paper_id, limit=args.limit, offset=args.offset, fields=args.fields
        )
    elif args.command == "author":
        result = search_author(args.query, limit=args.limit, fields=args.fields)
    elif args.command == "recommend":
        result = get_recommendations(args.paper_id, limit=args.limit, fields=args.fields)

    if result:
        print(format_output(result))
    else:
        print(json.dumps({"error": "No result"}))
        sys.exit(1)


if __name__ == "__main__":
    main()
