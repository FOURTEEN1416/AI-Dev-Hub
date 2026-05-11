"""
邮件发送服务模块
提供邮件发送功能，支持模板渲染
"""

import logging
from pathlib import Path

from aiosmtplib import SMTP
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email_validator import validate_email, EmailNotValidError
from jinja2 import Environment, FileSystemLoader, TemplateNotFound

from app.core.config import settings

# 配置日志
logger = logging.getLogger(__name__)


class EmailService:
    """邮件发送服务"""

    def __init__(self):
        """初始化邮件服务，配置SMTP和Jinja2模板"""
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL
        self.frontend_url = settings.FRONTEND_URL

        # Jinja2模板配置
        template_dir = Path(__file__).parent.parent / "templates" / "emails"
        self.template_env = Environment(loader=FileSystemLoader(template_dir))

    async def send_email(
        self,
        to_email: str,
        subject: str,
        html_content: str,
        text_content: str | None = None
    ) -> bool:
        """
        发送邮件

        Args:
            to_email: 收件人邮箱地址
            subject: 邮件主题
            html_content: HTML格式的邮件内容
            text_content: 纯文本格式的邮件内容（可选）

        Returns:
            bool: 发送成功返回True，失败返回False
        """
        try:
            # 验证邮箱地址
            validate_email(to_email)
        except EmailNotValidError as e:
            logger.error(f"邮箱地址无效: {to_email}, 错误: {e}")
            return False

        # 创建邮件消息
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = self.from_email
        message["To"] = to_email

        # 添加纯文本内容（如果提供）
        if text_content:
            text_part = MIMEText(text_content, "plain", "utf-8")
            message.attach(text_part)

        # 添加HTML内容
        html_part = MIMEText(html_content, "html", "utf-8")
        message.attach(html_part)

        try:
            # 连接SMTP服务器并发送邮件
            async with SMTP(
                hostname=self.smtp_host,
                port=self.smtp_port,
                start_tls=True
            ) as smtp:
                await smtp.login(self.smtp_user, self.smtp_password)
                await smtp.send_message(message)

            logger.info(f"邮件发送成功: {to_email}")
            return True

        except Exception as e:
            logger.error(f"邮件发送失败: {to_email}, 错误: {e}")
            return False

    def _render_template(self, template_name: str, context: dict) -> str:
        """
        渲染邮件模板

        Args:
            template_name: 模板文件名
            context: 模板上下文变量

        Returns:
            str: 渲染后的HTML内容
        """
        try:
            template = self.template_env.get_template(template_name)
            return template.render(**context)
        except TemplateNotFound:
            logger.error(f"邮件模板不存在: {template_name}")
            return ""
        except Exception as e:
            logger.error(f"模板渲染失败: {template_name}, 错误: {e}")
            return ""

    async def send_welcome_email(self, to_email: str, username: str) -> bool:
        """
        发送欢迎邮件

        Args:
            to_email: 收件人邮箱地址
            username: 用户名

        Returns:
            bool: 发送成功返回True，失败返回False
        """
        context = {
            "username": username or "用户",
            "frontend_url": self.frontend_url,
        }

        html_content = self._render_template("welcome.html", context)

        if not html_content:
            logger.error("欢迎邮件模板渲染失败")
            return False

        subject = "欢迎加入 AI 开发者机会聚合平台"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    async def send_notification_email(
        self,
        to_email: str,
        username: str,
        opportunities: list[dict]
    ) -> bool:
        """
        发送机会通知邮件

        Args:
            to_email: 收件人邮箱地址
            username: 用户名
            opportunities: 机会列表，每个机会包含title、type、source、deadline、description、url等字段

        Returns:
            bool: 发送成功返回True，失败返回False
        """
        context = {
            "username": username or "用户",
            "opportunities": opportunities,
            "unsubscribe_url": f"{self.frontend_url}/settings/notifications",
            "settings_url": f"{self.frontend_url}/settings/notifications",
        }

        html_content = self._render_template("notification.html", context)

        if not html_content:
            logger.error("通知邮件模板渲染失败")
            return False

        # 根据机会数量决定主题
        count = len(opportunities)
        if count == 0:
            subject = "AI 开发者机会聚合平台 - 暂无新机会"
        elif count == 1:
            subject = "为您发现 1 个新的 AI 开发者机会"
        else:
            subject = f"为您发现 {count} 个新的 AI 开发者机会"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )

    async def send_verification_email(
        self,
        to_email: str,
        username: str,
        verification_url: str
    ) -> bool:
        """
        发送邮箱验证邮件

        Args:
            to_email: 收件人邮箱地址
            username: 用户名
            verification_url: 验证链接

        Returns:
            bool: 发送成功返回True，失败返回False
        """
        context = {
            "username": username or "用户",
            "verification_url": verification_url,
            "frontend_url": self.frontend_url,
        }

        html_content = self._render_template("verification.html", context)

        if not html_content:
            logger.error("验证邮件模板渲染失败")
            return False

        subject = "验证您的邮箱地址 - AI 开发者机会聚合平台"

        return await self.send_email(
            to_email=to_email,
            subject=subject,
            html_content=html_content
        )


# 全局实例
email_service = EmailService()
