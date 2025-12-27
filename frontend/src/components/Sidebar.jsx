import React, { useState } from "react";

/**
 * مكون القائمة الجانبية (Sidebar)
 * يعرض قائمة المهام، الإعدادات، والأقسام المختلفة
 */
export default function Sidebar() {
  const [activeSection, setActiveSection] = useState("tasks");

  const sections = [
    { id: "tasks", label: "📋 المهام", icon: "📋" },
    { id: "workspace", label: "💼 مساحة العمل", icon: "💼" },
    { id: "events", label: "📊 الأحداث", icon: "📊" },
    { id: "settings", label: "⚙️ الإعدادات", icon: "⚙️" },
  ];

  return (
    <div
      style={{
        backgroundColor: "var(--color-bg-secondary)",
        height: "calc(100vh - 60px)",
        display: "flex",
        flexDirection: "column",
        borderLeft: "1px solid var(--color-bg-tertiary)",
      }}
    >
      {/* زر إنشاء مهمة جديدة */}
      <div style={{ padding: "var(--space-md)" }}>
        <button
          style={{
            width: "100%",
            padding: "12px",
            backgroundColor: "var(--color-accent)",
            color: "var(--color-text-primary)",
            border: "none",
            borderRadius: "var(--radius-md)",
            fontSize: "14px",
            fontWeight: "600",
            cursor: "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            gap: "8px",
            transition: "background-color 0.2s",
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = "var(--color-accent-hover)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "var(--color-accent)";
          }}
        >
          <span style={{ fontSize: "18px" }}>+</span>
          <span>إنشاء مهمة جديدة</span>
        </button>
      </div>

      {/* قائمة الأقسام */}
      <div style={{ flex: 1, overflowY: "auto", padding: "0 var(--space-md)" }}>
        {sections.map((section) => (
          <div
            key={section.id}
            onClick={() => setActiveSection(section.id)}
            style={{
              padding: "12px",
              marginBottom: "8px",
              backgroundColor:
                activeSection === section.id
                  ? "var(--color-bg-tertiary)"
                  : "transparent",
              borderRadius: "var(--radius-md)",
              cursor: "pointer",
              display: "flex",
              alignItems: "center",
              gap: "12px",
              transition: "background-color 0.2s",
            }}
            onMouseEnter={(e) => {
              if (activeSection !== section.id) {
                e.currentTarget.style.backgroundColor = "var(--color-bg-tertiary)";
              }
            }}
            onMouseLeave={(e) => {
              if (activeSection !== section.id) {
                e.currentTarget.style.backgroundColor = "transparent";
              }
            }}
          >
            <span style={{ fontSize: "20px" }}>{section.icon}</span>
            <span
              style={{
                fontSize: "14px",
                color:
                  activeSection === section.id
                    ? "var(--color-text-primary)"
                    : "var(--color-text-secondary)",
                fontWeight: activeSection === section.id ? "600" : "400",
              }}
            >
              {section.label}
            </span>
          </div>
        ))}
      </div>

      {/* معلومات النظام */}
      <div
        style={{
          padding: "var(--space-md)",
          borderTop: "1px solid var(--color-bg-tertiary)",
        }}
      >
        <div
          style={{
            fontSize: "12px",
            color: "var(--color-text-muted)",
            textAlign: "center",
          }}
        >
          نظام إدارة المهام المتقدم
        </div>
        <div
          style={{
            fontSize: "11px",
            color: "var(--color-text-muted)",
            textAlign: "center",
            marginTop: "4px",
          }}
        >
          © 2025 mkh_Manus Pro
        </div>
      </div>
    </div>
  );
}
