import { useState } from "react";
import { TaskPanel } from "../components/TaskPanel";
import { EventsPanel } from "../components/EventsPanel";
import { SettingsPanel } from "../components/SettingsPanel";
import { WorkspacePanel } from "../components/WorkspacePanel";
import type { TaskSummary } from "../api";

type TabKey = "tasks" | "events" | "settings" | "workspace";

export default function Dashboard() {
  const [activeTab, setActiveTab] = useState<TabKey>("tasks");
  const [selectedTask, setSelectedTask] = useState<TaskSummary | null>(null);

  function handleTaskSelect(task: TaskSummary) {
    setSelectedTask(task);
    setActiveTab("events");
  }

  return (
    <div style={{
      minHeight: "100vh",
      background: "linear-gradient(135deg, #0b1220 0%, #1a1f35 50%, #0f1729 100%)",
      color: "var(--text)",
      fontFamily: "'Cairo', 'Segoe UI', Tahoma, sans-serif"
    }}>
      {/* Header */}
      <header style={{
        background: "rgba(16, 26, 47, 0.8)",
        backdropFilter: "blur(10px)",
        borderBottom: "1px solid rgba(148, 163, 184, 0.18)",
        padding: "20px 40px",
        position: "sticky",
        top: 0,
        zIndex: 1000
      }}>
        <div style={{
          display: "flex",
          alignItems: "center",
          justifyContent: "space-between",
          maxWidth: 1600,
          margin: "0 auto"
        }}>
          <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
            <div style={{
              fontSize: 40,
              background: "linear-gradient(135deg, #7c3aed, #9333ea)",
              WebkitBackgroundClip: "text",
              WebkitTextFillColor: "transparent",
              fontWeight: 900
            }}>
              🚀
            </div>
            <div>
              <h1 style={{
                margin: 0,
                fontSize: 28,
                fontWeight: 900,
                background: "linear-gradient(135deg, #7c3aed, #9333ea)",
                WebkitBackgroundClip: "text",
                WebkitTextFillColor: "transparent"
              }}>
                mkh_Manus Pro
              </h1>
              <div style={{
                fontSize: 13,
                color: "var(--muted)",
                marginTop: 4,
                fontWeight: 600
              }}>
                نظام إدارة المهام المتقدم • الإصدار 2.1
              </div>
            </div>
          </div>

          <div style={{
            display: "flex",
            alignItems: "center",
            gap: 12,
            padding: "10px 20px",
            background: "rgba(124, 58, 237, 0.15)",
            borderRadius: 12,
            border: "1px solid rgba(124, 58, 237, 0.3)"
          }}>
            <div style={{ fontSize: 24 }}>👤</div>
            <div>
              <div style={{ fontWeight: 700, fontSize: 14 }}>المسؤول</div>
              <div style={{ fontSize: 12, color: "var(--muted)" }}>Admin</div>
            </div>
          </div>
        </div>
      </header>

      {/* Navigation Tabs */}
      <div style={{
        background: "rgba(16, 26, 47, 0.6)",
        borderBottom: "1px solid rgba(148, 163, 184, 0.18)",
        padding: "0 40px"
      }}>
        <div style={{
          maxWidth: 1600,
          margin: "0 auto",
          display: "flex",
          gap: 8
        }}>
          {[
            { key: "tasks" as TabKey, label: "⚙️ إدارة المهام", icon: "⚙️" },
            { key: "events" as TabKey, label: "📊 الأحداث والسجلات", icon: "📊" },
            { key: "workspace" as TabKey, label: "📁 مساحة العمل", icon: "📁" },
            { key: "settings" as TabKey, label: "🛠️ الإعدادات", icon: "🛠️" }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key)}
              style={{
                padding: "16px 24px",
                background: activeTab === tab.key
                  ? "linear-gradient(135deg, rgba(124, 58, 237, 0.3), rgba(147, 51, 234, 0.2))"
                  : "transparent",
                border: "none",
                borderBottom: activeTab === tab.key
                  ? "3px solid #7c3aed"
                  : "3px solid transparent",
                color: activeTab === tab.key ? "#fff" : "var(--muted)",
                fontSize: 15,
                fontWeight: activeTab === tab.key ? 700 : 600,
                cursor: "pointer",
                transition: "all 0.3s ease",
                fontFamily: "inherit"
              }}
            >
              {tab.label}
            </button>
          ))}
        </div>
      </div>

      {/* Main Content */}
      <main style={{
        maxWidth: 1600,
        margin: "0 auto",
        padding: "40px"
      }}>
        {activeTab === "tasks" && (
          <TaskPanel
            onSelect={handleTaskSelect}
            selectedId={selectedTask?.id}
          />
        )}

        {activeTab === "events" && (
          <EventsPanel taskId={selectedTask?.id} />
        )}

        {activeTab === "workspace" && (
          <WorkspacePanel />
        )}

        {activeTab === "settings" && (
          <SettingsPanel />
        )}
      </main>

      {/* Footer */}
      <footer style={{
        background: "rgba(16, 26, 47, 0.8)",
        borderTop: "1px solid rgba(148, 163, 184, 0.18)",
        padding: "30px 40px",
        marginTop: 60
      }}>
        <div style={{
          maxWidth: 1600,
          margin: "0 auto",
          textAlign: "center"
        }}>
          <div style={{
            fontSize: 14,
            color: "var(--muted)",
            marginBottom: 12
          }}>
            نظام mkh_Manus Pro - نظام إدارة مهام متقدم مدعوم بالذكاء الاصطناعي
          </div>
          <div style={{
            fontSize: 13,
            color: "var(--muted)",
            opacity: 0.7
          }}>
            © 2025 mkh_Manus. جميع الحقوق محفوظة.
          </div>
        </div>
      </footer>
    </div>
  );
}
