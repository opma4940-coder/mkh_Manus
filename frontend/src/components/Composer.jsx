import React, { useState } from "react";

/**
 * مكون محرر الرسائل (Composer)
 * يسمح للمستخدم بكتابة وإرسال الرسائل والمهام
 */
export default function Composer() {
  const [message, setMessage] = useState("");
  const [isUploading, setIsUploading] = useState(false);

  const handleSend = () => {
    if (message.trim()) {
      console.log("إرسال رسالة:", message);
      // هنا يتم إرسال الرسالة إلى الخادم
      setMessage("");
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleFileUpload = () => {
    setIsUploading(true);
    // محاكاة رفع الملف
    setTimeout(() => {
      setIsUploading(false);
      console.log("تم رفع الملف بنجاح");
    }, 1000);
  };

  return (
    <div
      style={{
        padding: "var(--space-md)",
        backgroundColor: "var(--color-bg-secondary)",
        borderTop: "1px solid var(--color-bg-tertiary)",
      }}
    >
      <div
        style={{
          display: "flex",
          alignItems: "flex-end",
          gap: "12px",
          backgroundColor: "var(--color-bg-tertiary)",
          borderRadius: "var(--radius-md)",
          padding: "12px",
        }}
      >
        {/* زر رفع الملفات */}
        <button
          onClick={handleFileUpload}
          disabled={isUploading}
          style={{
            width: "40px",
            height: "40px",
            backgroundColor: "var(--color-accent)",
            border: "none",
            borderRadius: "8px",
            cursor: isUploading ? "not-allowed" : "pointer",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "20px",
            opacity: isUploading ? 0.5 : 1,
            transition: "opacity 0.2s",
          }}
          title="رفع ملف"
        >
          {isUploading ? "⏳" : "📎"}
        </button>

        {/* حقل إدخال النص */}
        <textarea
          value={message}
          onChange={(e) => setMessage(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="اكتب رسالتك هنا... (اضغط Enter للإرسال، Shift+Enter لسطر جديد)"
          style={{
            flex: 1,
            minHeight: "40px",
            maxHeight: "200px",
            padding: "10px",
            backgroundColor: "var(--color-bg-primary)",
            color: "var(--color-text-primary)",
            border: "1px solid var(--color-bg-tertiary)",
            borderRadius: "8px",
            fontSize: "14px",
            fontFamily: "var(--font-base)",
            resize: "vertical",
            outline: "none",
          }}
        />

        {/* زر الإرسال */}
        <button
          onClick={handleSend}
          disabled={!message.trim()}
          style={{
            width: "40px",
            height: "40px",
            backgroundColor: message.trim()
              ? "var(--color-accent)"
              : "var(--color-bg-tertiary)",
            border: "none",
            borderRadius: "8px",
            cursor: message.trim() ? "pointer" : "not-allowed",
            display: "flex",
            alignItems: "center",
            justifyContent: "center",
            fontSize: "20px",
            transition: "background-color 0.2s",
          }}
          title="إرسال"
        >
          ➤
        </button>
      </div>

      {/* شريط الأدوات الإضافية */}
      <div
        style={{
          display: "flex",
          alignItems: "center",
          gap: "8px",
          marginTop: "8px",
          fontSize: "12px",
          color: "var(--color-text-muted)",
        }}
      >
        <button
          style={{
            padding: "6px 12px",
            backgroundColor: "transparent",
            border: "1px solid var(--color-bg-tertiary)",
            borderRadius: "6px",
            color: "var(--color-text-secondary)",
            cursor: "pointer",
            fontSize: "12px",
            transition: "all 0.2s",
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = "var(--color-bg-tertiary)";
            e.target.style.color = "var(--color-text-primary)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "transparent";
            e.target.style.color = "var(--color-text-secondary)";
          }}
        >
          📷 صورة
        </button>
        <button
          style={{
            padding: "6px 12px",
            backgroundColor: "transparent",
            border: "1px solid var(--color-bg-tertiary)",
            borderRadius: "6px",
            color: "var(--color-text-secondary)",
            cursor: "pointer",
            fontSize: "12px",
            transition: "all 0.2s",
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = "var(--color-bg-tertiary)";
            e.target.style.color = "var(--color-text-primary)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "transparent";
            e.target.style.color = "var(--color-text-secondary)";
          }}
        >
          🎥 فيديو
        </button>
        <button
          style={{
            padding: "6px 12px",
            backgroundColor: "transparent",
            border: "1px solid var(--color-bg-tertiary)",
            borderRadius: "6px",
            color: "var(--color-text-secondary)",
            cursor: "pointer",
            fontSize: "12px",
            transition: "all 0.2s",
          }}
          onMouseEnter={(e) => {
            e.target.style.backgroundColor = "var(--color-bg-tertiary)";
            e.target.style.color = "var(--color-text-primary)";
          }}
          onMouseLeave={(e) => {
            e.target.style.backgroundColor = "transparent";
            e.target.style.color = "var(--color-text-secondary)";
          }}
        >
          🎵 صوت
        </button>
      </div>
    </div>
  );
}
