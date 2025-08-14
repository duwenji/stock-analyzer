import React from 'react';
import '../styles/components/SimpleConfirmationDialog.css';

interface SimpleConfirmationDialogProps {
  message: string;
  onConfirm: () => void;
  onCancel: () => void;
}

const SimpleConfirmationDialog: React.FC<SimpleConfirmationDialogProps> = ({
  message,
  onConfirm,
  onCancel
}) => {
  return (
    <div className="simple-confirmation-dialog-overlay">
      <div className="simple-confirmation-dialog">
        <h3>確認</h3>
        <p>{message}</p>
        <div className="simple-confirmation-action-buttons">
          <button onClick={onCancel} className="simple-confirmation-cancel-btn">キャンセル</button>
          <button onClick={onConfirm} className="simple-confirmation-confirm-btn">確認</button>
        </div>
      </div>
    </div>
  );
};

export default SimpleConfirmationDialog;
