import React, { useState, useEffect } from 'react';
import { promptService } from './utils/apiService';
import SimpleConfirmationDialog from './components/SimpleConfirmationDialog';
import '../src/styles/components/PromptManagement.css';

interface Prompt {
  id: number;
  name: string;
  agent_type: string;
  system_role: string;
  user_template: string;
  output_format: string;
  created_at: string;
  updated_at: string;
}

const PromptManagement: React.FC = () => {
  const [prompts, setPrompts] = useState<Prompt[]>([]);
  const [currentPrompt, setCurrentPrompt] = useState<Prompt | null>(null);
  const [isEditing, setIsEditing] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [isDeleting, setIsDeleting] = useState(false);
  const [deleteTarget, setDeleteTarget] = useState<number | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);

  useEffect(() => {
    fetchPrompts();
  }, []);

  const fetchPrompts = async () => {
    try {
      const data = await promptService.getAllPrompts();
      // 日付フィールドを文字列に変換
      const formattedData = data.map((prompt: Prompt) => ({
        ...prompt,
        created_at: new Date(prompt.created_at).toISOString(),
        updated_at: new Date(prompt.updated_at).toISOString()
      }));
      setPrompts(formattedData);
    } catch (error) {
      console.error('プロンプト取得エラー:', error);
    }
  };

  const handleEdit = (prompt: Prompt) => {
    setCurrentPrompt(prompt);
    setIsEditing(true);
  };

  const handleCreate = () => {
    setCurrentPrompt({
      id: 0,
      name: '',
      agent_type: 'direct',
      system_role: '',
      user_template: '',
      output_format: '',
      created_at: '',
      updated_at: ''
    });
    setIsCreating(true);
  };

  const handleDelete = (id: number) => {
    setDeleteTarget(id);
    setIsDeleting(true);
  };

  const handleSave = async (promptData: { name: string; agent_type: string; system_role: string; user_template: string; output_format: string }) => {
    try {
      if (isCreating) {
        await promptService.createPrompt(promptData);
      } else {
        if (!currentPrompt) {
          throw new Error('編集するプロンプトが見つかりません');
        }
        await promptService.updatePrompt(currentPrompt.id, promptData);
      }
      setErrorMessage(null);
      fetchPrompts();
      setIsEditing(false);
      setIsCreating(false);
    } catch (error: any) {
      console.error('プロンプト保存エラー:', error);
      let errorMsg = '保存に失敗しました';
      if (error.response?.status === 422) {
        errorMsg = '入力データが不正です。必須項目を確認してください';
        if (error.response?.data?.detail) {
          errorMsg += `: ${JSON.stringify(error.response.data.detail)}`;
        }
      } else if (error.message) {
        errorMsg += `: ${error.message}`;
      }
      setErrorMessage(errorMsg);
    }
  };

  const confirmDelete = async () => {
    if (!deleteTarget) return;
    
    try {
      await promptService.deletePrompt(deleteTarget);
      fetchPrompts();
      setIsDeleting(false);
      setDeleteTarget(null);
    } catch (error) {
      console.error('プロンプト削除エラー:', error);
    }
  };

  return (
    <div className="prompt-management">
      <h2>プロンプト管理</h2>
      <button className="create-btn" onClick={handleCreate}>新規プロンプト作成</button>

      <div className="prompt-list">
        {prompts.map(prompt => (
          <div key={prompt.id} className="prompt-item">
            <div className="prompt-header">
              <h3 
                onClick={() => setExpandedId(expandedId === prompt.id ? null : prompt.id)}
                style={{ cursor: 'pointer' }}
              >
                {prompt.name} ({prompt.agent_type === 'direct' ? 'Direct' : 'MCP Agent'})
              </h3>
              <div className="prompt-actions">
                <button onClick={() => handleEdit(prompt)}>編集</button>
                <button onClick={() => handleDelete(prompt.id)}>削除</button>
              </div>
            </div>
            <div className="prompt-meta">
              <span>作成日: {new Date(prompt.created_at).toLocaleString()}</span>
              <span>更新日: {new Date(prompt.updated_at).toLocaleString()}</span>
            </div>
            {expandedId === prompt.id && (
              <div className="prompt-details">
                <div><strong>Agent Type:</strong> {prompt.agent_type}</div>
                <div><strong>System Role:</strong> {prompt.system_role}</div>
                <div><strong>User Template:</strong> {prompt.user_template}</div>
                <div><strong>Output Format:</strong> {prompt.output_format}</div>
              </div>
            )}
          </div>
        ))}
      </div>

      {(isEditing || isCreating) && currentPrompt && (
        <PromptEditModal
          prompt={currentPrompt}
          isCreating={isCreating}
          onSave={handleSave}
          onCancel={() => {
            setIsEditing(false);
            setIsCreating(false);
          }}
          errorMessage={errorMessage}
        />
      )}

      {isDeleting && (
        <SimpleConfirmationDialog
                message={`プロンプトID: ${deleteTarget} を削除しますか？`}
          onConfirm={confirmDelete}
          onCancel={() => setIsDeleting(false)}
        />
      )}
    </div>
  );
};

interface PromptEditModalProps {
  prompt: Prompt;
  isCreating: boolean;
  onSave: (data: { name: string; agent_type: string; system_role: string; user_template: string; output_format: string }) => void;
  onCancel: () => void;
  errorMessage: string | null;
}

const PromptEditModal: React.FC<PromptEditModalProps> = ({ prompt, isCreating, onSave, onCancel, errorMessage }) => {
  const [name, setName] = useState(prompt.name);
  const [agentType, setAgentType] = useState(prompt.agent_type);
  const [systemRole, setSystemRole] = useState(prompt.system_role);
  const [userTemplate, setUserTemplate] = useState(prompt.user_template);
  const [outputFormat, setOutputFormat] = useState(prompt.output_format);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const data = {
      name: isCreating ? name : prompt.name, // 編集時は元のnameを使用
      agent_type: agentType,
      system_role: systemRole,
      user_template: userTemplate,
      output_format: outputFormat
    };
    onSave(data);
  };

  return (
    <div className="modal-overlay">
      <div className="modal-content">
        <h3>{isCreating ? '新規プロンプト作成' : 'プロンプト編集'}</h3>
        {errorMessage && (
          <div className="error-message">
            {errorMessage.split('\n').map((line, i) => (
              <div key={i}>{line}</div>
            ))}
          </div>
        )}
        <form onSubmit={handleSubmit}>
          <div className="form-group">
            <label>プロンプト名:</label>
            <input
              type="text"
              value={name}
              onChange={(e) => setName(e.target.value)}
              required
              disabled={!isCreating}
            />
          </div>
          <div className="form-group">
            <label>エージェントタイプ:</label>
            <select
              value={agentType}
              onChange={(e) => setAgentType(e.target.value)}
              required
            >
              <option value="direct">Direct (シンプルな推奨生成)</option>
              <option value="mcpagent">MCP Agent (評価・最適化ループ付き)</option>
            </select>
          </div>
          <div className="form-group">
            <label>System Role:</label>
            <textarea
              value={systemRole}
              onChange={(e) => setSystemRole(e.target.value)}
              rows={5}
            />
          </div>
          <div className="form-group">
            <label>ユーザーテンプレート:</label>
            <textarea
              value={userTemplate}
              onChange={(e) => setUserTemplate(e.target.value)}
              required
              rows={10}
            />
          </div>
          <div className="form-group">
            <label>出力フォーマット:</label>
            <textarea
              value={outputFormat}
              onChange={(e) => setOutputFormat(e.target.value)}
              required
              rows={5}
            />
          </div>
          <div className="modal-actions">
            <button type="button" onClick={onCancel}>キャンセル</button>
            <button type="submit">保存</button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default PromptManagement;
