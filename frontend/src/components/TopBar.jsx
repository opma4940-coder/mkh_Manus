import React from "react";

/**
 * مكون شريط العلوي (TopBar)
 * يعرض شعار النظام، اسم المستخدم، وأزرار التحكم الرئيسية
 */
export default function TopBar() {
  return (
    <div
      style={{
        display: "flex",
        alignItems: "center",
        justifyContent: "space-between",
        padding: "var(--space-md)",
        backgroundColor: "var(--color-bg-secondary)",
        borderBottom: "1px solid var(--color-bg-tertiary)",
        height: "60px",
      }}
    >
      {/* الشعار والعنوان */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <div
          style={{
            width: "40px",
            height: "40px",
            borderRadius: "8px",
            backgroundColor: "var(--color-accent)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "20px",
            fontWeight: "bold",
            color: "var(--color-text-primary)",
          }}
        >
          🚀
        </div>
        <h1
          style={{
            fontSize: "18px",
            fontWeight: "600",
            color: "var(--color-text-primary)",
            margin: 0,
          }}
        >
          mkh_Manus Pro
        </h1>
      </div>

      {/* معلومات المستخدم */}
      <div style={{ display: "flex", alignItems: "center", gap: "12px" }}>
        <span
          style={{
            fontSize: "14px",
            color: "var(--color-text-secondary)",
          }}
        >
          المستخدم: Admin
        </span>
        <div
          style={{
            width: "32px",
            height: "32px",
            borderRadius: "50%",
            backgroundColor: "var(--color-accent)",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "14px",
            fontWeight: "bold",
            color: "var(--color-text-primary)",
            cursor: "pointer",
          }}
        >
          👤
        </div>
      </div>
    </div>
  );
}
