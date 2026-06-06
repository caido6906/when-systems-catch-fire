# When Systems Catch Fire / 点火

这是一本关于系统重写的思想型非虚构书。它研究关键人物在关键时期通过关键动作改变系统燃烧条件，使一个新系统被应约者接住、延迟接住、错误接住或无法接住的历史结构。

本书不宣称发现终极规律，而是尝试观察一种反复出现的现象：制度、资源、技术、流程都已经搭好以后，为什么有些系统真正活起来，有些系统仍然没有人愿意住进去。

## Naming / 命名关系

Book title: **When Systems Catch Fire**  
中文书名 / Chinese title: **点火**  
Core theory: **Ignition Framework / 点火框架**  
Repository: **when-systems-catch-fire**

说明：`Ignition Framework / 点火框架` 是本书使用和发展的核心理论名；`when-systems-catch-fire` 是当前 GitHub 仓库名。仓库名会保持为 `when-systems-catch-fire`，不要求也不暗示必须改名为 `ignition-framework`。

## English abstract

The Ignition Framework studies how new orders come alive. It distinguishes between a collaboration system, which builds institutions, processes, organizations, resources and technical structures, and a recognition system, which determines whether responders are willing to enter and claim the new order as their own.

The core question is not only whether a system can operate, but whether it can be recognized under pressure by the people who must decide whether to enter it.

## Reading entrances

人类读者入口：

- [SUMMARY.md](SUMMARY.md)
- [book/](book/)

AI Agent 入口：

- [llms.txt](llms.txt)
- [llms-full.txt](llms-full.txt)
- [agent/](agent/)
- [data/ignition-cases.csv](data/ignition-cases.csv)

## Repository structure

```text
book/      正式书稿整理层，面向人类读者
agent/     AI Agent 友好的摘要、概念、论点、案例、术语和问答路径
data/      结构化数据，目前包括 ignition case CSV
dianhuo/   原始书稿、框架笔记、证据材料和归档内容
SUMMARY.md 全书目录
llms.txt   AI Agent 简短入口
llms-full.txt AI Agent 一次性读取入口
```

## Current status

当前版本是非破坏性整理稿。`book/` 中的章节是基于现有目录、框架笔记和案例线索整理出的工作稿；`agent/` 中的材料用于检索、引用、重组和任务执行。原有 `dianhuo/` 内容未删除，仍作为来源层和后续扩写材料。

## License / 许可协议

本仓库是一个非商业开放内容项目。

本仓库中的书稿正文、概念说明、章节内容、案例整理、Agent-readable materials，除特别说明外，均采用：

License: **Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License**  
中文：**知识共享署名—非商业性使用—相同方式共享 4.0 国际许可协议**  
Short name: **CC BY-NC-SA 4.0**

你可以自由阅读、复制、传播、引用、改编本作品，但必须遵守以下条件：

1. **署名 Attribution**：必须保留作者署名与原始仓库链接。
2. **非商业 NonCommercial**：不得将本作品或其改编作品用于商业目的。
3. **相同方式共享 ShareAlike**：如果你改编、转换或基于本作品继续创作，发布时必须采用相同或兼容的许可协议。
4. **不得暗示背书 No endorsement**：不得暗示原作者认可你的使用方式、观点或改编版本。

完整协议见：

- `LICENSE`
- `NOTICE.md`

说明：本项目更准确地说是“非商业开放内容项目”，而不是 OSI 意义上的软件开源项目。因为本项目禁止商业使用。
