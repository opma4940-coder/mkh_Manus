import { useState, useRef, useEffect } from 'react';
import './styles.css';
import { TaskPanel } from './components/TaskPanel';
import { SettingsPanel } from './components/SettingsPanel';
import { EventsPanel } from './components/EventsPanel';
import type { TaskSummary } from './api';

interface ConversationMessage {
  id: string;
  type: 'user' | 'system';
  content: string;
  timestamp: Date;
  taskId?: string;
}

const App = () => {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activePanel, setActivePanel] = useState<'workspace' | 'tasks' | 'settings'>('workspace');
  const [selectedTask, setSelectedTask] = useState<TaskSummary | null>(null);
  const [conversationMessages, setConversationMessages] = useState<ConversationMessage[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [conversationMessages]);

  const handleSendMessage = async (message: string) => {
    if (!message.trim()) return;

    const userMessage: ConversationMessage = {
      id: Date.now().toString(),
      type: 'user',
      content: message,
      timestamp: new Date(),
    };

    setConversationMessages(prev => [...prev, userMessage]);
    setInputValue('');
    setIsLoading(true);

    setTimeout(() => {
      const systemMessage: ConversationMessage = {
        id: (Date.now() + 1).toString(),
        type: 'system',
        content: 'تم استقبال طلبك. يتم معالجة الأمر...',
        timestamp: new Date(),
      };
      setConversationMessages(prev => [...prev, systemMessage]);
      setIsLoading(false);
    }, 500);
  };

  return (
    <div className="app-container">
      <aside className={`sidebar ${sidebarOpen ? 'open' : 'closed'}`}>
        <div className="sidebar-header">
          <div className="sidebar-brand">
            <div className="brand-icon">🚀</div>
            <div className="brand-text">
              <div className="brand-name">mkh_Manus</div>
              <div className="brand-subtitle">Pro</div>
            </div>
          </div>
          <button 
            className="sidebar-toggle"
            onClick={() => setSidebarOpen(!sidebarOpen)}
            title={sidebarOpen ? 'إغلاق الشريط الجانبي' : 'فتح الشريط الجانبي'}
          >
            {sidebarOpen ? '←' : '→'}
          </button>
        </div>

        <nav className="sidebar-nav">
          <button
            className={`nav-item ${activePanel === 'workspace' ? 'active' : ''}`}
            onClick={() => setActivePanel('workspace')}
            title="مساحة العمل"
          >
            <span className="nav-icon">💼</span>
            {sidebarOpen && <span className="nav-text">مساحة العمل</span>}
          </button>
          
          <button
            className={`nav-item ${activePanel === 'tasks' ? 'active' : ''}`}
            onClick={() => setActivePanel('tasks')}
            title="إدارة المهام"
          >
            <span className="nav-icon">⚙️</span>
            {sidebarOpen && <span className="nav-text">إدارة المهام</span>}
          </button>

          <button
            className={`nav-item ${activePanel === 'settings' ? 'active' : ''}`}
            onClick={() => setActivePanel('settings')}
            title="الإعدادات"
          >
            <span className="nav-icon">⚡</span>
            {sidebarOpen && <span className="nav-text">الإعدادات</span>}
          </button>
        </nav>

        <div className="sidebar-footer">
          <button className="sidebar-btn" title="تسجيل الخروج">
            <span className="nav-icon">🚪</span>
            {sidebarOpen && <span>تسجيل الخروج</span>}
          </button>
        </div>
      </aside>

      <main className="main-content">
        {activePanel === 'workspace' && (
          <div className="workspace-layout">
            <div className="chat-container">
              <div className="chat-header">
                <div className="chat-title">
                  <h1>مساحة العمل الموحدة</h1>
                  <p>أرسل رسالة أو طلب مهمة أو استخدم نظام الوكيل</p>
                </div>
              </div>

              <div className="chat-messages">
                {conversationMessages.length === 0 ? (
                  <div className="empty-state">
                    <div className="empty-icon">💬</div>
                    <h2>مرحباً بك في mkh_Manus</h2>
                    <p>ابدأ محادثة جديدة أو أنشئ مهمة جديدة</p>
                    <div className="quick-actions">
                      <button className="quick-action-btn">
                        <span>📝</span>
                        <span>إنشاء مهمة</span>
                      </button>
                      <button className="quick-action-btn">
                        <span>🔍</span>
                        <span>استعلام</span>
                      </button>
                      <button className="quick-action-btn">
                        <span>🤖</span>
                        <span>وكيل ذكي</span>
                      </button>
                    </div>
                  </div>
                ) : (
                  <>
                    {conversationMessages.map(msg => (
                      <div key={msg.id} className={`message message-${msg.type}`}>
                        <div className="message-avatar">
                          {msg.type === 'user' ? '👤' : '🤖'}
                        </div>
                        <div className="message-content">
                          <div className="message-text">{msg.content}</div>
                          <div className="message-time">
                            {msg.timestamp.toLocaleTimeString('ar-SA')}
                          </div>
                        </div>
                      </div>
                    ))}
                    {isLoading && (
                      <div className="message message-system">
                        <div className="message-avatar">🤖</div>
                        <div className="message-content">
                          <div className="loading-dots">
                            <span></span><span></span><span></span>
                          </div>
                        </div>
                      </div>
                    )}
                    <div ref={messagesEndRef} />
                  </>
                )}
              </div>

              <div className="chat-input-area">
                <div className="input-wrapper">
                  <textarea
                    value={inputValue}
                    onChange={(e) => setInputValue(e.target.value)}
                    onKeyDown={(e) => {
                      if (e.key === 'Enter' && !e.shiftKey) {
                        e.preventDefault();
                        handleSendMessage(inputValue);
                      }
                    }}
                    placeholder="اكتب رسالتك هنا... (Shift+Enter للسطر الجديد)"
                    className="chat-input"
                    disabled={isLoading}
                  />
                  <button
                    onClick={() => handleSendMessage(inputValue)}
                    disabled={!inputValue.trim() || isLoading}
                    className="send-btn"
                    title="إرسال الرسالة"
                  >
                    ✈️
                  </button>
                </div>
                <div className="input-hints">
                  <span>💡 استخدم الأوامر: /task (مهمة), /agent (وكيل), /search (بحث)</span>
                </div>
              </div>
            </div>

            {selectedTask && (
              <div className="task-sidebar">
                <div className="task-sidebar-header">
                  <h3>تفاصيل المهمة</h3>
                  <button 
                    className="close-btn"
                    onClick={() => setSelectedTask(null)}
                    title="إغلاق"
                  >
                    ✕
                  </button>
                </div>
                <EventsPanel taskId={selectedTask.id} />
              </div>
            )}
          </div>
        )}

        {activePanel === 'tasks' && (
          <TaskPanel 
            onSelect={(task) => {
              setSelectedTask(task);
              setActivePanel('workspace');
            }} 
            selectedId={selectedTask?.id}
          />
        )}

        {activePanel === 'settings' && (
          <SettingsPanel />
        )}
      </main>
    </div>
  );
};

export default App;
