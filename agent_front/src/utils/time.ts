import { format, formatDistanceToNow } from 'date-fns';
import { zhCN } from 'date-fns/locale';

/**
 * 格式化时间为相对时间
 * @param timestamp 时间戳（毫秒）
 * @returns 相对时间字符串，如 "刚刚"、"5分钟前"
 */
export const formatRelativeTime = (timestamp: number): string => {
  const now = Date.now();
  const diff = now - timestamp;

  // 小于 1 分钟
  if (diff < 60 * 1000) {
    return '刚刚';
  }

  // 小于 1 小时
  if (diff < 60 * 60 * 1000) {
    const minutes = Math.floor(diff / (60 * 1000));
    return `${minutes}分钟前`;
  }

  // 小于 1 天
  if (diff < 24 * 60 * 60 * 1000) {
    const hours = Math.floor(diff / (60 * 60 * 1000));
    return `${hours}小时前`;
  }

  // 小于 7 天
  if (diff < 7 * 24 * 60 * 60 * 1000) {
    const days = Math.floor(diff / (24 * 60 * 60 * 1000));
    return `${days}天前`;
  }

  // 超过 7 天，显示具体日期
  return format(timestamp, 'MM月dd日 HH:mm', { locale: zhCN });
};

/**
 * 格式化时间为完整时间
 * @param timestamp 时间戳（毫秒）
 * @returns 完整时间字符串，如 "2024-01-01 12:00:00"
 */
export const formatFullTime = (timestamp: number): string => {
  return format(timestamp, 'yyyy-MM-dd HH:mm:ss', { locale: zhCN });
};

/**
 * 格式化时间为简短时间
 * @param timestamp 时间戳（毫秒）
 * @returns 简短时间字符串，如 "12:00"
 */
export const formatShortTime = (timestamp: number): string => {
  return format(timestamp, 'HH:mm', { locale: zhCN });
};
