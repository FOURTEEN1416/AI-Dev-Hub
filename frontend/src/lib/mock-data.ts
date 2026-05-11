/**
 * 模拟数据
 * 用于开发和演示，后续对接 API 后可移除
 */

import type { Opportunity } from '@/types';

/** 模拟机会数据 */
export const mockOpportunities: Opportunity[] = [
  {
    id: 1,
    title: 'OpenAI GPT-4 API 开发者计划 - 免费额度申请',
    type: 'developer_program',
    source: 'OpenAI',
    source_url: 'https://platform.openai.com',
    description:
      'OpenAI 推出 GPT-4 API 开发者计划，为符合条件的开发者提供免费 API 调用额度。申请者需要提交一个使用 GPT-4 的项目提案，展示创新性和社会价值。成功申请者将获得每月 $100 的免费 API 额度，持续 6 个月。',
    tags: ['GPT-4', 'API', '免费额度', 'LLM'],
    deadline: '2026-06-30T23:59:59Z',
    reward: '每月 $100 免费 API 额度，持续 6 个月',
    requirements: '需要提交项目提案，展示 GPT-4 的创新应用场景',
    official_link: 'https://platform.openai.com/docs/developer-program',
    status: 'active',
    created_at: '2026-05-01T10:00:00Z',
    updated_at: '2026-05-10T08:00:00Z',
  },
  {
    id: 2,
    title: 'Kaggle LLM 检索增强生成（RAG）挑战赛',
    type: 'competition',
    source: 'Kaggle',
    source_url: 'https://www.kaggle.com/competitions',
    description:
      'Kaggle 举办 RAG 挑战赛，要求参赛者构建一个高效的检索增强生成系统，在给定知识库的基础上回答复杂问题。评测指标包括答案准确性、响应速度和系统鲁棒性。奖金池总额 $50,000。',
    tags: ['RAG', 'LLM', 'NLP', 'Kaggle', '竞赛'],
    deadline: '2026-07-15T23:59:59Z',
    reward: '奖金池 $50,000（第一名 $15,000）',
    requirements: '任何对 NLP 和 RAG 感兴趣的开发者均可参加',
    official_link: 'https://www.kaggle.com/competitions/rag-challenge',
    status: 'active',
    created_at: '2026-05-03T14:00:00Z',
    updated_at: '2026-05-09T12:00:00Z',
  },
  {
    id: 3,
    title: 'Google Cloud AI 免费 $300 试用额度',
    type: 'free_credits',
    source: 'Google',
    source_url: 'https://cloud.google.com',
    description:
      'Google Cloud 为新用户提供 $300 的免费试用额度，可用于 Vertex AI、Cloud Run、BigQuery 等 AI 相关服务。无需信用卡即可开始使用，有效期 90 天。适合想要尝试 Google AI 平台的开发者。',
    tags: ['Google Cloud', '免费额度', 'Vertex AI', '云计算'],
    deadline: null,
    reward: '$300 免费试用额度，有效期 90 天',
    requirements: '新注册 Google Cloud 账户即可',
    official_link: 'https://cloud.google.com/free',
    status: 'active',
    created_at: '2026-04-28T09:00:00Z',
    updated_at: '2026-05-08T16:00:00Z',
  },
  {
    id: 4,
    title: 'Hugging Face Transformers 开源贡献活动',
    type: 'community',
    source: 'Hugging Face',
    source_url: 'https://huggingface.co',
    description:
      'Hugging Face 发起 Transformers 库开源贡献活动，鼓励开发者参与代码贡献、文档改进和问题修复。活跃贡献者将获得 Hugging Face 官方周边礼品和社区认证徽章。',
    tags: ['开源', 'Transformers', 'Hugging Face', '社区'],
    deadline: '2026-08-31T23:59:59Z',
    reward: '官方周边礼品 + 社区认证徽章',
    requirements: '熟悉 Python 和 Transformers 库',
    official_link: 'https://huggingface.co/docs/transformers/community',
    status: 'active',
    created_at: '2026-05-05T11:00:00Z',
    updated_at: '2026-05-10T10:00:00Z',
  },
  {
    id: 5,
    title: 'Anthropic Claude API 研究者访问计划',
    type: 'developer_program',
    source: 'Anthropic',
    source_url: 'https://www.anthropic.com',
    description:
      'Anthropic 推出 Claude API 研究者访问计划，为学术研究人员和独立开发者提供 Claude API 的优先访问权限。申请者需要说明研究目的和预期成果。获批者将获得更高的 API 速率限制和免费调用额度。',
    tags: ['Claude', 'API', '研究', 'Anthropic'],
    deadline: '2026-06-15T23:59:59Z',
    reward: '优先 API 访问 + 更高速率限制 + 免费额度',
    requirements: '需要提交研究计划，学术机构或独立研究者均可申请',
    official_link: 'https://www.anthropic.com/researcher-access',
    status: 'active',
    created_at: '2026-05-02T08:00:00Z',
    updated_at: '2026-05-09T14:00:00Z',
  },
  {
    id: 6,
    title: 'Meta LLaMA 3 微调挑战赛',
    type: 'competition',
    source: 'Meta',
    source_url: 'https://ai.meta.com',
    description:
      'Meta 举办 LLaMA 3 微调挑战赛，参赛者需要在特定任务上微调 LLaMA 3 模型，以达到最佳性能。评测涵盖多个下游任务，包括文本分类、摘要生成和代码生成。总奖金 $100,000。',
    tags: ['LLaMA', '微调', '开源模型', 'Meta', '竞赛'],
    deadline: '2026-07-30T23:59:59Z',
    reward: '总奖金 $100,000（第一名 $30,000）',
    requirements: '熟悉模型微调和 PyTorch',
    official_link: 'https://ai.meta.com/llama/finetune-challenge',
    status: 'active',
    created_at: '2026-05-04T16:00:00Z',
    updated_at: '2026-05-10T09:00:00Z',
  },
  {
    id: 7,
    title: 'GitHub Copilot 免费学生包',
    type: 'free_credits',
    source: 'GitHub',
    source_url: 'https://github.com',
    description:
      'GitHub 为学生提供免费的 Copilot 访问权限，包括 GitHub Copilot Individual 和 GitHub Codespaces 的免费使用。学生只需使用 .edu 邮箱验证即可激活，有效期一年。',
    tags: ['Copilot', '学生', '免费', 'GitHub'],
    deadline: null,
    reward: 'GitHub Copilot + Codespaces 免费使用一年',
    requirements: '需要有效的 .edu 学生邮箱',
    official_link: 'https://education.github.com/pack',
    status: 'active',
    created_at: '2026-04-25T13:00:00Z',
    updated_at: '2026-05-07T11:00:00Z',
  },
  {
    id: 8,
    title: 'Hacker News AI 项目 Show & Tell',
    type: 'community',
    source: 'Hacker News',
    source_url: 'https://news.ycombinator.com',
    description:
      'Hacker News 社区每周举办 AI 项目 Show & Tell 活动，开发者可以分享自己构建的 AI 项目，获得社区反馈和建议。优秀项目将获得 HN 社区的特别推荐和曝光。',
    tags: ['社区', '分享', 'AI项目', 'Hacker News'],
    deadline: null,
    reward: '社区曝光和反馈',
    requirements: '任何 AI 相关的个人或团队项目',
    official_link: 'https://news.ycombinator.com/show',
    status: 'active',
    created_at: '2026-05-06T10:00:00Z',
    updated_at: '2026-05-10T15:00:00Z',
  },
  {
    id: 9,
    title: 'AWS Bedrock Claude 3 免费试用',
    type: 'free_credits',
    source: 'AWS',
    source_url: 'https://aws.amazon.com/bedrock',
    description:
      'AWS Bedrock 提供 Claude 3 系列模型的免费试用，新用户可以获得一定数量的免费推理额度。支持 Claude 3 Haiku、Sonnet 和 Opus 三个版本，适合想要在 AWS 生态中使用 Claude 的开发者。',
    tags: ['AWS', 'Claude', '免费额度', '云计算'],
    deadline: '2026-09-30T23:59:59Z',
    reward: 'Claude 3 系列模型免费推理额度',
    requirements: 'AWS 新账户注册',
    official_link: 'https://aws.amazon.com/bedrock/claude',
    status: 'active',
    created_at: '2026-05-07T09:00:00Z',
    updated_at: '2026-05-10T12:00:00Z',
  },
  {
    id: 10,
    title: 'AI Agent 开发者大赛 - 构建下一代智能代理',
    type: 'competition',
    source: 'Google',
    source_url: 'https://ai.google',
    description:
      'Google 举办 AI Agent 开发者大赛，鼓励开发者使用 Gemini API 构建具有自主决策能力的 AI Agent。参赛作品将在任务完成率、创意性和用户体验三个维度进行评审。总奖金 $200,000。',
    tags: ['Agent', 'Gemini', 'Google', '竞赛', 'AI Agent'],
    deadline: '2026-08-15T23:59:59Z',
    reward: '总奖金 $200,000（第一名 $50,000）',
    requirements: '使用 Gemini API，个人或团队（最多 4 人）均可参加',
    official_link: 'https://ai.google/dev-challenge/agent',
    status: 'active',
    created_at: '2026-05-08T14:00:00Z',
    updated_at: '2026-05-10T16:00:00Z',
  },
  {
    id: 11,
    title: 'Stability AI 开源图像生成模型 SDXL Turbo',
    type: 'community',
    source: 'Stability AI',
    source_url: 'https://stability.ai',
    description:
      'Stability AI 发布 SDXL Turbo 开源图像生成模型，支持实时图像生成。社区开发者可以参与模型改进、LoRA 训练和工具链开发。活跃贡献者有机会加入 Stability AI 的开发者社区。',
    tags: ['图像生成', '开源', 'Stable Diffusion', '社区'],
    deadline: null,
    reward: '加入官方开发者社区 + 模型早期访问权限',
    requirements: '熟悉图像生成模型和 Python',
    official_link: 'https://stability.ai/community/sdxl-turbo',
    status: 'active',
    created_at: '2026-05-03T11:00:00Z',
    updated_at: '2026-05-09T10:00:00Z',
  },
  {
    id: 12,
    title: 'Microsoft Azure AI 认证考试免费券',
    type: 'free_credits',
    source: 'Microsoft',
    source_url: 'https://learn.microsoft.com',
    description:
      'Microsoft 提供 Azure AI Engineer Associate (AI-102) 认证考试的免费券，限量 500 张。通过认证可证明你在 Azure AI 服务方面的专业技能，有助于职业发展。',
    tags: ['Azure', '认证', '免费', 'Microsoft'],
    deadline: '2026-06-30T23:59:59Z',
    reward: 'Azure AI Engineer Associate 认证考试免费券（价值 $165）',
    requirements: '需要 Microsoft 账户，先到先得',
    official_link: 'https://learn.microsoft.com/certifications/azure-ai-engineer',
    status: 'active',
    created_at: '2026-05-01T08:00:00Z',
    updated_at: '2026-05-08T14:00:00Z',
  },
];

/** 模拟列表响应 */
export function getMockListResponse(
  page: number = 1,
  limit: number = 12,
  filters: Record<string, string> = {}
) {
  let filtered = [...mockOpportunities];

  // 按类型筛选
  if (filters.type) {
    filtered = filtered.filter((item) => item.type === filters.type);
  }

  // 按来源筛选
  if (filters.source) {
    filtered = filtered.filter((item) => item.source === filters.source);
  }

  // 按关键词搜索
  if (filters.keyword) {
    const kw = filters.keyword.toLowerCase();
    filtered = filtered.filter(
      (item) =>
        item.title.toLowerCase().includes(kw) ||
        item.description?.toLowerCase().includes(kw) ||
        item.tags?.some((tag) => tag.toLowerCase().includes(kw))
    );
  }

  const total = filtered.length;
  const start = (page - 1) * limit;
  const items = filtered.slice(start, start + limit);

  return {
    items,
    total,
    page,
    limit,
  };
}
