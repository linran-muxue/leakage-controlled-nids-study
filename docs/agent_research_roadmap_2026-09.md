# Agent 方向科研起步路线图（2026-09）

本文面向第一次进入 LLM Agent/智能体研究的研究者，目标是把“Agent 很宽泛”的兴趣收敛为可复现实验、可验证指标和可投稿的问题。引用优先选择论文原文、官方 benchmark 页面或项目文档。

## 1. 先给 Agent 下一个可研究的定义

建议采用一个可操作的闭环定义：Agent 是一个在环境中反复执行“观察（observation）→决策/推理（policy or reasoning）→行动（tool/action）→反馈（feedback）”的系统；LLM 可以作为策略、规划器或控制器，但 Agent 不等同于一次性文本生成。这个定义使实验至少包含：任务环境、动作空间、状态/轨迹记录、成功标准和成本约束。

最小形式化：给定环境状态 $s_t$、历史 $h_t$，Agent 产生动作 $a_t=\pi_\theta(h_t)$，环境返回 $o_{t+1},r_t$；研究问题通常是在固定预算下最大化任务成功率，同时降低步骤数、token、工具调用错误或安全违规。

## 2. 研究子方向地图（按“最容易做出可复现实验”排序）

### A. 工具使用与行动规划

核心问题：Agent 何时调用工具、如何选择参数、如何处理工具失败和长程依赖。经典基线是 ReAct（将思考与行动交错）和 Toolformer（自监督学习 API 调用）。

- ReAct：Yao et al., *ReAct: Synergizing Reasoning and Acting in Language Models*, ICLR 2023。论文展示了在问答、决策和交互环境中交错生成 reasoning traces 与 actions 的方法。原文：[arXiv:2210.03629](https://arxiv.org/abs/2210.03629)。
- Toolformer：Schick et al., *Toolformer: Language Models Can Teach Themselves to Use Tools*, NeurIPS 2023。原文：[arXiv:2302.04761](https://arxiv.org/abs/2302.04761)。

可做的小课题：固定模型和工具集合，只改变工具选择策略（ReAct、函数调用、检索后调用、反思后重试），比较成功率、调用次数、延迟和错误类型。

### B. 反思、自我改进与轨迹学习

核心问题：失败轨迹中的反馈如何转化为下一次策略改进；反思是否真正提高泛化，而不是只增加 token。Reflexion 用语言反馈和情景记忆替代参数更新，是很适合复现和做消融的基线。

- Reflexion：Shinn et al., *Reflexion: Language Agents with Verbal Reinforcement Learning*, NeurIPS 2023。原文：[arXiv:2303.11366](https://arxiv.org/abs/2303.11366)。

可做的小课题：比较“无反思、失败后反思、每步反思、周期性总结”四种 cadence；报告成功率增益与额外 token/延迟，并检查反思内容是否与真实错误相关。

### C. 记忆（短期、长期、程序性）

核心问题：何时写入记忆、如何检索、如何遗忘和避免污染；记忆是否跨任务泛化。实验应区分上下文窗口内 scratchpad、外部向量库、结构化 episodic memory 和可执行程序记忆。

可做的小课题：在多轮任务中控制历史长度，比较 recent-window、向量检索、摘要记忆和事件图记忆；指标除成功率外，增加检索 precision/recall、记忆冲突率和跨任务迁移。

### D. 多 Agent 协作与角色分工

核心问题：分工、通信协议、共识/辩论是否带来真实收益，还是重复调用造成成本上升。应设置单 Agent 等 token/时间预算的强基线，否则难以说明协作有效。

推荐从 AgentBench 的多环境任务或自建可控任务开始，再逐步加入角色数量、通信轮数和共享黑板消融。

### E. Web/桌面/软件工程环境中的长程交互

核心问题：视觉/DOM 感知、操作可靠性、状态跟踪、恢复策略和真实工具链适配。这类工作通常比纯问答更容易形成可复现实验，但环境安装成本较高。

- WebArena：Zhou et al., *WebArena: A Realistic Web Environment for Building Autonomous Agents*, ICLR 2024。项目与数据：[github.com/web-arena-x/webarena](https://github.com/web-arena-x/webarena)，论文：[arXiv:2307.13854](https://arxiv.org/abs/2307.13854)。
- OSWorld：Xie et al., *OSWorld: Benchmarking Multimodal Agents for Open-Ended Tasks in Real Computer Environments*, NeurIPS 2024。论文：[arXiv:2404.07972](https://arxiv.org/abs/2404.07972)，项目：[os-world.github.io](https://os-world.github.io/)。
- SWE-bench：Jimenez et al., *SWE-bench: Can Language Models Resolve Real-World GitHub Issues?*, ICLR 2024。官方评测器与数据：[github.com/swe-bench/SWE-bench](https://github.com/swe-bench/SWE-bench)，论文：[arXiv:2310.06770](https://arxiv.org/abs/2310.06770)。

### F. Agent 安全、对齐与提示注入防护

核心问题：不可信网页/工具返回内容如何注入指令；权限最小化、沙箱、敏感数据泄露和越权行动如何测量。AgentDojo 提供了包含工具和提示注入的动态环境，适合安全方向入门。

- AgentDojo：Debenedetti et al., *AgentDojo: A Dynamic Environment to Evaluate Prompt Injection Attacks and Defenses for LLM Agents*, NeurIPS 2024 workshop/benchmark release。论文：[arXiv:2406.13352](https://arxiv.org/abs/2406.13352)，项目：[github.com/ethz-spylab/agentdojo](https://github.com/ethz-spylab/agentdojo)。
- OWASP GenAI Security Project 的 LLM/Agent 风险分类可作为威胁建模入口，官方页面：[owasp.org/www-project-top-10-for-large-language-model-applications](https://owasp.org/www-project-top-10-for-large-language-model-applications/)。

### G. 评测、可观测性与成本效率

核心问题：Agent 的“成功”不是单一分数；需要同时测任务完成、轨迹质量、可靠性、安全和资源成本。研究贡献可以是新指标、评测协议或对现有 benchmark 的误差分析。

## 3. 常用 Benchmark 与应报告的指标

| Benchmark | 环境/任务 | 适合研究 | 主要指标（优先使用官方 evaluator） |
|---|---|---|---|
| AgentBench（ICLR 2024） | 8 类环境，含数据库、知识图谱、操作系统、Web 等 | 通用 Agent 能力、跨环境比较 | task success/accuracy、平均回合或步骤；论文：[arXiv:2308.03688](https://arxiv.org/abs/2308.03688) |
| WebArena（ICLR 2024） | 本地部署的真实网站副本 | 浏览器规划、工具调用、恢复 | task success rate；按站点/任务类型分层，官方 repo 提供 evaluator |
| GAIA（2023） | 需要工具、多步推理和多模态知识的通用问题 | 通用助手、工具链 | exact-match/人工核验的最终答案；[arXiv:2311.12983](https://arxiv.org/abs/2311.12983) |
| SWE-bench（ICLR 2024） | 真实 GitHub issue→代码修复 | 软件工程 Agent、补丁验证 | resolved rate（测试通过且补丁满足 issue）；区分 full/dev 与 Lite |
| OSWorld（NeurIPS 2024） | Linux/Windows/macOS 桌面操作 | GUI Agent、视觉 grounding | task success，支持基于状态的自动检查；报告操作步数和失败恢复 |
| τ-bench（2024） | 零售/航空等 API 对话任务 | 工具策略、对话状态、规则遵循 | pass rate、rule compliance、平均 tool calls；[arXiv:2406.12045](https://arxiv.org/abs/2406.12045) |
| AppWorld（2024） | 多应用 API 与长期状态 | 长程规划、跨应用记忆 | task completion、API correctness、state consistency；[arXiv:2407.18901](https://arxiv.org/abs/2407.18901) |
| MLE-bench（2024） | Kaggle 机器学习工程任务 | 端到端数据科学 Agent | competition metric、submission validity、成本；[arXiv:2410.07095](https://arxiv.org/abs/2410.07095) |
| AgentDojo（2024） | 动态工具环境+提示注入 | 安全防御、攻击成功率 | utility（正常任务成功）与 security（攻击阻断率）双指标 |

跨 benchmark 的最低报告集建议为：任务成功率（按任务类型分层）、平均/中位步骤数、总 token 与 wall-clock 延迟、工具错误率、重试率、失败类别分布、随机种子/模型版本/提示词、预算上限。若涉及安全，必须同时报告 utility–security trade-off，不能只报防御率。

## 4. 推荐的最小可行研究（MVP）

选择一个环境、一个明确变量和一个主指标：例如在 τ-bench 或 WebArena 的 50–100 个任务上，研究“失败后反思 cadence 对成功率与成本的影响”。固定底座模型和工具定义，预注册 3–4 个策略，至少运行 3 个随机种子或重复采样；保存完整轨迹（prompt、tool call、observation、error、终止原因）。

结果表至少包含：成功率及 95% 置信区间、每成功任务成本、步骤数、工具错误率；用 bootstrap 或 Wilson 区间，不要仅报告一次运行的百分比。人工分析 30–50 条失败轨迹，建立互斥错误 taxonomy（规划、参数、感知、权限、恢复、终止判断）。

## 5. 8 周入门执行计划

1. 第 1 周：读 ReAct、Toolformer、Reflexion 三篇原文；明确环境、动作空间和成功判据。
2. 第 2 周：跑通一个官方 benchmark（优先 SWE-bench Lite、τ-bench 或 WebArena 的小子集）；固定模型、温度和预算。
3. 第 3 周：实现可记录轨迹的 baseline runner；加入重试、超时、成本统计和断点续跑。
4. 第 4 周：复现两个强基线（例如 ReAct 与 function-calling planner），完成端到端 sanity check。
5. 第 5 周：只改一个研究变量（记忆、反思 cadence、工具路由或协作协议），做小规模消融。
6. 第 6 周：扩大任务集和重复次数；进行 bootstrap/Wilson 统计与失败 taxonomy。
7. 第 7 周：做鲁棒性和成本分析（任务扰动、工具故障、提示注入、预算变化）。
8. 第 8 周：整理可复现实验包（配置、模型版本、提示、轨迹 schema、评测脚本），写成 4–6 页 workshop 风格短文，再决定是否扩展为正式论文。

## 6. 工具链与官方文档入口

- LangGraph：以图结构显式表示有状态 Agent 工作流，适合需要 checkpoint、human-in-the-loop 和可观测性的实验。官方文档：[langchain-ai.github.io/langgraph](https://langchain-ai.github.io/langgraph/)。
- Microsoft AutoGen：多 Agent 对话与工具编排框架；官方仓库：[github.com/microsoft/autogen](https://github.com/microsoft/autogen)。
- OpenAI Agents SDK：提供 Agent、handoff、guardrail、tracing 等原语；官方文档：[openai.github.io/openai-agents-python](https://openai.github.io/openai-agents-python/)。
- Model Context Protocol（MCP）：定义模型与外部工具/资源连接的开放协议；规范与 SDK：[modelcontextprotocol.io](https://modelcontextprotocol.io/)。做工具生态研究时应记录协议版本和 server 权限。

框架不是研究贡献本身。论文中应把框架层与算法变量分离，并提供不依赖特定框架的伪代码和配置。

## 7. 选题筛选问题（避免“做了一个 Demo”）

在正式编码前，要求自己的问题回答四点：

1. 现有方法在哪个可量化指标上失败？
2. 你的变量是否能独立操控，并有等预算 baseline？
3. 结论是否能跨任务/模型/随机种子复现？
4. 失败轨迹是否能解释“为什么有效”，而不仅是分数上涨？

若四点中有两点答不上来，应先收窄问题，而不是继续堆更多 Agent 角色或工具。

## 参考文献（原始来源）

完整链接已在正文各节给出；核心论文包括 ReAct（ICLR 2023）、Toolformer（NeurIPS 2023）、Reflexion（NeurIPS 2023）、AgentBench（ICLR 2024）、WebArena（ICLR 2024）、SWE-bench（ICLR 2024）、OSWorld（NeurIPS 2024）、τ-bench（2024）、AppWorld（2024）、MLE-bench（2024）和 AgentDojo（2024）。使用时请以论文最终版本和 benchmark 官方仓库的 evaluator 为准，并在实验记录中固定 commit hash。
