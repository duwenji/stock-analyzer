import React from 'react';
import '../styles/components/ConfirmationDialog.css';

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
    <div className="confirmation-dialog-overlay">
      <div className="confirmation-dialog">
        <h3>確認</h3>
        <p>{message}</p>
        <div className="action-buttons">
          <button onClick={onCancel} className="cancel-btn">キャンセル</button>
          <button onClick={onConfirm} className="confirm-btn">確認</button>
        </div>
      </div>
    </div>
  );
};

export default SimpleConfirmationDialog;
