import { useState, useEffect, useCallback, useRef } from 'react';
import { toast } from 'react-hot-toast';
import {
  getInterruptStatus,
  approveOperation,
  rejectOperation
} from '../api/hitl';
import type { InterruptStatus } from '../types/api';

interface UseHITLOptions {
  threadId: string | null;
  enabled?: boolean;
  pollingInterval?: number;
}

export const useHITL = ({
  threadId,
  enabled = true,
  pollingInterval = 1000
}: UseHITLOptions) => {
  const [interruptStatus, setInterruptStatus] = useState<InterruptStatus | null>(null);
  const [isPolling, setIsPolling] = useState(false);
  const [isProcessing, setIsProcessing] = useState(false);

  // 使用 ref 存储定时器 ID，以便能够清除
  const intervalIdRef = useRef<number | null>(null);
  const startTimeoutRef = useRef<number | null>(null);
  const autoStopTimeoutRef = useRef<number | null>(null);
  const checkCountRef = useRef<number>(0); // 记录已检查次数

  /**
   * 停止轮询
   */
  const stopPolling = useCallback(() => {
    if (intervalIdRef.current) {
      clearInterval(intervalIdRef.current);
      intervalIdRef.current = null;
    }
    if (startTimeoutRef.current) {
      clearTimeout(startTimeoutRef.current);
      startTimeoutRef.current = null;
    }
    if (autoStopTimeoutRef.current) {
      clearTimeout(autoStopTimeoutRef.current);
      autoStopTimeoutRef.current = null;
    }
    checkCountRef.current = 0; // 重置检查计数
    setIsPolling(false);
  }, []);

  /**
   * 检查中断状态
   */
  const checkInterruptStatus = useCallback(async () => {
    if (!threadId || !enabled) {
      stopPolling();
      return;
    }

    checkCountRef.current += 1;

    try {
      const status = await getInterruptStatus(threadId);

      // state_exists: false - 会话还未初始化，继续轮询
      if (!status.state_exists) {
        console.log(`HITL check ${checkCountRef.current}: State not exists yet, continue polling`);

        // 如果轮询超过 10 次还没有状态，停止轮询
        if (checkCountRef.current >= 10) {
          console.log('State not exists after 10 checks, stopping polling');
          stopPolling();
        }
        return;
      }

      // state_exists: true - 会话已初始化
      if (status.is_interrupted) {
        // is_interrupted: true - 需要人工确认
        setInterruptStatus(status);
        stopPolling();
        toast('检测到需要人工确认的操作', {
          icon: '⚠️',
          duration: 5000,
        });
      } else {
        // is_interrupted: false - 已完成，没有需要确认的操作
        console.log('No HITL interrupt needed, stopping polling');
        stopPolling();
      }
    } catch (error: any) {
      // 网络错误等异常情况，继续轮询直到超时
      console.log('HITL check error:', error?.message);

      // 如果错误次数过多，停止轮询
      if (checkCountRef.current >= 10) {
        console.log('Too many errors, stopping polling');
        stopPolling();
      }
    }
  }, [threadId, enabled, stopPolling]);

  /**
   * 开始轮询
   */
  const startPolling = useCallback(() => {
    if (!threadId || !enabled || isPolling) return;

    // 先清除可能存在的旧定时器
    stopPolling();

    // 重置检查计数
    checkCountRef.current = 0;

    setIsPolling(true);

    // 延迟 1 秒后开始第一次检查（给后端处理时间）
    startTimeoutRef.current = setTimeout(() => {
      checkInterruptStatus();

      // 然后设置定时轮询
      intervalIdRef.current = setInterval(() => {
        checkInterruptStatus();
      }, pollingInterval);
    }, 1000);

    // 15 秒后自动停止轮询（简化超时时间）
    autoStopTimeoutRef.current = setTimeout(() => {
      stopPolling();
      console.log('HITL polling stopped: timeout');
    }, 15000);
  }, [threadId, enabled, isPolling, pollingInterval, checkInterruptStatus, stopPolling]);

  /**
   * 批准操作
   */
  const handleApprove = async (reason?: string) => {
    if (!threadId) return;

    setIsProcessing(true);

    try {
      await approveOperation(threadId, reason);
      toast.success('批准操作成功');
      setInterruptStatus(null);
    } catch (error) {
      console.error('Approve error:', error);
      toast.error('批准操作失败');
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * 拒绝操作
   */
  const handleReject = async (reason?: string) => {
    if (!threadId) return;

    setIsProcessing(true);

    try {
      await rejectOperation(threadId, reason);
      toast.success('拒绝操作成功');
      setInterruptStatus(null);
    } catch (error) {
      console.error('Reject error:', error);
      toast.error('拒绝操作失败');
    } finally {
      setIsProcessing(false);
    }
  };

  /**
   * 清除中断状态
   */
  const clearInterruptStatus = () => {
    setInterruptStatus(null);
  };

  // 如果 threadId 发生变化，清除中断状态和停止轮询
  useEffect(() => {
    setInterruptStatus(null);
    stopPolling();
  }, [threadId, stopPolling]);

  // 组件卸载时清除定时器
  useEffect(() => {
    return () => {
      stopPolling();
    };
  }, [stopPolling]);

  return {
    interruptStatus,
    isPolling,
    isProcessing,
    startPolling,
    stopPolling,
    handleApprove,
    handleReject,
    clearInterruptStatus,
  };
};
