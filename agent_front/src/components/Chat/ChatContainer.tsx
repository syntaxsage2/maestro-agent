import { MessageList } from './MessageList';
import { MessageInput } from './MessageInput';
import { ConfirmDialog } from '../HITL/ConfirmDialog';
import { useChatStore } from '../../store/chatStore';
import { useHITL } from '../../hooks/useHITL';

export const ChatContainer = () => {
  const { getCurrentConversation, currentNode } = useChatStore();
  const conversation = getCurrentConversation();
  
  const {
    interruptStatus,
    isProcessing,
    handleApprove,
    handleReject,
    clearInterruptStatus,
  } = useHITL({
    threadId: conversation?.id || null,
    enabled: true,
  });
  
  return (
    <>
      <div className="flex-1 flex flex-col overflow-hidden">
        <MessageList />
        <MessageInput />
      </div>
      
      {interruptStatus?.is_interrupted && (
        <ConfirmDialog
          status={interruptStatus}
          onApprove={handleApprove}
          onReject={handleReject}
          onClose={clearInterruptStatus}
          isProcessing={isProcessing}
        />
      )}
    </>
  );
};

