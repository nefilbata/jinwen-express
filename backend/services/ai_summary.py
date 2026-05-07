import logging

logger = logging.getLogger(__name__)

SUMMARY_PROMPT = """你是一位研究中国古代青铜器铭文（金文）的学者。请用一句话（不超过50个汉字）总结以下学术论文的核心发现或创新点。使用学术但通俗易懂的中文。直接输出总结，不要加任何前缀或引号。

论文标题：{title}
论文摘要：{abstract}

一句话解读："""


class AISummaryService:
    def __init__(self, api_key: str, base_url: str, model: str):
        self.api_key = api_key
        self.base_url = base_url
        self.model = model

    async def generate_summary(self, title: str, abstract: str) -> str | None:
        if not self.api_key:
            logger.warning("No API key configured, skipping AI summary")
            return None

        try:
            from openai import AsyncOpenAI

            client = AsyncOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
            )

            abstract_clean = abstract[:2000] if abstract else "暂无摘要"

            prompt = SUMMARY_PROMPT.format(title=title, abstract=abstract_clean)

            resp = await client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100,
                temperature=0.3,
            )

            summary = resp.choices[0].message.content
            if summary:
                summary = summary.strip().strip('"').strip("'").strip("。") + "。"
                return summary[:80]

        except Exception as e:
            logger.error(f"AI summary generation failed: {e}")

        return None

    async def generate_batch(
        self, papers: list[tuple[str, str]]
    ) -> list[str | None]:
        results = []
        for title, abstract in papers:
            result = await self.generate_summary(title, abstract)
            results.append(result)
        return results
