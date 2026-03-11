import { useState } from 'react';
import { X, AlertTriangle, Check, XCircle } from 'lucide-react';
import type { InterruptStatus } from '../../types/api';

interface ConfirmDialogProps {
  status: InterruptStatus;
  onApprove: (reason?: string) => void;
  onReject: (reason?: string) => void;
  onClose: () => void;
  isProcessing: boolean;
}

export const ConfirmDialog = ({
  status,
  onApprove,
  onReject,
  onClose,
  isProcessing,
}: ConfirmDialogProps) => {
  const [reason, setReason] = useState('');
  const [action, setAction] = useState<'approve' | 'reject' | null>(null);

  const handleSubmit = () => {
    if (action === 'approve') {
      onApprove(reason || undefined);
    } else if (action === 'reject') {
      onReject(reason || undefined);
    }
  };

  const getRiskLevelColor = (level?: string) => {
    switch (level) {
      case 'high':
        return 'text-red-500 bg-red-500/20';
      case 'medium':
        return 'text-yellow-500 bg-yellow-500/20';
      case 'low':
        return 'text-green-500 bg-green-500/20';
      default:
        return 'text-gray-500 bg-gray-500/20';
    }
  };

  const getRiskLevelLabel = (level?: string) => {
    switch (level) {
      case 'high':
        return '高风险';
      case 'medium':
        return '中风险';
      case 'low':
        return '低风险';
      default:
        return '未知';
    }
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/70 backdrop-blur-sm animate-fadeIn">
      <div className="bg-secondary border border-gray-800 rounded-2xl shadow-2xl max-w-2xl w-full mx-4 max-h-[80vh] overflow-y-auto custom-scrollbar">
        {/* 头部 */}
        <div className="flex items-center justify-between p-6 border-b border-gray-800">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 bg-yellow-500/20 rounded-full flex items-center justify-center">
              <AlertTriangle className="w-5 h-5 text-yellow-500" />
            </div>
            <div>
              <h2 className="text-xl font-bold text-gray-100">需要人工确认</h2>
              <p className="text-sm text-gray-400">AI 正在等待您的批准</p>
            </div>
          </div>
          <button
            onClick={onClose}
            className="p-2 hover:bg-gray-800 rounded-lg transition-colors"
            disabled={isProcessing}
            aria-label="关闭"
          >
            <X className="w-5 h-5" />
          </button>
        </div>

        {/* 内容 */}
        <div className="p-6 space-y-4">
          {status.interrupt_reason && (
            <div className="bg-primary/50 rounded-lg p-4">
              <h3 className="text-sm font-semibold text-gray-400 mb-2">中断原因</h3>
              <p className="text-gray-200">{status.interrupt_reason}</p>
            </div>
          )}

          {status.tool_calls && status.tool_calls.length > 0 && (
            <div className="space-y-3">
              <h3 className="text-sm font-semibold text-gray-400">待确认的操作</h3>

              {status.tool_calls.map((tool, index) => (
                <div
                  key={index}
                  className="bg-primary/50 rounded-lg p-4 border border-gray-800"
                >
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h4 className="font-semibold text-gray-100 mb-1">
                        {tool.name}
                      </h4>
                      {tool.risk_level && (
                        <span
                          className={`inline-block text-xs px-2 py-1 rounded ${getRiskLevelColor(
                            tool.risk_level
                          )}`}
                        >
                          {getRiskLevelLabel(tool.risk_level)}
                        </span>
                      )}
                    </div>
                  </div>

                  <div className="space-y-2">
                    <h5 className="text-xs font-semibold text-gray-400">参数</h5>
                    <pre className="bg-gray-900 rounded p-3 text-xs text-gray-300 overflow-x-auto">
                      {JSON.stringify(tool.args, null, 2)}
                    </pre>
                  </div>
                </div>
              ))}
            </div>
          )}

          {/* 原因输入 */}
          <div>
            <label className="block text-sm font-semibold text-gray-400 mb-2">
              备注（可选）
            </label>
            <textarea
              value={reason}
              onChange={(e) => setReason(e.target.value)}
              placeholder="请输入批准或拒绝的原因..."
              className="w-full bg-primary/50 border border-gray-800 rounded-lg px-4 py-3 text-gray-100 placeholder-gray-600 focus:border-accent outline-none resize-none"
              rows={3}
              disabled={isProcessing}
            />
          </div>
        </div>

        {/* 底部按钮 */}
        <div className="flex items-center justify-end gap-3 p-6 border-t border-gray-800">
          <button
            onClick={() => {
              setAction('reject');
              handleSubmit();
            }}
            disabled={isProcessing}
            className="flex items-center gap-2 px-6 py-2.5 bg-red-500/20 hover:bg-red-500/30 text-red-400 rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <XCircle className="w-4 h-4" />
            <span>拒绝</span>
          </button>

          <button
            onClick={() => {
              setAction('approve');
              handleSubmit();
            }}
            disabled={isProcessing}
            className="flex items-center gap-2 px-6 py-2.5 bg-accent hover:bg-accent-light text-white rounded-lg transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <Check className="w-4 h-4" />
            <span>{isProcessing ? '处理中...' : '批准'}</span>
          </button>
        </div>
      </div>
    </div>
  );
};
