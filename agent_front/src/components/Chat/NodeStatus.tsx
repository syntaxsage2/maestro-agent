import { Loader2 } from 'lucide-react';
import type { NodeType } from '../../types/api';

interface NodeStatusProps {
  node: NodeType | null;
}

const NODE_LABELS: Record<NodeType, string> = {
  entry: '正在处理',
  router: '路由分发',
  rag_agent: 'RAG 检索',
  tool_agent: '工具调用',
  planner: '任务规划',
  executor: '执行中',
  vision_agent: '图像分析',
  writer_agent: '写作中',
  human_review: '等待人工审核',
  output: '生成回复',
  memory_extractor: '记忆提取',
};

export const NodeStatus = ({ node }: NodeStatusProps) => {
  if (!node) return null;

  const label = NODE_LABELS[node] || '处理中';

  return (
    <div className="flex items-center gap-2 px-4 py-2 bg-secondary/50 rounded-lg backdrop-blur-sm border border-gray-800 animate-fadeIn">
      <Loader2 className="w-4 h-4 text-accent animate-spin" />
      <span className="text-sm text-gray-300">{label}</span>
    </div>
  );
};
