"""
文档模板和格式化工具
"""


class DocumentTemplate:
    def __init__(self, title: str, content_sections: dict[str, str]):
        self.title = title
        self.content_sections = content_sections

    def render(self) -> str:  # 抽象方法
        """渲染完整文档"""
        raise NotImplementedError


class TechnicalReportTemplate(DocumentTemplate):
    """技术报告模板"""

    def render(self) -> str:
        lines = []

        # 标题
        lines.append(f"# {self.title}\n")

        # 元信息
        from datetime import datetime
        lines.append(f"# **生成时间**: {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        lines.append("----\n")

        # 目录
        lines.append("## 目录 \n")
        for i, (section_id, content) in enumerate(self.content_sections.items(), 1):
            section_title = self._extract_title(content)
            lines.append(f"{i}. {section_title}")
            lines.append("\n---\n")

        # 各个章节内容
        for section_id, content in self.content_sections.items():
            lines.append(content)
            lines.append("\n---\n")

        return "\n".join(lines)

    def _extract_title(self, content: str) -> str:
        """从内容中提取标题, 默认以#开头的是标题"""
        lines = content.split("\n")
        for line in lines:
            if line.startswith("#"):
                return line.replace("#", "").strip()
        return "未命名章节"


class EmailTemplate(DocumentTemplate):
    """邮件模板"""

    def __init__(self, title: str, content_sections: dict[str, str], recipient: str = "尊敬的用户"):
        super().__init__(title, content_sections)
        self.recipient = recipient

    def render(self) -> str:
        """邮件渲染"""
        lines = []

        # 主题
        lines.append(f"**主题** {self.title}\n")

        # 称呼
        lines.append(f"{self.recipient}:\n")

        # 正文
        for section_id, content in self.content_sections.items():
            lines.append(content)
            lines.append("")

        # 结尾
        lines.append("此致")
        lines.append("敬礼")

        # 签名
        lines.append("————")
        lines.append("**发件人**: AI助手")
        from datetime import datetime
        lines.append(f"**日期**: {datetime.now().strftime('%Y-%m-%d')}")

        return "\n".join(lines)


class BlogPostTemplate(DocumentTemplate):
    """博客文章"""

    def render(self) -> str:
        """渲染博客文章"""
        lines = []

        # 标题
        lines.append(f"# {self.title}\n")

        # 元信息
        from datetime import datetime
        lines.append(f"*发布于 {datetime.now().strftime('%d.%m.%Y %H:%M:%S')}\n")
        lines.append("----\n")

        # 内容
        for section_id, content in self.content_sections.items():
            lines.append(content)
            lines.append("")

        # 结尾
        lines.append("\n---")
        lines.append("\n💬 **欢迎留言讨论！**")

        return "\n".join(lines)


class WeeklyReportTemplate(DocumentTemplate):
    """周报模板"""

    def render(self) -> str:
        """渲染周报"""
        lines = []

        # 标题
        from datetime import datetime
        week_num = datetime.now().isocalendar()[1]  # (year, week, weekday)
        datetime_str = datetime.now().strftime("%Y-%m-%d")
        lines.append(f"# {datetime_str} 第({week_num})周工作总结")
        lines.append(f"{self.title}\n")

        # 各部分
        for section_id, content in self.content_sections.items():
            lines.append(content)
            lines.append("")

        # 签名
        lines.append("---")
        lines.append(f"**汇报人**: 用户")
        lines.append(f"**日期**: {datetime.now().strftime('%Y-%m-%d')}")

        return "\n".join(lines)


def create_document_template(document_type: str, title: str,
                             content_sections: dict[str, str]) -> DocumentTemplate:
    """
    工厂函数: 根据文档类型创建对应模板

    Args:
        document_type: 文档类型
        title: 文档标题
        content_sections: 文档内容

    Returns:
        DocumentTemplate: 文档模板实例
    """

    # 文档类型 到 具体模板类 映射
    templates = {
        "report": TechnicalReportTemplate,
        "technical_doc": TechnicalReportTemplate,
        "email": EmailTemplate,
        "blog": BlogPostTemplate,
        "weekly_report": WeeklyReportTemplate
    }

    templates_class = templates.get(document_type, TechnicalReportTemplate)
    return templates_class(title, content_sections)
