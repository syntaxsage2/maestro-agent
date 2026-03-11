/**
 * IntentRouter Pro - API TypeScript 类型定义
 */

// ==================== 请求类型 ====================

/**
 * 聊天请求
 */
export interface ChatRequest {
  /** 用户消息 */
  message: string;
  /** 会话ID（可选，不提供则创建新会话） */
  thread_id?: string;
  /** 用户ID（可选） */
  user_id?: string;
  /** 是否流式返回（默认false） */
  stream?: boolean;
}

/**
 * 图片附件
 */
export interface ImageAttachment {
  /** 图片URL（http/https） */
  url?: string;
  /** 图片base64数据（data URI格式） */
  data?: string;
  /** 文件名 */
  name?: string;
  /** MIME类型 */
  mime_type?: string;
}

/**
 * 多模态聊天请求
 */
export interface MultimodalChatRequest {
  /** 用户消息 */
  message: string;
  /** 图片附件列表 */
  attachments: ImageAttachment[];
  /** 会话ID */
  thread_id?: string;
  /** 用户ID */
  user_id?: string;
  /** 是否流式返回 */
  stream?: boolean;
}

/**
 * HITL 人工反馈
 */
export interface HumanFeedback {
  /** 决策：approve | reject | modify */
  decision: 'approve' | 'reject' | 'modify';
  /** 决策原因 */
  reason?: string;
  /** 修改后的内容（在modify时） */
  modified_data?: Record<string, any>;
}

/**
 * HITL 恢复执行请求
 */
export interface ResumeRequest {
  /** 会话ID */
  thread_id: string;
  /** 人工反馈 */
  feedback: HumanFeedback;
}

// ==================== 响应类型 ====================

/**
 * 聊天响应
 */
export interface ChatResponse {
  /** 会话ID */
  thread_id: string;
  /** AI回复 */
  message: string;
  /** 识别的意图 */
  intent?: IntentType;
  /** 路由决策 */
  route?: RouteType;
  /** 检索的文档数量 */
  retrieved_docs_count: number;
}

/**
 * 多模态分析结果
 */
export interface MultimodalAnalysis {
  /** 分析类型 */
  type: string;
  /** 图片数量 */
  images_count: number;
  /** 分析结果 */
  result: string;
}

/**
 * 多模态聊天响应
 */
export interface MultimodalChatResponse {
  /** 会话ID */
  thread_id: string;
  /** AI回复 */
  message: string;
  /** 识别的意图 */
  intent?: IntentType;
  /** 路由决策 */
  route?: RouteType;
  /** 多模态分析结果 */
  multimodal_analysis?: MultimodalAnalysis;
}

/**
 * 消息
 */
export interface Message {
  /** 角色：human 或 ai */
  role: 'human' | 'ai';
  /** 消息内容 */
  content: string;
  /** 时间戳（前端添加） */
  timestamp?: number;
  /** 图片列表 */
  images?: string[];
}

/**
 * 历史记录响应
 */
export interface HistoryResponse {
  /** 会话ID */
  thread_id: string;
  /** 消息列表 */
  messages: Message[];
  /** 意图 */
  intent?: IntentType;
  /** 路由 */
  route?: RouteType;
}

/**
 * 工具调用
 */
export interface ToolCall {
  /** 工具名称 */
  name: string;
  /** 工具参数 */
  args: Record<string, any>;
  /** 执行结果 */
  result?: string;
  /** 时间戳 */
  timestamp?: number;
  /** 风险等级 */
  risk_level?: 'low' | 'medium' | 'high';
}

/**
 * 工具调用历史响应
 */
export interface ToolHistoryResponse {
  /** 会话ID */
  thread_id: string;
  /** 使用过的工具名称列表 */
  tools_used: string[];
  /** 工具调用详情 */
  tool_calls: ToolCall[];
  /** 总调用次数 */
  total_calls: number;
}

/**
 * HITL 中断状态
 */
export interface InterruptStatus {
  /** 是否处于中断状态 */
  is_interrupted: boolean;
  /** 会话ID */
  thread_id: string;
  /** 下一个要执行的节点 */
  next_node?: string;
  /** 中断原因 */
  interrupt_reason?: string;
  /** 待确认的工具调用 */
  tool_calls?: ToolCall[];
  /** 会话状态是否存在（用于区分'还未初始化'和'已完成'） */
  state_exists: boolean;
}

/**
 * HITL 恢复执行响应
 */
export interface ResumeResponse {
  /** 会话ID */
  thread_id: string;
  /** 消息 */
  message: string;
  /** 状态：completed | interrupted | error */
  status: 'completed' | 'interrupted' | 'error';
}

/**
 * 状态信息
 */
export interface StateInfo {
  /** 会话ID */
  thread_id: string;
  /** 消息数量 */
  messages_count: number;
  /** 意图 */
  intent?: IntentType;
  /** 路由 */
  route?: RouteType;
  /** 使用过的工具 */
  tools_used: string[];
  /** 是否中断 */
  is_interrupted: boolean;
  /** 下一个节点 */
  next_node?: string;
  /** 元数据 */
  metadata: Record<string, any>;
}

/**
 * Checkpoint 历史项
 */
export interface CheckpointHistoryItem {
  /** Checkpoint ID */
  checkpoint_id: string;
  /** 父 Checkpoint ID */
  parent_checkpoint_id?: string;
  /** 消息数量 */
  messages_count: number;
  /** 意图 */
  intent?: IntentType;
  /** 路由 */
  route?: RouteType;
  /** 下一个节点 */
  next_node?: string;
  /** 元数据 */
  metadata: Record<string, any>;
}

/**
 * Checkpoint 历史响应
 */
export interface CheckpointHistoryResponse {
  /** 会话ID */
  thread_id: string;
  /** 历史列表 */
  history: CheckpointHistoryItem[];
  /** 总数 */
  total: number;
}

/**
 * 工具信息
 */
export interface ToolInfo {
  /** 工具名称 */
  name: string;
  /** 工具描述 */
  description: string;
  /** 来源：builtin | MCP */
  source: 'builtin' | 'MCP';
}

/**
 * 工具列表响应
 */
export interface ToolsResponse {
  /** 工具总数 */
  total: number;
  /** MCP是否已加载 */
  mcp_loaded: boolean;
  /** 工具列表 */
  tools: ToolInfo[];
}

/**
 * 健康检查响应
 */
export interface HealthResponse {
  /** 状态 */
  status: 'healthy' | 'unhealthy';
  /** 工具总数 */
  tools_count: number;
  /** MCP是否已加载 */
  mcp_loaded: boolean;
  /** 可用工具列表 */
  tools: string[];
}

/**
 * 错误响应
 */
export interface ErrorResponse {
  /** 错误消息 */
  detail: string;
}

// ==================== SSE 事件类型 ====================

/**
 * SSE 基础事件
 */
export interface SSEBaseEvent {
  /** 事件类型 */
  event: 'start' | 'node_start' | 'node_end' | 'message' | 'token' | 'chunk' | 'metadata' | 'done' | 'error';
}

/**
 * 节点开始事件
 */
export interface SSENodeStartEvent extends SSEBaseEvent {
  event: 'node_start';
  /** 节点名称 */
  node: string;
}

/**
 * 节点结束事件
 */
export interface SSENodeEndEvent extends SSEBaseEvent {
  event: 'node_end';
  /** 节点名称 */
  node: string;
}

/**
 * 消息事件
 */
export interface SSEMessageEvent extends SSEBaseEvent {
  event: 'message';
  /** 节点名称 */
  node: string;
  /** 角色 */
  role: 'human' | 'ai';
  /** 内容 */
  content: string;
}

/**
 * Token 事件（流式输出）
 */
export interface SSETokenEvent extends SSEBaseEvent {
  event: 'token';
  /** Token 内容 */
  content: string;
}

/**
 * Chunk 事件（块级输出）
 */
export interface SSEChunkEvent extends SSEBaseEvent {
  event: 'chunk';
  /** 角色 */
  role: 'human' | 'ai';
  /** 内容块 */
  content: string;
}

/**
 * 开始事件
 */
export interface SSEStartEvent extends SSEBaseEvent {
  event: 'start';
}

/**
 * 元数据事件
 */
export interface SSEMetadataEvent extends SSEBaseEvent {
  event: 'metadata';
  /** 意图 */
  intent?: IntentType;
  /** 路由 */
  route?: RouteType;
  /** 检索文档数量 */
  retrieved_docs_count?: number;
}

/**
 * 完成事件
 */
export interface SSEDoneEvent extends SSEBaseEvent {
  event: 'done';
}

/**
 * 错误事件
 */
export interface SSEErrorEvent extends SSEBaseEvent {
  event: 'error';
  /** 错误消息 */
  data: {
    error: string;
  };
}

/**
 * SSE 事件联合类型
 */
export type SSEEvent =
  | SSEStartEvent
  | SSENodeStartEvent
  | SSENodeEndEvent
  | SSEMessageEvent
  | SSETokenEvent
  | SSEChunkEvent
  | SSEMetadataEvent
  | SSEDoneEvent
  | SSEErrorEvent;

// ==================== 枚举类型 ====================

/**
 * 意图类型
 */
export type IntentType =
  | 'general_chat'      // 闲聊
  | 'simple_qa'         // 简单问答
  | 'rag_required'      // 需要RAG检索
  | 'tool_required'     // 需要工具调用
  | 'complex_task'      // 复杂任务（需要规划）
  | 'multimodal'        // 多模态
  | 'unknown';          // 未知

/**
 * 路由类型
 */
export type RouteType =
  | 'output'           // 直接输出
  | 'rag_agent'        // RAG代理
  | 'tool_agent'       // 工具调用
  | 'planner'          // 任务规划
  | 'vision_agent'     // 视觉代理
  | 'writer_agent';    // 写作代理

/**
 * 节点类型
 */
export type NodeType =
  | 'entry'            // 入口
  | 'router'           // 路由
  | 'rag_agent'        // RAG
  | 'tool_agent'       // 工具（已废弃）
  | 'tool_call'        // 工具调用节点
  | 'tool_execute'     // 工具执行节点
  | 'planner'          // 规划
  | 'executor'         // 执行
  | 'executor_v2'      // 执行器V2
  | 'vision_agent'     // 视觉
  | 'writer_agent'     // 写作
  | 'human_review'     // 人工审核
  | 'output'           // 输出
  | 'memory_extractor';// 记忆提取

// ==================== 前端专用类型 ====================

/**
 * 会话
 */
export interface Conversation {
  /** 会话ID */
  id: string;
  /** 会话标题 */
  title: string;
  /** 消息列表 */
  messages: Message[];
  /** 最后更新时间 */
  lastUpdated: number;
  /** 是否收藏标记 */
  starred?: boolean;
}

/**
 * UI 状态
 */
export interface UIState {
  /** 是否正在流式响应 */
  isStreaming: boolean;
  /** 当前执行的节点 */
  currentNode: NodeType | null;
  /** 是否显示侧边栏 */
  showSidebar: boolean;
  /** 是否暗黑模式 */
  darkMode: boolean;
  /** 是否显示设置面板 */
  showSettings: boolean;
}

/**
 * 应用配置
 */
export interface AppConfig {
  /** API 基础URL */
  apiBaseUrl: string;
  /** 超时时间（毫秒） */
  timeout: number;
  /** 最大图片大小（字节） */
  maxImageSize: number;
  /** 最大图片数量 */
  maxImages: number;
  /** 用户ID */
  userId?: string;
}

// ==================== 工具和辅助类型 ====================

/**
 * API 请求选项
 */
export interface ApiOptions {
  /** 自定义headers */
  headers?: Record<string, string>;
  /** 超时时间 */
  timeout?: number;
  /** 是否显示加载指示器 */
  showLoading?: boolean;
}

/**
 * SSE 回调处理函数
 */
export type SSEEventHandler = (event: SSEEvent) => void;

/**
 * SSE 选项
 */
export interface SSEOptions {
  /** 事件处理函数 */
  onEvent: SSEEventHandler;
  /** 错误处理函数 */
  onError?: (error: Error) => void;
  /** 完成处理函数 */
  onComplete?: () => void;
}
